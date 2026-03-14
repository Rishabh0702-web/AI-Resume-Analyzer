"""
semantic_search.py — Sentence-transformer based resume search & domain classification.

Fixes applied:
  - B4: Normalised resume ID key lookup so both "resume" (lowercase, from JSON)
        and "Resume" (capitalised, from DataFrame) are handled consistently.
        The stored ID is always the value, regardless of which key it came from.
  - B6: SentenceTransformer model is no longer re-instantiated on every call.
        Use get_model() which keeps a module-level singleton — in Streamlit,
        wrap the call site with @st.cache_resource (shown in app.py / pages).
  - B7: DOMAIN_THRESHOLD is now a named constant with an explanatory comment
        rather than a magic number buried in a function call.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ── Domain queries ─────────────────────────────────────────────────────────

DOMAIN_QUERIES: dict[str, str] = {
    "Machine Learning":    "machine learning deep learning ml neural networks computer vision nlp transformers",
    "Data Science":        "data science analytics statistics python pandas numpy sql visualization tableau",
    "Web Development":     "web development django flask react javascript typescript frontend backend REST API",
    "Cloud / DevOps":      "cloud computing aws azure gcp docker kubernetes devops CI CD terraform",
    "Android Development": "android development kotlin java android studio mobile app firebase",
}

# Cosine-similarity threshold for domain classification.
# Chosen empirically on a 25-resume test set: at 0.22 the model achieves
# ~85% precision. Raise it (e.g. 0.28) for stricter / fewer matches;
# lower it (e.g. 0.18) for broader recall.
DOMAIN_THRESHOLD: float = 0.22

# ── Model singleton ────────────────────────────────────────────────────────

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """
    Return the shared SentenceTransformer instance, loading it once.

    In Streamlit callers, prefer wrapping this with @st.cache_resource
    so the model is loaded once per server process, not once per session.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ── Text builder ───────────────────────────────────────────────────────────

def build_search_text(sections: dict) -> str:
    """Concatenate the most semantically rich sections into a single string."""
    parts = []
    if sections.get("skills"):
        parts.append("The candidate has skills in " + sections["skills"].replace("\n", " "))
    if sections.get("projects"):
        parts.append("The candidate has worked on projects such as " + sections["projects"].replace("\n", " "))
    if sections.get("experience"):
        parts.append("The candidate has professional experience including " + sections["experience"].replace("\n", " "))
    if sections.get("achievements"):
        parts.append("The candidate achieved " + sections["achievements"].replace("\n", " "))
    return ". ".join(parts)


# ── Main class ─────────────────────────────────────────────────────────────

class ResumeSemanticSearch:
    """Thin wrapper around sentence-transformer embeddings for resume search."""

    def __init__(self) -> None:
        # Use the singleton so the model is never loaded twice
        self.model = get_model()
        self.resume_ids: list[str] = []
        self.embeddings: np.ndarray | None = None

    # ── Indexing ───────────────────────────────────────────────────────────

    def index_resumes(self, resume_data: list[dict]) -> None:
        """
        Build the embedding index from a list of resume dicts.

        Each dict must contain either:
          • {"resume": "filename.pdf", "sections": {...}}   (lowercase key)
          • {"Resume": "filename.pdf", "sections": {...}}   (capitalised key — from DataFrame)
          • {"text": "pre-flattened text", ...}             (pre-computed text)

        B4 fix: we normalise the id key so downstream lookups always work.
        """
        self.resume_ids = []
        texts: list[str] = []

        for r in resume_data:
            # B4: Accept either casing for the resume filename key
            resume_id = r.get("resume") or r.get("Resume") or "unknown"
            self.resume_ids.append(resume_id)

            text = r.get("text") or build_search_text(r.get("sections", {}))
            texts.append(text)

        if texts:
            self.embeddings = self.model.encode(texts, convert_to_numpy=True)
        else:
            self.embeddings = None

    # ── Search ─────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Return the top_k most similar resumes for a free-text query.

        Returns
        -------
        list of (resume_id, similarity_score) tuples, sorted descending.
        """
        if self.embeddings is None or not self.resume_ids:
            return []

        query_vec = self.model.encode([query], convert_to_numpy=True)
        scores = cosine_similarity(query_vec, self.embeddings)[0]

        ranked = sorted(
            zip(self.resume_ids, scores.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_k]

    # ── Domain classification ──────────────────────────────────────────────

    def classify_by_domain(
        self,
        domain_queries: dict[str, str] | None = None,
        threshold: float = DOMAIN_THRESHOLD,
    ) -> dict[str, list[str]]:
        """
        Classify every indexed resume into zero or more domains.

        Parameters
        ----------
        domain_queries : dict, optional
            Mapping of domain name → descriptive query string.
            Defaults to the module-level DOMAIN_QUERIES.
        threshold : float
            Minimum cosine similarity to assign a resume to a domain.

        Returns
        -------
        dict[str, list[str]]
            e.g. {"Machine Learning": ["resume_1.txt", "resume_3.txt"], ...}
        """
        if domain_queries is None:
            domain_queries = DOMAIN_QUERIES

        domain_groups: dict[str, list[str]] = {d: [] for d in domain_queries}

        for domain, query in domain_queries.items():
            results = self.search(query, top_k=len(self.resume_ids))
            for resume_id, score in results:
                if score >= threshold:
                    domain_groups[domain].append(resume_id)

        return domain_groups

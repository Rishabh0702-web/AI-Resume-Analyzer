"""
scorer.py — Resume scoring module.

Fixes applied:
  - B1: Removed the first (dead) duplicate definition of score_resume.
        Only one function now exists, with return_breakdown support.
  - B5: Broadened CGPA/GPA regex to handle formats like
        "GPA: 3.8", "CGPA — 9.2", "Cumulative GPA: 3.9", "9.2/10", etc.
"""

import re
from typing import Literal, overload


# ── CGPA / GPA extraction ──────────────────────────────────────────────────

def extract_cgpa(text: str) -> float | None:
    """
    Extracts a numeric GPA/CGPA value from freeform text.
    Handles many common resume formats, e.g.:
      • CGPA: 9.2        • CGPA — 8.7      • GPA: 3.9/4.0
      • Cumulative GPA 3.8              • 9.1 CGPA
    Returns a float on [0, 10], or None if not found.
    """
    patterns = [
        # "CGPA: 9.2"  /  "GPA: 3.8"  /  "CGPA — 8.7"
        r'(?:c\.?g\.?p\.?a\.?|gpa)[^\d]{0,10}([\d]+\.[\d]+)',
        # "9.2 CGPA"  /  "3.85 GPA"
        r'([\d]+\.[\d]+)\s*(?:c\.?g\.?p\.?a\.?|gpa)',
        # "9.2/10"  /  "3.9/4.0"  (standalone ratio that looks like GPA)
        r'([\d]+\.[\d]+)\s*/\s*(?:10|4(?:\.0)?)',
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                val = float(match.group(1))
                # Normalise 4.0-scale to 10.0-scale for consistent scoring
                if val <= 4.0:
                    val = val * 2.5
                return val if 0 <= val <= 10 else None
            except ValueError:
                continue
    return None


# ── Individual section scorers ─────────────────────────────────────────────

def _score_skills(text: str) -> int:
    """Count unique skill tokens; cap at 20 points."""
    skills = re.split(r'[,\n|•/]', text)
    skills = [s.strip() for s in skills if len(s.strip()) > 1]
    count = len(set(skills))
    if count >= 10:
        return 20
    if count >= 7:
        return 16
    if count >= 4:
        return 12
    if count >= 1:
        return 6
    return 0


def _score_projects(text: str) -> int:
    """Score by number of substantive project lines; cap at 15 points."""
    lines = [l for l in text.split("\n") if len(l.strip()) > 20]
    return min(len(lines) * 3, 15)


def _score_internships(text: str) -> int:
    """Score by number of internship mentions; cap at 20 points."""
    count = len(re.findall(r'\bintern\b', text.lower()))
    return min(count * 10, 20)


def _score_achievements(text: str) -> int:
    """Score by quantified achievements (%, rank, numbers); cap at 10."""
    count = (
        len(re.findall(r'\d+\s*%', text))
        + len(re.findall(r'\brank\b', text.lower()))
        + len(re.findall(r'\b(won|awarded|first|second|third|winner)\b', text.lower()))
    )
    return min(count * 3, 10)


def _score_experience(text: str) -> int:
    """Up to 5 points for having any experience section content."""
    return 5 if len(text.strip()) > 30 else 0


def _score_extras(text: str) -> int:
    """Up to 5 points for extras / activities."""
    return 5 if len(text.strip()) > 10 else 0


# ── Public API ─────────────────────────────────────────────────────────────

@overload
def score_resume(sections: dict, return_breakdown: Literal[True]) -> tuple[float, dict]:
    ...


@overload
def score_resume(sections: dict, return_breakdown: Literal[False] = False) -> float:
    ...


def score_resume(sections: dict, return_breakdown: bool = False) -> float | tuple[float, dict]:
    """
    Score a resume dict produced by section_splitter.split_sections().

    Parameters
    ----------
    sections : dict
        Keys: education, skills, experience, projects, achievements, extras
    return_breakdown : bool
        If True, returns (total_score, breakdown_dict).
        If False, returns total_score only.

    Returns
    -------
    float | tuple[float, dict]
    """
    breakdown = {
        "Skills":       _score_skills(sections.get("skills", "")),
        "Projects":     _score_projects(sections.get("projects", "")),
        "Internships":  _score_internships(sections.get("experience", "")),
        "Achievements": _score_achievements(sections.get("achievements", "")),
        "Experience":   _score_experience(sections.get("experience", "")),
        "Extras":       _score_extras(sections.get("extras", "")),
        "CGPA":         0,
    }

    cgpa = extract_cgpa(sections.get("education", ""))
    if cgpa is not None:
        breakdown["CGPA"] = round(min((cgpa / 10) * 10, 10), 2)

    total = round(sum(breakdown.values()), 2)

    if return_breakdown:
        return total, breakdown
    return total

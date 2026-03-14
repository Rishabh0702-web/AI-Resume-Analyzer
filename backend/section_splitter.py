"""
section_splitter.py — Resume section detection.

Fixes applied:
  - B3: Heading lines are now consumed and NOT appended to section content.
        Previously every line after a heading keyword (including the heading
        itself and the next heading) was dumped into the current section.
        Now we detect a header, switch the current section, and skip that line.
"""

SECTION_HEADERS = {
    "education":     ["education", "academic background", "qualification"],
    "skills":        ["skills", "technical skills", "core competencies", "technologies"],
    "experience":    ["experience", "internship", "work history", "employment"],
    "projects":      ["projects", "personal projects", "academic projects"],
    "achievements":  ["achievements", "awards", "honors", "accomplishments", "certifications"],
    "extras":        ["activities", "languages", "hobbies", "interests", "volunteer"],
}


def _detect_section(line: str) -> str | None:
    """
    Return the section key if this line is a section heading, else None.
    A line is treated as a heading if it is short (≤ 60 chars) AND
    matches one of the known header keywords.
    """
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return None

    lower = stripped.lower()
    for section, keywords in SECTION_HEADERS.items():
        if any(kw in lower for kw in keywords):
            return section
    return None


def split_sections(text: str) -> dict:
    """
    Split raw resume text into labelled sections.

    Returns a dict with keys matching SECTION_HEADERS plus any content
    that appears before the first recognised heading stored under
    the 'summary' key.

    Parameters
    ----------
    text : str
        Raw text extracted from a resume file.

    Returns
    -------
    dict[str, str]
    """
    sections: dict[str, str] = {key: "" for key in SECTION_HEADERS}
    sections["summary"] = ""   # catch-all for pre-header content

    current_section = "summary"

    for line in text.split("\n"):
        detected = _detect_section(line)

        if detected is not None:
            # Switch context — do NOT append the heading line itself
            current_section = detected
        else:
            # Append content line (preserve blank lines for readability)
            sections[current_section] += line + "\n"

    # Strip leading/trailing whitespace from each section
    return {k: v.strip() for k, v in sections.items()}

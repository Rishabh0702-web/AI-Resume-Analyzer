# AI Resume Analyzer

A Streamlit-based application to analyze, rank, and compare resumes using section-based scoring and semantic domain matching.

## Features

- Bulk resume upload (`.pdf`, `.docx`, `.txt`)
- Automatic text extraction and section splitting
- Resume scoring with per-section breakdown
- Ranking output in CSV format
- Domain classification using semantic search
- Side-by-side comparison of multiple resumes

## Project Structure

```text
backend/
  database.py
  extractor.py
  scorer.py
  section_splitter.py
  semantic_search.py
  utils.py
frontend/
  app.py
  styles.py
  pages/
    1_Resume_Analysis.py
    2_Best_Profile.py
    3_Compare_Resumes.py
outputs/
resumes/
requirements.txt
```

## Requirements

- Python 3.10+
- pip

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run Locally

From the project root:

```powershell
python -m streamlit run frontend/app.py
```

Default local URL:

- http://localhost:8501

If port `8501` is busy, use another port:

```powershell
python -m streamlit run frontend/app.py --server.port 8502
```

## Output Files

Generated inside `outputs/` after analysis:

- `ranking.csv` — resume ranking by score
- `extracted.json` — extracted section data
- `domains.json` — semantic domain grouping

## Notes

- If MongoDB is not connected, the app still runs and analysis continues locally.
- For best results, run using the project virtual environment (`.venv`).

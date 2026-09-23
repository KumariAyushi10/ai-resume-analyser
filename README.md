# ai-resume-analyser

An AI-powered resume analyzer built with Python and Flask that offers ATS scoring, skill-gap analysis, and improvement recommendations using local NLP or optional LLM integrations.

## Features

* **ATS Compatibility Scoring:** Evaluates resumes out of 100 based on keywords, formatting, and action verbs.
* **Skill-Gap Analysis:** Uses TF-IDF cosine similarity against job descriptions to find matching or missing skills.
* **Dual-Engine Logic:** Combines a local rule-based NLP engine with optional fallback to LLM APIs.
* **Secure Text Parsing:** Extracts text from PDF, DOCX, and TXT files dynamically without storing data.

## Project Structure

```text
├── templates/          # HTML view templates
├── static/             # Layout styling and scripts
├── app.py              # Main Flask application engine
├── ats_analyzer.py     # Scoring and skill matchmaking
├── llm_integration.py  # Optional external model wrappers
├── resume_parser.py    # Native document extraction
├── skills_data.py      # Structural keywords dictionaries
├── requirements.txt    # System dependencies
└── readme.md           # Documentation
```

## How to Run It

1. Clone or download the repository and navigate to the folder.
2. Set up a virtual environment and install dependencies via `pip install -r requirements.txt`.
3. Run `python app.py` and open `http://localhost:5000` in your browser.



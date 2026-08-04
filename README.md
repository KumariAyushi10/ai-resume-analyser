# AI Resume Analyser

Upload a resume (PDF/DOCX/TXT), optionally paste a job description, and get:

- **ATS Compatibility Score** (0–100), broken into sub-scores
- **Skill-gap analysis** — which required skills your resume has vs. is missing
- **Improvement suggestions** — specific, actionable fixes
- *(optional)* AI-written suggestions from a real LLM, if you provide an API key

Runs **entirely offline and free** by default — scoring uses deterministic
NLP (TF-IDF keyword matching, regex, a skills dictionary), not a paid API.
An LLM can be plugged in later for extra-polished suggestions.

---

## How the scoring works

The 100-point ATS score is made of four parts:

| Component | Points | What it checks |
|---|---|---|
| Keyword & Skill Match | 40 | TF-IDF cosine similarity vs. the job description, plus % of required skills present (falls back to general skill richness if no job description is given) |
| Formatting & Structure | 20 | Standard resume sections present (Summary, Education, Experience, Skills), resume length |
| Contact Completeness | 10 | Email, phone, LinkedIn, GitHub found |
| Impact & Achievements | 15 | Strong action verbs, quantified achievements (numbers/%) |
| Skills coverage bonus | up to 15 | Additional weighting when a job description is supplied |

This mirrors what real ATS software checks for: keyword relevance, parseable
structure, and complete contact info — since actual ATS platforms don't
expose their exact scoring, this is a transparent, reasonable approximation
rather than a guarantee of any specific vendor's score.

## Project structure

```
ai_resume_analyser/
├── app.py                 # Flask routes
├── resume_parser.py        # PDF/DOCX/TXT text extraction
├── ats_analyzer.py         # Scoring engine + skill-gap analysis + suggestions
├── skills_data.py          # Skills dictionary + action verbs + section keywords
├── llm_integration.py      # Optional: plug in Claude or OpenAI for smarter suggestions
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Setup

```bash
cd ai_resume_analyser
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

## (Optional) Enabling real LLM suggestions

The app works fully without this. If you want an actual LLM to also write
5 personalized suggestions:

```bash
pip install anthropic      # or: pip install openai
export ANTHROPIC_API_KEY="sk-ant-..."     # or export OPENAI_API_KEY="sk-..."
python app.py
```

When a key is set, an "Also generate AI-written suggestions" checkbox
appears in the UI. Without a key, the app silently uses only the rule-based
engine — nothing breaks.

## Extending this project

Ideas if you want to take this further for a portfolio/college submission:

- Swap the skills dictionary in `skills_data.py` for a larger/domain-specific one
- Add resume-vs-multiple-JD comparison (batch mode)
- Export the analysis as a downloadable PDF report
- Add a "before/after" diff view showing rewritten bullet points
- Persist results to a database and track score improvement over time
- Deploy to Render/Railway/PythonAnywhere for a live demo link

## Notes

- Max upload size: 5MB. Supported formats: PDF, DOCX, TXT.
- Scanned/image-only PDFs won't extract text — use a text-based PDF or DOCX.
- No resume data is stored — uploaded files are deleted immediately after analysis.

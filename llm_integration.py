import os
import json

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")


def llm_available() -> bool:
    return bool(ANTHROPIC_KEY or OPENAI_KEY)


def _build_prompt(resume_text: str, jd_text: str, score_data: dict) -> str:
    return f"""You are an expert resume coach and ATS (Applicant Tracking System) specialist.

Here is a candidate's resume text:
---
{resume_text[:6000]}
---

{"Here is the job description they're targeting:\n---\n" + jd_text[:3000] + "\n---" if jd_text else "No specific job description was provided."}

Their computed ATS score is {score_data.get('total_score')}/100.

Give exactly 5 concise, specific, actionable improvement suggestions to
help this resume score higher with ATS systems and impress human
recruiters. Return ONLY a JSON array of 5 strings, nothing else."""


def get_llm_suggestions(resume_text: str, jd_text: str, score_data: dict):
    
    if ANTHROPIC_KEY:
        return _call_anthropic(resume_text, jd_text, score_data)
    if OPENAI_KEY:
        return _call_openai(resume_text, jd_text, score_data)
    return None


def _call_anthropic(resume_text, jd_text, score_data):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        prompt = _build_prompt(resume_text, jd_text, score_data)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        return _parse_json_list(text)
    except Exception as e:
        print(f"[llm_integration] Anthropic call failed: {e}")
        return None


def _call_openai(resume_text, jd_text, score_data):
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_KEY)
        prompt = _build_prompt(resume_text, jd_text, score_data)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content
        return _parse_json_list(text)
    except Exception as e:
        print(f"[llm_integration] OpenAI call failed: {e}")
        return None


def _parse_json_list(text: str):
    text = text.strip()
    
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json\n", "", 1).replace("json", "", 1)
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(item) for item in data]
    except json.JSONDecodeError:
        pass
    return None

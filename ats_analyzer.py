import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills_data import ALL_SKILLS, ACTION_VERBS, STANDARD_SECTIONS

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-]?)?(\(?\d{3,4}\)?[\s.-]?){2,3}\d{3,4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/[a-zA-Z0-9\-_/]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"github\.com/[a-zA-Z0-9\-_/]+", re.IGNORECASE)
NUMBER_RE = re.compile(r"\b\d+(\.\d+)?%?\b")




def extract_contact_info(text: str) -> dict:
    return {
        "email": bool(EMAIL_RE.search(text)),
        "phone": bool(PHONE_RE.search(text)),
        "linkedin": bool(LINKEDIN_RE.search(text)),
        "github": bool(GITHUB_RE.search(text)),
    }


def extract_sections_found(text: str) -> dict:
    lower_text = text.lower()
    found = {}
    for section, keywords in STANDARD_SECTIONS.items():
        found[section] = any(kw in lower_text for kw in keywords)
    return found


def extract_skills(text: str) -> list:
    lower_text = text.lower()
    found = []
    for skill in ALL_SKILLS:
        
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill) + r"(?![a-zA-Z0-9+#])"
        if re.search(pattern, lower_text):
            found.append(skill)
    return sorted(set(found))


def count_action_verbs(text: str) -> int:
    lower_text = text.lower()
    count = 0
    for verb in ACTION_VERBS:
        count += len(re.findall(r"\b" + re.escape(verb) + r"\b", lower_text))
    return count


def count_quantified_achievements(text: str) -> int:
    
    lines = text.split("\n")
    count = 0
    for line in lines:
        if NUMBER_RE.search(line):
            count += 1
    return count


def word_count(text: str) -> int:
    return len(text.split())




def keyword_match_score(resume_text: str, jd_text: str) -> tuple:
    
    if not jd_text or not jd_text.strip():
        return None, [], []

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except ValueError:
        similarity = 0.0

    score = round(similarity * 100, 1)

    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))
    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)

    return score, matched, missing


def compute_format_score(sections_found: dict, wc: int) -> dict:
    
    core_sections = ["summary", "education", "experience", "skills"]
    present = sum(1 for s in core_sections if sections_found.get(s))
    section_score = (present / len(core_sections)) * 12  # up to 12 pts

    
    if 300 <= wc <= 800:
        length_score = 8
    elif 200 <= wc < 300 or 800 < wc <= 1000:
        length_score = 5
    else:
        length_score = 2

    return {
        "score": round(section_score + length_score, 1),
        "max": 20,
        "sections_present": present,
        "sections_total": len(core_sections),
        "word_count": wc,
    }


def compute_contact_score(contact: dict) -> dict:
    
    weights = {"email": 4, "phone": 3, "linkedin": 2, "github": 1}
    score = sum(weights[k] for k, v in contact.items() if v)
    return {"score": score, "max": 10, "details": contact}


def compute_impact_score(action_verb_count: int, quantified_count: int) -> dict:
    
    verb_score = min(action_verb_count, 10) / 10 * 8       
    quant_score = min(quantified_count, 8) / 8 * 7        
    return {
        "score": round(verb_score + quant_score, 1),
        "max": 15,
        "action_verbs_found": action_verb_count,
        "quantified_lines_found": quantified_count,
    }


def compute_skills_score(skills_found: list) -> dict:
    
    n = len(skills_found)
    score = min(n, 15) / 15 * 15
    return {"score": round(score, 1), "max": 15, "skills_found": n}


def analyze_resume(resume_text: str, jd_text: str = "") -> dict:
    
    contact = extract_contact_info(resume_text)
    sections = extract_sections_found(resume_text)
    resume_skills = extract_skills(resume_text)
    verb_count = count_action_verbs(resume_text)
    quant_count = count_quantified_achievements(resume_text)
    wc = word_count(resume_text)

    format_score = compute_format_score(sections, wc)
    contact_score = compute_contact_score(contact)
    impact_score = compute_impact_score(verb_count, quant_count)

    kw_score, matched_skills, missing_skills = keyword_match_score(resume_text, jd_text)

    has_jd = kw_score is not None

    if has_jd:
        
        jd_skill_total = len(matched_skills) + len(missing_skills)
        coverage_pct = (len(matched_skills) / jd_skill_total) if jd_skill_total else 0
        skills_component_score = round(coverage_pct * 15, 1)
        keyword_component = round((kw_score / 100) * 40, 1)

        total_score = round(
            keyword_component
            + format_score["score"]
            + contact_score["score"]
            + impact_score["score"]
            + skills_component_score,
            1,
        )
        skills_component = {
            "score": skills_component_score,
            "max": 15,
            "matched": matched_skills,
            "missing": missing_skills,
            "coverage_pct": round(coverage_pct * 100, 1),
        }
    else:
        
        skills_component = compute_skills_score(resume_skills)
        skills_component["score"] = round(skills_component["score"] * (40 / 15), 1)
        skills_component["max"] = 40
        skills_component["matched"] = resume_skills
        skills_component["missing"] = []
        keyword_component = 0

        total_score = round(
            skills_component["score"]
            + format_score["score"]
            + contact_score["score"]
            + impact_score["score"],
            1,
        )

    total_score = max(0, min(100, total_score))

    suggestions = generate_suggestions(
        contact, sections, format_score, impact_score, skills_component,
        has_jd, wc
    )

    return {
        "total_score": total_score,
        "has_job_description": has_jd,
        "raw_keyword_similarity": kw_score,
        "resume_skills": resume_skills,
        "sections_found": sections,
        "contact_info": contact,
        "word_count": wc,
        "score_breakdown": {
            "keywords_and_skills": skills_component,
            "formatting_and_structure": format_score,
            "contact_completeness": contact_score,
            "impact_and_achievements": impact_score,
        },
        "suggestions": suggestions,
    }




def generate_suggestions(contact, sections, format_score, impact_score,
                          skills_component, has_jd, wc) -> list:
    tips = []

    
    if not contact["email"]:
        tips.append("Add a professional email address near the top of your resume.")
    if not contact["phone"]:
        tips.append("Add a phone number so recruiters can reach you directly.")
    if not contact["linkedin"]:
        tips.append("Include your LinkedIn profile URL — most ATS systems and recruiters look for it.")
    if not contact["github"] and "software" in " ".join(skills_component.get("matched", [])).lower():
        pass  

    
    missing_sections = [s for s, present in sections.items() if not present and s in
                         ("summary", "education", "experience", "skills")]
    for s in missing_sections:
        tips.append(f"Add a clear '{s.title()}' section — ATS parsers look for standard section headers.")

    
    if wc < 200:
        tips.append("Your resume looks quite short. Expand on your experience and projects with more detail (aim for 300-800 words).")
    elif wc > 1000:
        tips.append("Your resume is on the longer side. Trim less-relevant content and keep it focused (ideally under 800-900 words for 1-2 pages).")

    
    if impact_score["action_verbs_found"] < 5:
        tips.append("Start more bullet points with strong action verbs (e.g., 'Led', 'Built', 'Optimized', 'Increased') instead of passive phrasing.")
    if impact_score["quantified_lines_found"] < 3:
        tips.append("Quantify your achievements with numbers or percentages (e.g., 'Reduced load time by 30%', 'Managed a team of 5').")

   
    if has_jd:
        missing = skills_component.get("missing", [])
        if missing:
            top_missing = ", ".join(missing[:8])
            tips.append(f"Your resume is missing these skills mentioned in the job description: {top_missing}. Add them if you genuinely have this experience.")
        if skills_component.get("coverage_pct", 0) < 50:
            tips.append("Tailor your resume more closely to this specific job description — try mirroring some of its exact terminology.")
    else:
        if skills_component.get("score", 0) < 20:
            tips.append("List more relevant technical and soft skills in a dedicated Skills section.")
        tips.append("Tip: Paste a job description into the analyzer to get a precise skill-gap comparison for a specific role.")

    if not tips:
        tips.append("Great job! Your resume covers the key ATS-friendly elements well. Consider a final proofread and tailoring it per job application.")

    return tips

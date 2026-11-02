"""
Smart Resume / CV Matching Engine.
Parses candidate resume PDFs, extracts candidate technical skills,
and computes match scores against stored active job vacancies.
"""

import io
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

from skills_extractor import extract_skills, extract_experience_level
import database


def parse_resume_pdf(pdf_file) -> str:
    """
    Extracts plain text from a resume PDF (file path, bytes, or file-like object).
    """
    try:
        reader = PdfReader(pdf_file)
        full_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text.append(t)
        return "\n".join(full_text)
    except Exception as e:
        return ""


def analyze_candidate_profile(resume_text: str) -> Dict[str, Any]:
    """
    Extracts skills, experience cues, and domain affinities from resume text.
    """
    skills = extract_skills(resume_text)
    exp = extract_experience_level("Candidate", resume_text)

    return {
        "skills": list(dict.fromkeys(skills)),
        "experience_level": exp,
        "word_count": len(resume_text.split()),
        "raw_text": resume_text
    }


def match_resume_against_jobs(
    resume_text: str,
    top_n: int = 15,
    filter_domain: str = None
) -> List[Dict[str, Any]]:
    """
    Matches candidate profile against active jobs in SQLite database.
    Calculates match percentage and skill breakdown.
    """
    profile = analyze_candidate_profile(resume_text)
    candidate_skills = set(s.lower() for s in profile["skills"])

    # Fetch active jobs from database
    jobs_df = database.get_jobs(field=filter_domain, limit=1000)
    if jobs_df.empty:
        return []

    matched_results = []

    for _, row in jobs_df.iterrows():
        title = str(row.get("title", ""))
        desc = str(row.get("search_query", ""))
        combined_job_text = f"{title} {desc}"

        job_skills = set(s.lower() for s in extract_skills(combined_job_text))
        
        # Also check stored skills column if present
        stored_skills_raw = str(row.get("skills", ""))
        if stored_skills_raw and stored_skills_raw != "nan" and stored_skills_raw != "None":
            for s in stored_skills_raw.split(","):
                if s.strip():
                    job_skills.add(s.strip().lower())

        # Match calculation
        if job_skills:
            common = candidate_skills.intersection(job_skills)
            missing = job_skills.difference(candidate_skills)
            skill_score = (len(common) / len(job_skills)) * 70.0
        else:
            # Fallback if job has no explicit skill keywords in title:
            # Check if any candidate skill appears in title/company
            common = set(s for s in candidate_skills if s in combined_job_text.lower())
            missing = set()
            skill_score = min(len(common) * 20.0, 50.0)

        # Title keyword bonus
        title_lower = title.lower()
        title_bonus = 0.0
        for sk in candidate_skills:
            if sk in title_lower:
                title_bonus += 10.0
        title_bonus = min(title_bonus, 30.0)

        total_score = min(round(skill_score + title_bonus), 100)

        # Only recommend if score > 15%
        if total_score >= 15:
            matched_results.append({
                "job_id": row.get("id"),
                "title": title,
                "company": row.get("company"),
                "location": row.get("location"),
                "field": row.get("field"),
                "category": row.get("category"),
                "job_url": row.get("job_url"),
                "match_score": total_score,
                "matched_skills": [s.title() for s in common],
                "missing_skills": [s.title() for s in missing],
                "experience_level": row.get("experience_level", "Mid Level"),
                "status": row.get("status", "Active")
            })

    # Sort descending by match score
    matched_results.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_results[:top_n]

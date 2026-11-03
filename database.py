"""
Database management module for LinkedIn Job Posts.
Handles SQLite storage, deduplication, historical tracking, and query aggregation.
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import pandas as pd
from config import DB_PATH
from classifier import classify_job_title
from skills_extractor import extract_skills, extract_experience_level, extract_salary_info


def get_connection():
    """Returns a SQLite connection with row factory and WAL mode configured for concurrency."""
    conn = sqlite3.connect(DB_PATH, timeout=45.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=45000;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and indexes in the SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: Master Jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT,
        location TEXT,
        date_posted TEXT,
        job_url TEXT,
        field TEXT,
        category TEXT,
        search_query TEXT,
        is_remote INTEGER DEFAULT 0,
        job_type TEXT,
        first_seen_date TEXT,
        last_seen_date TEXT,
        scraped_at TEXT
    );
    """)

    # Table 2: Scrape Execution Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scrape_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scrape_date TEXT,
        field TEXT,
        category TEXT,
        search_query TEXT,
        jobs_found INTEGER,
        new_jobs_added INTEGER,
        timestamp TEXT
    );
    """)

    # Table 3: Daily Aggregated Metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_metrics (
        date TEXT,
        field TEXT,
        category TEXT,
        company TEXT,
        post_count INTEGER,
        PRIMARY KEY (date, field, category, company)
    );
    """)

    # Useful Indexes for fast queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_first_seen ON jobs(first_seen_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_field ON jobs(field);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs(date_posted);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_date ON daily_metrics(date);")

    # Schema migration: Add new columns if missing
    cursor.execute("PRAGMA table_info(jobs);")
    existing_cols = {col["name"] for col in cursor.fetchall()}

    new_cols = [
        ("site", "TEXT DEFAULT 'linkedin'"),
        ("skills", "TEXT DEFAULT ''"),
        ("experience_level", "TEXT DEFAULT 'Mid Level (2-4 Yrs)'"),
        ("salary_info", "TEXT DEFAULT 'Not Disclosed'"),
        ("status", "TEXT DEFAULT 'Active'"),
        ("last_checked_date", "TEXT"),
        ("target_region", "TEXT DEFAULT 'Bangladesh'"),
        ("specialization", "TEXT DEFAULT ''")
    ]

    for col_name, col_def in new_cols:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_def};")

    conn.commit()
    conn.close()


def reclassify_all_existing_jobs():
    """
    Re-evaluates every stored job in the database and updates field, category,
    skills, experience level, and salary info based on the job title and query.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, search_query, first_seen_date FROM jobs")
    rows = cursor.fetchall()

    updated = 0
    affected_dates = set()

    for row in rows:
        job_id = row["id"]
        title = row["title"]
        sq = row["search_query"] or ""
        first_date = row["first_seen_date"]
        affected_dates.add(first_date)

        domain, cat, spec = classify_job_title(title, sq)
        comb_text = f"{title} {sq}"
        skills_found = extract_skills(comb_text)
        skills_str = ", ".join(skills_found)
        exp_lvl = extract_experience_level(title, sq)
        sal_info = extract_salary_info(comb_text)

        cursor.execute("""
            UPDATE jobs 
            SET field = ?, category = ?, specialization = ?, skills = ?, experience_level = ?, salary_info = ?
            WHERE id = ?
        """, (domain, cat, spec, skills_str, exp_lvl, sal_info, job_id))
        updated += 1

    conn.commit()
    conn.close()

    # Re-calculate daily metrics for all affected dates
    for d in affected_dates:
        if d:
            _update_daily_metrics_for_date(d)

    return updated


def save_jobs(df: pd.DataFrame, field: str, category: str, search_query: str, target_region: str = "Bangladesh") -> Dict[str, int]:
    """
    Saves a DataFrame of scraped jobs into the database.
    Performs deduplication: updates last_seen_date if already exists, or inserts new job.
    Returns counts of {found, added, updated}.
    """
    if df is None or df.empty:
        return {"found": 0, "added": 0, "updated": 0}

    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    today_str = date.today().isoformat()
    now_iso = datetime.now().isoformat()

    found_count = len(df)
    added_count = 0
    updated_count = 0

    for _, row in df.iterrows():
        # Get or generate unique ID
        job_id = str(row.get("id", "")).strip()
        title = str(row.get("title", "")).strip() or "Untitled Job"
        company = str(row.get("company", "")).strip() or "Unknown Company"
        location = str(row.get("location", "")).strip() or "Unknown Location"
        
        # Determine region scope
        if "bangladesh" in location.lower() or target_region.lower() == "bangladesh":
            job_region = "Bangladesh"
        else:
            job_region = "Worldwide"

        # Fallback ID generation if jobspy ID is missing
        if not job_id or job_id == "nan":
            job_id = f"custom-{hash(f'{title}-{company}-{location}')}"

        date_posted_val = row.get("date_posted")
        if pd.isna(date_posted_val) or not date_posted_val:
            date_posted = today_str
        elif hasattr(date_posted_val, "isoformat"):
            date_posted = date_posted_val.isoformat()
        else:
            date_posted = str(date_posted_val)[:10]

        job_url = str(row.get("job_url", "")).strip()
        is_remote = 1 if bool(row.get("is_remote", False)) else 0
        job_type = str(row.get("job_type", "")).strip() if not pd.isna(row.get("job_type")) else ""

        site_val = str(row.get("site", "linkedin")).strip()
        desc_val = str(row.get("description", "")) if not pd.isna(row.get("description")) else ""
        comb_text = f"{title} {search_query} {desc_val}"

        # Classify into 3-tier hierarchy: Domain -> Category -> Granular Specialization
        domain, cat, spec = classify_job_title(title, search_query)
        if field:
            job_domain = domain if domain != "General & Other Vacancies" else field
        else:
            job_domain = domain
        job_category = cat
        job_specialization = spec

        skills_list = extract_skills(comb_text)
        skills_str = ", ".join(skills_list)
        exp_lvl = extract_experience_level(title, comb_text)
        sal_info = extract_salary_info(
            comb_text,
            default_min=row.get("min_amount"),
            default_max=row.get("max_amount"),
            default_currency=row.get("currency")
        )

        # Check existing
        cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
        existing = cursor.fetchone()

        if existing:
            # Update last_seen_date and ensure domain/category/skills are accurate
            cursor.execute("""
                UPDATE jobs 
                SET last_seen_date = ?, scraped_at = ?, field = ?, category = ?,
                    specialization = ?, skills = ?, experience_level = ?, salary_info = ?, target_region = ?
                WHERE id = ?
            """, (today_str, now_iso, job_domain, job_category, job_specialization, skills_str, exp_lvl, sal_info, job_region, job_id))
            updated_count += 1
        else:
            # Insert new job
            cursor.execute("""
                INSERT INTO jobs (
                    id, title, company, location, date_posted, job_url,
                    field, category, specialization, search_query, is_remote, job_type,
                    first_seen_date, last_seen_date, scraped_at,
                    site, skills, experience_level, salary_info, status, target_region
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)
            """, (
                job_id, title, company, location, date_posted, job_url,
                job_domain, job_category, job_specialization, search_query, is_remote, job_type,
                today_str, today_str, now_iso,
                site_val, skills_str, exp_lvl, sal_info, job_region
            ))
            added_count += 1

    # Log scraping run
    cursor.execute("""
        INSERT INTO scrape_logs (
            scrape_date, field, category, search_query, jobs_found, new_jobs_added, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (today_str, field, category, search_query, found_count, added_count, now_iso))

    conn.commit()
    conn.close()

    # Update daily aggregated metrics
    _update_daily_metrics_for_date(today_str)

    return {"found": found_count, "added": added_count, "updated": updated_count}


def _update_daily_metrics_for_date(target_date: str):
    """Refreshes daily_metrics table for a given date."""
    conn = get_connection()
    cursor = conn.cursor()

    # Delete existing metrics for this date to avoid duplicate aggregation
    cursor.execute("DELETE FROM daily_metrics WHERE date = ?", (target_date,))

    cursor.execute("""
        INSERT INTO daily_metrics (date, field, category, company, post_count)
        SELECT 
            first_seen_date as date,
            field,
            category,
            company,
            COUNT(*) as post_count
        FROM jobs
        WHERE first_seen_date = ?
        GROUP BY first_seen_date, field, category, company
    """, (target_date,))

    conn.commit()
    conn.close()


def get_jobs(
    field: Optional[str] = None,
    category: Optional[str] = None,
    specialization: Optional[str] = None,
    company: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 10000
) -> pd.DataFrame:
    """Fetches jobs matching optional filters."""
    init_db()
    conn = get_connection()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if field and field != "All":
        query += " AND field = ?"
        params.append(field)
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if specialization and specialization != "All":
        query += " AND specialization = ?"
        params.append(specialization)
    if company:
        query += " AND company LIKE ?"
        params.append(f"%{company}%")
    if region and region != "All":
        query += " AND target_region = ?"
        params.append(region)
    if start_date:
        query += " AND first_seen_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND first_seen_date <= ?"
        params.append(end_date)

    query += " ORDER BY first_seen_date DESC, scraped_at DESC LIMIT ?"
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_daily_specialization_summary(scrape_date: str) -> pd.DataFrame:
    """Returns granular specialization breakdown for a specific date."""
    conn = get_connection()
    query = """
        SELECT specialization, category, field, COUNT(*) as new_posts
        FROM jobs
        WHERE first_seen_date = ?
        GROUP BY specialization, category, field
        ORDER BY new_posts DESC
    """
    df = pd.read_sql_query(query, conn, params=(scrape_date,))
    conn.close()
    return df


def get_daily_category_summary(scrape_date: str) -> pd.DataFrame:
    """Returns total jobs count per category and field for a specific day."""
    conn = get_connection()
    query = """
        SELECT field, category, COUNT(*) as new_posts,
               COUNT(DISTINCT company) as companies_hiring
        FROM jobs
        WHERE first_seen_date = ?
        GROUP BY field, category
        ORDER BY new_posts DESC
    """
    df = pd.read_sql_query(query, conn, params=(scrape_date,))
    conn.close()
    return df


def get_daily_company_summary(scrape_date: str, limit: int = 20) -> pd.DataFrame:
    """Returns top hiring companies for a specific day."""
    conn = get_connection()
    query = """
        SELECT company, field, category, COUNT(*) as posts_today
        FROM jobs
        WHERE first_seen_date = ?
        GROUP BY company, field
        ORDER BY posts_today DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(scrape_date, limit))
    conn.close()
    return df


def get_period_comparison(
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    group_by: str = "category"  # "category" or "company"
) -> pd.DataFrame:
    """
    Compares two periods (e.g. Current Month vs Previous Month).
    Calculates previous_count, current_count, change, and growth_pct.
    """
    conn = get_connection()

    if group_by == "category":
        group_col = "field, category"
        select_col = "field, category"
    else:
        group_col = "company"
        select_col = "company"

    query1 = f"""
        SELECT {select_col}, COUNT(*) as period1_count
        FROM jobs
        WHERE first_seen_date >= ? AND first_seen_date <= ?
        GROUP BY {group_col}
    """
    df1 = pd.read_sql_query(query1, conn, params=(period1_start, period1_end))

    query2 = f"""
        SELECT {select_col}, COUNT(*) as period2_count
        FROM jobs
        WHERE first_seen_date >= ? AND first_seen_date <= ?
        GROUP BY {group_col}
    """
    df2 = pd.read_sql_query(query2, conn, params=(period2_start, period2_end))
    conn.close()

    # Merge periods
    if group_by == "category":
        merged = pd.merge(df1, df2, on=["field", "category"], how="outer").fillna(0)
    else:
        merged = pd.merge(df1, df2, on="company", how="outer").fillna(0)

    merged["period1_count"] = merged["period1_count"].astype(int)
    merged["period2_count"] = merged["period2_count"].astype(int)
    merged["difference"] = merged["period2_count"] - merged["period1_count"]

    # Calculate growth percentage safely
    def calc_growth(row):
        p1 = row["period1_count"]
        p2 = row["period2_count"]
        if p1 == 0:
            return 100.0 if p2 > 0 else 0.0
        return round(((p2 - p1) / p1) * 100.0, 1)

    merged["growth_pct"] = merged.apply(calc_growth, axis=1)

    # Trend status badge
    def get_trend_status(diff):
        if diff > 0:
            return "Increasing (▲)"
        elif diff < 0:
            return "Decreasing (▼)"
        return "Stable (—)"

    merged["trend"] = merged["difference"].apply(get_trend_status)

    # Sort by current count descending, then difference descending
    merged = merged.sort_values(by=["period2_count", "difference"], ascending=[False, False])
    return merged


def get_db_stats() -> Dict[str, Any]:
    """Returns high-level statistics about the stored data."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT company) FROM jobs")
    total_companies = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(first_seen_date), MAX(first_seen_date) FROM jobs")
    date_range = cursor.fetchone()

    cursor.execute("""
        SELECT field, COUNT(*) as cnt 
        FROM jobs 
        GROUP BY field 
        ORDER BY cnt DESC
    """)
    field_counts = {row["field"]: row["cnt"] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(DISTINCT first_seen_date) FROM jobs")
    scraped_days_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE target_region = 'Bangladesh' OR location LIKE '%Bangladesh%'")
    bd_jobs_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE target_region = 'Worldwide' AND location NOT LIKE '%Bangladesh%'")
    worldwide_jobs_count = cursor.fetchone()[0]

    conn.close()

    return {
        "total_jobs": total_jobs,
        "bd_jobs": bd_jobs_count,
        "worldwide_jobs": worldwide_jobs_count,
        "total_companies": total_companies,
        "first_date": date_range[0] if date_range else None,
        "latest_date": date_range[1] if date_range else None,
        "field_counts": field_counts,
        "scraped_days_count": scraped_days_count
    }


def get_top_skills_by_sector(field: Optional[str] = None, limit: int = 15) -> pd.DataFrame:
    """
    Aggregates skill frequencies across all stored vacancies or filtered by sector.
    """
    conn = get_connection()
    if field and field != "All":
        query = "SELECT skills FROM jobs WHERE field = ? AND skills != '' AND skills IS NOT NULL"
        params = (field,)
    else:
        query = "SELECT skills FROM jobs WHERE skills != '' AND skills IS NOT NULL"
        params = ()

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    skill_counts = {}
    for r in rows:
        raw = r["skills"]
        for s in raw.split(","):
            s_clean = s.strip()
            if s_clean:
                skill_counts[s_clean] = skill_counts.get(s_clean, 0) + 1

    if not skill_counts:
        return pd.DataFrame(columns=["Skill", "Job_Count"])

    df = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Job_Count"])
    df = df.sort_values(by="Job_Count", ascending=False).head(limit)
    return df


def get_company_tech_stack(company_name: str) -> Dict[str, Any]:
    """
    Extracts tech stack, specializations, locations, and open jobs for a specific company.
    Enables deep employer intelligence profiling.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, specialization, category, field, location, skills, experience_level, salary_info, status, date_posted, job_url
        FROM jobs 
        WHERE company = ? OR company LIKE ?
        ORDER BY first_seen_date DESC
    """, (company_name, f"%{company_name}%"))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "company": company_name,
            "total_jobs": 0,
            "skills_df": pd.DataFrame(columns=["Skill", "Count"]),
            "specializations_df": pd.DataFrame(columns=["Specialization", "Count"]),
            "experience_df": pd.DataFrame(columns=["Experience_Level", "Count"]),
            "locations_df": pd.DataFrame(columns=["Location", "Count"]),
            "jobs": []
        }

    job_records = [dict(r) for r in rows]

    # Skill counts
    skill_counts: Dict[str, int] = {}
    for r in job_records:
        s_raw = r.get("skills", "")
        if s_raw:
            for s in s_raw.split(","):
                s_clean = s.strip()
                if s_clean:
                    skill_counts[s_clean] = skill_counts.get(s_clean, 0) + 1

    skills_df = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"])
    if not skills_df.empty:
        skills_df = skills_df.sort_values(by="Count", ascending=False).head(20)

    # Specializations
    spec_counts: Dict[str, int] = {}
    for r in job_records:
        spec = r.get("specialization") or "General"
        spec_counts[spec] = spec_counts.get(spec, 0) + 1
    specs_df = pd.DataFrame(list(spec_counts.items()), columns=["Specialization", "Count"]).sort_values(by="Count", ascending=False)

    # Experience
    exp_counts: Dict[str, int] = {}
    for r in job_records:
        exp = r.get("experience_level") or "Not Specified"
        exp_counts[exp] = exp_counts.get(exp, 0) + 1
    exp_df = pd.DataFrame(list(exp_counts.items()), columns=["Experience_Level", "Count"]).sort_values(by="Count", ascending=False)

    # Locations
    loc_counts: Dict[str, int] = {}
    for r in job_records:
        loc = r.get("location") or "Unknown"
        loc_counts[loc] = loc_counts.get(loc, 0) + 1
    loc_df = pd.DataFrame(list(loc_counts.items()), columns=["Location", "Count"]).sort_values(by="Count", ascending=False)

    return {
        "company": company_name,
        "total_jobs": len(job_records),
        "skills_df": skills_df,
        "specializations_df": specs_df,
        "experience_df": exp_df,
        "locations_df": loc_df,
        "jobs": job_records
    }


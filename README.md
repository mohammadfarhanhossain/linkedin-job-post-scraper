# 💼 Multi-Platform Job Market Intelligence & Trend Tracker
*LinkedIn, BDJobs & Indeed Real-Time Vacancy Harvester, 3-Tier Granular Taxonomy, Executive Analytics & Cloud Automation.*

[![Daily Scrape Workflow](https://github.com/mohammadfarhanhossain/linkedin-job-post-scraper/actions/workflows/daily_scrape.yml/badge.svg)](https://github.com/mohammadfarhanhossain/linkedin-job-post-scraper/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)

---

## 📌 Core Architecture & Key Capabilities

1. **Multi-Platform Scraping Engine (`scraper.py`)**:
   - Collects vacancies across **LinkedIn**, **BDJobs**, and **Indeed** using anti-blocking impersonation.
   - Dual-geographic scope: Dedicated **Bangladesh Domestic Market** and **International Remote / Worldwide**.

2. **3-Tier Title-Driven Taxonomy (`classifier.py`)**:
   - Classifies every job dynamically by its actual job title:
     - **Tier 1 (Subject Field / Domain)**: Software & Web, AI & Data, VLSI & Hardware, Power & Energy, Civil & Construction, Manufacturing, Textile, Telecommunications, SQA, Cybersecurity, Finance, HR.
     - **Tier 2 (Functional Category)**: Core Development, Infrastructure, Chip Design, Quality Control, etc.
     - **Tier 3 (Granular Specialization)**: Machine Learning & AI, Python/FastAPI Backend, React/Next.js, Spring Boot, Flutter, Embedded Firmware, DevOps/SRE, Substation/MEP, etc.

3. **Master Concurrency-Safe SQLite Database (`data/jobs.db`)**:
   - Configured with WAL (`Write-Ahead Logging`) mode and busy-timeout protection for concurrent reads/writes.
   - Deduplicates posts automatically across platforms, tracks first-seen/last-seen timestamps, and stores extracted skills, salaries, and experience levels.

4. **Multi-Tab Interactive Web Dashboard (`dashboard.py`)**:
   - **Tab 1: Sector Trends**: Tracks whether vacancies are increasing (bartese) vs decreasing (komtese) across specializations.
   - **Tab 2: In-Demand Skills Analytics**: Extracts and ranks top tools, frameworks, and programming languages.
   - **Tab 3: Company Recruitment & Tech-Stack Intelligence**:
     - Visualizes top hiring organizations.
     - **Interactive Tech-Stack Profiler**: Inspect any employer (e.g. Brain Station 23, Therap, Enosis, Walton) to view their required technical stack, role distribution, and open positions.
   - **Tab 4: Browse All Vacancies & Custom Filtered Excel Download**:
     - Filter by Domain, Category, Specialization, Experience, and Status.
     - **1-Click Instant Download**: Exports the currently filtered search result directly as a custom formatted `.xlsx` spreadsheet in memory!
   - **Tab 5: Smart Resume / CV Matcher**:
     - Upload PDF resume to get match scores, skill gap analysis, and tailored job recommendations with direct apply links.
   - **Tab 6: Salary Benchmarking & Compensation Intelligence**:
     - Interactive compensation calculator for Bangladesh Domestic (BDT/mo) and International Remote (USD/mo).
     - Compensation ladder across experience tiers (Fresher, Junior, Mid, Senior, Lead).
     - Filterable list of postings with explicit salary figures.
   - **Tab 7: 3-Day Link Health, Executive Reports & Email Digest**:
     - Active vs expired URL verification.
     - Printable ReportLab executive PDF report generator.
     - Morning Email Digest preview and send center.

5. **Daily Morning Email Digest (`email_digest.py`)**:
   - Compiles daily market statistics, top sector breakdown, trending skills, and featured vacancies with clickable apply links into a responsive HTML email.
   - Automatically attaches the generated daily Excel report (`daily_jobs_YYYY-MM-DD.xlsx`).
   - Supports SMTP (Gmail, Outlook, SendGrid, etc.) with SSL/TLS.

6. **Free Cloud Automation (GitHub Actions)**:
   - Configured via `.github/workflows/daily_scrape.yml`.
   - Runs automatically every night at 00:00 UTC (06:00 AM BST), harvests fresh jobs, compiles reports, and commits updates back to GitHub without needing your computer turned on.

7. **Streamlit Community Cloud Deployment Ready**:
   - Ready to deploy in 1 click using the `.streamlit/config.toml` configuration and `requirements.txt`.

---

## 🚀 Quick Start Guide

### 1. Local Environment Setup
```powershell
# Clone the repository
git clone https://github.com/mohammadfarhanhossain/linkedin-job-post-scraper.git
cd "linkedin-job-post-scraper"

# Activate Python Virtual Environment
.venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Launching the Web Dashboard
Double-click `start_dashboard.bat` or run:
```powershell
.venv\Scripts\python.exe -m streamlit run dashboard.py
```
Open **`http://localhost:8501`** in your browser.

### 3. Running Daily Scrape & Full Pipeline
Double-click `run_daily.bat` or run:
```powershell
.venv\Scripts\python.exe automation_runner.py
```
This runs:
1. Multi-platform scrape (LinkedIn + BDJobs)
2. 3-day link verification check
3. Multi-tab daily Excel report compilation (`reports/daily/`)
4. Executive printable PDF report generation (`reports/monthly/`)
5. Daily morning email digest

### 4. Running Specialized Scrapers
- **CSE & Software Specialization Sweep**:
  ```powershell
  .venv\Scripts\python.exe harvest_cse.py
  ```
- **High-Yield Mega Harvester (1,500 - 2,500+ Jobs)**:
  ```powershell
  .venv\Scripts\python.exe mega_harvest.py
  ```

---

## 🌐 Deploying to Streamlit Community Cloud (Free 24/7 Hosting)

You can host your dashboard live on the internet for free so you can access it from your phone or any computer:

1. Push your repository to your GitHub account (`mohammadfarhanhossain/linkedin-job-post-scraper`).
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with your GitHub account.
3. Click **"New app"**.
4. Select your repository: `mohammadfarhanhossain/linkedin-job-post-scraper`.
5. Set:
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
6. Click **"Deploy!"**.
7. In a minute, your dashboard will be live at `https://your-app-name.streamlit.app`!

---

## ⚙️ Configuring Daily Email Digest & GitHub Actions Secrets

To enable live email delivery via GitHub Actions or locally, configure the following secrets/environment variables:

| Secret Name | Description | Example |
|---|---|---|
| `SMTP_SERVER` | SMTP Host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP Port | `587` |
| `SMTP_USER` | Sending Email Address | `your-email@gmail.com` |
| `SMTP_PASSWORD` | App Password (not normal password) | `abcd efgh ijkl mnop` |
| `DIGEST_RECIPIENT_EMAIL` | Destination Email Address | `recipient@example.com` |

> **Note:** If SMTP credentials are not configured, the system automatically runs in **Preview Mode**, generating an interactive HTML preview at `reports/daily/daily_email_digest_preview.html`.

---

## 📁 Repository Directory Structure

```text
├── .github/
│   └── workflows/
│       └── daily_scrape.yml           # GitHub Actions daily automated cron pipeline
├── .streamlit/
│   └── config.toml                    # Streamlit Cloud deployment & theme configuration
├── data/
│   └── jobs.db                        # SQLite Database with WAL mode & indexes (2,050+ vacancies)
├── reports/
│   ├── daily/                         # Multi-tab Excel reports & email HTML previews
│   └── monthly/                       # Executive printable PDF reports & trend charts
├── automation_runner.py               # Master daily automation orchestrator
├── classifier.py                      # 3-tier dynamic title classifier
├── config.py                          # Scraping parameters, sectors, and locations
├── dashboard.py                       # 7-Tab Streamlit web intelligence dashboard
├── database.py                        # SQLite engine, company profiler, and aggregations
├── email_digest.py                    # Daily morning HTML email digest with Excel attachment
├── harvest_cse.py                     # Specialized CSE role harvester
├── mega_harvest.py                    # High-volume multi-partition harvester
├── link_checker.py                    # 3-day active link verification engine
├── pdf_reporter.py                    # ReportLab executive PDF generator
├── reporter.py                        # Daily & monthly multi-tab Excel generator
├── resume_matcher.py                  # Smart CV PDF parsing & match score algorithm
├── scraper.py                         # Multi-platform scraper (LinkedIn, BDJobs, Indeed)
├── skills_extractor.py                # Regex & NLP skill and compensation extractor
├── run_daily.bat                      # 1-click daily automation runner
└── start_dashboard.bat                # 1-click web dashboard launcher
```

---

## 📄 License & Attribution
Designed and built for automated industrial market intelligence, data-driven recruitment tracking, and candidate career matching.

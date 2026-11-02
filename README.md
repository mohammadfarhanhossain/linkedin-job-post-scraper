# 💼 LinkedIn Job Post Scraper & Monthly Trend Tracker
*Multi-Industry Real-Time Vacancy Scraping, Database Tracking ebong Monthly Market Trend Comparison System.*

---

## 📌 Features & Highlights

1. **Title-Wise Dynamic Classification (Actual Job Title onujayi Categorization)**:
   - Job post gulo r generic "CSE", "EEE", "Civil" academic bucket-e jabe na!
   - Protita job post-er **Original Title** analyse kore specific industrial & technical domain-e classify kora hoy:
     - ⚡ **Power, Energy & Electrical** (Power Plant, Substation, High Voltage, MEP, Transformer, Grid)
     - 🔌 **VLSI, Hardware & Embedded Systems** (VLSI, FPGA, PCB Designer, Firmware, Embedded, IoT)
     - 🏗️ **Construction, Civil & Real Estate** (Structural, Civil Engineer, Site Engineer, Geotechnical, BIM)
     - 🏭 **Manufacturing, Production & Industrial** (Production, Industrial, Mechanical, Maintenance, Plant)
     - 🧵 **Textile, Garments & Apparel** (Textile Engineer, Garments Merchandiser, Dyeing, Apparel)
     - 💻 **Software & Web Engineering** (Full Stack, Backend, Frontend, Python, Java, Golang, .NET)
     - 🤖 **AI, Machine Learning & Data** (Data Scientist, AI Engineer, ML, Data Analyst)
     - ☁️ **Cloud, DevOps & Infrastructure** (DevOps, Cloud Engineer, System Admin, SRE)
     - 🛡️ **Cybersecurity & Networks** (SOC Analyst, Information Security, Network Engineer, Cisco)
     - 🧪 **Quality Assurance (SQA)** (SQA Engineer, Automation Tester, QA Lead)
     - 📱 **Mobile App Development** (Flutter, Android, iOS, React Native)
     - 📡 **Telecommunications & ISP** (Telecom, Optical Fiber, RF, NOC)
     - ✈️ **Aviation, Marine & Automotive** (CAMO Engineer, Aircraft Technical, Marine)
     - 📦 **Supply Chain & Logistics** (Supply Chain, Procurement, Logistics, Warehouse)
     - 🎨 **Design, UI/UX & Creative** (UI/UX Designer, Graphic Designer, Video Editor)
     - 💰 **Finance, Accounting & Tax** (Core Banking, Accounts, Tax, VAT, Audit)
     - 👥 **HR & Talent Acquisition** (HR Executive, Recruiter, Admin)

2. **Master SQLite Database (`data/jobs.db`)**:
   - Shob job post automatic deduplicate hoy (ekoi job 2 bar count hobe na).
   - Protita job-er Title, Company, Location, Date Posted, Sector Domain, Specialization, Job URL o First/Last seen date track hoy.

3. **Daily Scraped Report File**:
   - Protidin scrape korar sathe sathe Excel (`.xlsx`) ebong CSV (`.csv`) file toiri hoy:
     - `reports/daily/daily_jobs_YYYY-MM-DD.xlsx`
     - Tab 1: **All Vacancies** (direct LinkedIn post link shoh)
     - Tab 2: **Category Summary** (Power, Construction, VLSI, Software, Manufacturing er kontay koyta vacancy)
     - Tab 3: **Top Companies Hiring** (kon company koyta post dise)

4. **Monthly Trend Comparison ("kontar post bartese kontar komtese")**:
   - Current Month vs Previous Month (ba Last 30 Days vs Prior 30 Days) comparison:
     - **Sector Trends**: Kontar recruitment barchhe (🚀 Increasing), kontar komchhe (🔻 Decreasing), % Growth koto.
     - **Company Recruitment Trends**: Kon company recruitment barachhe o komachhe.
     - **Visual Charts**: Automatic high-resolution charts (`reports/monthly/charts/`):
       - `latest_category_trends.png`
       - `latest_top_companies.png`
     - **Monthly Reports**:
       - Excel: `reports/monthly/monthly_trend_report_YYYY-MM.xlsx`
       - Interactive HTML: Browser e open korle graph, table o summary shundor kore dekhabe!

5. **Interactive Web Dashboard (Streamlit - port 8501)**:
   - Visual web interface: KPI metrics, dynamic charts, searchable tables, industry sector filters, and CSV/Excel download.
   - **Market Scope Filter**: Bangladesh (Local) vs Worldwide / Global (Remote) toggle.
   - **3-Tier Cascading Filter**: Subject Field -> Category -> Granular Specialization.

6. **Smart Resume / CV Matcher (`resume_matcher.py`)**:
   - PDF Resume drag-and-drop support.
   - Profile skills analysis, experience extraction, and percentage match ranking against active vacancies with direct apply links.

7. **3-Day Active Link Verification (`link_checker.py`)**:
   - Automatically tests HTTP response and redirection of scraped posts every 3 days.
   - Marks live vacancies as `Active` and closed/removed posts as `Expired`.

8. **Executive Printable PDF Report (`pdf_reporter.py`)**:
   - Generates a publication-quality PDF report with executive KPI cards, domain breakdown tables, in-demand technical skills, and top employer recruitment velocity.

9. **1-Click / Automated Daily Scheduling**:
   - `run_daily.bat`: 1-click execution for daily scraping and reporting.
   - `start_dashboard.bat`: 1-click startup for the web dashboard.
   - `schedule_daily_task.bat`: Windows Task Scheduler automation to scrape every morning at 9:00 AM.
   - `harvest_more_jobs.bat`: High-yield scraper that sweeps broad roles to scale up vacancies into thousands.

---

## 🚀 How to Use

### 1. Daily Scraping Run (CLI)
```powershell
.venv\Scripts\python.exe main.py scrape --mode quick
```
*Tips: `--mode full` dile shob categorised role scrape korbe. `--mode deep` division cities sweep korbe.*

### 2. High-Yield Mega Harvester (Scale to 1,500 - 2,000+ Vacancies)
```powershell
.venv\Scripts\python.exe mega_harvest.py
```

### 3. View Monthly Trend Report (kontar post bartese / komtese)
```powershell
.venv\Scripts\python.exe main.py monthly
```
Eta run korle `reports\monthly\` ফোল্ডারে তৈরি হবে:
- `monthly_trend_report_YYYY-MM.xlsx`
- `monthly_trend_report_YYYY-MM.html` (Interactive web preview)
- `executive_job_market_report_YYYY-MM.pdf` (Printable Executive PDF)

### 4. Open Web Dashboard
```powershell
.venv\Scripts\python.exe -m streamlit run dashboard.py
```
Ba shudhu `start_dashboard.bat` file-ti double-click korun! Browser-e `http://localhost:8501` automatically open hoye jabe.

### 5. Check Active Status of Job Links
```powershell
.venv\Scripts\python.exe main.py check-links
```

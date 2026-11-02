"""
Configuration file for LinkedIn Job Scraper & Trend Analyzer.
Multi-Industry Comprehensive Job Search & Classification Configuration.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
DAILY_REPORTS_DIR = REPORTS_DIR / "daily"
MONTHLY_REPORTS_DIR = REPORTS_DIR / "monthly"
CHARTS_DIR = MONTHLY_REPORTS_DIR / "charts"

# Ensure directories exist
for folder in [DATA_DIR, DAILY_REPORTS_DIR, MONTHLY_REPORTS_DIR, CHARTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Database Path
DB_PATH = DATA_DIR / "jobs.db"

# Scraping Settings
SCRAPE_SETTINGS = {
    # Default target locations
    "default_location": "Bangladesh",
    "global_location": "Worldwide",
    "supported_regions": ["Bangladesh", "Worldwide"],
    
    # Locations for deep partitioning sweep
    "partition_locations": [
        "Bangladesh",
        "Dhaka, Bangladesh",
        "Chattogram, Bangladesh",
        "Sylhet, Bangladesh",
        "Rajshahi, Bangladesh",
        "Khulna, Bangladesh",
        "Gazipur, Bangladesh",
        "Narayanganj, Bangladesh",
        "Worldwide"
    ],

    # Results wanted per search query per partition
    "results_wanted_per_term": 25,
    
    # Hours old: 720 hours = last 30 days (captures all currently active live vacancies)
    "hours_old": 720,
    
    # Delay between requests in seconds to stay under LinkedIn's radar
    "request_delay_min": 3,
    "request_delay_max": 6,
    
    # Optional proxies list (e.g. ["http://user:pass@proxy:port"])
    "proxies": []
}

# Core search sectors and search terms for broad and deep scraping
SECTOR_SEARCH_QUERIES = {
    # 1. Broad General Sweeps (Pulls ALL latest live postings across every department)
    "General_Sweep": [
        "",  # Empty string scrapes LinkedIn's master latest live jobs feed
        "Executive",
        "Officer",
        "Manager",
        "Specialist",
        "Intern",
    ],

    # 2. VLSI & Embedded Systems
    "VLSI_Embedded": [
        "VLSI",
        "Embedded Systems",
        "PCB Designer",
        "Firmware Engineer",
        "Hardware Engineer",
        "FPGA",
    ],

    # 3. Power, Energy & Electrical Systems
    "Power_Energy": [
        "Power Engineer",
        "Substation Engineer",
        "Electrical Engineer",
        "High Voltage",
        "Solar Energy",
        "MEP Engineer",
    ],

    # 4. Construction, Civil & Real Estate
    "Construction_Civil": [
        "Civil Engineer",
        "Structural Engineer",
        "Site Engineer",
        "Construction Manager",
        "Architect",
        "Quantity Surveyor",
    ],

    # 5. Manufacturing, Production & Industrial
    "Manufacturing_Production": [
        "Production Engineer",
        "Industrial Engineer",
        "Manufacturing",
        "Mechanical Engineer",
        "Maintenance Engineer",
        "Plant Manager",
    ],

    # 6. Textile, Garments & Apparel
    "Textile_Garments": [
        "Textile Engineer",
        "Garments Merchandiser",
        "Apparel Merchandiser",
        "Dyeing Specialist",
        "Fashion Designer",
    ],

    # 7. Software & Web Engineering
    "Software_Web": [
        "Software Engineer",
        "Full Stack Developer",
        "Backend Developer",
        "Frontend Developer",
        "Python Developer",
        "Java Developer",
        ".NET Developer",
        "Node.js Developer",
    ],

    # 8. AI, ML & Data Science
    "AI_DataScience": [
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
        "Data Analyst",
        "Data Engineer",
    ],

    # 9. Cloud, DevOps & System Admin
    "Cloud_DevOps": [
        "DevOps Engineer",
        "Cloud Engineer",
        "System Administrator",
        "Linux Administrator",
        "Site Reliability Engineer",
    ],

    # 10. Cybersecurity & Networks
    "Cybersecurity_Networks": [
        "Cyber Security Analyst",
        "Network Engineer",
        "SOC Analyst",
        "Information Security",
    ],

    # 11. Quality Assurance & SQA
    "QA_Testing": [
        "SQA Engineer",
        "QA Automation Engineer",
        "Software Tester",
    ],

    # 12. Mobile App Development
    "Mobile_Apps": [
        "Flutter Developer",
        "Android Developer",
        "iOS Developer",
        "React Native",
    ],

    # 13. Telecommunications & ISP
    "Telecom": [
        "Telecom Engineer",
        "RF Engineer",
        "Optical Fiber Engineer",
        "NOC Engineer",
    ],

    # 14. Supply Chain, Logistics & Procurement
    "SupplyChain_Logistics": [
        "Supply Chain Officer",
        "Procurement Executive",
        "Logistics Executive",
        "Warehouse Manager",
    ],

    # 15. Sales, Marketing & Business Development
    "Sales_Marketing": [
        "Digital Marketing",
        "Sales Executive",
        "Business Development",
        "SEO Specialist",
        "Brand Manager",
    ],

    # 16. Design, UI/UX & Creative
    "Design_Creative": [
        "Graphic Designer",
        "UI/UX Designer",
        "Video Editor",
        "Product Designer",
    ],

    # 17. Finance, Banking & Accounting
    "Finance_Accounts": [
        "Accountant",
        "Finance Officer",
        "Tax Executive",
        "Audit Officer",
    ],

    # 18. HR & Talent Acquisition
    "HR_Admin": [
        "HR Executive",
        "Talent Acquisition",
        "Recruitment Officer",
        "Admin Executive",
    ],

    # 19. Aviation, Marine & Automotive
    "Aviation_Marine": [
        "CAMO Engineer",
        "Aeronautical Engineer",
        "Marine Engineer",
        "Automotive Engineer",
    ],

    # 20. Healthcare & Pharma
    "Healthcare_Pharma": [
        "Pharmacist",
        "Medical Officer",
        "Pharma Executive",
    ],
}

# Quick scan search terms (fast daily scan covering key sectors)
QUICK_SCAN_QUERIES = [
    "",  # Broadest sweep (captures all latest posts in Bangladesh)
    "VLSI",
    "Power Engineer",
    "Civil Engineer",
    "Production Engineer",
    "Software Engineer",
    "Full Stack Developer",
    "Data Scientist",
    "DevOps Engineer",
    "Cyber Security",
    "SQA Engineer",
    "Flutter Developer",
    "Textile Engineer",
    "Merchandiser",
    "Supply Chain",
    "Digital Marketing",
    "UI/UX Designer",
    "Accountant",
    "HR Executive",
    "CAMO Engineer",
]

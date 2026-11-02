"""
Skills, Experience Level, and Salary Extraction Engine.
Extracts technical skills, experience requirements, and salary figures
from job titles and descriptions across all industrial domains.
"""

import re
from typing import List, Dict, Any, Optional

# Master skills dictionary organized by industry sector
SKILLS_DICTIONARY = {
    "Power, Energy & Electrical": [
        "PLC", "SCADA", "AutoCAD Electrical", "Substation", "Switchgear", "ETAP",
        "High Voltage", "Transformer", "Solar PV", "Renewable Energy", "MEP",
        "Revit MEP", "Power Distribution", "Transmission Line", "Protection Relay",
        "Single Line Diagram", "Generator", "HVAC", "Circuit Breaker", "MATLAB",
        "Power Plant", "Grid", "Load Calculation"
    ],
    "VLSI, Hardware & Embedded Systems": [
        "Verilog", "VHDL", "FPGA", "ASIC", "PCB Design", "Altium Designer",
        "KiCad", "Firmware", "Embedded C", "C++", "Microcontroller", "STM32",
        "ESP32", "Arduino", "RTL Design", "I2C", "SPI", "UART", "Cadence",
        "Synopsys", "SoC", "IoT", "Circuit Simulation", "Digital Electronics"
    ],
    "Software & Web Engineering": [
        "Python", "JavaScript", "TypeScript", "Java", "Golang", "C#", ".NET",
        "PHP", "Laravel", "React", "React.js", "Node.js", "Vue.js", "Angular",
        "Next.js", "Django", "FastAPI", "Spring Boot", "Express.js", "GraphQL",
        "REST API", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Microservices"
    ],
    "AI, Machine Learning & Data": [
        "Machine Learning", "Deep Learning", "Data Science", "Python", "TensorFlow",
        "PyTorch", "NLP", "Computer Vision", "Pandas", "NumPy", "Scikit-Learn",
        "LLM", "Generative AI", "LangChain", "Power BI", "Tableau", "Data Analysis",
        "Data Engineering", "Apache Spark", "Big Data", "Data Pipeline", "ETL"
    ],
    "Cloud, DevOps & Infrastructure": [
        "DevOps", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD",
        "Terraform", "GitHub Actions", "Jenkins", "Linux", "System Administration",
        "Nginx", "Bash Scripting", "Ansible", "Cloud Architecture", "SRE", "Networking"
    ],
    "Cybersecurity & Networks": [
        "Cyber Security", "Information Security", "SOC", "SIEM", "Penetration Testing",
        "Ethical Hacking", "Network Security", "Cisco", "CCNA", "Firewall", "Wireshark",
        "Vulnerability Assessment", "ISO 27001", "OWASP", "Incident Response"
    ],
    "Quality Assurance (SQA)": [
        "SQA", "Selenium", "Cypress", "Playwright", "Postman", "API Testing",
        "Manual Testing", "Automation Testing", "Jira", "JMeter", "Test Automation",
        "Performance Testing", "Bug Tracking", "Test Case Design", "Regression Testing"
    ],
    "Mobile App Development": [
        "Flutter", "React Native", "Android", "iOS", "Dart", "Kotlin", "Swift",
        "Mobile App Development", "Firebase", "State Management", "Bloc", "Provider"
    ],
    "Construction, Civil & Real Estate": [
        "AutoCAD", "ETABS", "STAAD Pro", "Revit", "BIM", "Civil 3D",
        "Primavera P6", "MS Project", "Quantity Surveying", "Estimation",
        "Structural Analysis", "Geotechnical", "Concrete Design", "Site Supervision",
        "Total Station", "BOQ", "Piling"
    ],
    "Manufacturing, Production & Industrial": [
        "SolidWorks", "AutoCAD Mechanical", "CNC", "Machining", "Lean Manufacturing",
        "Six Sigma", "5S", "Kaizen", "TPM", "Preventive Maintenance", "Pneumatics",
        "Hydraulics", "Quality Control", "Supply Planning", "Production Planning"
    ],
    "Textile, Garments & Apparel": [
        "Garment Merchandising", "Textile Engineering", "Pattern Making", "Gerber",
        "Optitex", "Dyeing", "Washing", "Fabric Sourcing", "Apparel Costing",
        "Quality Inspection", "Yarn Manufacturing", "Spinning"
    ],
    "Design, UI/UX & Creative": [
        "Figma", "Adobe XD", "Photoshop", "Illustrator", "After Effects",
        "Premiere Pro", "UI/UX", "User Research", "Wireframing", "Prototyping",
        "Design Systems", "3D Modeling", "Blender", "Motion Graphics"
    ],
    "Finance, Accounting & Tax": [
        "Accounting", "Financial Analysis", "Taxation", "VAT", "Income Tax",
        "Audit", "Tally", "QuickBooks", "ERP", "SAP", "Advanced Excel",
        "Financial Modeling", "Budgeting", "Cash Flow"
    ],
    "Supply Chain & Logistics": [
        "Supply Chain", "Procurement", "Inventory Management", "Logistics",
        "Warehouse Management", "ERP", "Vendor Management", "Customs Clearance",
        "Freight Forwarding", "Import Export"
    ]
}

# Flat list of all skill patterns compiled for fast matching
ALL_SKILLS = []
for sector, skills in SKILLS_DICTIONARY.items():
    for sk in skills:
        if sk not in ALL_SKILLS:
            ALL_SKILLS.append(sk)


def extract_skills(text: str) -> List[str]:
    """
    Extracts matched technical skills and keywords from title and description.
    """
    if not text:
        return []

    matched = []
    text_lower = " " + text.lower() + " "

    for skill in ALL_SKILLS:
        # Match with word boundaries
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            matched.append(skill)

    return matched


def extract_experience_level(title: str, text: str = "") -> str:
    """
    Classifies experience requirement into:
    - Fresher / Entry Level
    - Junior Level (1-2 yrs)
    - Mid Level (2-5 yrs)
    - Senior Level (5+ yrs)
    - Lead / Executive / Manager
    """
    combined = f"{title} {text}".lower()

    if re.search(r"\b(fresher|entry[\s-]level|intern|internship|trainee|fresh\s+graduate)\b", combined):
        return "Fresher / Entry Level"

    if re.search(r"\b(junior|jr\.?|associate)\b", combined) or re.search(r"\b(1|2)\s*(?:-\s*2)?\s*years?\b", combined):
        return "Junior (1-2 Yrs)"

    if re.search(r"\b(senior|sr\.?|specialist|expert)\b", combined) or re.search(r"\b(5|6|7|8)\+?\s*years?\b", combined):
        return "Senior (5+ Yrs)"

    if re.search(r"\b(lead|principal|head|director|chief|c-level|vp|manager|architect)\b", combined):
        return "Lead / Manager / Executive"

    if re.search(r"\b(mid[\s-]level|mid|intermediate)\b", combined) or re.search(r"\b(2|3|4)\s*(?:-\s*4)?\s*years?\b", combined):
        return "Mid Level (2-4 Yrs)"

    # Default based on title cues
    if "lead" in combined or "manager" in combined or "head" in combined:
        return "Lead / Manager / Executive"
    if "senior" in combined:
        return "Senior (5+ Yrs)"

    return "Mid Level (2-4 Yrs)"  # Common industry standard baseline


def extract_salary_info(text: str, default_min=None, default_max=None, default_currency=None) -> str:
    """
    Detects salary details from job text or jobspy fields.
    """
    if default_min and default_max:
        curr = default_currency or "BDT"
        return f"{int(default_min):,} - {int(default_max):,} {curr}"

    if not text:
        return "Not Disclosed"

    # Search for BDT / TK / USD salary patterns
    bdt_match = re.search(r"(\b\d{2,3}[,\.]\d{3}\s*(?:-\s*\d{2,3}[,\.]\d{3})?\s*(?:bdt|tk|taka)\b)", text, re.IGNORECASE)
    if bdt_match:
        return bdt_match.group(1).strip()

    usd_match = re.search(r"(\$\s*\d{1,4}(?:\s*-\s*\$\s*\d{1,4})?\s*(?:\/(?:hr|hour|mo|month|yr|year))?)", text, re.IGNORECASE)
    if usd_match:
        return usd_match.group(1).strip()

    k_match = re.search(r"(\b\d{2}\s*k\s*-\s*\d{2,3}\s*k\b)", text, re.IGNORECASE)
    if k_match:
        return k_match.group(1).upper() + " BDT"

    return "Negotiable / Company Standard"


if __name__ == "__main__":
    t = "Senior Software Engineer (Python, Django, Docker, AWS) | $25/hr"
    print("Skills:", extract_skills(t))
    print("Exp:", extract_experience_level(t))
    print("Salary:", extract_salary_info(t))

"""
Targeted CSE Specializations LinkedIn Job Harvester.
Scrapes every granular Computer Science & Engineering (CSE) specialization title-wise:
Frontend, Backend, Full Stack, Mobile, AI/ML, Data Engineering, DevOps, Cybersecurity, SQA, Systems & Embedded.
Sweeps both Bangladesh (Local) and Worldwide (Global Remote), classifies them,
updates SQLite DB, and regenerates all reports.
"""

import time
import random
from datetime import datetime, date
from typing import List, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from scraper import scrape_single_term
import database
import reporter

console = Console()

# Granular CSE Specialization Search Titles
CSE_SPECIALIZATION_TITLES = [
    # 1. Frontend & Web Development
    "React Developer",
    "Next.js Developer",
    "Frontend Developer",
    "Vue Developer",
    "Angular Developer",

    # 2. Backend & Server Engineering
    "Python Developer",
    "Django Developer",
    "FastAPI Developer",
    "Java Developer",
    "Spring Boot Developer",
    "Node.js Developer",
    "Golang Developer",
    ".NET Developer",
    "PHP Laravel Developer",

    # 3. Full Stack Engineering
    "Full Stack Developer",
    "MERN Stack Developer",

    # 4. Mobile App Engineering
    "Flutter Developer",
    "React Native Developer",
    "Android Developer",
    "iOS Developer",

    # 5. AI, Machine Learning & Data Science
    "Machine Learning Engineer",
    "Data Scientist",
    "AI Engineer",
    "Computer Vision Engineer",
    "NLP Engineer",
    "Generative AI",

    # 6. Data Engineering & Big Data
    "Data Engineer",
    "Big Data Engineer",
    "Database Administrator",

    # 7. Cloud, DevOps, Platform & SRE
    "DevOps Engineer",
    "Cloud Engineer",
    "Site Reliability Engineer",
    "Platform Engineer",
    "Kubernetes",

    # 8. Cybersecurity & InfoSec
    "Cyber Security Analyst",
    "SOC Analyst",
    "Penetration Tester",
    "Information Security",

    # 9. Quality Assurance & Testing (SQA)
    "SQA Engineer",
    "QA Automation Engineer",
    "Software Tester",

    # 10. Low-level, Systems & Embedded
    "Embedded Software",
    "C++ Developer",
    "Firmware Engineer"
]


def run_cse_harvest(results_per_query: int = 20):
    """
    Sweeps every CSE specialization title across Bangladesh and Worldwide.
    """
    database.init_db()
    start_time = time.time()
    today_str = date.today().isoformat()

    tasks: List[Tuple[str, str]] = []

    # 1. Bangladesh CSE Sweep
    for title in CSE_SPECIALIZATION_TITLES:
        tasks.append(("Bangladesh", title))

    # 2. Worldwide / Global Remote CSE Sweep
    for title in CSE_SPECIALIZATION_TITLES:
        tasks.append(("Worldwide", title))

    console.print(f"[bold cyan]💻 Launching CSE Specializations Title-Wise Harvester[/bold cyan]")
    console.print(f"• Total Scheduled Sweeps: [green]{len(tasks)} queries[/green] ({len(CSE_SPECIALIZATION_TITLES)} titles × 2 regions)")
    console.print(f"• Target Sectors: [yellow]Frontend, Backend, Full Stack, Mobile, AI/ML, Data Eng, DevOps, Cybersecurity, SQA, Embedded[/yellow]\n")

    total_scraped = 0
    total_added = 0
    total_updated = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task_id = progress.add_task("[cyan]Harvesting CSE Titles...", total=len(tasks))

        for region, title in tasks:
            reg_label = "BD" if region == "Bangladesh" else "Global"
            progress.update(task_id, description=f"[cyan]Harvesting [{reg_label}]: [bold]{title}[/bold]")

            df = scrape_single_term(
                search_term=title,
                location=region,
                results_wanted=results_per_query,
                hours_old=720  # Past 30 days active postings
            )

            if df is not None and not df.empty:
                save_res = database.save_jobs(
                    df, field="", category="", search_query=title, target_region=region
                )
                total_scraped += save_res["found"]
                total_added += save_res["added"]
                total_updated += save_res["updated"]

            progress.advance(task_id)

            # Delay to maintain zero rate limits
            if df is None or df.empty:
                time.sleep(random.uniform(5.0, 8.0))
            else:
                time.sleep(random.uniform(3.0, 5.0))

    duration = round(time.time() - start_time, 1)

    console.print(f"\n[bold green]✔ CSE Specialization Harvest Completed in {duration}s![/bold green]")
    console.print(f"• Total Posts Encountered: [bold]{total_scraped}[/bold]")
    console.print(f"• New Unique Vacancies Added: [bold green]{total_added}[/bold green]")
    console.print(f"• Existing Posts Refreshed: [bold yellow]{total_updated}[/bold yellow]")

    # Regenerate daily reports, monthly reports and PDF
    console.print("[cyan]📊 Regenerating Daily Excel (with BD & World Sheets) and Reports...[/cyan]")
    reporter.generate_daily_report(today_str)
    reporter.generate_monthly_report()
    try:
        import pdf_reporter
        pdf_reporter.generate_executive_pdf_report()
    except Exception as e:
        console.print(f"[yellow]PDF notice: {e}[/yellow]")

    stats = database.get_db_stats()
    console.print(f"\n[bold cyan]📊 Updated Database Total: {stats['total_jobs']} Vacancies ({stats['bd_jobs']} BD / {stats['worldwide_jobs']} Global) across {stats['total_companies']} Employers![/bold cyan]")


if __name__ == "__main__":
    run_cse_harvest(results_per_query=20)

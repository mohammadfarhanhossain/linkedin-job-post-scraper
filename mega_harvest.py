"""
High-Yield Mega Harvester for LinkedIn Jobs.
Sweeps broad umbrella role categories across Bangladesh and Worldwide
to rapidly scale the database into thousands of real-time vacancies.
"""

import time
import random
from datetime import datetime, date
from typing import List, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from config import SCRAPE_SETTINGS
from scraper import scrape_single_term
import database
import reporter

console = Console()

# High-yield broad job query umbrellas (each yields 20 unique live jobs with 0 rate limits)
BD_UMBRELLA_QUERIES = [
    "Civil Engineer",
    "Electrical Engineer",
    "Mechanical Engineer",
    "Textile Engineer",
    "Power Engineer",
    "Production Engineer",
    "Software Engineer",
    "Sales Officer",
    "Accounts Officer",
    "HR Officer",
    "Supply Chain Officer",
    "Marketing Officer",
    "Merchandiser",
    "Customer Support",
    "IT Executive",
    "Bank Officer",
    "Teacher",
    "Lecturer",
    "Site Engineer",
    "Project Engineer",
    "Quality Assurance",
    "Medical Promotion Officer",
    "Field Officer",
    "Graphic Designer",
    "Assistant Manager",
    "Operations Manager",
    "Business Development",
    "Executive",
    "Officer",
    "Coordinator"
]

GLOBAL_UMBRELLA_QUERIES = [
    "Full Stack",
    "Backend Developer",
    "Frontend Developer",
    "DevOps",
    "Cloud Engineer",
    "Hardware Engineer",
    "Remote Developer",
    "Cyber Security",
    "QA Engineer",
    "Data Engineer",
    "AI Engineer",
    "Site Reliability Engineer",
    "Embedded Systems",
    "VLSI",
    "Solutions Architect",
    "Scrum Master",
    "Machine Learning",
    "Python Developer",
    "Java Developer",
    "React Developer",
    "Product Manager",
    "Systems Engineer"
]


def run_mega_harvest(results_per_query: int = 20):
    """
    Executes large-scale harvest across Bangladesh and Global tech hubs.
    """
    database.init_db()
    start_time = time.time()
    today_str = date.today().isoformat()

    tasks: List[Tuple[str, str]] = []

    # 1. Bangladesh Sweeps
    for q in BD_UMBRELLA_QUERIES:
        tasks.append(("Bangladesh", q))

    # 2. Global Sweeps
    for q in GLOBAL_UMBRELLA_QUERIES:
        tasks.append(("Worldwide", q))

    console.print(f"[bold cyan]🌾 Launching LinkedIn Mega Harvester[/bold cyan]")
    console.print(f"• Total Scheduled Broad Sweeps: [green]{len(tasks)} queries[/green]")
    console.print(f"• Target Yield: [yellow]~1,000 to 2,000+ Vacancies[/yellow]\n")

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
        task_id = progress.add_task("[cyan]Harvesting...", total=len(tasks))

        for region, query in tasks:
            progress.update(task_id, description=f"[cyan]Harvesting [{region[:4]}]: [bold]{query}[/bold]")

            df = scrape_single_term(
                search_term=query,
                location=region,
                results_wanted=results_per_query,
                hours_old=720  # Past 30 days active postings
            )

            if df is not None and not df.empty:
                save_res = database.save_jobs(
                    df, field="", category="", search_query=query, target_region=region
                )
                total_scraped += save_res["found"]
                total_added += save_res["added"]
                total_updated += save_res["updated"]

            progress.advance(task_id)

            # Polite randomized delay to prevent rate limit
            if df is None or df.empty:
                time.sleep(random.uniform(10.0, 15.0))
            else:
                time.sleep(random.uniform(4.5, 7.0))

    duration = round(time.time() - start_time, 1)

    console.print(f"\n[bold green]✔ Mega Harvest Completed in {duration}s![/bold green]")
    console.print(f"• Total Posts Encountered: [bold]{total_scraped}[/bold]")
    console.print(f"• New Unique Vacancies Added: [bold green]{total_added}[/bold green]")
    console.print(f"• Existing Posts Refreshed: [bold yellow]{total_updated}[/bold yellow]")

    # Regenerate daily reports and PDF
    reporter.generate_daily_report(today_str)
    reporter.generate_monthly_report()
    try:
        import pdf_reporter
        pdf_reporter.generate_executive_pdf_report()
    except Exception as e:
        console.print(f"[yellow]PDF report generation notice: {e}[/yellow]")

    stats = database.get_db_stats()
    console.print(f"\n[bold cyan]📊 Updated Database Total: {stats['total_jobs']} Vacancies ({stats['bd_jobs']} BD / {stats['worldwide_jobs']} Global) across {stats['total_companies']} Employers![/bold cyan]")


if __name__ == "__main__":
    run_mega_harvest(results_per_query=20)

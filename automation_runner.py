"""
Automation Runner for Daily Job Harvesting, Link Health Verification, Reports & Email Digest.
Executed automatically by GitHub Actions Cron, Windows Task Scheduler, or manual dispatch.
"""

import sys
import time
from datetime import date
from rich.console import Console

import database
import scraper
import link_checker
import reporter
import pdf_reporter
import email_digest

console = Console()


def run_full_daily_automation():
    console.print("[bold cyan]======================================================[/bold cyan]")
    console.print("[bold cyan]🚀 STARTING DAILY AUTOMATED RECRUITMENT PIPELINE[/bold cyan]")
    console.print("[bold cyan]======================================================[/bold cyan]\n")

    start_all = time.time()
    today_str = date.today().isoformat()

    # Step 1: Database Initialization
    console.print("[bold yellow]Step 1/5: Initializing Database & Indexes...[/bold yellow]")
    database.init_db()

    # Step 2: Multi-Platform Scrape Sweep
    console.print("[bold yellow]Step 2/5: Harvesting Vacancies (LinkedIn + BDJobs)...[/bold yellow]")
    try:
        scrape_res = scraper.run_scraper(mode="quick", sites=["linkedin", "bdjobs"])
        console.print(f"✔ Scraping finished: Found {scrape_res.get('total_scraped', 0)}, Added {scrape_res.get('total_added', 0)} new.\n")
    except Exception as e:
        console.print(f"[bold red]⚠️ Error during scraping step: {e}[/bold red]\n")

    # Step 3: Job Link Verification (3-Day Expiry Check)
    console.print("[bold yellow]Step 3/5: Checking Link Health (Active vs Expired)...[/bold yellow]")
    try:
        link_res = link_checker.run_link_health_check(days_interval=3, max_check=25)
        console.print(f"✔ Link check done: Checked {link_res.get('checked', 0)}, Active {link_res.get('active', 0)}, Expired {link_res.get('expired', 0)}.\n")
    except Exception as e:
        console.print(f"[bold red]⚠️ Error during link check step: {e}[/bold red]\n")

    # Step 4: Generate Excel & PDF Reports
    console.print("[bold yellow]Step 4/5: Compiling Daily Multi-Tab Excel & Executive PDF Reports...[/bold yellow]")
    try:
        excel_res = reporter.generate_daily_report()
        console.print(f"✔ Daily Excel Report generated: {excel_res.get('excel')}")
    except Exception as e:
        console.print(f"[bold red]⚠️ Error compiling Excel report: {e}[/bold red]")

    try:
        pdf_res = pdf_reporter.generate_executive_pdf_report()
        console.print(f"✔ Executive PDF Report generated: {pdf_res}\n")
    except Exception as e:
        console.print(f"[bold red]⚠️ Error compiling PDF report: {e}[/bold red]\n")

    # Step 5: Send Daily Email Digest
    console.print("[bold yellow]Step 5/5: Processing Daily Email Digest...[/bold yellow]")
    try:
        digest_res = email_digest.send_daily_digest(attach_excel=True)
        console.print(f"✔ Email digest status: {digest_res.get('status')}\n")
    except Exception as e:
        console.print(f"[bold red]⚠️ Error sending email digest: {e}[/bold red]\n")

    elapsed = round(time.time() - start_all, 1)
    console.print("[bold green]======================================================[/bold green]")
    console.print(f"[bold green]✔ DAILY AUTOMATION COMPLETED IN {elapsed} SECONDS[/bold green]")
    console.print("[bold green]======================================================[/bold green]")


if __name__ == "__main__":
    run_full_daily_automation()

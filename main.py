"""
Main Command Line Interface for LinkedIn Multi-Sector Job Scraper & Trend Tracker.
Usage:
    python main.py scrape [--mode quick|full] [--location ...]
    python main.py daily [--date YYYY-MM-DD]
    python main.py monthly [--month YYYY-MM]
    python main.py pdf [--month YYYY-MM]
    python main.py check-links
    python main.py skills [--sector <domain>]
    python main.py stats
    python main.py dashboard
    python main.py schedule
"""

import sys
import argparse
import subprocess
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import database
import scraper
import reporter
import analyzer
import pdf_reporter
import link_checker
from config import SCRAPE_SETTINGS

console = Console()


def cmd_scrape(args):
    """Executes a scraping run, verifies links if 3 days passed, and generates today's report."""
    mode = getattr(args, "mode", "quick")
    loc = getattr(args, "location", SCRAPE_SETTINGS["default_location"])
    results_per_term = getattr(args, "results", SCRAPE_SETTINGS["results_wanted_per_term"])

    res = scraper.run_scraper(
        mode=mode,
        location=loc,
        results_per_term=results_per_term
    )

    console.print("\n[cyan]📊 Generating Daily Report for Today...[/cyan]")
    rep = reporter.generate_daily_report(res["date"])
    console.print(f"[green]✔ Daily Excel saved: {rep['excel']}[/green]")
    console.print(f"[green]✔ Daily CSV saved:   {rep['csv']}[/green]")

    # Automatic 3-day link check in the background
    console.print("\n[cyan]⏱️ Checking for links needing 3-day active verification...[/cyan]")
    link_res = link_checker.run_link_health_check(days_interval=3, max_check=25)
    if link_res["checked"] > 0:
        console.print(f"[green]✔ Verified {link_res['checked']} job links (Active: {link_res['active']}, Expired: {link_res['expired']})[/green]")


def cmd_daily(args):
    """Generates daily report for a specific date or today."""
    target_date = getattr(args, "date", None) or date.today().isoformat()
    console.print(f"[cyan]Generating Daily Report for: {target_date}[/cyan]")
    rep = reporter.generate_daily_report(target_date)
    console.print(f"[bold green]✔ Done! Found {rep['total_jobs']} jobs.[/bold green]")
    console.print(f"• Excel: [underline]{rep['excel']}[/underline]")
    console.print(f"• CSV:   [underline]{rep['csv']}[/underline]")


def cmd_monthly(args):
    """Generates monthly trend comparison report (showing increasing vs decreasing)."""
    month = getattr(args, "month", None)
    label = f"Month: {month}" if month else "Latest 30 Days Comparison"
    console.print(f"[cyan]📈 Generating Trend Comparison Report ({label})...[/cyan]")

    rep = reporter.generate_monthly_report(year_month=month)
    console.print("[bold green]✔ Trend Analysis & Charts Generated Successfully![/bold green]")
    console.print(f"• Excel Report:  [underline]{rep['excel']}[/underline]")
    console.print(f"• Interactive HTML: [underline]{rep['html']}[/underline]")
    console.print(f"• Markdown Summary: [underline]{rep['markdown']}[/underline]")


def cmd_pdf(args):
    """Generates a publication-ready printable Executive PDF report."""
    month = getattr(args, "month", None)
    console.print(f"[cyan]📑 Generating Executive PDF Market Report...[/cyan]")
    pdf_path = pdf_reporter.generate_executive_pdf_report(year_month=month)
    console.print(f"[bold green]✔ Executive PDF Successfully Generated![/bold green]")
    console.print(f"• PDF File: [underline]{pdf_path}[/underline]")


def cmd_check_links(args):
    """Checks job link health every 3 days and marks expired vacancies."""
    days = getattr(args, "days", 3)
    console.print(f"[cyan]🔄 Running {days}-day Job Link Active/Expiry Verification...[/cyan]")
    res = link_checker.run_link_health_check(days_interval=days, max_check=50)
    console.print(f"[bold green]✔ Finished![/bold green] Checked: {res['checked']}, Active: {res['active']}, Expired: {res['expired']}")


def cmd_skills(args):
    """Displays top in-demand skills extracted from vacancies."""
    sector = getattr(args, "sector", None)
    df = database.get_top_skills_by_sector(field=sector, limit=15)

    title = f"Top In-Demand Skills ({sector if sector else 'All Sectors'})"
    table = Table(title=f"🎯 {title}", style="green")
    table.add_column("Rank", style="bold white", width=6)
    table.add_column("Skill / Technology", style="cyan")
    table.add_column("Job Vacancies Requiring", style="bold yellow")

    if not df.empty:
        for idx, row in df.reset_index().iterrows():
            table.add_row(str(idx + 1), row["Skill"], str(row["Job_Count"]))
    else:
        table.add_row("-", "No skills recorded yet", "0")

    console.print(table)


def cmd_stats(args):
    """Displays stored database statistics."""
    stats = database.get_db_stats()
    table = Table(title="📊 LinkedIn Job Scraper Database Statistics", style="cyan")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="green")

    table.add_row("Total Vacancies in Database", f"{stats['total_jobs']:,}")
    table.add_row("Unique Companies Hiring", f"{stats['total_companies']:,}")
    table.add_row("Scraped Days Count", f"{stats['scraped_days_count']}")
    table.add_row("First Date Recorded", str(stats['first_date']))
    table.add_row("Latest Date Recorded", str(stats['latest_date']))

    for fld, cnt in stats["field_counts"].items():
        table.add_row(f"Domain: {fld}", f"{cnt:,} posts")

    console.print(table)


def cmd_dashboard(args):
    """Launches the Streamlit Web Dashboard."""
    console.print("[bold green]🚀 Launching Streamlit Interactive Dashboard...[/bold green]")
    console.print("[cyan]Press Ctrl+C in terminal to stop.[/cyan]\n")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])


def cmd_schedule(args):
    """Shows instructions for setting up Windows Task Scheduler for daily scraping."""
    panel_text = """
[bold yellow]Automated Daily Scraping Setup (Windows Task Scheduler)[/bold yellow]

To make this script run automatically every day at 9:00 AM:
1. Double-click [bold green]schedule_daily_task.bat[/bold green] (or run in Administrator command prompt).
2. Or create a scheduled task using Windows Task Scheduler (taskschd.msc):
   - Action: Start a program
   - Program/script: run_daily.bat
   - Trigger: Daily at 09:00 AM

This will:
• Scrape today's new vacancy posts across all technical & industrial domains
• Extract in-demand tech skills, experience level, and salary info
• Auto-verify job links older than 3 days
• Generate today's Excel & CSV reports
• Keep your monthly trend analytics up to date!
    """
    console.print(Panel(panel_text, border_style="cyan"))


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Multi-Sector Job Scraper & Trend Intelligence System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available sub-commands")

    # Scrape command
    p_scrape = subparsers.add_parser("scrape", help="Run scraper, update DB, and verify links")
    p_scrape.add_argument("--mode", choices=["quick", "full", "deep"], default="quick",
                          help="Scrape mode: 'quick' (key sectors), 'full' (all sector queries), 'deep' (exhaustive all cities & worldwide)")
    p_scrape.add_argument("--location", default=SCRAPE_SETTINGS["default_location"],
                          help="Target location (default: Bangladesh)")
    p_scrape.add_argument("--results", type=int, default=SCRAPE_SETTINGS["results_wanted_per_term"],
                          help="Results wanted per search term")

    # Daily report command
    p_daily = subparsers.add_parser("daily", help="Generate daily report for a given date")
    p_daily.add_argument("--date", help="Target date in YYYY-MM-DD format (default: today)")

    # Monthly report command
    p_monthly = subparsers.add_parser("monthly", help="Generate monthly comparison report & charts")
    p_monthly.add_argument("--month", help="Target month in YYYY-MM format (e.g. 2026-11)")

    # PDF report command
    p_pdf = subparsers.add_parser("pdf", help="Generate printable Executive PDF report")
    p_pdf.add_argument("--month", help="Target month in YYYY-MM format")

    # Check links command
    p_links = subparsers.add_parser("check-links", help="Run 3-day active link verification")
    p_links.add_argument("--days", type=int, default=3, help="Days interval between checks (default: 3)")

    # Skills command
    p_skills = subparsers.add_parser("skills", help="Display top in-demand skills")
    p_skills.add_argument("--sector", help="Filter by sector domain")

    # Stats command
    subparsers.add_parser("stats", help="Display database summary")

    # Dashboard command
    subparsers.add_parser("dashboard", help="Start the interactive Streamlit web dashboard")

    # Schedule command
    subparsers.add_parser("schedule", help="Show automated daily scheduling guide")

    args = parser.parse_args()

    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "daily":
        cmd_daily(args)
    elif args.command == "monthly":
        cmd_monthly(args)
    elif args.command == "pdf":
        cmd_pdf(args)
    elif args.command == "check-links":
        cmd_check_links(args)
    elif args.command == "skills":
        cmd_skills(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

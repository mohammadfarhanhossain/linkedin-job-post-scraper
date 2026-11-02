"""
LinkedIn Multi-Sector Job Scraper Engine.
Scrapes jobs using jobspy with anti-blocking impersonation.
Dynamically classifies all jobs by actual Title into specific domains:
VLSI, Power, Construction, Manufacturing, Software, AI, Textile, Aviation, etc.
"""

import time
import random
from datetime import datetime, date
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from config import SCRAPE_SETTINGS, SECTOR_SEARCH_QUERIES, QUICK_SCAN_QUERIES
import database
from classifier import classify_job_title

console = Console()


def scrape_single_term(
    search_term: str,
    location: str = SCRAPE_SETTINGS["default_location"],
    results_wanted: int = SCRAPE_SETTINGS["results_wanted_per_term"],
    hours_old: int = SCRAPE_SETTINGS["hours_old"],
    max_retries: int = 2
) -> Optional[pd.DataFrame]:
    """
    Scrapes LinkedIn for a search term with automatic exponential backoff on 429.
    """
    from jobspy import scrape_jobs

    proxies_list = SCRAPE_SETTINGS.get("proxies") or None

    for attempt in range(max_retries + 1):
        try:
            jobs = scrape_jobs(
                site_name=["linkedin"],
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                proxies=proxies_list
            )
            return jobs
        except Exception as e:
            err_str = str(e).lower()
            term_label = search_term if search_term else "All Jobs Sweep"
            
            # Check for 429 rate limit
            if "429" in err_str or "too many requests" in err_str or "blocked" in err_str:
                if attempt < max_retries:
                    backoff = random.uniform(15, 25)
                    console.print(f"[yellow]⏳ LinkedIn 429 cooldown: sleeping {int(backoff)}s before retry for '{term_label}'...[/yellow]")
                    time.sleep(backoff)
                    continue
            
            console.print(f"[yellow]⚠️ Warning while scraping '{term_label}' in {location}: {str(e)}[/yellow]")
            return None
    return None


def run_scraper(
    mode: str = "quick",
    sector_filter: Optional[str] = None,
    location: str = SCRAPE_SETTINGS["default_location"],
    results_per_term: int = SCRAPE_SETTINGS["results_wanted_per_term"],
    hours_old: int = SCRAPE_SETTINGS["hours_old"]
) -> Dict[str, Any]:
    """
    Executes scraping session.
    mode: 'quick' (QUICK_SCAN_QUERIES - covers all key sectors),
          'full' (all terms in SECTOR_SEARCH_QUERIES),
          or sector name (e.g. 'VLSI_Embedded', 'Power_Energy', 'Software_Web', etc.)
    """
    database.init_db()
    start_time = time.time()
    today_str = date.today().isoformat()

    # Determine tasks to search: list of (target_loc, search_query)
    search_tasks: List[Tuple[str, str]] = []

    if mode == "deep":
        # Sweeps all major division cities and worldwide
        locations = SCRAPE_SETTINGS.get("partition_locations", [location])
        for loc in locations:
            for q in QUICK_SCAN_QUERIES:
                search_tasks.append((loc, q))
    elif mode == "quick":
        for q in QUICK_SCAN_QUERIES:
            search_tasks.append((location, q))
    elif sector_filter and sector_filter in SECTOR_SEARCH_QUERIES:
        for q in SECTOR_SEARCH_QUERIES[sector_filter]:
            search_tasks.append((location, q))
    elif mode in SECTOR_SEARCH_QUERIES:
        for q in SECTOR_SEARCH_QUERIES[mode]:
            search_tasks.append((location, q))
    else:  # 'full'
        full_terms = []
        for sec, queries in SECTOR_SEARCH_QUERIES.items():
            full_terms.extend(queries)
        full_terms = list(dict.fromkeys(full_terms))
        for q in full_terms:
            search_tasks.append((location, q))

    console.print(f"[bold cyan]🔍 Starting LinkedIn Multi-Industry Job Scraper[/bold cyan]")
    console.print(f"• Mode: [green]{mode.upper()}[/green] | Total Scheduled Searches: [green]{len(search_tasks)}[/green]")
    console.print(f"• Target Region: [yellow]{location}[/yellow] | Time Window: [yellow]{hours_old} hours[/yellow]")
    console.print(f"• Classification: [bold magenta]Title-Based Dynamic Industrial Domain Mapping[/bold magenta]\n")

    total_scraped = 0
    total_added = 0
    total_updated = 0
    failed_terms = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Scraping LinkedIn...", total=len(search_tasks))

        for target_loc, query in search_tasks:
            query_label = query if query else "★ All Jobs Sweep ★"
            progress.update(task, description=f"[cyan]Scraping [{target_loc[:12]}]: [bold]{query_label}[/bold]")

            df = scrape_single_term(
                search_term=query,
                location=target_loc,
                results_wanted=results_per_term,
                hours_old=hours_old
            )

            if df is not None and not df.empty:
                # database.save_jobs uses classifier.classify_job_title on each row's actual title
                save_res = database.save_jobs(
                    df, field="", category="", search_query=query, target_region=target_loc
                )
                total_scraped += save_res["found"]
                total_added += save_res["added"]
                total_updated += save_res["updated"]
            else:
                failed_terms.append(f"{target_loc} - {query_label}")

            progress.advance(task)

            # Random polite delay between requests
            sleep_sec = random.uniform(
                SCRAPE_SETTINGS["request_delay_min"],
                SCRAPE_SETTINGS["request_delay_max"]
            )
            time.sleep(sleep_sec)

    duration = round(time.time() - start_time, 1)

    console.print("\n[bold green]✅ Scraping Session Completed![/bold green]")
    console.print(f"• Duration: [bold]{duration}s[/bold]")
    console.print(f"• Total Posts Encountered: [bold]{total_scraped}[/bold]")
    console.print(f"• New Unique Vacancies Stored in DB: [bold green]{total_added}[/bold green]")
    console.print(f"• Existing Vacancies Refreshed: [bold yellow]{total_updated}[/bold yellow]")

    return {
        "date": today_str,
        "mode": mode,
        "duration_seconds": duration,
        "total_scraped": total_scraped,
        "total_added": total_added,
        "total_updated": total_updated,
        "failed_terms": failed_terms
    }


if __name__ == "__main__":
    run_scraper(mode="quick")

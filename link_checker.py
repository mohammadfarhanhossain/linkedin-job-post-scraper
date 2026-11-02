"""
Job Link Active / Expiry Verification Engine.
Runs every 3 days to verify if posted vacancies are still open or expired/closed.
"""

import time
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

import database

console = Console()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def check_single_url_status(url: str, timeout: int = 6) -> str:
    """
    Checks if a job URL is active or expired.
    Returns: 'Active' or 'Expired'
    """
    if not url or not url.startswith("http"):
        return "Expired"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code in [404, 410]:
            return "Expired"

        page_text = resp.text.lower()
        if "no longer accepting applications" in page_text or "job has expired" in page_text:
            return "Expired"

        return "Active"
    except Exception:
        # If timeout or temporary network issue, do not prematurely mark as expired
        return "Active"


def run_link_health_check(days_interval: int = 3, max_check: int = 40) -> Dict[str, Any]:
    """
    Verifies jobs that haven't been checked in `days_interval` days (default 3 days).
    """
    database.init_db()
    conn = database.get_connection()
    cursor = conn.cursor()

    cutoff_date = (date.today() - timedelta(days=days_interval)).isoformat()
    today_str = date.today().isoformat()

    # Find jobs needing check: either never checked, or checked >= 3 days ago
    cursor.execute("""
        SELECT id, title, company, job_url, status, last_checked_date
        FROM jobs
        WHERE status = 'Active' 
          AND (last_checked_date IS NULL OR last_checked_date <= ?)
        ORDER BY first_seen_date ASC
        LIMIT ?
    """, (cutoff_date, max_check))

    jobs_to_check = cursor.fetchall()
    conn.close()

    if not jobs_to_check:
        console.print(f"[green]✔ All active job links have been verified within the last {days_interval} days![/green]")
        return {"checked": 0, "active": 0, "expired": 0}

    console.print(f"[cyan]🔄 Running 3-Day Link Verification on {len(jobs_to_check)} jobs...[/cyan]")

    active_count = 0
    expired_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Checking Links...", total=len(jobs_to_check))

        for job in jobs_to_check:
            job_id = job["id"]
            url = job["job_url"]
            progress.update(task, description=f"[cyan]Checking: {job['title'][:30]}...")

            new_status = check_single_url_status(url)

            # Update DB
            update_conn = database.get_connection()
            u_cursor = update_conn.cursor()
            u_cursor.execute("""
                UPDATE jobs
                SET status = ?, last_checked_date = ?
                WHERE id = ?
            """, (new_status, today_str, job_id))
            update_conn.commit()
            update_conn.close()

            if new_status == "Active":
                active_count += 1
            else:
                expired_count += 1

            progress.advance(task)
            time.sleep(0.3)  # Polite delay

    console.print(f"[bold green]✔ Link Check Complete![/bold green] Active: [green]{active_count}[/green], Expired: [red]{expired_count}[/red]")

    return {
        "checked": len(jobs_to_check),
        "active": active_count,
        "expired": expired_count
    }


if __name__ == "__main__":
    run_link_health_check()

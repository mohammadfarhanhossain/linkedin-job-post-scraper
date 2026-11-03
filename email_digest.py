"""
Daily Morning Email Digest Module for LinkedIn & Multi-Platform Job Market Intelligence.
Generates and sends a daily executive email digest with:
- Top newly posted vacancies and direct apply links
- Sector & Specialization distribution
- Top trending skills of the day
- Optional daily Excel report attachment
Configurable via standard SMTP environment variables.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from rich.console import Console

from config import DAILY_REPORTS_DIR, SCRAPE_SETTINGS
import database

console = Console()


def generate_digest_html(today_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Compiles daily statistics and formats an HTML email digest.
    """
    if not today_date:
        today_date = date.today().isoformat()

    conn = database.get_connection()
    stats = database.get_db_stats()

    # Get today's or latest 20 vacancies
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, company, location, field, category, specialization, skills, experience_level, salary_info, job_url, target_region
        FROM jobs
        ORDER BY first_seen_date DESC, scraped_at DESC
        LIMIT 15
    """)
    top_jobs = [dict(r) for r in cursor.fetchall()]

    # Today's new job count
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE first_seen_date = ?", (today_date,))
    today_count = cursor.fetchone()[0]

    # Sector breakdown for latest jobs
    cursor.execute("""
        SELECT field, COUNT(*) as cnt
        FROM jobs
        GROUP BY field
        ORDER BY cnt DESC
        LIMIT 5
    """)
    top_fields = cursor.fetchall()
    conn.close()

    # In-demand skills
    skills_df = database.get_top_skills_by_sector(limit=10)
    top_skills_list = skills_df["Skill"].tolist() if not skills_df.empty else []

    # Build HTML rows for top vacancies
    job_rows_html = ""
    for j in top_jobs:
        skills_pills = ""
        if j.get("skills"):
            s_list = [s.strip() for s in j["skills"].split(",")[:4] if s.strip()]
            skills_pills = " ".join([f"<span style='background:#e0f2fe;color:#0369a1;padding:2px 6px;border-radius:4px;font-size:11px;margin-right:4px;'>{s}</span>" for s in s_list])

        region_badge = "🇧🇩 BD" if j.get("target_region") == "Bangladesh" else "🌐 Global"
        spec_text = j.get("specialization") or j.get("category") or "General"

        job_rows_html += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 12px 8px;">
                <div style="font-weight: 600; font-size: 14px; color: #0a66c2;">
                    <a href="{j['job_url']}" style="color: #0a66c2; text-decoration: none;">{j['title']}</a>
                </div>
                <div style="font-size: 12px; color: #475569; margin: 3px 0;">
                    <b>{j['company']}</b> • {j['location']} • <span style="color:#059669; font-weight: 600;">{spec_text}</span> • <span style="font-size:11px; background:#f1f5f9; padding:1px 5px; border-radius:3px;">{region_badge}</span>
                </div>
                <div style="margin-top: 4px;">{skills_pills}</div>
            </td>
            <td style="padding: 12px 8px; text-align: right; white-space: nowrap;">
                <a href="{j['job_url']}" style="background-color: #0a66c2; color: #ffffff; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: bold; display: inline-block;">Apply Now</a>
            </td>
        </tr>
        """

    # Sector summary badges
    sector_summary_html = "".join([
        f"<div style='display:inline-block; margin-right:12px; margin-bottom:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px; font-size:12px;'><b>{f['field'][:18]}</b>: <span style='color:#0a66c2; font-weight:bold;'>{f['cnt']}</span></div>"
        for f in top_fields
    ])

    # Top skills pills
    skills_summary_html = " ".join([
        f"<span style='background:#f1f5f9; color:#1e293b; padding:3px 8px; border-radius:12px; font-size:12px; display:inline-block; margin:2px 3px;'>{s}</span>"
        for s in top_skills_list
    ])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Daily Job Market Intelligence Digest</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px;">
        <div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            
            <!-- Header Banner -->
            <div style="background: linear-gradient(135deg, #0a66c2 0%, #004182 100%); color: #ffffff; padding: 24px 28px;">
                <h1 style="margin: 0; font-size: 22px; font-weight: 700;">💼 Daily Job Market Intelligence Digest</h1>
                <p style="margin: 6px 0 0 0; font-size: 13px; opacity: 0.9;">Multi-Platform Hiring Digest • {today_date} • Automated Summary</p>
            </div>

            <!-- Main KPI Metrics -->
            <div style="padding: 20px 28px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                <table style="width: 100%; text-align: center; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px;">
                            <div style="font-size: 22px; font-weight: bold; color: #0a66c2;">{stats.get('total_jobs', 0):,}</div>
                            <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Total Vacancies</div>
                        </td>
                        <td style="padding: 8px; border-left: 1px solid #cbd5e1;">
                            <div style="font-size: 22px; font-weight: bold; color: #059669;">{stats.get('bd_jobs', 0):,}</div>
                            <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Bangladesh Local</div>
                        </td>
                        <td style="padding: 8px; border-left: 1px solid #cbd5e1;">
                            <div style="font-size: 22px; font-weight: bold; color: #7c3aed;">{stats.get('worldwide_jobs', 0):,}</div>
                            <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Global Remote</div>
                        </td>
                        <td style="padding: 8px; border-left: 1px solid #cbd5e1;">
                            <div style="font-size: 22px; font-weight: bold; color: #d97706;">{stats.get('total_companies', 0):,}</div>
                            <div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Active Employers</div>
                        </td>
                    </tr>
                </table>
            </div>

            <!-- Content Body -->
            <div style="padding: 24px 28px;">
                
                <!-- Sector Distribution -->
                <h3 style="font-size: 15px; color: #1e293b; margin-top: 0; margin-bottom: 10px;">📊 Sector Volume Distribution</h3>
                <div style="margin-bottom: 20px;">
                    {sector_summary_html}
                </div>

                <!-- Trending Skills -->
                <h3 style="font-size: 15px; color: #1e293b; margin-top: 0; margin-bottom: 10px;">🔥 Top In-Demand Skills Today</h3>
                <div style="margin-bottom: 24px;">
                    {skills_summary_html}
                </div>

                <!-- Top Vacancies -->
                <h3 style="font-size: 15px; color: #1e293b; margin-top: 0; margin-bottom: 12px;">🌟 Featured Open Vacancies</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    {job_rows_html}
                </table>

                <div style="margin-top: 25px; padding: 15px; background: #eff6ff; border-radius: 6px; border: 1px solid #bfdbfe; font-size: 12px; color: #1e40af;">
                    💡 <b>Pro Tip:</b> Open the local Streamlit dashboard to test your resume with the Smart CV Matcher or run customized Excel exports.
                </div>
            </div>

            <!-- Footer -->
            <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px 28px; text-align: center; font-size: 11px; color: #94a3b8;">
                Generated by LinkedIn & Multi-Platform Job Market Intelligence System<br>
                Empowering data-driven career navigation and recruitment analytics.
            </div>

        </div>
    </body>
    </html>
    """

    return {
        "date": today_date,
        "subject": f"💼 Daily Job Intelligence Digest ({today_date}): {stats.get('total_jobs', 0):,} Vacancies Tracked",
        "html_content": html_content,
        "total_jobs": stats.get("total_jobs", 0),
        "bd_jobs": stats.get("bd_jobs", 0)
    }


def send_daily_digest(
    recipient_email: Optional[str] = None,
    attach_excel: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Sends the compiled daily email digest via SMTP.
    If credentials are missing or dry_run=True, saves HTML preview locally.
    """
    digest_data = generate_digest_html()
    today_str = digest_data["date"]
    
    # Save preview locally for instant inspection
    preview_path = DAILY_REPORTS_DIR / f"daily_email_digest_preview.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(digest_data["html_content"])

    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    target_recipient = recipient_email or os.environ.get("DIGEST_RECIPIENT_EMAIL")

    if dry_run or not (smtp_server and smtp_user and smtp_password and target_recipient):
        reason = "dry-run mode requested" if dry_run else "SMTP credentials not configured"
        console.print(f"[yellow]ℹ️ Email digest preview generated ({reason}).[/yellow]")
        console.print(f"• Preview HTML: [cyan]{preview_path}[/cyan]")
        console.print(f"• Subject: [bold]{digest_data['subject']}[/bold]")
        return {
            "status": "preview_saved",
            "preview_file": str(preview_path),
            "subject": digest_data["subject"],
            "message": f"Preview HTML saved to {preview_path}. To send live emails, configure SMTP_SERVER, SMTP_USER, SMTP_PASSWORD, and DIGEST_RECIPIENT_EMAIL."
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = digest_data["subject"]
        msg["From"] = smtp_user
        msg["To"] = target_recipient

        # Attach HTML body
        part_html = MIMEText(digest_data["html_content"], "html")
        msg.attach(part_html)

        # Attach daily excel if requested
        if attach_excel:
            excel_file = DAILY_REPORTS_DIR / f"daily_jobs_{today_str}.xlsx"
            if excel_file.exists():
                with open(excel_file, "rb") as f:
                    part_attach = MIMEBase("application", "octet-stream")
                    part_attach.set_payload(f.read())
                encoders.encode_base64(part_attach)
                part_attach.add_header(
                    "Content-Disposition",
                    f"attachment; filename={excel_file.name}"
                )
                msg.attach(part_attach)

        # Connect and send
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=25)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=25)
            server.starttls()

        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [target_recipient], msg.as_string())
        server.quit()

        console.print(f"[bold green]✔ Daily email digest sent successfully to {target_recipient}![/bold green]")
        return {
            "status": "sent",
            "recipient": target_recipient,
            "subject": digest_data["subject"],
            "preview_file": str(preview_path)
        }

    except Exception as e:
        console.print(f"[bold red]❌ Failed to send email digest: {str(e)}[/bold red]")
        return {
            "status": "error",
            "error": str(e),
            "preview_file": str(preview_path)
        }


if __name__ == "__main__":
    send_daily_digest(dry_run=True)

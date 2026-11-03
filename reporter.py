"""
Report Generation Engine.
Generates daily and monthly Excel spreadsheets, CSVs, and interactive HTML/Markdown reports.
"""

from datetime import date
from typing import Dict, Any, Optional
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from config import DAILY_REPORTS_DIR, MONTHLY_REPORTS_DIR
import database
import analyzer


def style_excel_sheet(ws, header_color="1F497D", font_color="FFFFFF"):
    """Applies professional formatting to an Excel worksheet."""
    header_fill = PatternFill(start_color=header_color, end_color=header_color, fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color=font_color)
    data_font = Font(name="Segoe UI", size=10)
    border_thin = Border(
        left=Side(style='thin', color='E0E0E0'),
        right=Side(style='thin', color='E0E0E0'),
        top=Side(style='thin', color='E0E0E0'),
        bottom=Side(style='thin', color='E0E0E0')
    )

    # Header row
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Data rows
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = data_font
            cell.border = border_thin
            if isinstance(cell.value, (int, float)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-adjust column width
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)


def generate_daily_report(target_date: Optional[str] = None) -> Dict[str, str]:
    """
    Generates Daily Excel & CSV reports for a specified date (defaults to today).
    """
    if not target_date:
        target_date = date.today().isoformat()

    # Fetch jobs scraped today
    jobs_df = database.get_jobs(start_date=target_date, end_date=target_date, limit=3000)
    spec_summary = database.get_daily_specialization_summary(target_date)
    cat_summary = database.get_daily_category_summary(target_date)
    comp_summary = database.get_daily_company_summary(target_date, limit=40)

    excel_path = DAILY_REPORTS_DIR / f"daily_jobs_{target_date}.xlsx"
    csv_path = DAILY_REPORTS_DIR / f"daily_jobs_{target_date}.csv"

    # Export CSV of all jobs
    jobs_df.to_csv(csv_path, index=False)

    # Export Multi-tab Excel
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Columns definition
        desired_cols = [
            "title", "company", "specialization", "category", "field",
            "location", "target_region", "skills", "experience_level",
            "salary_info", "status", "date_posted", "job_url"
        ]
        export_jobs_df = jobs_df[[c for c in desired_cols if c in jobs_df.columns]] if not jobs_df.empty else pd.DataFrame(columns=desired_cols)
        
        # Sheet 1: Whole World (BD + All Countries Combined)
        export_jobs_df.to_excel(writer, sheet_name="World Total (BD + Global)", index=False)

        # Sheet 2: Just Bangladesh (Local BD Jobs)
        bd_jobs_df = export_jobs_df[export_jobs_df["target_region"] == "Bangladesh"]
        bd_jobs_df.to_excel(writer, sheet_name="Bangladesh Only (Local)", index=False)

        # Sheet 3: International / Remote (Outside BD)
        global_jobs_df = export_jobs_df[export_jobs_df["target_region"] != "Bangladesh"]
        global_jobs_df.to_excel(writer, sheet_name="International Remote", index=False)

        # Sheet 4: Granular Specialization Breakdown
        spec_summary.to_excel(writer, sheet_name="Specialization Breakdown", index=False)

        # Sheet 5: Functional Category Summary
        cat_summary.to_excel(writer, sheet_name="Category Summary", index=False)

        # Sheet 6: Top Hiring Companies
        comp_summary.to_excel(writer, sheet_name="Top Companies Hiring", index=False)

    # Apply styling
    from openpyxl import load_workbook
    wb = load_workbook(excel_path)
    for sheetname in wb.sheetnames:
        style_excel_sheet(wb[sheetname])
    wb.save(excel_path)

    return {
        "excel": str(excel_path),
        "csv": str(csv_path),
        "total_jobs": len(jobs_df),
        "date": target_date
    }


def generate_monthly_report(year_month: Optional[str] = None) -> Dict[str, str]:
    """
    Generates comprehensive Monthly Trend Comparison Report in Excel, Markdown, and HTML.
    Shows what's increasing (bartese), what's decreasing (komtese), and top hiring companies.
    """
    analysis = analyzer.analyze_trends(year_month=year_month)
    target_label = year_month if year_month else f"{analysis['period2']['start']}_to_{analysis['period2']['end']}"

    excel_path = MONTHLY_REPORTS_DIR / f"monthly_trend_report_{target_label}.xlsx"
    html_path = MONTHLY_REPORTS_DIR / f"monthly_trend_report_{target_label}.html"
    md_path = MONTHLY_REPORTS_DIR / f"monthly_trend_report_{target_label}.md"

    cat_df = analysis["category_trends"]
    comp_df = analysis["company_trends"]

    # 1. Multi-tab Excel Report
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        cat_df.to_excel(writer, sheet_name="Category Trends", index=False)
        comp_df.to_excel(writer, sheet_name="Company Activity", index=False)

    from openpyxl import load_workbook
    wb = load_workbook(excel_path)
    style_excel_sheet(wb["Category Trends"], header_color="16A085")
    style_excel_sheet(wb["Company Activity"], header_color="2980B9")
    wb.save(excel_path)

    # 2. Markdown Report
    md_content = f"""# 📊 LinkedIn Monthly Job Post & Vacancy Trend Report
**Period Analysed:** Current ({analysis['period2']['start']} to {analysis['period2']['end']}) vs Previous ({analysis['period1']['start']} to {analysis['period1']['end']})  
**Report Generated:** {date.today().isoformat()}

---

## 🚀 Key Market Highlights
- **Total Posts in Current Period:** {analysis['period2']['total_posts']}
- **Total Posts in Previous Period:** {analysis['period1']['total_posts']}
- **Net Job Growth:** {analysis['net_change']:+d} posts
- **Categories Increasing (Growing):** {analysis['growing_categories_count']}
- **Categories Decreasing (Declining):** {analysis['declining_categories_count']}

---

## 📈 Category Trend Breakdown (CSE & Engineering)
*Showing which fields are posting more vacancies (bartese) vs less vacancies (komtese):*

{cat_df.to_markdown(index=False) if not cat_df.empty else "No category trend data recorded yet."}

---

## 🏢 Top Recruiting Companies & Activity
*Companies posting the most vacancies and their recruitment changes:*

{comp_df.head(20).to_markdown(index=False) if not comp_df.empty else "No company trend data recorded yet."}

---
*Generated automatically by LinkedIn Job Post Scraper & Trend Tracker.*
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 3. HTML Visual Report
    chart_img_tags = ""
    for name, path in analysis.get("charts", {}).items():
        # Use relative path so images display cleanly when viewing html
        import os
        rel_path = os.path.relpath(path, MONTHLY_REPORTS_DIR)
        chart_img_tags += f'<div class="chart-box"><img src="{rel_path}" alt="{name}"></div>'

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LinkedIn Job Market & Trend Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 25px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); }}
        h1 {{ color: #0a66c2; border-bottom: 3px solid #0a66c2; padding-bottom: 10px; margin-top: 0; }}
        h2 {{ color: #2c3e50; margin-top: 30px; border-left: 4px solid #0a66c2; padding-left: 10px; }}
        .metric-cards {{ display: flex; gap: 20px; margin: 25px 0; flex-wrap: wrap; }}
        .card {{ flex: 1; min-width: 200px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center; }}
        .card-val {{ font-size: 28px; font-weight: bold; color: #0a66c2; margin-top: 5px; }}
        .card-label {{ font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
        .badge-up {{ color: #27ae60; font-weight: bold; }}
        .badge-down {{ color: #e74c3c; font-weight: bold; }}
        .badge-stable {{ color: #7f8c8d; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
        th {{ background: #0a66c2; color: #fff; text-align: left; padding: 12px 10px; }}
        td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        tr:hover {{ background: #f1f5f9; }}
        .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-top: 25px; }}
        .chart-box {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; }}
        .chart-box img {{ max-width: 100%; height: auto; border-radius: 4px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>📊 LinkedIn Job Post & Trend Analysis Report</h1>
    <p><strong>Evaluation Window:</strong> {analysis['period2']['start']} to {analysis['period2']['end']} (Compared with {analysis['period1']['start']} to {analysis['period1']['end']})</p>
    
    <div class="metric-cards">
        <div class="card">
            <div class="card-label">Current Period Posts</div>
            <div class="card-val">{analysis['period2']['total_posts']}</div>
        </div>
        <div class="card">
            <div class="card-label">Previous Period Posts</div>
            <div class="card-val">{analysis['period1']['total_posts']}</div>
        </div>
        <div class="card">
            <div class="card-label">Net Growth</div>
            <div class="card-val" style="color: {'#27ae60' if analysis['net_change'] >= 0 else '#e74c3c'}">{analysis['net_change']:+d}</div>
        </div>
        <div class="card">
            <div class="card-label">Growing Roles</div>
            <div class="card-val badge-up">{analysis['growing_categories_count']} 🚀</div>
        </div>
        <div class="card">
            <div class="card-label">Declining Roles</div>
            <div class="card-val badge-down">{analysis['declining_categories_count']} 🔻</div>
        </div>
    </div>

    <h2>📈 Visual Trends & Growth Charts</h2>
    <div class="chart-grid">
        {chart_img_tags}
    </div>

    <h2>📋 Category Trend Breakdown (kontar post bartese kontar komtese)</h2>
    {cat_df.to_html(classes='table', index=False, escape=False) if not cat_df.empty else '<p>No data recorded yet.</p>'}

    <h2>🏢 Top Recruiting Companies & Vacancies</h2>
    {comp_df.head(25).to_html(classes='table', index=False, escape=False) if not comp_df.empty else '<p>No data recorded yet.</p>'}
</div>
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return {
        "excel": str(excel_path),
        "markdown": str(md_path),
        "html": str(html_path)
    }

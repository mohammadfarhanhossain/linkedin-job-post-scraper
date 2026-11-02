"""
Professional Executive PDF Report Generator.
Generates printable, publication-ready PDF reports using ReportLab.
Includes KPI blocks, Sector trends, Skill demands, and Employer rankings.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

from config import MONTHLY_REPORTS_DIR
import database
import analyzer


def generate_executive_pdf_report(year_month: Optional[str] = None) -> str:
    """
    Builds a clean, multi-page executive PDF report.
    Returns the file path of the generated PDF.
    """
    analysis = analyzer.analyze_trends(year_month=year_month)
    label = year_month if year_month else f"{analysis['period2']['start']}_to_{analysis['period2']['end']}"
    pdf_path = MONTHLY_REPORTS_DIR / f"executive_job_market_report_{label}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0a66c2")
    )
    subtitle_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#555555")
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#222222")
    )
    header_cell_style = ParagraphStyle(
        "TableHeaderCell",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Title & Header
    story.append(Paragraph("💼 LinkedIn Job Market & Industrial Trend Report", title_style))
    meta_text = (
        f"<b>Evaluation Period:</b> {analysis['period2']['start']} to {analysis['period2']['end']} | "
        f"<b>Generated:</b> {date.today().isoformat()} | "
        f"<b>Region:</b> Bangladesh Multi-Sector"
    )
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0a66c2"), spaceAfter=12))

    # KPI Summary Box
    stats = database.get_db_stats()
    kpi_data = [
        [
            Paragraph("<b>Total Tracked Vacancies</b>", cell_style),
            Paragraph("<b>Net Periodic Change</b>", cell_style),
            Paragraph("<b>Active Employers</b>", cell_style),
            Paragraph("<b>Growing Domains</b>", cell_style)
        ],
        [
            Paragraph(f"<font size=14 color='#0a66c2'><b>{analysis['period2']['total_posts']}</b></font>", cell_style),
            Paragraph(f"<font size=14 color='#27ae60'><b>{analysis['net_change']:+d}</b></font>", cell_style),
            Paragraph(f"<font size=14 color='#0a66c2'><b>{stats['total_companies']}</b></font>", cell_style),
            Paragraph(f"<font size=14 color='#27ae60'><b>{analysis['growing_categories_count']} 🚀</b></font>", cell_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[135, 135, 135, 135])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # Sector Breakdown Table
    story.append(Paragraph("1. Industry Sector Vacancy Trends (Increasing vs Decreasing)", h2_style))
    cat_df = analysis["category_trends"]

    sector_table_rows = [
        [
            Paragraph("<b>Industry Domain / Sector</b>", header_cell_style),
            Paragraph("<b>Specialization</b>", header_cell_style),
            Paragraph("<b>Prev Posts</b>", header_cell_style),
            Paragraph("<b>Curr Posts</b>", header_cell_style),
            Paragraph("<b>Net Change</b>", header_cell_style),
            Paragraph("<b>Trend</b>", header_cell_style)
        ]
    ]

    for _, r in cat_df.head(12).iterrows():
        diff = int(r["difference"])
        trend_label = "Increasing (▲)" if diff > 0 else "Decreasing (▼)" if diff < 0 else "Stable (—)"
        diff_color = "#27ae60" if diff > 0 else "#e74c3c" if diff < 0 else "#7f8c8d"

        sector_table_rows.append([
            Paragraph(str(r["field"])[:26], cell_style),
            Paragraph(str(r["category"])[:22], cell_style),
            Paragraph(str(r["period1_count"]), cell_style),
            Paragraph(str(r["period2_count"]), cell_style),
            Paragraph(f"<font color='{diff_color}'><b>{diff:+d}</b></font>", cell_style),
            Paragraph(f"<font color='{diff_color}'><b>{trend_label}</b></font>", cell_style)
        ])

    sec_table = Table(sector_table_rows, colWidths=[140, 130, 60, 60, 70, 80])
    sec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0a66c2")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sec_table)
    story.append(Spacer(1, 14))

    # Top In-Demand Skills Table
    story.append(Paragraph("2. Top In-Demand Skills & Technologies", h2_style))
    skills_df = database.get_top_skills_by_sector(limit=10)

    if not skills_df.empty:
        skill_rows = [
            [
                Paragraph("<b>Rank</b>", header_cell_style),
                Paragraph("<b>Skill / Technology</b>", header_cell_style),
                Paragraph("<b>Open Vacancies</b>", header_cell_style),
                Paragraph("<b>Demand Index</b>", header_cell_style)
            ]
        ]
        max_cnt = max(skills_df["Job_Count"].max(), 1)
        for idx, row in skills_df.reset_index().iterrows():
            bar_len = int((row["Job_Count"] / max_cnt) * 10)
            bar_visual = "█" * bar_len
            skill_rows.append([
                Paragraph(f"#{idx+1}", cell_style),
                Paragraph(f"<b>{row['Skill']}</b>", cell_style),
                Paragraph(str(row["Job_Count"]), cell_style),
                Paragraph(f"<font color='#0a66c2'>{bar_visual}</font>", cell_style)
            ])

        skill_table = Table(skill_rows, colWidths=[40, 200, 100, 200])
        skill_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#16a085")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(skill_table)
        story.append(Spacer(1, 14))

    # Top Employers Table
    story.append(Paragraph("3. Top Hiring Employers This Month", h2_style))
    comp_df = analysis["company_trends"].head(10)

    comp_rows = [
        [
            Paragraph("<b>Employer / Organization</b>", header_cell_style),
            Paragraph("<b>Open Positions</b>", header_cell_style),
            Paragraph("<b>Recruitment Activity</b>", header_cell_style)
        ]
    ]
    for _, cr in comp_df.iterrows():
        comp_rows.append([
            Paragraph(f"<b>{str(cr['company'])[:35]}</b>", cell_style),
            Paragraph(str(cr["period2_count"]), cell_style),
            Paragraph(f"<font color='#27ae60'>Active Recruitment ({cr['trend']})</font>", cell_style)
        ])

    comp_table = Table(comp_rows, colWidths=[240, 100, 200])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(comp_table)

    doc.build(story)
    return str(pdf_path)


if __name__ == "__main__":
    p = generate_executive_pdf_report()
    print("PDF generated at:", p)

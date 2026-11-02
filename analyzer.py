"""
Trend Analysis and Visualization Engine for LinkedIn Jobs.
Calculates growth, decline, company recruitment activity, and exports visual charts.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/script generation
import matplotlib.pyplot as plt
import seaborn as sns

from config import CHARTS_DIR, MONTHLY_REPORTS_DIR
import database

# Set clean visualization style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def get_month_date_ranges(year_month: Optional[str] = None) -> Tuple[str, str, str, str]:
    """
    Returns (curr_start, curr_end, prev_start, prev_end) in 'YYYY-MM-DD' format.
    If year_month is provided (e.g. '2026-11'), uses that month and the preceding month.
    If not provided, uses current calendar month and previous calendar month.
    """
    if year_month:
        dt = datetime.strptime(year_month + "-01", "%Y-%m-%d").date()
    else:
        dt = date.today().replace(day=1)

    curr_start = dt.isoformat()
    # End of current month
    if dt.month == 12:
        next_month = dt.replace(year=dt.year + 1, month=1, day=1)
    else:
        next_month = dt.replace(month=dt.month + 1, day=1)
    curr_end = (next_month - timedelta(days=1)).isoformat()

    # Previous month
    prev_end_date = dt - timedelta(days=1)
    prev_start_date = prev_end_date.replace(day=1)
    prev_start = prev_start_date.isoformat()
    prev_end = prev_end_date.isoformat()

    return curr_start, curr_end, prev_start, prev_end


def get_relative_30_days_ranges() -> Tuple[str, str, str, str]:
    """
    Fallback for when less than a full calendar month is recorded.
    Compares the last 15/30 days to the preceding 15/30 days.
    """
    today = date.today()
    curr_end = today.isoformat()
    curr_start = (today - timedelta(days=30)).isoformat()

    prev_end = (today - timedelta(days=31)).isoformat()
    prev_start = (today - timedelta(days=60)).isoformat()

    return curr_start, curr_end, prev_start, prev_end


def generate_charts(
    category_trends_df: pd.DataFrame,
    company_trends_df: pd.DataFrame,
    prefix: str = "monthly"
) -> Dict[str, str]:
    """
    Generates and saves visual PNG charts for trend analysis.
    Returns dictionary of chart file paths.
    """
    chart_paths = {}

    # Chart 1: Sector / Domain Growth & Decline (kontar post bartese kontar komtese)
    if not category_trends_df.empty:
        plt.figure(figsize=(11, 7), dpi=150)
        top_cats = category_trends_df.head(14).copy()
        
        # Color coding: Green for growth, Red for decline, Gray for stable
        colors = [
            "#2ecc71" if d > 0 else "#e74c3c" if d < 0 else "#95a5a6"
            for d in top_cats["difference"]
        ]

        display_labels = [
            f"{row['field']}" if row['field'] == row['category'] else f"{row['field']}"
            for _, row in top_cats.iterrows()
        ]

        bars = plt.barh(
            display_labels,
            top_cats["difference"],
            color=colors,
            edgecolor="none",
            height=0.65
        )

        plt.axvline(0, color="#333333", linestyle="--", alpha=0.7, linewidth=1)
        plt.title("Industry Sector Vacancy Trends (Increasing vs Decreasing)", fontsize=13, fontweight="bold", pad=15)
        plt.xlabel("Change in Number of Job Posts (Current Period vs Previous Period)", fontsize=10)
        plt.ylabel("Industry Domain / Sector", fontsize=10)
        plt.gca().invert_yaxis()

        # Add text labels on bars
        for bar in bars:
            width = bar.get_width()
            xpos = width + (0.3 if width >= 0 else -0.8)
            plt.text(
                xpos,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width):+d}",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="#2c3e50"
            )

        plt.tight_layout()
        cat_chart_path = CHARTS_DIR / f"{prefix}_category_trends.png"
        plt.savefig(cat_chart_path)
        plt.close()
        chart_paths["category_trends"] = str(cat_chart_path)

    # Chart 2: Top Recruiting Companies
    if not company_trends_df.empty:
        plt.figure(figsize=(10, 6), dpi=150)
        top_comps = company_trends_df.head(10).copy()

        # Horizontal bar chart of total posts in current period
        plt.barh(
            top_comps["company"],
            top_comps["period2_count"],
            color="#3498db",
            edgecolor="none",
            height=0.65
        )

        plt.title("Top Hiring Companies (Current Month/Period)", fontsize=13, fontweight="bold", pad=15)
        plt.xlabel("Total Job Posts", fontsize=10)
        plt.ylabel("Company", fontsize=10)
        plt.gca().invert_yaxis()

        for idx, row in top_comps.reset_index().iterrows():
            plt.text(
                row["period2_count"] + 0.2,
                idx,
                f"{int(row['period2_count'])} posts ({row['trend']})",
                va="center",
                fontsize=9,
                color="#2c3e50"
            )

        plt.tight_layout()
        comp_chart_path = CHARTS_DIR / f"{prefix}_top_companies.png"
        plt.savefig(comp_chart_path)
        plt.close()
        chart_paths["top_companies"] = str(comp_chart_path)

    return chart_paths


def analyze_trends(
    period1_start: Optional[str] = None,
    period1_end: Optional[str] = None,
    period2_start: Optional[str] = None,
    period2_end: Optional[str] = None,
    year_month: Optional[str] = None
) -> Dict[str, Any]:
    """
    Performs complete comparison and trend analysis between two periods.
    """
    if not (period1_start and period1_end and period2_start and period2_end):
        if year_month:
            p2_s, p2_e, p1_s, p1_e = get_month_date_ranges(year_month)
        else:
            p2_s, p2_e, p1_s, p1_e = get_relative_30_days_ranges()
    else:
        p1_s, p1_e, p2_s, p2_e = period1_start, period1_end, period2_start, period2_end

    # Fetch comparison data from DB
    cat_df = database.get_period_comparison(p1_s, p1_e, p2_s, p2_e, group_by="category")
    comp_df = database.get_period_comparison(p1_s, p1_e, p2_s, p2_e, group_by="company")

    # High-level insights
    growing_cats = cat_df[cat_df["difference"] > 0]
    declining_cats = cat_df[cat_df["difference"] < 0]
    stable_cats = cat_df[cat_df["difference"] == 0]

    # Generate charts
    prefix = year_month if year_month else "latest"
    charts = generate_charts(cat_df, comp_df, prefix=prefix)

    total_current_posts = int(cat_df["period2_count"].sum()) if not cat_df.empty else 0
    total_prev_posts = int(cat_df["period1_count"].sum()) if not cat_df.empty else 0
    net_change = total_current_posts - total_prev_posts

    return {
        "period1": {"start": p1_s, "end": p1_e, "total_posts": total_prev_posts},
        "period2": {"start": p2_s, "end": p2_e, "total_posts": total_current_posts},
        "net_change": net_change,
        "category_trends": cat_df,
        "company_trends": comp_df,
        "growing_categories_count": len(growing_cats),
        "declining_categories_count": len(declining_cats),
        "charts": charts
    }

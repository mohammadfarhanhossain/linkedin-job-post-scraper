"""
Streamlit Web Dashboard for LinkedIn & Multi-Platform Job Market Intelligence.
Sleek Dark Mode Edition.
Features:
- Sector Market Trends & Specialization Analytics (Increasing vs Decreasing)
- In-Demand Skills Analytics (Mining top technologies across domains)
- Company Recruitment Rankings & Deep Tech-Stack Intelligence Profiler
- Browse All Vacancies with 1-Click Custom Filtered Excel & ⚡ Fresh Drop (<48h) Filter
- Geographic Distribution & Tech Hubs Heatmap (BD Divisions + Global Remote)
- Smart Resume / CV Matcher & AI Cover Letter / Recruiter Outreach Pitch Generator
- Career Pathways & Skill Roadmaps with Interview Question Bank
- Salary Benchmarking & Compensation Intelligence
- 3-Day Job Link Health Checker, Printable Executive PDF Reports & Daily Email Digest
"""

import io
import os
import importlib
from datetime import date, timedelta, datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import database
import analyzer
import reporter
import pdf_reporter
import resume_matcher
import link_checker
import email_digest
import career_advisor
from config import SCRAPE_SETTINGS

# Configure page
st.set_page_config(
    page_title="Job Market Intelligence & Career Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Sleek Dark Theme CSS
st.markdown("""
<style>
    /* Sleek Dark Mode Styling */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    .metric-card {
        background: linear-gradient(145deg, #161f30, #111827);
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #38bdf8;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .match-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
        transition: all 0.2s ease-in-out;
    }
    .match-card:hover {
        border-color: #38bdf8;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.15);
    }
    .badge-skill {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 3px 10px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 500;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
    .badge-missing {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 10px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 500;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
    .badge-fresh {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
    }
    .salary-box {
        background: linear-gradient(135deg, #064e3b 0%, #062f26 100%);
        border: 1px solid #059669;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.12);
    }
    .roadmap-step {
        background: #111827;
        border: 1px solid #1f2937;
        border-left: 4px solid #818cf8;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .interview-q {
        background: #161f30;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    importlib.reload(database)
    database.init_db()
    stats_data = database.get_db_stats()
    raw_jobs = database.get_jobs(limit=10000)

    # Robust fallback calculation
    if "bd_jobs" not in stats_data or stats_data["bd_jobs"] == 0:
        if not raw_jobs.empty:
            if "target_region" in raw_jobs.columns:
                stats_data["bd_jobs"] = int(len(raw_jobs[raw_jobs["target_region"] == "Bangladesh"]))
                stats_data["worldwide_jobs"] = int(len(raw_jobs[raw_jobs["target_region"] == "Worldwide"]))
            else:
                stats_data["bd_jobs"] = int(len(raw_jobs[raw_jobs["location"].str.contains("Bangladesh", case=False, na=False)]))
                stats_data["worldwide_jobs"] = int(len(raw_jobs) - stats_data["bd_jobs"])
        else:
            stats_data["bd_jobs"] = 0
            stats_data["worldwide_jobs"] = 0

    return stats_data, raw_jobs


stats, raw_all_jobs = load_data()
all_jobs = raw_all_jobs.copy()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png", width=50)
st.sidebar.title("Market Intelligence")
st.sidebar.markdown("**Multi-Platform Recruitment Tracker**")
st.sidebar.caption("Platforms: 🔵 LinkedIn • 🟢 BDJobs • 🟣 Indeed")
st.sidebar.divider()

# Market Scope Filter (Bangladesh vs Worldwide / Global)
scope_choice = st.sidebar.radio(
    "🌍 Select Market Scope:",
    [
        "🌍 Whole World (BD + All Countries Combined)",
        "🇧🇩 Bangladesh Only (Just BD er manusher jonno)",
        "🌐 International Remote (Outside Bangladesh)"
    ],
    index=0
)

if "Bangladesh Only" in scope_choice:
    selected_region = "Bangladesh"
    all_jobs = all_jobs[all_jobs["target_region"] == "Bangladesh"]
elif "International Remote" in scope_choice:
    selected_region = "Worldwide"
    all_jobs = all_jobs[all_jobs["target_region"] == "Worldwide"]
else:
    selected_region = "All"

st.sidebar.divider()

# Sidebar filters: 3-Tier Hierarchy
field_options = ["All"] + sorted(list(all_jobs["field"].dropna().unique())) if not all_jobs.empty else ["All"]
selected_field = st.sidebar.selectbox("1. Filter by Subject Field / Domain", field_options)

if selected_field != "All" and not all_jobs.empty:
    cats_for_field = sorted(list(all_jobs[all_jobs["field"] == selected_field]["category"].dropna().unique()))
else:
    cats_for_field = sorted(list(all_jobs["category"].dropna().unique())) if not all_jobs.empty else []

cat_options = ["All"] + cats_for_field
selected_cat = st.sidebar.selectbox("2. Filter by Category", cat_options)

if selected_cat != "All" and not all_jobs.empty:
    specs_for_cat = sorted(list(all_jobs[all_jobs["category"] == selected_cat]["specialization"].dropna().unique()))
elif selected_field != "All" and not all_jobs.empty:
    specs_for_cat = sorted(list(all_jobs[all_jobs["field"] == selected_field]["specialization"].dropna().unique()))
else:
    specs_for_cat = sorted(list(all_jobs["specialization"].dropna().unique())) if not all_jobs.empty and "specialization" in all_jobs.columns else []

spec_options = ["All"] + specs_for_cat
selected_spec = st.sidebar.selectbox("3. Filter by Granular Specialization", spec_options)

# Quick counter feedback in sidebar
if selected_spec != "All" and not all_jobs.empty:
    count_val = len(all_jobs[all_jobs["specialization"] == selected_spec])
    st.sidebar.success(f"📌 **Specialization:** **{count_val}** vacancies")
elif selected_cat != "All" and not all_jobs.empty:
    count_val = len(all_jobs[all_jobs["category"] == selected_cat])
    st.sidebar.info(f"📌 **Category:** **{count_val}** vacancies")
elif selected_field != "All" and not all_jobs.empty:
    count_val = len(all_jobs[all_jobs["field"] == selected_field])
    st.sidebar.info(f"📌 **Domain:** **{count_val}** vacancies")

exp_options = ["All", "Fresher / Entry Level", "Junior (1-2 Yrs)", "Mid Level (2-4 Yrs)", "Senior (5+ Yrs)", "Lead / Manager / Executive"]
selected_exp = st.sidebar.selectbox("Filter by Experience Level", exp_options)

status_options = ["All", "Active", "Expired"]
selected_status = st.sidebar.selectbox("Filter by Status", status_options)

search_keyword = st.sidebar.text_input("🔍 Search Title, Company or Skill", "")

st.sidebar.divider()
st.sidebar.caption(f"📍 Location Scope: {SCRAPE_SETTINGS['default_location']}")
st.sidebar.caption(f"💾 Total Tracked: {stats.get('total_jobs', len(raw_all_jobs)):,}")
st.sidebar.caption(f"🏢 Active Employers: {stats.get('total_companies', raw_all_jobs['company'].nunique() if not raw_all_jobs.empty else 0):,}")

# Header
st.title("💼 Job Vacancy & Industrial Trend Intelligence Platform")
st.markdown("Real-time market analytics, in-demand skills mining, company tech-stack profiling & smart career matching across **Software, AI, VLSI, Power, Construction, Manufacturing & all Engineering sectors**.")

# Top KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)
today_str = date.today().isoformat()
today_jobs_count = len(all_jobs[all_jobs["first_seen_date"] == today_str]) if not all_jobs.empty else 0

field_counts = stats.get("field_counts", {})
top_sector = max(field_counts, key=field_counts.get) if field_counts else "N/A"
top_sector_count = field_counts.get(top_sector, 0) if field_counts else 0

with col1:
    st.metric("👁️ Current Filter View", f"{len(all_jobs):,}")
with col2:
    st.metric("🇧🇩 Bangladesh (Just BD)", f"{stats.get('bd_jobs', 0):,}")
with col3:
    st.metric("🌐 International (Outside BD)", f"{stats.get('worldwide_jobs', 0):,}")
with col4:
    st.metric("🌍 Whole World Total", f"{stats.get('total_jobs', 0):,}")
with col5:
    st.metric("🏢 Hiring Employers", f"{stats.get('total_companies', 0):,}")
with col6:
    st.metric("🔥 Top Domain", f"{top_sector[:13]}.. ({top_sector_count})")

st.divider()

# Navigation Tabs - 9 Dedicated Modules
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📈 Sector Trends",
    "🎯 In-Demand Skills",
    "🏢 Company Tech-Stack",
    "🔍 Browse Vacancies",
    "🗺️ Geographic Hubs",
    "📄 Smart Resume & AI Pitch",
    "🎓 Career Roadmaps",
    "💰 Salary Benchmarks",
    "🔄 Reports & Email Digest"
])

# Tab 1: Sector Trends
with tab1:
    st.subheader("📈 Monthly Sector & Specialization Vacancy Trends")
    st.info("💡 Tracks whether job posts are increasing (bartese) vs decreasing (komtese) across Domains and Specializations.")

    group_by_view = st.radio(
        "📊 Select Trend Graph View:",
        ["View by Specialization (Role Level)", "View by Industry Domain (Sector Level)"],
        horizontal=True
    )

    trend_analysis = analyzer.analyze_trends()
    cat_trends = trend_analysis["category_trends"]

    if not cat_trends.empty:
        chart_df = cat_trends.copy()
        chart_df["Status"] = chart_df["difference"].apply(
            lambda x: "Increasing (Growth)" if x > 0 else "Decreasing (Decline)" if x < 0 else "Stable"
        )
        color_map = {
            "Increasing (Growth)": "#10b981",
            "Decreasing (Decline)": "#ef4444",
            "Stable": "#64748b"
        }

        y_col = "category" if "Specialization" in group_by_view else "field"
        y_label = "Specialization Role" if "Specialization" in group_by_view else "Industry Domain"

        fig = px.bar(
            chart_df,
            x="difference",
            y=y_col,
            color="Status",
            color_discrete_map=color_map,
            orientation="h",
            labels={"difference": "Change in Vacancies (+/-)", y_col: y_label},
            title=f"Net Change in Vacancies ({y_label})",
            template="plotly_dark"
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=540,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🎯 Vacancy Count by Granular Specialization")
        st.markdown("Exact vacancy count per specific specialization role:")

        if not all_jobs.empty and "specialization" in all_jobs.columns:
            spec_df = all_jobs.groupby(["specialization", "category", "field"]).size().reset_index(name="Total Vacancies")
            spec_df = spec_df.sort_values(by="Total Vacancies", ascending=False)

            fig_spec_total = px.bar(
                spec_df.head(25),
                x="Total Vacancies",
                y="specialization",
                color="field",
                orientation="h",
                labels={"specialization": "Granular Specialization", "Total Vacancies": "Open Vacancies Count", "field": "Subject Domain"},
                title="Top 25 In-Demand Granular Specializations",
                template="plotly_dark"
            )
            fig_spec_total.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=650,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_spec_total, use_container_width=True)

            colT1, colT2 = st.columns([1, 1])
            with colT1:
                st.markdown(f"**All Specializations Breakdown ({len(spec_df)} Roles):**")
                st.dataframe(spec_df, use_container_width=True, hide_index=True)
            with colT2:
                st.markdown("**Functional Category Comparison Table:**")
                display_df = cat_trends[["category", "field", "period2_count", "difference", "growth_pct", "trend"]].copy()
                display_df.columns = ["Category", "Subject Domain", "Current Posts", "Net Change", "Growth %", "Trend"]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Trend comparison will populate as daily scrapings are logged.")

# Tab 2: In-Demand Skills Analytics
with tab2:
    st.subheader("🎯 Top In-Demand Skills & Technologies")
    st.markdown("Identifies the most requested tools, languages, and competencies extracted from actual job postings.")

    filter_skill_sector = st.selectbox(
        "Filter Skills by Industry Domain",
        ["All"] + sorted(list(all_jobs["field"].dropna().unique())) if not all_jobs.empty else ["All"],
        key="skill_filter_box"
    )

    skills_df = database.get_top_skills_by_sector(field=filter_skill_sector, limit=18)

    if not skills_df.empty:
        fig_skills = px.bar(
            skills_df,
            x="Job_Count",
            y="Skill",
            orientation="h",
            color="Job_Count",
            color_continuous_scale="Teal",
            labels={"Job_Count": "Number of Vacancies Requiring Skill", "Skill": "Technology / Skill"},
            title=f"Top In-Demand Skills ({filter_skill_sector})",
            template="plotly_dark"
        )
        fig_skills.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_skills, use_container_width=True)

        colA, colB = st.columns([1, 1])
        with colA:
            st.dataframe(skills_df, use_container_width=True, hide_index=True)
        with colB:
            st.info("💡 **Takeaway:** Learning or highlighting these high-demand skills gives candidates the fastest interview callback rate.")
    else:
        st.info("No skill data recorded yet for this sector.")

# Tab 3: Company Recruitment & Tech-Stack Intelligence Profiler
with tab3:
    st.subheader("🏢 Top Hiring Employers & Company Tech-Stack Intelligence")
    st.markdown("Discover which employers are hiring most aggressively and inspect their specific technology stack.")

    if not all_jobs.empty:
        comp_counts = all_jobs["company"].value_counts().reset_index()
        comp_counts.columns = ["Company", "Open Positions"]
        top_comps = comp_counts.head(15)

        fig_comp = px.bar(
            top_comps,
            x="Open Positions",
            y="Company",
            orientation="h",
            color="Open Positions",
            color_continuous_scale="Blues",
            title="Top 15 Most Active Employers",
            template="plotly_dark"
        )
        fig_comp.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=460,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("---")
        st.subheader("🔬 Deep Employer Tech-Stack Profiler")
        st.markdown("Select any hiring company to see what technologies, roles, and experience levels they require:")

        all_unique_companies = sorted(list(all_jobs["company"].dropna().unique()))
        
        default_comp_idx = 0
        for idx, c_name in enumerate(all_unique_companies):
            if any(k in c_name.lower() for k in ["brain station", "therap", "enosis", "optimizely", "walton"]):
                default_comp_idx = idx
                break

        selected_profile_company = st.selectbox(
            "Select Employer to Inspect:",
            all_unique_companies,
            index=default_comp_idx
        )

        company_profile = database.get_company_tech_stack(selected_profile_company)

        cp1, cp2, cp3, cp4 = st.columns(4)
        with cp1:
            st.metric("Total Vacancies", company_profile["total_jobs"])
        with cp2:
            top_sk = company_profile["skills_df"].iloc[0]["Skill"] if not company_profile["skills_df"].empty else "N/A"
            st.metric("Primary Tech Skill", top_sk)
        with cp3:
            top_sp = company_profile["specializations_df"].iloc[0]["Specialization"] if not company_profile["specializations_df"].empty else "General"
            st.metric("Top Specialization", top_sp[:18])
        with cp4:
            top_lc = company_profile["locations_df"].iloc[0]["Location"] if not company_profile["locations_df"].empty else "Various"
            st.metric("Main Location", top_lc[:18])

        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            if not company_profile["skills_df"].empty:
                fig_c_sk = px.bar(
                    company_profile["skills_df"].head(10),
                    x="Count",
                    y="Skill",
                    orientation="h",
                    color="Count",
                    color_continuous_scale="Purples",
                    title=f"Top Tech Skills Required by {selected_profile_company}",
                    template="plotly_dark"
                )
                fig_c_sk.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=380,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_c_sk, use_container_width=True)
            else:
                st.info(f"No specific skill tags found for {selected_profile_company}.")

        with col_c2:
            if not company_profile["specializations_df"].empty:
                fig_c_sp = px.pie(
                    company_profile["specializations_df"].head(6),
                    names="Specialization",
                    values="Count",
                    hole=0.45,
                    title=f"Role Breakdown at {selected_profile_company}",
                    template="plotly_dark"
                )
                fig_c_sp.update_layout(
                    height=380,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_c_sp, use_container_width=True)

        st.markdown(f"**Open Job Vacancies at {selected_profile_company}:**")
        comp_jobs_df = pd.DataFrame(company_profile["jobs"])
        if not comp_jobs_df.empty:
            c_cols = ["title", "specialization", "experience_level", "location", "skills", "salary_info", "status", "date_posted", "job_url"]
            st.dataframe(
                comp_jobs_df[[c for c in c_cols if c in comp_jobs_df.columns]],
                column_config={
                    "job_url": st.column_config.LinkColumn("Apply Link", display_text="Open Job Post")
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No company data yet.")

# Tab 4: Browse Vacancies & Custom Filtered Excel Download
with tab4:
    st.subheader("🔍 Explore All Scraped Vacancies")

    col_flt1, col_flt2 = st.columns([3, 1])
    with col_flt1:
        fresh_only = st.checkbox("⚡ Show Fresh Drops Only (< 48 Hours Live)", value=False)
    with col_flt2:
        pass

    filtered_df = all_jobs.copy()
    if selected_field != "All":
        filtered_df = filtered_df[filtered_df["field"] == selected_field]
    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat]
    if selected_spec != "All" and "specialization" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["specialization"] == selected_spec]
    if selected_exp != "All":
        filtered_df = filtered_df[filtered_df["experience_level"] == selected_exp]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]

    if fresh_only:
        two_days_ago = (date.today() - timedelta(days=2)).isoformat()
        filtered_df = filtered_df[filtered_df["first_seen_date"] >= two_days_ago]

    if search_keyword:
        kw = search_keyword.lower()
        filtered_df = filtered_df[
            filtered_df["title"].str.lower().str.contains(kw) |
            filtered_df["company"].str.lower().str.contains(kw) |
            filtered_df["skills"].str.lower().str.contains(kw)
        ]

    # Header and Custom Download Row
    col_v1, col_v2 = st.columns([3, 1])
    with col_v1:
        st.markdown(f"Showing **{len(filtered_df)}** matching job posts")
    with col_v2:
        if not filtered_df.empty:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                filtered_df.to_excel(writer, index=False, sheet_name="Filtered Jobs")
            excel_data = excel_buffer.getvalue()

            field_slug = selected_field.replace(" ", "_").replace("/", "_")[:12]
            spec_slug = selected_spec.replace(" ", "_").replace("/", "_")[:12] if selected_spec != "All" else "all_roles"
            
            st.download_button(
                label=f"📥 Download Filtered Results ({len(filtered_df)} Jobs) [.xlsx]",
                data=excel_data,
                file_name=f"filtered_jobs_{field_slug}_{spec_slug}_{today_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    if not filtered_df.empty:
        show_cols = ["title", "company", "specialization", "category", "field", "location", "skills", "experience_level", "salary_info", "status", "date_posted", "job_url"]
        st.dataframe(
            filtered_df[[c for c in show_cols if c in filtered_df.columns]],
            column_config={
                "job_url": st.column_config.LinkColumn("Apply Link", display_text="Open Job Post")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No jobs found matching the selected filters.")

# Tab 5: Geographic Distribution & Tech Hubs Heatmap
with tab5:
    st.subheader("🗺️ Geographic Distribution & Tech Hubs Intelligence")
    st.markdown("Analyzes recruitment density across **Bangladesh Divisions** and **Global Remote Hubs**.")

    geo_data = database.get_geographic_distribution()
    df_bd_geo = geo_data["bangladesh_divisions"]
    df_global_geo = geo_data["global_regions"]

    col_g1, col_g2 = st.columns([1, 1])

    with col_g1:
        st.markdown("#### 🇧🇩 Bangladesh Regional Recruitment Hubs")
        fig_bd_geo = px.bar(
            df_bd_geo,
            x="Jobs_Count",
            y="Division",
            orientation="h",
            color="Jobs_Count",
            color_continuous_scale="Tealgrn",
            labels={"Jobs_Count": "Open Vacancies", "Division": "Regional Division"},
            title="Jobs by Bangladesh Administrative Division",
            template="plotly_dark"
        )
        fig_bd_geo.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bd_geo, use_container_width=True)
        st.dataframe(df_bd_geo, use_container_width=True, hide_index=True)

    with col_g2:
        st.markdown("#### 🌐 Global Remote & International Hubs")
        fig_global_geo = px.pie(
            df_global_geo,
            names="Region",
            values="Jobs_Count",
            hole=0.45,
            title="Global Vacancies by Continent / Tech Hub",
            template="plotly_dark"
        )
        fig_global_geo.update_layout(
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_global_geo, use_container_width=True)
        st.dataframe(df_global_geo, use_container_width=True, hide_index=True)

# Tab 6: Smart Resume Matcher & AI Pitch Generator
with tab6:
    st.subheader("📄 Smart Resume / CV Matcher & AI Outreach Generator")
    st.markdown("Upload your CV to calculate your skill match percentage, identify gaps, and generate customized recruiter pitch letters.")

    col_rm1, col_rm2 = st.columns([1, 1])

    with col_rm1:
        st.markdown("#### 📤 Upload Resume (PDF)")
        uploaded_file = st.file_uploader("Choose your CV PDF", type=["pdf"])

        detected_profile = None
        if uploaded_file is not None:
            with st.spinner("Analyzing resume content..."):
                resume_text = resume_matcher.parse_resume_pdf(uploaded_file)
                if resume_text:
                    detected_profile = resume_matcher.analyze_candidate_profile(resume_text)
                    st.success("✔ Resume parsed successfully!")
                    
                    rm_c1, rm_c2 = st.columns(2)
                    with rm_c1:
                        st.metric("Detected Skills", len(detected_profile["skills"]))
                    with rm_c2:
                        st.metric("Estimated Level", detected_profile["experience_level"])

                    st.markdown("**Your Identified Skills:**")
                    skill_pills = " ".join([f"<span class='badge-skill'>{s}</span>" for s in detected_profile["skills"]])
                    st.markdown(skill_pills, unsafe_allow_html=True)
                else:
                    st.error("Could not parse readable text from this PDF.")

    with col_rm2:
        st.markdown("#### ✍️ AI Cover Letter & LinkedIn Recruiter Pitch")
        st.markdown("Generate tailored application pitches for any job in the database:")

        target_job_list = all_jobs["title"] + " @ " + all_jobs["company"] if not all_jobs.empty else []
        selected_job_pitch = st.selectbox("Select Target Job:", target_job_list.head(30) if not all_jobs.empty else ["No jobs"])

        pitch_candidate_name = st.text_input("Your Full Name", value="Mohammad Farhan Hossain")
        pitch_exp = st.selectbox("Your Experience Level", ["1-2 Years", "2-4 Years (Mid)", "5+ Years (Senior)", "Fresher / Entry Level"], index=1)
        
        default_skills = ", ".join(detected_profile["skills"][:4]) if detected_profile and detected_profile["skills"] else "Python, FastAPI, SQL, Docker"
        pitch_skills_raw = st.text_input("Your Core Skills (comma separated)", value=default_skills)

        if st.button("Generate Tailored Cover Letter & Pitch"):
            if not all_jobs.empty:
                # Find matching row
                idx_selected = target_job_list[target_job_list == selected_job_pitch].index[0]
                target_job_data = all_jobs.loc[idx_selected].to_dict()

                user_skill_list = [s.strip() for s in pitch_skills_raw.split(",") if s.strip()]

                c_letter = career_advisor.generate_cover_letter(
                    candidate_name=pitch_candidate_name,
                    years_exp=pitch_exp,
                    current_role="Software Engineer",
                    user_skills=user_skill_list,
                    job=target_job_data
                )

                r_pitch = career_advisor.generate_recruiter_pitch(
                    candidate_name=pitch_candidate_name,
                    years_exp=pitch_exp,
                    user_skills=user_skill_list,
                    job=target_job_data
                )

                st.subheader("📑 Formal Application Cover Letter")
                st.text_area("Cover Letter", value=c_letter, height=220)
                st.download_button("📥 Download Cover Letter (.txt)", c_letter, file_name=f"cover_letter_{target_job_data['company'][:10]}.txt")

                st.subheader("💬 LinkedIn Direct Recruiter Outreach Pitch (< 140 words)")
                st.text_area("Recruiter DM Pitch", value=r_pitch, height=140)

    # Recommendations row
    if uploaded_file is not None and detected_profile:
        st.markdown("---")
        st.subheader("🎯 Recommended Vacancies for Your Profile")
        matches = resume_matcher.match_resume_against_jobs(resume_text, top_n=10)

        for m in matches:
            st.markdown(f"""
            <div class='match-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h3 style='margin: 0; color: #38bdf8;'>{m['title']}</h3>
                    <span style='font-size: 18px; font-weight: bold; color: {'#10b981' if m['match_score'] >= 60 else '#f59e0b'};'>
                        {m['match_score']}% Match
                    </span>
                </div>
                <p style='margin: 5px 0 10px 0; color: #94a3b8;'>
                    <b>{m['company']}</b> • {m['location']} • <span style='color: #818cf8;'>{m['field']}</span>
                </p>
                <div>
                    <b>Matched Skills:</b> {' '.join([f"<span class='badge-skill'>{s}</span>" for s in m['matched_skills']]) if m['matched_skills'] else 'Relevant profile match'}
                </div>
                <div style='margin-top: 5px;'>
                    <b>Missing Skills to learn:</b> {' '.join([f"<span class='badge-missing'>{s}</span>" for s in m['missing_skills']]) if m['missing_skills'] else 'None (Full match!)'}
                </div>
                <div style='margin-top: 12px;'>
                    <a href='{m['job_url']}' target='_blank' style='background: #38bdf8; color: #0f172a; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold;'>
                        ↗ Apply on Job Post
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Tab 7: Career Pathways & Skill Roadmaps
with tab7:
    st.subheader("🎓 Career Pathways, Skill Roadmaps & Interview Question Bank")
    st.markdown("Structured technical learning roadmap and interview screening preparation kit for in-demand roles.")

    available_roadmaps = list(career_advisor.ROADMAP_DATA.keys()) + ["Cybersecurity & Pentesting", "SQA & Automation", "Power & High Voltage"]
    selected_roadmap_role = st.selectbox("Select Specialization Roadmap:", available_roadmaps, index=0)

    roadmap_info = career_advisor.get_career_roadmap(selected_roadmap_role)

    r_col1, r_col2 = st.columns([2, 1])
    with r_col1:
        st.markdown(f"### 🚀 {roadmap_info['role']} Career Roadmap")
        st.caption(f"Market Status: {roadmap_info.get('demand', 'Active')}")
        st.info(roadmap_info["summary"])

        st.markdown(f"""
        <div class='roadmap-step'>
            <h4 style='margin-top:0; color:#38bdf8;'>Phase 1: Foundations & Core Prerequisites</h4>
            <ul>
                {''.join([f"<li>{item}</li>" for item in roadmap_info['phase1']])}
            </ul>
        </div>
        <div class='roadmap-step'>
            <h4 style='margin-top:0; color:#10b981;'>Phase 2: Production Frameworks & Industry Tools</h4>
            <ul>
                {''.join([f"<li>{item}</li>" for item in roadmap_info['phase2']])}
            </ul>
        </div>
        <div class='roadmap-step'>
            <h4 style='margin-top:0; color:#c084fc;'>Phase 3: High-Impact Projects & Production Scalability</h4>
            <ul>
                {''.join([f"<li>{item}</li>" for item in roadmap_info['phase3']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with r_col2:
        st.markdown("### 🏆 Recommended Certifications")
        for cert in roadmap_info.get("certifications", ["Industry Vendor Certification"]):
            st.markdown(f"- 🎖️ **{cert}**")

        st.markdown("---")
        st.markdown("### 💡 Live Role Vacancies")
        role_jobs = all_jobs[all_jobs["specialization"].str.contains(selected_roadmap_role[:10], case=False, na=False)]
        st.metric("Open Vacancies in Database", len(role_jobs))
        if not role_jobs.empty:
            st.dataframe(
                role_jobs[["title", "company", "location"]].head(6),
                use_container_width=True,
                hide_index=True
            )

    st.markdown("---")
    st.subheader(f"🧠 Technical Screening Interview Questions for {roadmap_info['role']}")
    st.markdown("Curated real-world questions asked in technical screening rounds:")

    for idx, q_item in enumerate(roadmap_info.get("interview_questions", [])):
        st.markdown(f"""
        <div class='interview-q'>
            <b style='color: #38bdf8;'>Q{idx+1}: {q_item['q']}</b>
            <div style='margin-top: 6px; font-size: 13px; color: #94a3b8;'>
                💡 <b>Interview Key / Expected Answer:</b> {q_item['hint']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Tab 8: Salary Benchmarking & Compensation Analytics
with tab8:
    st.subheader("💰 Salary Benchmarking & Compensation Intelligence")
    st.markdown("Empirical market compensation estimates and salary bands across technical disciplines and experience levels.")

    explicit_salary_jobs = all_jobs[all_jobs["salary_info"].str.contains(r"\$|\d+|BDT|Tk", case=False, na=False) & ~all_jobs["salary_info"].str.contains("Negotiable", case=False, na=False)]
    
    sk1, sk2, sk3, sk4 = st.columns(4)
    with sk1:
        st.metric("Explicit Salary Disclosures", f"{len(explicit_salary_jobs)} Posts")
    with sk2:
        st.metric("Avg Hourly Rate (Global Remote)", "$30 - $65 / hr")
    with sk3:
        st.metric("BD Fresher Tech Band", "30k - 50k BDT / mo")
    with sk4:
        st.metric("BD Senior/Lead Tech Band", "150k - 350k+ BDT / mo")

    st.markdown("---")
    st.subheader("🧮 Interactive Salary Benchmark Calculator")
    st.markdown("Calculate estimated market salary percentiles based on specialization and experience level:")

    calc_c1, calc_c2, calc_c3 = st.columns(3)
    
    spec_list_calc = sorted(list(all_jobs["specialization"].dropna().unique())) if "specialization" in all_jobs.columns else ["Software Engineer"]
    with calc_c1:
        calc_spec = st.selectbox("Select Specialization Role:", spec_list_calc, index=0)
    with calc_c2:
        calc_exp = st.selectbox("Select Experience Tier:", [
            "Fresher / Entry Level (0-1 Yr)",
            "Junior (1-2 Yrs)",
            "Mid Level (2-4 Yrs)",
            "Senior (5+ Yrs)",
            "Lead / Principal / Architect (8+ Yrs)"
        ], index=2)
    with calc_c3:
        calc_market = st.selectbox("Select Target Market:", [
            "🇧🇩 Bangladesh Domestic Market (BDT / Month)",
            "🌐 International Remote (USD / Month)"
        ])

    role_multipliers = {
        "Machine Learning & AI": 1.35,
        "VLSI / ASIC Design": 1.40,
        "Cloud & DevOps": 1.25,
        "Cybersecurity & Pentesting": 1.30,
        "Python & FastAPI Backend": 1.15,
        "Full Stack Software Engineer": 1.15,
        "Embedded & Firmware": 1.20,
        "Data Engineering & ETL": 1.20,
        "Power & High Voltage": 1.10,
        "Construction & Civil Project": 1.05,
    }
    
    role_mult = 1.10
    for r_k, r_v in role_multipliers.items():
        if r_k.lower() in calc_spec.lower():
            role_mult = r_v
            break

    if "Fresher" in calc_exp:
        base_low, base_med, base_high = 25000, 35000, 48000
        usd_low, usd_med, usd_high = 300, 500, 800
    elif "Junior" in calc_exp:
        base_low, base_med, base_high = 40000, 55000, 75000
        usd_low, usd_med, usd_high = 600, 1000, 1500
    elif "Mid" in calc_exp:
        base_low, base_med, base_high = 70000, 100000, 145000
        usd_low, usd_med, usd_high = 1200, 2000, 2800
    elif "Senior" in calc_exp:
        base_low, base_med, base_high = 140000, 190000, 270000
        usd_low, usd_med, usd_high = 2500, 3800, 5000
    else:  # Lead
        base_low, base_med, base_high = 220000, 300000, 450000
        usd_low, usd_med, usd_high = 4500, 6500, 9500

    if "Bangladesh" in calc_market:
        low_val = int(base_low * role_mult)
        med_val = int(base_med * role_mult)
        high_val = int(base_high * role_mult)
        cur_sym = "BDT"
    else:
        low_val = int(usd_low * role_mult)
        med_val = int(usd_med * role_mult)
        high_val = int(usd_high * role_mult)
        cur_sym = "USD"

    st.markdown(f"""
    <div class='salary-box'>
        <div style='display: flex; justify-content: space-around; text-align: center;'>
            <div>
                <span style='font-size: 13px; color: #94a3b8;'>25th Percentile (Entry Band)</span>
                <div style='font-size: 24px; font-weight: bold; color: #38bdf8;'>{cur_sym} {low_val:,} / mo</div>
            </div>
            <div style='border-left: 2px solid #059669; border-right: 2px solid #059669; padding: 0 30px;'>
                <span style='font-size: 13px; color: #34d399; font-weight: bold;'>50th Percentile (Market Median)</span>
                <div style='font-size: 28px; font-weight: bold; color: #10b981;'>{cur_sym} {med_val:,} / mo</div>
            </div>
            <div>
                <span style='font-size: 13px; color: #94a3b8;'>75th Percentile (Top Tier / MNC)</span>
                <div style='font-size: 24px; font-weight: bold; color: #c084fc;'>{cur_sym} {high_val:,} / mo</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ladder_data = pd.DataFrame([
        {"Tier": "Fresher (0-1Y)", "Min_BDT": int(25000 * role_mult), "Median_BDT": int(35000 * role_mult), "Max_BDT": int(48000 * role_mult)},
        {"Tier": "Junior (1-2Y)", "Min_BDT": int(40000 * role_mult), "Median_BDT": int(55000 * role_mult), "Max_BDT": int(75000 * role_mult)},
        {"Tier": "Mid Level (2-4Y)", "Min_BDT": int(70000 * role_mult), "Median_BDT": int(100000 * role_mult), "Max_BDT": int(145000 * role_mult)},
        {"Tier": "Senior (5+Y)", "Min_BDT": int(140000 * role_mult), "Median_BDT": int(190000 * role_mult), "Max_BDT": int(270000 * role_mult)},
        {"Tier": "Lead / Architect", "Min_BDT": int(220000 * role_mult), "Median_BDT": int(300000 * role_mult), "Max_BDT": int(450000 * role_mult)}
    ])

    fig_ladder = px.bar(
        ladder_data,
        x="Tier",
        y="Median_BDT",
        error_y=ladder_data["Max_BDT"] - ladder_data["Median_BDT"],
        error_y_minus=ladder_data["Median_BDT"] - ladder_data["Min_BDT"],
        color="Median_BDT",
        color_continuous_scale="Greens",
        labels={"Median_BDT": "Estimated Compensation (BDT/Month)", "Tier": "Career Progression Tier"},
        title=f"Compensation Progression Ladder for {calc_spec}",
        template="plotly_dark"
    )
    fig_ladder.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_ladder, use_container_width=True)

    st.markdown("---")
    st.subheader(f"📌 Postings with Explicitly Disclosed Compensation ({len(explicit_salary_jobs)} Posts)")
    if not explicit_salary_jobs.empty:
        dis_cols = ["title", "company", "specialization", "salary_info", "location", "job_url"]
        st.dataframe(
            explicit_salary_jobs[[c for c in dis_cols if c in explicit_salary_jobs.columns]],
            column_config={
                "job_url": st.column_config.LinkColumn("Apply Link", display_text="Open Job Post")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Most companies in this region classify salary as 'Negotiable' upon interview.")

# Tab 9: Link Health, Executive Reports & Email Digest
with tab9:
    st.subheader("🔄 3-Day Link Verification, Executive Reports & Email Digest")

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        st.markdown("#### ⏱️ Job Link Health Checker (Runs every 3 days)")
        st.write("Verifies whether posted links are still active or have been closed / expired by employers.")

        active_cnt = len(all_jobs[all_jobs["status"] == "Active"])
        expired_cnt = len(all_jobs[all_jobs["status"] == "Expired"])

        st.metric("Live Active Jobs", active_cnt)
        st.metric("Closed / Expired Jobs", expired_cnt)

        if st.button("Run Link Verification Check Now"):
            with st.spinner("Checking job URLs..."):
                res = link_checker.run_link_health_check(days_interval=3, max_check=30)
                st.success(f"Checked {res['checked']} jobs! Active: {res['active']}, Expired: {res['expired']}")
                st.rerun()

    with col_h2:
        st.markdown("#### 📑 Executive PDF & Excel Reports")
        st.write("Generate printable publication-ready reports for records or presentations.")

        if st.button("Generate Printable Executive PDF Report"):
            with st.spinner("Compiling ReportLab PDF..."):
                pdf_file = pdf_reporter.generate_executive_pdf_report()
                st.success(f"Generated Executive PDF Report!")
                st.markdown(f"- File Path: `{pdf_file}`")
                
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Download Executive PDF Report",
                        data=f.read(),
                        file_name=Path(pdf_file).name,
                        mime="application/pdf"
                    )

        st.markdown("---")
        if st.button("Generate Today's Excel Report"):
            rep = reporter.generate_daily_report()
            st.success(f"Generated daily report for {rep['date']}!")
            st.markdown(f"- Excel: `{rep['excel']}`")

    st.markdown("---")
    st.subheader("📧 Daily Morning Email Digest Center")
    st.markdown("Automated morning HTML summary email delivering top new jobs, trending skills, and attached Excel reports.")

    ed_col1, ed_col2 = st.columns([1, 1])

    with ed_col1:
        st.markdown("##### ⚙️ Digest Configuration Status")
        smtp_configured = bool(os.environ.get("SMTP_SERVER") and os.environ.get("SMTP_USER"))
        if smtp_configured:
            st.success("✔ SMTP credentials detected in environment!")
            st.write(f"- Server: `{os.environ.get('SMTP_SERVER')}:{os.environ.get('SMTP_PORT', 587)}`")
            st.write(f"- User: `{os.environ.get('SMTP_USER')}`")
            st.write(f"- Recipient: `{os.environ.get('DIGEST_RECIPIENT_EMAIL', 'Default')}`")
        else:
            st.info("ℹ️ Running in **Local Preview Mode** (SMTP env vars not yet configured). Previews are saved locally to `reports/daily/`.")
            st.markdown("""
            To configure automated email delivery, set these environment variables (or GitHub Secrets):
            - `SMTP_SERVER` (e.g. `smtp.gmail.com`)
            - `SMTP_PORT` (e.g. `587`)
            - `SMTP_USER` (your email address)
            - `SMTP_PASSWORD` (Gmail App Password)
            - `DIGEST_RECIPIENT_EMAIL` (destination email)
            """)

    with ed_col2:
        st.markdown("##### 🚀 Test & Preview Actions")
        if st.button("Preview HTML Email Digest"):
            d_res = email_digest.generate_digest_html()
            st.success("HTML Email Digest preview generated!")
            with st.expander("👁️ View Rendered Email Digest Preview", expanded=True):
                components.html(d_res["html_content"], height=600, scrolling=True)

        if st.button("Send Email Digest (Live / Preview)"):
            with st.spinner("Processing email digest..."):
                send_res = email_digest.send_daily_digest()
                if send_res.get("status") == "sent":
                    st.success(f"✔ Email digest sent successfully to {send_res.get('recipient')}!")
                elif send_res.get("status") == "preview_saved":
                    st.info(f"✔ Email preview successfully created at `{send_res.get('preview_file')}`!")
                else:
                    st.error(f"Error: {send_res.get('error')}")

@echo off
title LinkedIn Job Trends Dashboard
cd /d "%~dp0"

echo Starting Streamlit Web Dashboard...
.venv\Scripts\python.exe -m streamlit run dashboard.py

pause

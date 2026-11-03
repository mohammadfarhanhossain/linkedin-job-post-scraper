@echo off
title LinkedIn & Multi-Platform Daily Job Pipeline
cd /d "%~dp0"

echo ========================================================
echo     LinkedIn, BDJobs ^& Indeed Daily Recruitment Pipeline
echo ========================================================
echo Running daily automation (Scraping, Link Health, Excel, PDF ^& Email Digest)...

.venv\Scripts\python.exe automation_runner.py >> reports\daily_automation.log 2>&1

echo.
echo Automation completed! Check reports\ for generated reports and logs.
timeout /t 5

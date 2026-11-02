@echo off
title LinkedIn Daily Job Scraper
cd /d "%~dp0"

echo ========================================================
echo     LinkedIn Daily Job Scraper & Trend Tracker
echo ========================================================
echo Running daily scrape...

.venv\Scripts\python.exe main.py scrape --mode quick >> reports\daily_scrape.log 2>&1

echo.
echo Scraping complete! Check reports\daily\ for today's Excel report.
timeout /t 5

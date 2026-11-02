@echo off
title LinkedIn Deep Exhaustive Job Scraper
cd /d "%~dp0"

echo ===================================================================
echo     LinkedIn Deep Multi-City & Global Exhaustive Scraper
echo     (Sweeping Dhaka, Chattogram, Sylhet, Khulna, Worldwide...)
echo ===================================================================
echo.
echo Running deep multi-partition scrape (past 30 days active posts)...

.venv\Scripts\python.exe main.py scrape --mode deep >> reports\deep_scrape.log 2>&1

echo.
echo Deep scraping completed! Check dashboard or reports\daily for updated jobs.
pause

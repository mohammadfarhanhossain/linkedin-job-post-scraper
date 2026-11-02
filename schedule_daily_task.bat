@echo off
title Setup Windows Daily Task Scheduler
cd /d "%~dp0"

echo ========================================================
echo     Schedule LinkedIn Daily Scraper (Everyday 9:00 AM)
echo ========================================================
echo.

set SCRIPT_PATH=%~dp0run_daily.bat
set TASK_NAME=LinkedInJobScraperDaily

echo Creating Windows Scheduled Task: %TASK_NAME%
echo It will run everyday at 09:00 AM.
echo.

schtasks /create /tn "%TASK_NAME%" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 09:00 /f

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] Daily scheduled task successfully registered!
    echo Your job scraper will run automatically every day at 09:00 AM.
) else (
    echo.
    echo [NOTE] If this failed with Access Denied, please right-click this file
    echo and select "Run as administrator".
)

echo.
pause

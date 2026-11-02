@echo off
title LinkedIn Mega Job Harvester
cd /d "%~dp0"

echo ===================================================================
echo     LinkedIn Mega Job Harvester (Scaling to Thousands of Jobs)
echo     Sweeping Bangladesh Umbrella Roles + Global Tech Hubs...
echo ===================================================================
echo.

.venv\Scripts\python.exe mega_harvest.py

echo.
echo ===================================================================
echo Harvesting completed! Check dashboard at http://localhost:8501
echo ===================================================================
pause

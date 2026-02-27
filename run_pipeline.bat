@echo off
REM Weekly wireless research digest pipeline
REM Run manually or via Windows Task Scheduler (see automation/weekly_digest.xml)

cd /d E:\59357\Documents\GitHub\wireless-research-intel

echo [%DATE% %TIME%] Starting ingest...
python ingest_openalex.py
if %ERRORLEVEL% NEQ 0 (
    echo [%DATE% %TIME%] ERROR: ingest_openalex.py failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Generating report...
python generate_report.py --weeks 4
if %ERRORLEVEL% NEQ 0 (
    echo [%DATE% %TIME%] ERROR: generate_report.py failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Pipeline complete.

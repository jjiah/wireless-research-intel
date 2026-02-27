@echo off
REM Weekly wireless research digest pipeline
REM Run manually or via Windows Task Scheduler (see automation/weekly_digest.xml)
REM
REM NOTE: Task Scheduler may not use your interactive PATH.
REM If 'python' is not found, set PYTHON_CMD to the full path of your Python executable:
REM   set PYTHON_CMD=C:\Users\<you>\AppData\Local\Programs\Python\Python313\python.exe

cd /d "%~dp0"

set PYTHON_CMD=python
set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set LOGFILE=%LOGDIR%\pipeline_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%.log

echo [%DATE% %TIME%] Starting pipeline >> "%LOGFILE%" 2>&1
echo [%DATE% %TIME%] Starting pipeline

echo [%DATE% %TIME%] Starting ingest... >> "%LOGFILE%" 2>&1
echo [%DATE% %TIME%] Starting ingest...
%PYTHON_CMD% ingest_openalex.py >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [%DATE% %TIME%] ERROR: ingest_openalex.py failed with code %ERRORLEVEL% >> "%LOGFILE%" 2>&1
    echo [%DATE% %TIME%] ERROR: ingest_openalex.py failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Generating report... >> "%LOGFILE%" 2>&1
echo [%DATE% %TIME%] Generating report...
%PYTHON_CMD% generate_report.py --weeks 4 >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [%DATE% %TIME%] ERROR: generate_report.py failed with code %ERRORLEVEL% >> "%LOGFILE%" 2>&1
    echo [%DATE% %TIME%] ERROR: generate_report.py failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Pipeline complete. >> "%LOGFILE%" 2>&1
echo [%DATE% %TIME%] Pipeline complete.

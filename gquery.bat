@echo off
REM Google Agent CLI - Quick query tool for Gmail and Calendar
REM Usage: gquery "your query here"

if "%1"=="" (
    echo Usage: gquery "your query here"
    echo.
    echo Examples:
    echo   gquery "How many unread emails in my inbox?"
    echo   gquery "How many emails from alice@example.com in inbox?"
    echo   gquery "What events do I have today?"
    echo   gquery "How many days does AJ work this week?"
    exit /b 1
)

python -c "from agents import GoogleAgent; from utils import print_result; result = GoogleAgent().execute_task('%*'); print_result(result)"

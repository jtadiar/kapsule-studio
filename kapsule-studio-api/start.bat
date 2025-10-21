@echo off
REM Kapsule Studio API Startup Script for Windows

echo Starting Kapsule Studio API...

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env with your configuration before continuing.
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo Warning: FFmpeg is not installed!
    echo Please install FFmpeg and add it to your PATH.
    pause
    exit /b 1
)

echo All checks passed!
echo.
echo Starting server on port 8000...
echo API docs available at: http://localhost:8000/docs
echo.

REM Start the server
uvicorn main:app --reload --port 8000


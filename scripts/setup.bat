@echo off
REM Setup script for Tipster IA Bot (Windows)
REM Run this script to initialize the project

echo ==========================================
echo 🤖 TIPSTER IA BOT - Setup Script
echo ==========================================
echo.

REM Check Python version
echo 🔍 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

python -c "import sys; print(sys.version)" >nul 2>&1
echo ✅ Python found
echo.

REM Create virtual environment
echo 📦 Creating virtual environment...
if exist "venv" (
    echo ⚠️  Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)
echo.

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip -q
echo ✅ pip upgraded
echo.

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt -q
echo ✅ Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env file from .env.example...
    copy .env.example .env
    echo ✅ .env file created
    echo.
    echo ⚠️  IMPORTANT: Edit .env file with your credentials before running the bot!
    echo    Required variables:
    echo    - TELEGRAM_BOT_TOKEN
    echo    - TELEGRAM_ADMIN_ID
    echo    - ANTHROPIC_API_KEY
    echo.
) else (
    echo ⚠️  .env file already exists. Skipping...
    echo.
)

REM Create logs directory
echo 📁 Creating logs directory...
if not exist "logs" mkdir logs
echo ✅ Logs directory created
echo.

REM Initialize git repository if not already initialized
if not exist ".git" (
    echo 🔧 Initializing Git repository...
    git init
    echo ✅ Git repository initialized
    echo.
    
    echo 📝 Creating initial commit...
    git add .
    git commit -m "chore: initial project setup - Día 1 Sprint"
    echo ✅ Initial commit created
    echo.
) else (
    echo ⚠️  Git repository already initialized. Skipping...
    echo.
)

echo ==========================================
echo ✅ Setup completed successfully!
echo ==========================================
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your credentials
echo 2. Run: python main.py
echo.
echo 📚 Documentation: See README.md
echo.
pause
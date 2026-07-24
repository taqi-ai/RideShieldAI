@echo off
echo =========================================
echo RideShieldAI Launcher
echo =========================================

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Please ensure Python is installed.
        pause
        exit /b
    )
    echo Virtual environment created successfully.
)

echo Activating virtual environment and checking dependencies...
call .venv\Scripts\activate.bat

echo Installing/Updating dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo Starting RideShieldAI...
python main.py

echo.
pause

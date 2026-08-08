@echo off
echo Starting Rental Management System Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the application
echo Starting FastAPI server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

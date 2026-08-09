@echo off
setlocal EnableDelayedExpansion

:: ============================================
:: Reprico - Full Stack Startup Script (Windows)
:: Runs: Backend + Frontend + Redis
:: ============================================

title Reprico - Rental Management System

echo.
echo  ========================================
echo     REPRICO - Rental Management System
echo           Full Stack Startup
echo  ========================================
echo.

:: ============================================
:: [1/6] Check Prerequisites
:: ============================================
echo [1/6] Checking prerequisites...

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  X Python not found. Install from https://python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo  OK %%i

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo  X Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo  OK Node.js %%i

:: Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo  X npm not found.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version 2^>^&1') do echo  OK npm %%i

echo.

:: ============================================
:: [2/6] Setup Backend
:: ============================================
echo [2/6] Setting up backend...

cd /d "%~dp0rental-backend"

if not exist "venv" (
    echo  Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtualenv
call venv\Scripts\activate.bat

:: Install dependencies
echo  Installing Python dependencies...
pip install -r requirements.txt -q 2>nul

:: Check .env
if not exist ".env" (
    echo  WARNING: .env file not found!
    echo  Copying from .env.example...
    copy .env.example .env >nul
    echo  Edit .env with your API keys before production use.
) else (
    echo  OK .env found
)

echo  OK Backend ready
echo.

:: ============================================
:: [3/6] Setup Frontend
:: ============================================
echo [3/6] Setting up frontend...

cd /d "%~dp0rental-frontend\ODOO-FRONT-"

if not exist "node_modules" (
    echo  Installing npm dependencies...
    call npm install --silent 2>nul
)

echo  OK Frontend ready
echo.

:: ============================================
:: [4/6] Start Redis
:: ============================================
echo [4/6] Starting Redis...

docker --version >nul 2>&1
if errorlevel 1 (
    echo  WARNING: Docker not found. Make sure Redis is running on localhost:6379
    echo  Install Docker Desktop: https://docker.com
) else (
    docker ps --format "{{.Names}}" 2>nul | findstr /i "reprico-redis" >nul 2>&1
    if errorlevel 1 (
        echo  Creating Redis container...
        docker run -d --name reprico-redis -p 6379:6379 redis:7-alpine
        timeout /t 3 /nobreak >nul
        echo  OK Redis started on port 6379
    ) else (
        docker ps --format "{{.Names}}" 2>nul | findstr /i "reprico-redis" >nul 2>&1
        if errorlevel 1 (
            docker start reprico-redis
            echo  OK Redis started
        ) else (
            echo  OK Redis already running
        )
    )
)

echo.

:: ============================================
:: [5/6] Run Migrations
:: ============================================
echo [5/6] Running database migrations...

cd /d "%~dp0rental-backend"
call venv\Scripts\activate.bat

alembic upgrade head 2>nul
if errorlevel 1 (
    echo  WARNING: Migration skipped. Run manually: alembic upgrade head
) else (
    echo  OK Migrations complete
)

echo.

:: ============================================
:: [6/6] Start Services
:: ============================================
echo [6/6] Starting services...
echo.

:: Start backend in new window
echo  Starting Backend (FastAPI on port 8000)...
start "Reprico Backend" cmd /k "cd /d %~dp0rental-backend && venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

:: Start frontend in new window
echo  Starting Frontend (Next.js on port 3000)...
start "Reprico Frontend" cmd /k "cd /d %~dp0rental-frontend\ODOO-FRONT- && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo  ========================================
echo     All services are running!
echo  ========================================
echo.
echo   Backend API:   http://localhost:8000/docs
echo   Frontend:      http://localhost:3000
echo   Health Check:  http://localhost:8000/health
echo   Redis:         localhost:6379
echo.
echo   Close the Backend and Frontend windows
echo   or press Ctrl+C in each to stop.
echo  ========================================
echo.

:: Open browser
echo  Opening browser...
start http://localhost:3000

pause

#!/bin/bash
# ============================================
# Reprico - Full Stack Startup Script
# Runs: Backend + Frontend + Redis
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/rental-backend"
FRONTEND_DIR="$PROJECT_ROOT/rental-frontend/ODOO-FRONT-"

print_banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         REPRICO - Rental Management System      ║${NC}"
    echo -e "${CYAN}║              Full Stack Startup                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_prerequisites() {
    echo -e "${BLUE}[1/6] Checking prerequisites...${NC}"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python3 not found. Install: brew install python${NC}"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}  ✓ $PYTHON_VERSION${NC}"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}✗ Node.js not found. Install: brew install node${NC}"
        exit 1
    fi
    NODE_VERSION=$(node --version 2>&1)
    echo -e "${GREEN}  ✓ Node.js $NODE_VERSION${NC}"

    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}✗ npm not found.${NC}"
        exit 1
    fi
    echo -e "${GREEN}  ✓ npm $(npm --version)${NC}"

    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}  ✓ Docker $(docker --version | cut -d' ' -f3 | tr -d ',')${NC}"
    else
        echo -e "${YELLOW}  ⚠ Docker not found (optional, needed for Redis)${NC}"
    fi

    echo ""
}

setup_backend() {
    echo -e "${BLUE}[2/6] Setting up backend...${NC}"

    cd "$BACKEND_DIR"

    # Create virtualenv if not exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}  Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi

    # Activate venv
    source venv/bin/activate

    # Set OpenSSL paths for macOS
    if [ -d "/usr/local/opt/openssl@3" ]; then
        export LDFLAGS="-L/usr/local/opt/openssl@3/lib"
        export CPPFLAGS="-I/usr/local/opt/openssl@3/include"
        export PKG_CONFIG_PATH="/usr/local/opt/openssl@3/lib/pkgconfig"
    elif [ -d "/opt/homebrew/opt/openssl@3" ]; then
        export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
        export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
        export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
    fi

    # Install dependencies
    echo -e "${YELLOW}  Installing Python dependencies...${NC}"
    pip install -r requirements.txt -q 2>/dev/null

    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo -e "${RED}  ✗ .env file not found!${NC}"
        echo -e "${YELLOW}  Copying from .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}  ⚠ Edit .env with your API keys before running in production${NC}"
    else
        echo -e "${GREEN}  ✓ .env found${NC}"
    fi

    echo -e "${GREEN}  ✓ Backend ready${NC}"
    echo ""
}

setup_frontend() {
    echo -e "${BLUE}[3/6] Setting up frontend...${NC}"

    cd "$FRONTEND_DIR"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}  Installing npm dependencies...${NC}"
        npm install --silent 2>/dev/null
    fi

    # Check if .env.local exists
    if [ ! -f ".env.local" ]; then
        echo -e "${YELLOW}  ⚠ .env.local not found. Using defaults.${NC}"
    fi

    echo -e "${GREEN}  ✓ Frontend ready${NC}"
    echo ""
}

start_redis() {
    echo -e "${BLUE}[4/6] Starting Redis...${NC}"

    if command -v docker &> /dev/null; then
        # Check if container already exists
        if docker ps -a --format '{{.Names}}' | grep -q 'reprico-redis'; then
            if docker ps --format '{{.Names}}' | grep -q 'reprico-redis'; then
                echo -e "${GREEN}  ✓ Redis already running${NC}"
            else
                echo -e "${YELLOW}  Starting existing Redis container...${NC}"
                docker start reprico-redis
                echo -e "${GREEN}  ✓ Redis started${NC}"
            fi
        else
            echo -e "${YELLOW}  Creating Redis container...${NC}"
            docker run -d \
                --name reprico-redis \
                -p 6379:6379 \
                redis:7-alpine
            sleep 2
            echo -e "${GREEN}  ✓ Redis started on port 6379${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠ Docker not found. Make sure Redis is running on localhost:6379${NC}"
        # Try to ping local redis
        if command -v redis-cli &> /dev/null; then
            if redis-cli ping | grep -q "PONG"; then
                echo -e "${GREEN}  ✓ Local Redis is responding${NC}"
            else
                echo -e "${RED}  ✗ Redis not responding. Install: brew install redis && brew services start redis${NC}"
            fi
        fi
    fi
    echo ""
}

run_migrations() {
    echo -e "${BLUE}[5/6] Running database migrations...${NC}"

    cd "$BACKEND_DIR"
    source venv/bin/activate

    # Check if DATABASE_URL is set to localhost (local dev)
    if grep -q "localhost" .env 2>/dev/null; then
        echo -e "${YELLOW}  Using local database. Run 'alembic upgrade head' if needed.${NC}"
    else
        echo -e "${YELLOW}  Running Alembic migrations...${NC}"
        alembic upgrade head 2>/dev/null || echo -e "${YELLOW}  ⚠ Migration skipped (DB may not be reachable)${NC}"
    fi

    echo -e "${GREEN}  ✓ Migrations complete${NC}"
    echo ""
}

start_services() {
    echo -e "${BLUE}[6/6] Starting services...${NC}"
    echo ""

    # Start backend
    echo -e "${CYAN}  Starting Backend (FastAPI on port 8000)...${NC}"
    cd "$BACKEND_DIR"
    source venv/bin/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    sleep 3

    # Start frontend
    echo -e "${CYAN}  Starting Frontend (Next.js on port 3000)...${NC}"
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    sleep 3

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           All services are running!              ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║                                                  ║${NC}"
    echo -e "${GREEN}║  Backend API:   http://localhost:8000/docs       ║${NC}"
    echo -e "${GREEN}║  Frontend:      http://localhost:3000            ║${NC}"
    echo -e "${GREEN}║  Health Check:  http://localhost:8000/health     ║${NC}"
    echo -e "${GREEN}║  Redis:         localhost:6379                   ║${NC}"
    echo -e "${GREEN}║                                                  ║${NC}"
    echo -e "${GREEN}║  Press Ctrl+C to stop all services               ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""

    # Trap to cleanup on exit
    cleanup() {
        echo ""
        echo -e "${YELLOW}Stopping services...${NC}"
        kill $BACKEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}All services stopped.${NC}"
        exit 0
    }

    trap cleanup SIGINT SIGTERM

    # Wait for processes
    wait
}

# ============================================
# MAIN
# ============================================
print_banner
check_prerequisites
setup_backend
setup_frontend
start_redis
run_migrations
start_services

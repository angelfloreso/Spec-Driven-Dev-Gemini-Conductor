#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# ANSI escape codes for colors
GREEN='\033[1;32m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   MedSched Development Server Starter  ${NC}"
echo -e "${BLUE}========================================${NC}"

# Find script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"
DB_FILE="${BACKEND_DIR}/medsched.db"

RESET_DB=0
FORCE_BOOTSTRAP=0

show_help() {
    echo -e "Usage: $0 [options]"
    echo -e ""
    echo -e "Options:"
    echo -e "  -r, --reset      Reset the database (delete medsched.db) before starting"
    echo -e "  -b, --bootstrap  Force bootstrapping demo users on startup"
    echo -e "  -h, --help       Show this help message"
    echo -e ""
}

# Parse command line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -r|--reset)
            RESET_DB=1
            shift
            ;;
        -b|--bootstrap)
            FORCE_BOOTSTRAP=1
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    python3 -c "
import socket
try:
    s = socket.socket()
    s.bind(('127.0.0.1', $port))
    s.close()
    print('FREE')
except Exception:
    print('IN_USE')
" 2>/dev/null | grep -q "IN_USE"
}

# Check port availability before starting
if is_port_in_use 8000; then
    echo -e "${RED}Error: Port 8000 (Backend) is already in use.${NC}"
    echo -e "Please stop any running backend processes and try again."
    exit 1
fi

if is_port_in_use 5173; then
    echo -e "${RED}Error: Port 5173 (Frontend) is already in use.${NC}"
    echo -e "Please stop any running frontend processes and try again."
    exit 1
fi

# Step 1: Handle Database Reset
if [ "$RESET_DB" = "1" ]; then
    if [ -f "$DB_FILE" ]; then
        echo -e "${YELLOW}Resetting database (deleting $DB_FILE)...${NC}"
        rm -f "$DB_FILE"
    else
        echo -e "${YELLOW}Database file not found, starting fresh...${NC}"
    fi
fi

# Determine if bootstrap is needed
DB_EXISTS=0
if [ -f "$DB_FILE" ]; then
    DB_EXISTS=1
fi

BOOTSTRAP_NEEDED=0
if [ $DB_EXISTS -eq 0 ] || [ "$FORCE_BOOTSTRAP" = "1" ]; then
    BOOTSTRAP_NEEDED=1
fi

# Step 2: Set up Backend virtual environment & dependencies
if [ ! -d "${BACKEND_DIR}/.venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment in backend/.venv...${NC}"
    python3 -m venv "${BACKEND_DIR}/.venv"
fi

echo -e "${GREEN}Verifying and installing backend dependencies...${NC}"
"${BACKEND_DIR}/.venv/bin/pip" install --upgrade pip
"${BACKEND_DIR}/.venv/bin/pip" install -r "${BACKEND_DIR}/requirements.txt"

# Step 3: Set up Frontend dependencies
if [ ! -d "${FRONTEND_DIR}/node_modules" ]; then
    echo -e "${YELLOW}node_modules not found. Installing frontend dependencies...${NC}"
    (cd "${FRONTEND_DIR}" && npm install)
fi

# Cleanup function to kill all spawned processes on exit
cleanup() {
    # Disable traps to avoid recursive calls
    trap - SIGINT SIGTERM EXIT
    echo -e "\n${YELLOW}Stopping backend and frontend processes...${NC}"
    
    # Kill the process group to ensure all background commands terminate cleanly
    kill -TERM -$$ 2>/dev/null || true
    
    if [ -n "${BACKEND_PID:-}" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "${FRONTEND_PID:-}" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}Cleaned up successfully. Bye!${NC}"
}
trap cleanup SIGINT SIGTERM EXIT

# Function to bootstrap database after backend is online
bootstrap_database() {
    echo -e "${GREEN}Waiting for backend to start up before bootstrapping...${NC}"
    local max_attempts=15
    local attempt=1
    local success=0
    
    while [ $attempt -le $max_attempts ]; do
        local status
        status=$(python3 -c "
import urllib.request
try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/docs', timeout=1)
    print(response.getcode())
except Exception:
    print('DOWN')
" 2>/dev/null)
        
        if [ "$status" = "200" ]; then
            success=1
            break
        fi
        
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ $success -eq 1 ]; then
        echo -e "${GREEN}Backend is ready! Bootstrapping demo users...${NC}"
        local bootstrap_res
        bootstrap_res=$(python3 -c "
import urllib.request
try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/auth/bootstrap', method='POST')
    response = urllib.request.urlopen(req, timeout=5)
    print(response.read().decode('utf-8'))
except Exception as e:
    print('ERROR:', e)
" 2>/dev/null)
        echo -e "${GREEN}Database bootstrap completed: ${NC}${CYAN}${bootstrap_res}${NC}"
    else
        echo -e "${RED}Warning: Backend did not start within 15 seconds. Skipping bootstrap.${NC}"
    fi
}

# Step 4: Start Backend in the background
echo -e "${GREEN}Starting backend on http://127.0.0.1:8000...${NC}"
export PYTHONUNBUFFERED=1
cd "${BACKEND_DIR}"
./.venv/bin/uvicorn app.main:app --reload --port 8000 > >(awk '{print "\033[1;32m[Backend]\033[0m " $0; fflush()}') 2>&1 &
BACKEND_PID=$!

# Step 5: Start Frontend in the background
echo -e "${GREEN}Starting frontend on http://127.0.0.1:5173...${NC}"
cd "${FRONTEND_DIR}"
npm run dev -- --port 5173 > >(awk '{print "\033[1;36m[Frontend]\033[0m " $0; fflush()}') 2>&1 &
FRONTEND_PID=$!

# Step 6: Perform database bootstrap if necessary
if [ $BOOTSTRAP_NEEDED -eq 1 ]; then
    bootstrap_database &
fi

# Wait for background services to exit
wait

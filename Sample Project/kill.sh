#!/usr/bin/env bash

set -e

GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

SIGTERM_ONLY=1

show_help() {
    echo -e "Usage: $0 [options]"
    echo -e ""
    echo -e "Options:"
    echo -e "  -f, --force      Use SIGKILL (force stop)"
    echo -e "  -h, --help       Show this help message"
    echo -e ""
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--force)
            SIGTERM_ONLY=0
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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   MedSched Development Server Killer   ${NC}"
echo -e "${BLUE}========================================${NC}"

# Return a unique list of PIDs listening on a given TCP port.
get_pids_on_port() {
    local port="$1"
    if command -v ss >/dev/null 2>&1; then
        ss -ltnp 2>/dev/null \
            | awk -v p=":${port}" '$4 ~ p {print $NF}' \
            | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' \
            | sort -u
    fi
}

kill_pid() {
    local pid="$1"
    local signal="$2"
    if kill "-${signal}" "$pid" 2>/dev/null; then
        echo -e "${GREEN}Stopped PID ${pid} with SIG${signal}.${NC}"
        return 0
    fi
    return 1
}

STOPPED_ANY=0
SIGNAL="TERM"
if [[ "$SIGTERM_ONLY" -eq 0 ]]; then
    SIGNAL="KILL"
fi

# Kill by ports first (most reliable for this project).
for port in 8000 5173; do
    mapfile -t pids < <(get_pids_on_port "$port")
    if [[ "${#pids[@]}" -gt 0 ]]; then
        echo -e "${YELLOW}Found process(es) on port ${port}: ${pids[*]}${NC}"
        for pid in "${pids[@]}"; do
            if kill_pid "$pid" "$SIGNAL"; then
                STOPPED_ANY=1
            fi
        done
    fi
done

# Fallback: kill known dev processes if still running.
if command -v pkill >/dev/null 2>&1; then
    if [[ "$SIGTERM_ONLY" -eq 1 ]]; then
        pkill -f "uvicorn app.main:app --reload --port 8000" 2>/dev/null && STOPPED_ANY=1 || true
        pkill -f "vite --port 5173" 2>/dev/null && STOPPED_ANY=1 || true
        pkill -f "npm run dev -- --port 5173" 2>/dev/null && STOPPED_ANY=1 || true
    else
        pkill -9 -f "uvicorn app.main:app --reload --port 8000" 2>/dev/null && STOPPED_ANY=1 || true
        pkill -9 -f "vite --port 5173" 2>/dev/null && STOPPED_ANY=1 || true
        pkill -9 -f "npm run dev -- --port 5173" 2>/dev/null && STOPPED_ANY=1 || true
    fi
fi

if [[ "$STOPPED_ANY" -eq 1 ]]; then
    echo -e "${GREEN}Done. Requested MedSched processes were stopped.${NC}"
else
    echo -e "${YELLOW}No MedSched backend/frontend processes were found.${NC}"
fi

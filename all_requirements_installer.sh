#!/bin/bash

# ============================================================
#  PPA-DUN API Project - Dependency Installer
#  Usage: bash install.sh
#  Run this from the project root directory.
# ============================================================

# --- Color codes for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   PPA-DUN Dependency Installer       ${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# -----------------------------------------------
# HELPER: print section header
# -----------------------------------------------
section() {
    echo ""
    echo -e "${YELLOW}--------------------------------------${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}--------------------------------------${NC}"
}

# -----------------------------------------------
# HELPER: print result
# -----------------------------------------------
ok()   { echo -e "  ${GREEN}[OK]${NC}    $1"; PASS=$((PASS+1)); }
fail() { echo -e "  ${RED}[FAIL]${NC}  $1"; FAIL=$((FAIL+1)); }
skip() { echo -e "  ${YELLOW}[SKIP]${NC}  $1"; }

# -----------------------------------------------
# 1. API — Python (api/requirements.txt)
# -----------------------------------------------
section "API  |  Python packages  (api/requirements.txt)"

if [ ! -f "api/requirements.txt" ]; then
    skip "api/requirements.txt not found — skipping"
else
    # Check that python / pip exist
    if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
        fail "Python is not installed. Install Python 3.9+ and re-run."
    else
        PY=$(command -v python3 || command -v python)
        PIP=$(command -v pip3 || command -v pip)

        echo "  Using: $PY  |  $PIP"
        echo ""

        $PIP install -r api/requirements.txt

        if [ $? -eq 0 ]; then
            ok "api/requirements.txt installed successfully"
        else
            fail "api/requirements.txt installation failed"
        fi
    fi
fi

# -----------------------------------------------
# 2. Backend — Python (backend/requirements.txt)
# -----------------------------------------------
section "Backend  |  Python packages  (backend/requirements.txt)"

if [ ! -f "backend/requirements.txt" ]; then
    skip "backend/requirements.txt not found — skipping"
else
    if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
        fail "Python is not installed. Install Python 3.9+ and re-run."
    else
        PIP=$(command -v pip3 || command -v pip)

        $PIP install -r backend/requirements.txt

        if [ $? -eq 0 ]; then
            ok "backend/requirements.txt installed successfully"
        else
            fail "backend/requirements.txt installation failed"
        fi
    fi
fi

# -----------------------------------------------
# 3. Frontend — Node.js (frontend/package.json)
# -----------------------------------------------
section "Frontend  |  Node packages  (frontend/package.json)"

if [ ! -f "frontend/package.json" ]; then
    skip "frontend/package.json not found — skipping"
else
    if ! command -v node &>/dev/null; then
        fail "Node.js is not installed. Install Node.js 18+ and re-run."
    elif ! command -v npm &>/dev/null; then
        fail "npm is not installed. It usually comes with Node.js."
    else
        echo "  Using: $(node -v)  |  npm $(npm -v)"
        echo ""

        cd frontend
        npm install
        RESULT=$?
        cd ..

        if [ $RESULT -eq 0 ]; then
            ok "frontend/package.json installed successfully"
        else
            fail "frontend/package.json installation failed"
        fi
    fi
fi

# -----------------------------------------------
# 4. Summary
# -----------------------------------------------
echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Installation Summary                ${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "  ${GREEN}Passed : $PASS${NC}"
echo -e "  ${RED}Failed : $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}  All dependencies installed. Ready to run!${NC}"
else
    echo -e "${RED}  Some installations failed. Check the errors above.${NC}"
    exit 1
fi

echo ""
#!/bin/bash
# Nerdy Holder - Environment Check

echo "=================================="
echo "Nerdy Holder - Environment Check"
echo "=================================="
echo

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0

check_item() {
    local name=$1
    local status=$2
    local detail=$3

    if [ "$status" = "ok" ]; then
        echo -e "${GREEN}✓${NC} $name: $detail"
        ((PASS++))
    elif [ "$status" = "warn" ]; then
        echo -e "${YELLOW}⚠${NC} $name: $detail"
    else
        echo -e "${RED}✗${NC} $name: $detail"
        ((FAIL++))
    fi
}

echo "System Info:"
echo "----------------------------------------"

# Operating system
OS=$(uname -s)
if [ "$OS" = "Linux" ]; then
    DISTRO=$(cat /etc/os-release | grep "^NAME=" | cut -d'"' -f2)
    check_item "OS" "ok" "$DISTRO"
else
    check_item "OS" "fail" "$OS (unsupported, Linux only)"
fi

# Memory
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
FREE_MEM=$(free -g | awk '/^Mem:/{print $4}')
if [ "$TOTAL_MEM" -ge 4 ]; then
    check_item "Memory" "ok" "${TOTAL_MEM}GB (${FREE_MEM}GB free)"
else
    check_item "Memory" "warn" "${TOTAL_MEM}GB (4GB+ recommended)"
fi

# CPU
CPU_CORES=$(nproc)
check_item "CPU cores" "ok" "${CPU_CORES}"

echo
echo "Software Dependencies:"
echo "----------------------------------------"

# Python
if command -v python3 &> /dev/null; then
    PY_VER=$(python3 --version | cut -d' ' -f2)
    PY_MAJOR=$(echo $PY_VER | cut -d'.' -f1)
    PY_MINOR=$(echo $PY_VER | cut -d'.' -f2)

    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 8 ]; then
        check_item "Python" "ok" "$PY_VER"
    else
        check_item "Python" "fail" "$PY_VER (3.8+ required)"
    fi
else
    check_item "Python" "fail" "not installed"
fi

# pip
if command -v pip3 &> /dev/null; then
    PIP_VER=$(pip3 --version | awk '{print $2}')
    check_item "pip3" "ok" "$PIP_VER"
else
    check_item "pip3" "fail" "not installed"
fi

# systemd
if command -v systemctl &> /dev/null; then
    check_item "systemd" "ok" "installed"
else
    check_item "systemd" "fail" "not installed"
fi

# git (optional)
if command -v git &> /dev/null; then
    GIT_VER=$(git --version | awk '{print $3}')
    check_item "git" "ok" "$GIT_VER (optional)"
else
    check_item "git" "warn" "not installed (optional, for updates)"
fi

echo
echo "Permissions:"
echo "----------------------------------------"

# Root
if [ "$EUID" -eq 0 ]; then
    check_item "Current user" "ok" "root"
else
    check_item "Current user" "warn" "non-root (deployment needs sudo)"
fi

# /opt write permission
if [ -w "/opt" ]; then
    check_item "/opt writable" "ok" "yes"
else
    check_item "/opt writable" "fail" "no"
fi

echo
echo "Python Modules:"
echo "----------------------------------------"

# Check psutil
if python3 -c "import psutil" 2>/dev/null; then
    PSUTIL_VER=$(python3 -c "import psutil; print(psutil.__version__)")
    check_item "psutil" "ok" "$PSUTIL_VER"
else
    check_item "psutil" "fail" "not installed (pip3 install psutil)"
fi

# Check pytest (dev)
if python3 -c "import pytest" 2>/dev/null; then
    PYTEST_VER=$(python3 -c "import pytest; print(pytest.__version__)")
    check_item "pytest" "ok" "$PYTEST_VER (dev dependency)"
else
    check_item "pytest" "warn" "not installed (dev only)"
fi

echo
echo "=================================="
echo "Check Result:"
echo "=================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ Environment meets deployment requirements${NC}"
    echo
    echo "Ready to deploy:"
    echo "  sudo bash install.sh"
    exit 0
else
    echo -e "${RED}✗ Environment does not meet requirements${NC}"
    echo
    echo "Quick install (Ubuntu/Debian):"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y python3 python3-pip"
    echo "  pip3 install -r requirements.txt"
    exit 1
fi

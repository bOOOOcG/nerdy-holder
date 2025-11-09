#!/bin/bash
# Nerdy Holder - One-command Installation
# Usage: sudo bash install.sh

set -e

# Colors
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; B='\033[0;34m'; NC='\033[0m'

echo "Nerdy Holder 🤓☝ - Installation Script"
echo

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${R}Error: root privileges required${NC}"
    echo "Please use: sudo bash install.sh"
    exit 1
fi

# Quick check
echo -e "${G}▶ Checking environment...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${R}  ✗ Python3 not found, installing...${NC}"
    apt-get update -qq
    apt-get install -y python3 python3-pip -qq
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${G}  ✓ Python $PY_VER${NC}"

if ! command -v pip3 &> /dev/null; then
    echo -e "${Y}  Installing pip3...${NC}"
    apt-get install -y python3-pip -qq
fi

echo

# Ask mode
echo -e "${Y}Mode selection:${NC}"
echo "  1) Dynamic (25-35% random, recommended)"
echo "  2) Fixed target"
echo "  3) Custom dynamic range"
read -p "Enter [1]: " MODE
MODE=${MODE:-1}

if [ "$MODE" = "1" ]; then
    echo -e "${G}  ✓ Mode: Dynamic (25-35%)${NC}"
    RUN_ARGS=""
    MODE_DESC="Dynamic (25-35%)"
elif [ "$MODE" = "2" ]; then
    echo -e "${Y}Fixed target percentage? (${NC}recommended 70-85${Y})${NC}"
    read -p "Enter: " TARGET

    if ! [[ "$TARGET" =~ ^[0-9]+$ ]] || [ "$TARGET" -lt 10 ] || [ "$TARGET" -gt 95 ]; then
        echo -e "${R}Invalid input, using default dynamic mode${NC}"
        RUN_ARGS=""
        MODE_DESC="Dynamic (25-35%)"
    else
        echo -e "${G}  ✓ Mode: Fixed ${TARGET}%${NC}"
        RUN_ARGS="--fixed-target $TARGET"
        MODE_DESC="Fixed ${TARGET}%"
    fi
elif [ "$MODE" = "3" ]; then
    echo -e "${Y}Custom range - Minimum percentage? (${NC}10-90${Y})${NC}"
    read -p "Enter: " MIN_TARGET
    echo -e "${Y}Custom range - Maximum percentage? (${NC}10-95${Y})${NC}"
    read -p "Enter: " MAX_TARGET

    if ! [[ "$MIN_TARGET" =~ ^[0-9]+$ ]] || [ "$MIN_TARGET" -lt 10 ] || [ "$MIN_TARGET" -gt 90 ]; then
        echo -e "${R}Invalid min value, using default dynamic mode${NC}"
        RUN_ARGS=""
        MODE_DESC="Dynamic (25-35%)"
    elif ! [[ "$MAX_TARGET" =~ ^[0-9]+$ ]] || [ "$MAX_TARGET" -lt 10 ] || [ "$MAX_TARGET" -gt 95 ]; then
        echo -e "${R}Invalid max value, using default dynamic mode${NC}"
        RUN_ARGS=""
        MODE_DESC="Dynamic (25-35%)"
    elif [ "$MIN_TARGET" -ge "$MAX_TARGET" ]; then
        echo -e "${R}Min must be less than max, using default dynamic mode${NC}"
        RUN_ARGS=""
        MODE_DESC="Dynamic (25-35%)"
    else
        echo -e "${G}  ✓ Mode: Custom dynamic (${MIN_TARGET}-${MAX_TARGET}%)${NC}"
        RUN_ARGS="--dynamic-range $MIN_TARGET $MAX_TARGET"
        MODE_DESC="Custom dynamic (${MIN_TARGET}-${MAX_TARGET}%)"
    fi
else
    echo -e "${R}Invalid mode, using default dynamic${NC}"
    RUN_ARGS=""
    MODE_DESC="Dynamic (25-35%)"
fi
echo

# Install directory
DIR="/opt/nerdy-holder"

echo -e "${G}▶ Installing...${NC}"

# Create directory
mkdir -p $DIR

# Copy files
echo -e "${G}  Copying files...${NC}"
cp -r nerdy_holder/ $DIR/ 2>/dev/null || true
cp run_holder.py $DIR/ 2>/dev/null || true
cp run_benchmark.py $DIR/ 2>/dev/null || true
cp requirements.txt $DIR/ 2>/dev/null || true

# Install dependencies
echo -e "${G}  Installing dependencies...${NC}"
cd $DIR
pip3 install -q -r requirements.txt

# Create service
echo -e "${G}  Configuring service...${NC}"
cat > /etc/systemd/system/nerdy-holder.service << EOF
[Unit]
Description=Nerdy Holder - Over-engineering Memory Management
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 $DIR/run_holder.py $RUN_ARGS
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=nerdy-holder
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

# Start service
systemctl daemon-reload
systemctl enable nerdy-holder.service > /dev/null 2>&1
systemctl start nerdy-holder.service

sleep 2

# Verify
if systemctl is-active --quiet nerdy-holder.service; then
    echo
    echo -e "${G}Installation complete, service started${NC}"
    echo
    echo -e "${B}Mode:${NC}        $MODE_DESC"
    echo -e "${B}Install dir:${NC} $DIR"
    echo
    echo -e "${Y}Common commands:${NC}"
    echo "  Status:   systemctl status nerdy-holder"
    echo "  Restart:  systemctl restart nerdy-holder"
    echo "  Stop:     systemctl stop nerdy-holder"
    echo

    # Show current status
    if [ -f "$DIR/nerdy_status.json" ]; then
        sleep 1
        echo -e "${Y}Current status:${NC}"
        python3 << 'PYEOF'
import json
try:
    with open('/opt/nerdy-holder/nerdy_status.json', 'r') as f:
        s = json.load(f)
    print(f"  System memory: {s.get('system_memory', 0):.1f}%")
    print(f"  Holding:       {s.get('holding_mb', 0):.0f}MB")
    print(f"  Optimizations: {s.get('stats', {}).get('optimizations', 0)}")
except:
    pass
PYEOF
    fi

    echo
    echo -e "${G}Monitor:${NC}   bash deployment/monitor.sh"
    echo -e "${G}Uninstall:${NC} bash deployment/uninstall.sh"
    echo
else
    echo -e "${R}✗ Service failed to start${NC}"
    echo "Check status: systemctl status nerdy-holder"
    exit 1
fi

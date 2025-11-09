#!/bin/bash
# Nerdy Holder - Remote Installation
# Usage: curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-install.sh | sudo bash
# Auto mode: AUTO=yes curl -fsSL ... | sudo bash

set -e

G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; NC='\033[0m'

echo "Nerdy Holder 🤓☝ - Remote Installation"
echo

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${R}Error: root privileges required${NC}"
    exit 1
fi

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${Y}Installing git...${NC}"
    apt-get update -qq
    apt-get install -y git -qq
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${Y}Installing python3...${NC}"
    apt-get update -qq
    apt-get install -y python3 python3-pip -qq
fi

# Download project
TEMP_DIR="/tmp/nerdy-holder-$$"
REPO_URL="https://github.com/bOOOOcG/nerdy-holder.git"
DIR="/opt/nerdy-holder"

echo -e "${G}Downloading...${NC}"
if ! git clone -q $REPO_URL $TEMP_DIR 2>/dev/null; then
    echo -e "${R}Download failed${NC}"
    exit 1
fi

cd $TEMP_DIR

# Install dependencies
echo -e "${G}Installing dependencies...${NC}"
pip3 install -q -r requirements.txt

# Copy files
echo -e "${G}Installing files...${NC}"
mkdir -p $DIR
cp -r nerdy_holder/ $DIR/
cp run_holder.py $DIR/
cp run_benchmark.py $DIR/
cp requirements.txt $DIR/

# Auto mode selection
if [ "$AUTO" = "yes" ]; then
    MODE=1
    RUN_ARGS=""
else
    echo
    echo -e "${Y}Mode: 1) Dynamic (25-35%, default)  2) Fixed  3) Custom${NC}"
    read -p "Enter [1]: " MODE < /dev/tty
    MODE=${MODE:-1}

    case $MODE in
        2)
            read -p "Fixed target %: " TARGET < /dev/tty
            if [[ "$TARGET" =~ ^[0-9]+$ ]] && [ "$TARGET" -ge 10 ] && [ "$TARGET" -le 95 ]; then
                RUN_ARGS="--fixed-target $TARGET"
            else
                RUN_ARGS=""
            fi
            ;;
        3)
            read -p "Min %: " MIN < /dev/tty
            read -p "Max %: " MAX < /dev/tty
            if [[ "$MIN" =~ ^[0-9]+$ ]] && [[ "$MAX" =~ ^[0-9]+$ ]] && [ "$MIN" -lt "$MAX" ]; then
                RUN_ARGS="--dynamic-range $MIN $MAX"
            else
                RUN_ARGS=""
            fi
            ;;
        *)
            RUN_ARGS=""
            ;;
    esac
fi

# Create systemd service
echo -e "${G}Configuring service...${NC}"
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

# Cleanup
cd /
rm -rf $TEMP_DIR

sleep 2

if systemctl is-active --quiet nerdy-holder.service; then
    echo
    echo -e "${G}Installation complete, service started${NC}"
    echo
    echo -e "${Y}Commands:${NC}"
    echo "  Status:    systemctl status nerdy-holder"
    echo "  Restart:   systemctl restart nerdy-holder"
    echo "  Stop:      systemctl stop nerdy-holder"
    echo
    echo "  Monitor:   curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/deployment/monitor.sh | bash"
    echo "  Uninstall: curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-uninstall.sh | sudo bash"
    echo
else
    echo -e "${R}✗ Service failed to start${NC}"
    echo "Check status: systemctl status nerdy-holder"
    exit 1
fi

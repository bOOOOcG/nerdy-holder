#!/bin/bash
# Nerdy Holder - Remote Uninstall
# Usage: curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-uninstall.sh | sudo bash
# Skip confirm: CONFIRM=yes curl -fsSL ... | sudo bash

set -e

R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'; NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${R}Root privileges required${NC}"
    exit 1
fi

echo "Nerdy Holder - Uninstall"
echo

# Confirm unless CONFIRM=yes
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${Y}Confirm uninstall? (yes/no):${NC}"
    read -r CONFIRM_INPUT < /dev/tty
    if [ "$CONFIRM_INPUT" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
fi

echo -e "${G}Uninstalling...${NC}"

# Stop service
systemctl stop nerdy-holder.service 2>/dev/null || true
systemctl disable nerdy-holder.service 2>/dev/null || true

# Remove files
rm -f /etc/systemd/system/nerdy-holder.service
systemctl daemon-reload

# Ask about keeping params
if [ "$CONFIRM" != "yes" ] && [ -f "/opt/nerdy-holder/nerdy_params.json" ]; then
    echo -e "${Y}Keep parameter file? (yes/no):${NC}"
    read -r KEEP < /dev/tty
    if [ "$KEEP" = "yes" ]; then
        cp /opt/nerdy-holder/nerdy_params.json /tmp/nerdy_params_backup.json
        echo -e "${G}Backed up to: /tmp/nerdy_params_backup.json${NC}"
    fi
fi

rm -rf /opt/nerdy-holder

echo
echo -e "${G}✓ Uninstall complete${NC}"

#!/bin/bash
# Nerdy Holder - Uninstall
# Usage: sudo bash uninstall.sh

set -e

R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'; NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${R}Root privileges required${NC}"
    echo "Use: sudo bash uninstall.sh"
    exit 1
fi

echo -e "${Y}Confirm uninstall Nerdy Holder? (yes/no):${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

echo -e "${G}Uninstalling...${NC}"

# Stop service
systemctl stop nerdy-holder.service 2>/dev/null || true
systemctl disable nerdy-holder.service 2>/dev/null || true

# Remove files
rm -f /etc/systemd/system/nerdy-holder.service
systemctl daemon-reload

# Ask about keeping data
if [ -f "/opt/nerdy-holder/nerdy_params.json" ]; then
    echo -e "${Y}Keep parameter file? (yes/no):${NC}"
    read -r KEEP

    if [ "$KEEP" = "yes" ]; then
        cp /opt/nerdy-holder/nerdy_params.json /tmp/nerdy_params_backup.json
        echo -e "${G}Parameters backed up to: /tmp/nerdy_params_backup.json${NC}"
    fi
fi

rm -rf /opt/nerdy-holder

echo
echo -e "${G}✓ Uninstall complete${NC}"

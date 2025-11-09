#!/bin/bash
# Nerdy Holder - Monitoring Script

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

STATUS_FILE="/opt/nerdy-holder/nerdy_status.json"
PARAMS_FILE="/opt/nerdy-holder/nerdy_params.json"

clear

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Nerdy Holder - Real-time Monitor                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo

# Check service status
if systemctl is-active --quiet nerdy-holder.service; then
    echo -e "${GREEN}● Service: Running${NC}"
else
    echo -e "${RED}● Service: Stopped${NC}"
    echo
    echo "Start service: sudo systemctl start nerdy-holder"
    exit 1
fi

# Service uptime
UPTIME=$(systemctl show nerdy-holder.service --property=ActiveEnterTimestamp | cut -d'=' -f2)
echo "  Started: $UPTIME"

echo
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}System Overview${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

# System memory
free -h | awk '
/^Mem:/ {
    total=$2
    used=$3
    free=$4
    percent=int(($3/$2)*100)

    printf "  Total:    %6s\n", total
    printf "  Used:     %6s (%d%%)\n", used, percent
    printf "  Free:     %6s\n", free
}
'

echo
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Holder Status${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

if [ -f "$STATUS_FILE" ]; then
    # Parse JSON with python
    python3 << EOF
import json
import sys

try:
    with open('$STATUS_FILE', 'r') as f:
        status = json.load(f)

    target = status.get('current_target', 0)
    system_mem = status.get('system_memory', 0)
    holding_mb = status.get('holding_mb', 0)
    chunks = status.get('chunks_count', 0)

    stats = status.get('stats', {})
    perf = status.get('performance', {})

    error = system_mem - target

    print(f"  Target:  {target:.1f}%")
    print(f"  Actual:  {system_mem:.1f}%", end='')

    if abs(error) < 1:
        print(" \\033[92m✓ On target\\033[0m")
    elif error > 0:
        print(f" \\033[93m▲ +{error:.1f}%\\033[0m")
    else:
        print(f" \\033[96m▼ {error:.1f}%\\033[0m")

    print(f"  Holding: {holding_mb:.0f}MB ({chunks} chunks)")
    print()
    print("  Statistics:")
    print(f"    Decisions:     {stats.get('decisions', 0)}")
    print(f"    Adjustments:   {stats.get('adjustments', 0)}")
    print(f"    Blocked:       {stats.get('blocked', 0)}")
    print(f"    Optimizations: {stats.get('optimizations', 0)}")
    print()
    print("  Performance:")
    print(f"    Avg error:     {perf.get('avg_error', 0):.2f}%")
    print(f"    Volatility:    {perf.get('error_volatility', 0):.2f}%")
    print(f"    Block rate:    {perf.get('block_rate', 0):.1%}")
    print(f"    Score:         {perf.get('score', 0):.1f}")

except Exception as e:
    print(f"  Failed to parse status file: {e}", file=sys.stderr)
    sys.exit(1)
EOF

else
    echo -e "  ${RED}Status file not found: $STATUS_FILE${NC}"
fi

echo
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Parameters${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

if [ -f "$PARAMS_FILE" ]; then
    python3 << EOF
import json

try:
    with open('$PARAMS_FILE', 'r') as f:
        params = json.load(f)

    print(f"  PID:")
    print(f"    Kp: {params.get('pid_kp', 0):.2f}")
    print(f"    Ki: {params.get('pid_ki', 0):.2f}")
    print(f"    Kd: {params.get('pid_kd', 0):.2f}")
    print()
    print(f"  Response:")
    print(f"    Base:  {params.get('response_base', 0):.2f}")
    print(f"    Curve: {params.get('response_curve', 0):.2f}")
    print()
    print(f"  Best score:   {params.get('best_score', 0):.1f}")
    print(f"  Total runtime: {params.get('total_runtime_hours', 0):.1f}h")

except Exception as e:
    print(f"  Failed to parse params file: {e}", file=sys.stderr)
EOF

else
    echo -e "  ${RED}Params file not found: $PARAMS_FILE${NC}"
fi

echo
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Process Info${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

ps aux | grep "run_holder.py" | grep -v grep | awk '{
    printf "  PID:     %s\n", $2
    printf "  CPU:     %s%%\n", $3
    printf "  Memory:  %s%%\n", $4
    printf "  Runtime: %s\n", $10
}'

echo
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo
echo "Commands:"
echo "  Restart: sudo systemctl restart nerdy-holder"
echo "  Stop:    sudo systemctl stop nerdy-holder"
echo
echo "Press Ctrl+C to exit"
echo

# Continuous monitoring (optional)
if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
    echo "Refreshing every 5 seconds..."
    while true; do
        sleep 5
        bash $0
    done
fi

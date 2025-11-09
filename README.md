# nerdy-holder 🤓☝

**English** | [中文](README.zh-CN.md)

over-engineering memory holder

## Features

- PID controller
- Asymmetric strategy (fast release, conservative allocation)
- Scene-aware scoring (5 scenarios)
- Adaptive parameter optimization
- Performance tracking
- Benchmark system (9 test scenarios including nonlinear patterns)

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_controllers.py -v
```

## Usage

### Local Usage

```bash
# Standard mode (dynamic target, random 25-35%)
python run_holder.py

# Fixed target mode
python run_holder.py --fixed-target 80

# Disable benchmark export
python run_holder.py --no-benchmark
```

### Benchmark

```bash
python run_benchmark.py
```

### Server Deployment

**Quick Install (recommended):**
```bash
curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-install.sh | sudo bash
```

**Auto Install (skip prompts, use defaults):**
```bash
AUTO=yes curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-install.sh | sudo bash
```

**Manual Install:**
```bash
git clone https://github.com/bOOOOcG/nerdy-holder.git
cd nerdy-holder
sudo bash install.sh
```

**Uninstall:**
```bash
curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-uninstall.sh | sudo bash
```

**Auto Uninstall (skip confirmation):**
```bash
CONFIRM=yes curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-uninstall.sh | sudo bash
```

Monitoring:
```bash
systemctl status nerdy-holder          # Service status
bash deployment/monitor.sh             # Monitoring dashboard
```

Change target memory usage: Edit `/etc/systemd/system/nerdy-holder.service`, modify `--fixed-target` parameter, then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart nerdy-holder
```

Note: Must run directly on host machine. Docker containers not supported (isolated memory namespace). Requirements: Linux (Ubuntu 20.04+), Python 3.8+, root privileges.

## Project Structure

```
nerdy-holder/
├── nerdy_holder/          # Core package
│   ├── controllers/       # PID and response calculators
│   ├── predictors/        # EMA predictors
│   ├── optimizers/        # Parameter optimizers
│   ├── trackers/          # Performance trackers
│   ├── memory/            # Memory block management
│   └── core.py            # Core program
├── tests/                 # Test modules
│   ├── benchmark/         # Benchmark system
│   └── test_*.py          # Unit tests (35 tests)
├── deployment/            # Deployment scripts
├── run_holder.py          # Holder entry point
└── run_benchmark.py       # Benchmark entry point
```

## Algorithm

### PID Control
- Kp: Proportional control
- Ki: Integral control (with asymmetric recovery)
- Kd: Derivative control

### Asymmetric Strategy
- Release: Fast response, low cost
- Allocation: Conservative filling, high cost

### Performance Scoring
- 35% Error
- 30% Stability
- 20% Block rate
- 15% Adjustment rhythm

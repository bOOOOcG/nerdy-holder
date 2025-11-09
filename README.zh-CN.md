# nerdy-holder 🤓☝

[English](README.md) | **中文**

过度设计的内存持有器

## 特性

- PID控制器
- 非对称策略（快速释放，保守分配）
- 场景感知评分（5种场景）
- 自适应参数优化
- 性能追踪
- Benchmark系统（9个测试场景，含非线性变化测试）

## 安装

```bash
pip install -r requirements.txt
```

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_controllers.py -v
```

## 使用

### 本地运行

```bash
# 标准模式（动态目标，25-35%范围内随机变化）
python run_holder.py

# 固定目标模式
python run_holder.py --fixed-target 80

# 禁用benchmark导出
python run_holder.py --no-benchmark
```

### Benchmark

```bash
python run_benchmark.py
```

### 服务器部署

**快速安装（推荐）：**
```bash
curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-install.sh | sudo bash
```

**自动安装（跳过提示，使用默认值）：**
```bash
AUTO=yes curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-install.sh | sudo bash
```

**手动安装：**
```bash
git clone https://github.com/bOOOOcG/nerdy-holder.git
cd nerdy-holder
sudo bash install.sh
```

**卸载：**
```bash
curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-uninstall.sh | sudo bash
```

**自动卸载（跳过确认）：**
```bash
CONFIRM=yes curl -fsSL https://raw.githubusercontent.com/bOOOOcG/nerdy-holder/main/remote-uninstall.sh | sudo bash
```

监控：
```bash
systemctl status nerdy-holder          # 服务状态
bash deployment/monitor.sh             # 监控仪表板
```

修改目标占用率：编辑 `/etc/systemd/system/nerdy-holder.service`，修改 `--fixed-target` 参数，然后：
```bash
sudo systemctl daemon-reload
sudo systemctl restart nerdy-holder
```

注：需要直接在宿主机运行，不支持Docker容器（容器内存空间隔离）。系统要求：Linux (Ubuntu 20.04+), Python 3.8+, root权限。

## 项目结构

```
nerdy-holder/
├── nerdy_holder/          # 核心包
│   ├── controllers/       # PID和响应计算器
│   ├── predictors/        # EMA预测器
│   ├── optimizers/        # 参数优化器
│   ├── trackers/          # 性能追踪器
│   ├── memory/            # 内存块管理
│   └── core.py            # 核心主程序
├── tests/                 # 测试模块
│   ├── benchmark/         # Benchmark系统
│   └── test_*.py          # 单元测试（35个）
├── deployment/            # 部署脚本
├── run_holder.py          # Holder入口
└── run_benchmark.py       # Benchmark入口
```

## 算法

### PID控制
- Kp: 比例控制
- Ki: 积分控制（带非对称恢复）
- Kd: 微分控制

### 非对称策略
- 释放：快速响应，低成本
- 分配：保守填充，高成本

### 性能评分
- 35% 误差
- 30% 稳定性
- 20% 阻止率
- 15% 调整节奏

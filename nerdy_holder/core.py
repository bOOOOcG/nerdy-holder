"""Nerdy Holder Pro - 核心程序"""

import os
import time
import psutil
import random
import json
import math
from datetime import datetime
from collections import deque

from .controllers import EnhancedPIDController, UnifiedResponseCalculator
from .predictors import AdaptiveEMAPredictor
from .optimizers import ParameterOptimizer
from .trackers import PerformanceTracker
from .memory import MemoryChunk


class NerdyHolderPro:
    """Nerdy Holder Pro 🤓☝"""

    def __init__(self, enable_benchmark=True, fixed_target=None, dynamic_range=None):
        # 系统信息
        mem = psutil.virtual_memory()
        self.total_gb = mem.total / (1024**3)
        self.total_bytes = mem.total

        # 目标设置
        if fixed_target:
            self.min_target = fixed_target
            self.max_target = fixed_target
            self.current_target = fixed_target
            self.test_mode = True
        elif dynamic_range:
            self.min_target = dynamic_range[0]
            self.max_target = dynamic_range[1]
            self.current_target = (dynamic_range[0] + dynamic_range[1]) / 2
            self.test_mode = False
        else:
            self.min_target = 25
            self.max_target = 35
            self.current_target = 30
            self.test_mode = False

        # 内存块
        self.chunks = []

        # 参数优化器
        self.optimizer = ParameterOptimizer()

        # 算法组件
        self.ema_predictor = AdaptiveEMAPredictor(
            self.optimizer.params['ema_fast'],
            self.optimizer.params['ema_slow']
        )

        self.pid_controller = EnhancedPIDController(
            self.optimizer.params['pid_kp'],
            self.optimizer.params['pid_ki'],
            self.optimizer.params['pid_kd'],
            self.current_target
        )

        self.response_calculator = UnifiedResponseCalculator(self.total_bytes)
        self.response_calculator.response_base = self.optimizer.params['response_base']
        self.response_calculator.response_curve = self.optimizer.params['response_curve']
        self.response_calculator.urgency_threshold = self.optimizer.params['urgency_threshold']
        self.response_calculator.cost_decay_release = self.optimizer.params['cost_decay_release']
        self.response_calculator.cost_decay_allocate = self.optimizer.params['cost_decay_allocate']
        self.response_calculator.base_min_interval_release = self.optimizer.params['min_interval_release']
        self.response_calculator.base_min_interval_allocate = self.optimizer.params['min_interval_allocate']

        self.performance_tracker = PerformanceTracker()

        # 历史数据
        self.memory_history = deque(maxlen=100)

        # Benchmark支持
        self.enable_benchmark = enable_benchmark
        self.status_file = 'nerdy_status.json'

        # 统计
        self.stats = {
            'start_time': datetime.now(),
            'decisions': 0,
            'adjustments': 0,
            'blocked': 0,
            'optimizations': 0
        }

        self.running = True
        self.next_variation = time.time() + random.randint(180, 360)
        self.last_optimization = time.time()

    def log(self, msg, level="INFO"):
        """日志"""
        colors = {
            "INFO": "\033[37m",
            "SUCCESS": "\033[92m",
            "WARN": "\033[93m",
            "ALGO": "\033[96m",
            "OPT": "\033[95m"
        }
        timestamp = datetime.now().strftime('%H:%M:%S')
        color = colors.get(level, "")
        reset = "\033[0m" if color else ""
        print(f"{color}[{timestamp}] {msg}{reset}", flush=True)

    def get_system_memory(self):
        """获取系统内存"""
        mem_percent = psutil.virtual_memory().percent
        self.memory_history.append((time.time(), mem_percent))
        self.ema_predictor.update(mem_percent)
        return mem_percent

    def get_holding_mb(self):
        """获取持有量"""
        return sum(c.size_mb for c in self.chunks)

    def calculate_volatility(self):
        """计算波动性"""
        if len(self.memory_history) < 10:
            return 0

        recent = [v for t, v in list(self.memory_history)[-20:]]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        return math.sqrt(variance)

    def allocate_memory(self, target_mb):
        """分配内存"""
        allocated = 0

        while allocated < target_mb:
            remaining = target_mb - allocated

            if remaining >= 1000:
                chunk_size = 500
            elif remaining >= 500:
                chunk_size = 300
            elif remaining >= 200:
                chunk_size = 200
            elif remaining >= 100:
                chunk_size = 100
            else:
                chunk_size = max(50, int(remaining))

            try:
                chunk = MemoryChunk(chunk_size)
                self.chunks.append(chunk)
                allocated += chunk_size
            except Exception:
                break

            if allocated >= target_mb * 0.95:
                break

        return allocated

    def release_memory(self, target_mb):
        """释放内存"""
        if not self.chunks:
            return 0

        self.chunks.sort(key=lambda x: x.size_mb, reverse=True)

        released = 0
        to_remove = []

        for i, chunk in enumerate(self.chunks):
            if released >= target_mb * 0.9:
                break
            to_remove.append(i)
            released += chunk.size_mb

        for i in reversed(to_remove):
            self.chunks.pop(i)

        return released

    def adjust_target(self):
        """随机变化目标"""
        if self.test_mode:
            return

        if time.time() >= self.next_variation:
            old = self.current_target
            self.current_target = random.uniform(self.min_target, self.max_target)
            self.next_variation = time.time() + random.randint(180, 360)

            self.pid_controller.set_target(self.current_target)
            self.log(f"目标变化: {old:.1f}% → {self.current_target:.1f}%", "SUCCESS")

    def make_decision(self):
        """统一决策流程"""
        self.stats['decisions'] += 1

        # 获取状态
        current_mem = self.get_system_memory()
        target = self.current_target
        error = current_mem - target
        volatility = self.calculate_volatility()

        # 容差检查
        if abs(error) <= self.optimizer.params['tolerance']:
            self.performance_tracker.record(abs(error), 0, False)
            return

        # 早期能力检查：需要释放但持有0MB，直接返回避免无用计算
        if error > 0:  # 系统高于目标，需要释放
            holding = self.get_holding_mb()
            if holding == 0:
                # 无能为力，记录并直接返回
                self.stats['blocked'] += 1
                self.performance_tracker.record(abs(error), 0, True)
                return

        # 预测和控制
        momentum = self.ema_predictor.get_momentum()
        pid_result = self.pid_controller.compute(current_mem)

        # 计算响应大小
        response_mb = self.response_calculator.calculate_response_size(
            error, pid_result['output'], momentum, volatility
        )

        # 决策判断
        decision = self.response_calculator.should_adjust(error, response_mb, volatility)

        if not decision['should_adjust']:
            self.stats['blocked'] += 1
            self.performance_tracker.record(abs(error), response_mb, True)

            if abs(error) > 3:
                self.log(f"阻止: {decision['reason']}", "ALGO")
            return

        # 执行调整
        self.stats['adjustments'] += 1
        self.performance_tracker.record(abs(error), response_mb, False)

        if error < 0:
            # 分配
            self.log(f"分配 {int(response_mb)}MB (误差{error:.1f}%)", "SUCCESS")
            allocated = self.allocate_memory(int(response_mb))
            new_mem = self.get_system_memory()
            self.log(f"   {current_mem:.1f}% → {new_mem:.1f}% | 持有{self.get_holding_mb():.0f}MB", "INFO")
        else:
            # 释放
            holding = self.get_holding_mb()
            release_size = min(int(response_mb), holding)
            self.log(f"释放 {release_size}MB (误差{error:.1f}%)", "WARN")
            released = self.release_memory(release_size)
            new_mem = self.get_system_memory()
            self.log(f"   {current_mem:.1f}% → {new_mem:.1f}% | 剩余{self.get_holding_mb():.0f}MB", "INFO")

    def optimize_parameters(self):
        """优化参数"""
        now = time.time()
        if now - self.last_optimization < 30:
            return

        self.last_optimization = now

        stats = self.performance_tracker.get_stats()
        if not stats:
            return

        updated, result = self.optimizer.maybe_optimize(stats)

        if updated:
            if isinstance(result, str):
                self.log(f"{result}", "OPT")
            elif isinstance(result, tuple):
                # 新格式：(current_score, scenario, scenario_improved)
                current_score, scenario, scenario_improved = result
                self.stats['optimizations'] += 1

                scenario_names = {
                    'optimal': '理想',
                    'normal': '正常',
                    'constrained': '受限',
                    'volatile': '波动',
                    'mismatch': '失配'
                }
                scenario_cn = scenario_names.get(scenario, scenario)

                msg = f"优化: 场景[{scenario_cn}] 得分{current_score:.1f}"
                if scenario_improved:
                    msg += " [场景新高]"
                msg += f" | 误差{stats['avg_error']:.2f}% | 稳定性{stats['error_volatility']:.2f}% | 阻止率{stats['block_rate']:.1%}"
                self.log(msg, "OPT")
            else:
                # 旧格式兼容
                self.stats['optimizations'] += 1
                self.log(f"优化: 得分 {result:.1f} | "
                        f"误差{stats['avg_error']:.2f}% | "
                        f"稳定性{stats['error_volatility']:.2f}% | "
                        f"阻止率{stats['block_rate']:.1%}", "OPT")

            # 更新算法组件参数
            self.response_calculator.response_base = self.optimizer.params['response_base']
            self.response_calculator.response_curve = self.optimizer.params['response_curve']
            self.response_calculator.urgency_threshold = self.optimizer.params['urgency_threshold']
            self.response_calculator.cost_decay_release = self.optimizer.params['cost_decay_release']
            self.response_calculator.cost_decay_allocate = self.optimizer.params['cost_decay_allocate']
            self.response_calculator.base_min_interval_release = self.optimizer.params['min_interval_release']
            self.response_calculator.base_min_interval_allocate = self.optimizer.params['min_interval_allocate']
        elif result:
            self.log(f"{result}", "OPT")

    def export_status(self):
        """导出状态"""
        try:
            uptime = (datetime.now() - self.stats['start_time']).total_seconds()
            stats = self.performance_tracker.get_stats()

            status = {
                'timestamp': time.time(),
                'current_target': float(self.current_target),
                'system_memory': float(psutil.virtual_memory().percent),
                'holding_mb': int(self.get_holding_mb()),
                'chunks_count': int(len(self.chunks)),

                'params': {
                    'pid_kp': float(self.optimizer.params['pid_kp']),
                    'pid_ki': float(self.optimizer.params['pid_ki']),
                    'pid_kd': float(self.optimizer.params['pid_kd']),
                    'response_base': float(self.optimizer.params['response_base']),
                    'response_curve': float(self.optimizer.params['response_curve']),
                    'tolerance': float(self.optimizer.params['tolerance'])
                },

                'stats': {
                    'uptime_seconds': float(uptime),
                    'decisions': int(self.stats['decisions']),
                    'adjustments': int(self.stats['adjustments']),
                    'blocked': int(self.stats['blocked']),
                    'optimizations': int(self.stats['optimizations'])
                },

                'performance': {
                    'avg_error': float(stats['avg_error']) if stats else 0,
                    'error_volatility': float(stats['error_volatility']) if stats else 0,
                    'block_rate': float(stats['block_rate']) if stats else 0,
                    'score': float(self.optimizer.params['best_score'])
                }
            }

            temp_file = self.status_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2)

            if os.path.exists(self.status_file):
                os.remove(self.status_file)
            os.rename(temp_file, self.status_file)
        except Exception:
            pass

    def print_status(self):
        """状态汇总"""
        current = self.get_system_memory()
        uptime = datetime.now() - self.stats['start_time']
        holding = self.get_holding_mb()
        volatility = self.calculate_volatility()
        momentum = self.ema_predictor.get_momentum()
        predicted = self.ema_predictor.predict()

        stats = self.performance_tracker.get_stats()

        print("\n" + "=" * 80)
        print(f"Nerdy Holder Pro | 运行: {uptime}")
        print("=" * 80)
        print(f"系统: {current:.1f}% | 目标: {self.current_target:.1f}% | "
              f"持有: {holding:.0f}MB ({len(self.chunks)}块)")
        print(f"预测: {predicted:.1f}% | 动量: {momentum:+.1f} | 波动: {volatility:.2f}%")

        if stats:
            print(f"性能: 误差{stats['avg_error']:.2f}% | "
                  f"稳定性{stats['error_volatility']:.2f}% | "
                  f"阻止率{stats['block_rate']:.1%} | "
                  f"得分{self.optimizer.params['best_score']:.1f}")

        print("-" * 80)
        print(f"统计: 决策{self.stats['decisions']} | "
              f"调整{self.stats['adjustments']} | "
              f"阻止{self.stats['blocked']} | "
              f"优化{self.stats['optimizations']}次")
        print("=" * 80)

    def initialize(self):
        """初始化"""
        print("\n" + "=" * 80)
        print("🤓 Nerdy Holder Pro")
        print("=" * 80)

        self.log(f"系统: {self.total_gb:.1f} GB", "INFO")

        if self.test_mode:
            self.log(f"固定模式: 目标 {self.current_target:.1f}%", "INFO")
        else:
            self.log(f"目标: {self.current_target:.1f}% (范围: {self.min_target}-{self.max_target}%)", "INFO")

        self.log(f"历史最佳得分: {self.optimizer.params['best_score']:.1f}", "OPT")

        # 初始化内存
        current = self.get_system_memory()
        need = self.current_target - current

        if need > 0:
            need_mb = int(need * self.total_bytes / 100 / (1024*1024))
            self.log(f"初始化分配: {need_mb}MB", "INFO")
            self.allocate_memory(need_mb)
            final = self.get_system_memory()
            self.log(f"初始化完成: {final:.1f}%", "SUCCESS")
        else:
            self.log(f"系统内存已达标: {current:.1f}%", "SUCCESS")

    def run(self):
        """主循环"""
        self.initialize()
        print()

        if self.enable_benchmark:
            self.log("Benchmark导出已启用", "INFO")

        self.log("开始运行...\n", "INFO")

        last_status = time.time()
        last_export = time.time()

        try:
            while self.running:
                # 目标变化
                self.adjust_target()

                # 核心决策
                self.make_decision()

                # 参数优化
                self.optimize_parameters()

                # 导出状态
                if self.enable_benchmark and time.time() - last_export >= 1:
                    self.export_status()
                    last_export = time.time()

                # 状态汇总
                if time.time() - last_status >= 120:
                    self.print_status()
                    last_status = time.time()

                time.sleep(3)

        except KeyboardInterrupt:
            print("\n")
            self.log("停止中...", "WARN")
            self.running = False

            runtime_hours = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
            self.optimizer.params['total_runtime_hours'] += runtime_hours
            self.optimizer.save_params(force=True)

            self.chunks.clear()
            self.print_status()
            self.log("已停止", "SUCCESS")

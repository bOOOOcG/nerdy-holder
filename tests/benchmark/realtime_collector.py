"""实时数据收集器 - 持续监控holder状态"""

import time
import json
import threading
from collections import deque
from pathlib import Path


class RealtimeCollector:
    """实时数据收集器 - 在测试期间持续收集holder状态"""

    def __init__(self, status_file='nerdy_status.json', sample_interval=1.0):
        self.status_file = status_file
        self.sample_interval = sample_interval
        self.snapshots = deque(maxlen=1000)  # 最多保存1000个快照
        self.collecting = False
        self.collector_thread = None
        self.start_time = None

    def start_collection(self):
        """开始收集数据"""
        if self.collecting:
            return

        self.collecting = True
        self.start_time = time.time()
        self.snapshots.clear()

        self.collector_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.collector_thread.start()

    def stop_collection(self):
        """停止收集数据"""
        self.collecting = False
        if self.collector_thread:
            self.collector_thread.join(timeout=2)

    def _collect_loop(self):
        """收集循环"""
        while self.collecting:
            snapshot = self._read_status()
            if snapshot:
                # 添加时间戳
                snapshot['collection_time'] = time.time()
                snapshot['elapsed'] = time.time() - self.start_time
                self.snapshots.append(snapshot)

            time.sleep(self.sample_interval)

    def _read_status(self):
        """读取holder状态文件"""
        try:
            if not Path(self.status_file).exists():
                return None

            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def get_snapshots(self):
        """获取所有快照"""
        return list(self.snapshots)

    def get_recent_snapshots(self, count=10):
        """获取最近N个快照"""
        return list(self.snapshots)[-count:]

    def analyze_collection(self):
        """分析收集的数据"""
        if not self.snapshots:
            return None

        analysis = {
            'total_samples': len(self.snapshots),
            'duration': time.time() - self.start_time if self.start_time else 0,
            'timeline': self._build_timeline(),
            'metrics_evolution': self._analyze_metrics_evolution(),
            'scenario_changes': self._track_scenario_changes(),
            'parameter_evolution': self._track_parameter_changes(),
            'anomaly_events': self._detect_anomaly_events()
        }

        return analysis

    def _build_timeline(self):
        """构建时间线"""
        timeline = []
        for snap in self.snapshots:
            timeline.append({
                'time': snap.get('elapsed', 0),
                'system_memory': snap.get('system_memory', 0),
                'target': snap.get('current_target', 0),
                'holding_mb': snap.get('holding_mb', 0),
                'error': snap.get('system_memory', 0) - snap.get('current_target', 0)
            })
        return timeline

    def _analyze_metrics_evolution(self):
        """分析指标演化"""
        errors = []
        volatilities = []
        block_rates = []
        scores = []

        for snap in self.snapshots:
            perf = snap.get('performance', {})
            if perf:
                errors.append(perf.get('avg_error', 0))
                volatilities.append(perf.get('error_volatility', 0))
                block_rates.append(perf.get('block_rate', 0))
                scores.append(perf.get('score', 0))

        if not errors:
            return None

        return {
            'error_trend': self._calculate_trend(errors),
            'volatility_trend': self._calculate_trend(volatilities),
            'block_rate_trend': self._calculate_trend(block_rates),
            'score_trend': self._calculate_trend(scores),
            'final_metrics': {
                'avg_error': errors[-1] if errors else 0,
                'avg_volatility': volatilities[-1] if volatilities else 0,
                'avg_block_rate': block_rates[-1] if block_rates else 0,
                'final_score': scores[-1] if scores else 0
            }
        }

    def _calculate_trend(self, values):
        """计算趋势（简单线性回归）"""
        if len(values) < 2:
            return 'stable'

        # 简化：比较前半段和后半段
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(values[mid:]) / (len(values) - mid)

        diff = second_half_avg - first_half_avg

        if abs(diff) < 0.5:
            return 'stable'
        elif diff > 0:
            return 'increasing'
        else:
            return 'decreasing'

    def _track_scenario_changes(self):
        """追踪场景变化"""
        # 从性能数据推断场景
        scenario_timeline = []
        current_scenario = None
        scenario_start = 0

        for i, snap in enumerate(self.snapshots):
            perf = snap.get('performance', {})
            scenario = self._infer_scenario(perf)

            if scenario != current_scenario:
                if current_scenario is not None:
                    scenario_timeline.append({
                        'scenario': current_scenario,
                        'start_index': scenario_start,
                        'end_index': i - 1,
                        'duration_samples': i - scenario_start
                    })
                current_scenario = scenario
                scenario_start = i

        # 添加最后一个场景
        if current_scenario is not None:
            scenario_timeline.append({
                'scenario': current_scenario,
                'start_index': scenario_start,
                'end_index': len(self.snapshots) - 1,
                'duration_samples': len(self.snapshots) - scenario_start
            })

        return scenario_timeline

    def _infer_scenario(self, perf):
        """从性能数据推断场景"""
        if not perf:
            return 'unknown'

        avg_error = perf.get('avg_error', 0)
        volatility = perf.get('error_volatility', 0)
        block_rate = perf.get('block_rate', 0)

        if block_rate > 0.8:
            return 'constrained'
        elif volatility > 3.0:
            return 'volatile'
        elif avg_error > 10:
            return 'mismatch'
        elif avg_error < 2 and volatility < 1.0 and 0.15 <= block_rate <= 0.3:
            return 'optimal'
        else:
            return 'normal'

    def _track_parameter_changes(self):
        """追踪参数变化"""
        param_changes = []
        prev_params = None

        for i, snap in enumerate(self.snapshots):
            params = snap.get('params', {})
            if not params:
                continue

            if prev_params:
                # 检测参数变化
                changes = {}
                for key in ['pid_kp', 'pid_ki', 'pid_kd', 'response_base', 'response_curve']:
                    prev_val = prev_params.get(key, 0)
                    curr_val = params.get(key, 0)
                    if abs(curr_val - prev_val) > 0.01:
                        changes[key] = {
                            'from': prev_val,
                            'to': curr_val,
                            'change': curr_val - prev_val
                        }

                if changes:
                    param_changes.append({
                        'index': i,
                        'time': snap.get('elapsed', 0),
                        'changes': changes
                    })

            prev_params = params

        return param_changes

    def _detect_anomaly_events(self):
        """检测异常事件"""
        events = []

        for i in range(1, len(self.snapshots)):
            curr = self.snapshots[i]
            prev = self.snapshots[i-1]

            # 1. 检测内存突变
            curr_mem = curr.get('system_memory', 0)
            prev_mem = prev.get('system_memory', 0)
            mem_change = abs(curr_mem - prev_mem)

            if mem_change > 10:  # 内存变化超过10%
                events.append({
                    'type': 'sudden_memory_change',
                    'time': curr.get('elapsed', 0),
                    'index': i,
                    'details': f"内存突变 {prev_mem:.1f}% → {curr_mem:.1f}%"
                })

            # 2. 检测持有量异常
            curr_holding = curr.get('holding_mb', 0)
            prev_holding = prev.get('holding_mb', 0)
            holding_change = abs(curr_holding - prev_holding)

            if holding_change > 5000:  # 持有量变化超过5GB
                events.append({
                    'type': 'large_holder_change',
                    'time': curr.get('elapsed', 0),
                    'index': i,
                    'details': f"Holder变化 {prev_holding:.0f}MB → {curr_holding:.0f}MB"
                })

            # 3. 检测阻止率突变
            curr_perf = curr.get('performance', {})
            prev_perf = prev.get('performance', {})

            curr_block = curr_perf.get('block_rate', 0)
            prev_block = prev_perf.get('block_rate', 0)

            if abs(curr_block - prev_block) > 0.5:  # 阻止率变化超过50%
                events.append({
                    'type': 'block_rate_spike',
                    'time': curr.get('elapsed', 0),
                    'index': i,
                    'details': f"阻止率突变 {prev_block:.1%} → {curr_block:.1%}"
                })

        return events

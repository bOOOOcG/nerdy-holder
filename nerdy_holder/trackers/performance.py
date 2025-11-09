"""性能追踪器 - 多维度"""

import time
import statistics
from collections import deque


class PerformanceTracker:
    """性能追踪器 - 多维度"""

    def __init__(self):
        self.metrics_window = deque(maxlen=100)
        self.adjustment_times = deque(maxlen=50)

    def record(self, error, adjustment_size, was_blocked):
        """记录一次决策"""
        now = time.time()

        if adjustment_size > 0 and not was_blocked:
            self.adjustment_times.append(now)

        self.metrics_window.append({
            'timestamp': now,
            'error': error,
            'adjustment_size': adjustment_size,
            'was_blocked': was_blocked
        })

    def get_stats(self):
        """获取统计数据 - 多维度"""
        if len(self.metrics_window) < 10:
            return None

        recent = list(self.metrics_window)[-30:]

        # 1. 平均误差
        avg_error = sum(m['error'] for m in recent) / len(recent)

        # 2. 误差波动（稳定性）
        errors = [m['error'] for m in recent]
        error_volatility = statistics.stdev(errors) if len(errors) > 1 else 0

        # 3. 阻止率
        block_rate = sum(1 for m in recent if m['was_blocked']) / len(recent)

        # 4. 调整频率
        adj_count = sum(1 for m in recent if not m['was_blocked'])
        time_span = recent[-1]['timestamp'] - recent[0]['timestamp']
        adjustment_rate = adj_count / max(1, time_span / 60)

        # 5. 调整间隔稳定性
        if len(self.adjustment_times) > 3:
            recent_times = list(self.adjustment_times)[-10:]
            intervals = [recent_times[i] - recent_times[i-1]
                        for i in range(1, len(recent_times))]
            interval_volatility = statistics.stdev(intervals) if len(intervals) > 1 else 0
        else:
            interval_volatility = 0

        return {
            'avg_error': avg_error,
            'error_volatility': error_volatility,
            'block_rate': block_rate,
            'adjustment_rate': adjustment_rate,
            'interval_volatility': interval_volatility
        }

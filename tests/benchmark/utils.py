"""Benchmark工具类"""

import time
import json
import psutil
import statistics
from pathlib import Path


class HolderStatusReader:
    """读取holder状态"""

    def __init__(self, status_file='nerdy_status.json'):
        self.status_file = status_file
        self.last_status = None
        self.last_read_time = 0

    def read_status(self):
        """读取状态文件"""
        try:
            now = time.time()
            if now - self.last_read_time < 0.3:
                return self.last_status

            if not Path(self.status_file).exists():
                return None

            with open(self.status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)

            self.last_status = status
            self.last_read_time = now
            return status
        except Exception:
            return self.last_status

    def get_target(self):
        status = self.read_status()
        return status.get('current_target', 0) if status else 0

    def get_holding_mb(self):
        status = self.read_status()
        return status.get('holding_mb', 0) if status else 0

    def get_chunks(self):
        status = self.read_status()
        return status.get('chunks_count', 0) if status else 0

    def is_available(self):
        status = self.read_status()
        if not status:
            return False
        return time.time() - status.get('timestamp', 0) < 10


class SmartMonitor:
    """智能监控器"""

    def __init__(self, holder_status):
        self.holder_status = holder_status
        self.samples = []
        self.start_time = None
        self.holder_start_holding = 0

    def start(self):
        """开始"""
        self.start_time = time.time()
        self.samples = []
        self.holder_start_holding = self.holder_status.get_holding_mb()

    def record(self):
        """记录样本"""
        sample = {
            'timestamp': time.time(),
            'system_mem_percent': psutil.virtual_memory().percent,
            'system_mem_mb': psutil.virtual_memory().used / (1024*1024),
            'holder_target': self.holder_status.get_target(),
            'holder_holding': self.holder_status.get_holding_mb(),
            'holder_chunks': self.holder_status.get_chunks(),
            'holder_delta': self.holder_status.get_holding_mb() - self.holder_start_holding
        }

        sample['error'] = abs(sample['system_mem_percent'] - sample['holder_target'])
        self.samples.append(sample)
        return sample

    def get_holder_delta(self):
        """获取holder变化量"""
        if not self.samples:
            return 0
        return self.samples[-1]['holder_delta']

    def get_max_holder_delta(self):
        """获取holder最大变化"""
        if not self.samples:
            return 0
        return max(abs(s['holder_delta']) for s in self.samples)

    def get_response_time(self, target_error=2.0):
        """计算响应时间"""
        if not self.samples:
            return None

        for i, s in enumerate(self.samples):
            if s['error'] < target_error:
                return s['timestamp'] - self.start_time
        return None

    def get_adjustment_count(self):
        """计算调整次数"""
        if len(self.samples) < 2:
            return 0

        count = 0
        for i in range(1, len(self.samples)):
            if self.samples[i]['holder_chunks'] != self.samples[i-1]['holder_chunks']:
                count += 1
        return count

    def get_metrics(self):
        """获取指标"""
        if not self.samples:
            return {}

        errors = [s['error'] for s in self.samples]
        system_mems = [s['system_mem_percent'] for s in self.samples]

        metrics = {
            'avg_error': statistics.mean(errors),
            'max_error': max(errors),
            'min_error': min(errors),
            'stability': statistics.stdev(system_mems) if len(system_mems) > 1 else 0,
            'response_time': self.get_response_time(),
            'adjustments': self.get_adjustment_count(),
            'samples': len(self.samples),
            'duration': self.samples[-1]['timestamp'] - self.samples[0]['timestamp'],
            'holder_delta': self.get_holder_delta(),
            'holder_max_delta': self.get_max_holder_delta()
        }

        if metrics['duration'] > 0:
            metrics['adjustment_rate'] = metrics['adjustments'] / (metrics['duration'] / 60)
        else:
            metrics['adjustment_rate'] = 0

        return metrics

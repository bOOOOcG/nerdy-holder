"""统一响应计算器 - 非对称优化版"""

import time
import math


class UnifiedResponseCalculator:
    """统一响应计算器 - 非对称优化版"""

    def __init__(self, total_memory_bytes):
        self.total_memory_bytes = total_memory_bytes
        self.total_memory_mb = total_memory_bytes / (1024*1024)

        # 响应参数
        self.response_base = 1.6
        self.response_curve = 1.7
        self.urgency_threshold = 3.5

        # ★ 非对称成本参数
        self.cost_decay_release = 0.3      # 释放：快速衰减（成本低）
        self.cost_decay_allocate = 0.8     # 分配：慢速衰减（成本高）

        self.base_min_interval_release = 1.5   # 释放：短间隔
        self.base_min_interval_allocate = 3.5  # 分配：长间隔

        self.large_adj_interval_release = 2.5  # 释放：大调整后也短
        self.large_adj_interval_allocate = 6.0 # 分配：大调整后更长

        self.large_adj_threshold = 3000

        self.last_adjustment_time = time.time()
        self.last_adjustment_size = 0
        self.last_was_release = False  # 追踪上次是否是释放

    def calculate_response_size(self, error, pid_output, momentum, volatility):
        """核心方法：统一计算响应大小"""

        # 判断操作类型
        is_release = error > 0  # 正误差=需要释放

        # 1. 基础响应量
        base_mb = abs(error) * self.total_memory_mb / 100

        # 2. 紧急度系数
        normalized_error = abs(error) / self.urgency_threshold
        urgency_factor = math.pow(normalized_error, self.response_curve)
        urgency_factor = max(0.3, min(3.0, urgency_factor))

        # ★ 释放时提高紧急度
        if is_release:
            urgency_factor *= 1.3  # 释放额外提升30%

        # 3. PID增强系数
        pid_factor = 1.0 + (pid_output / 50)
        pid_factor = max(0.5, min(2.0, pid_factor))

        # 4. 动量修正
        if error * momentum > 0:
            momentum_factor = 1.0 + abs(momentum) / 10
            momentum_factor = min(1.5, momentum_factor)
        elif error * momentum < 0 and abs(momentum) > 2:
            momentum_factor = 1.2
        else:
            momentum_factor = 1.0

        # 5. 波动抑制
        volatility_factor = 1.0 / (1.0 + volatility / 15)
        volatility_factor = max(0.8, min(1.0, volatility_factor))

        # 6. 统一计算
        response_mb = (base_mb *
                      self.response_base *
                      urgency_factor *
                      pid_factor *
                      momentum_factor *
                      volatility_factor)

        # 7. 平滑限制
        if abs(error) > 15:
            response_mb = max(1000, min(10000, response_mb))
        elif abs(error) > 8:
            response_mb = max(500, min(5000, response_mb))
        elif abs(error) > 3:
            response_mb = max(200, min(2000, response_mb))
        else:
            response_mb = max(50, min(1000, response_mb))

        return response_mb

    def should_adjust(self, error, response_mb, volatility):
        """统一的调整决策 - 非对称策略"""
        now = time.time()
        time_since_last = now - self.last_adjustment_time

        is_release = error > 0  # 需要释放内存

        # ★ 释放紧急判断 - 误差>8%直接通过
        if is_release and abs(error) > 8:
            self.last_adjustment_time = now
            self.last_adjustment_size = response_mb
            self.last_was_release = True
            return {
                'should_adjust': True,
                'ratio': 999,
                'threshold': 0,
                'benefit': 999,
                'cost': 0,
                'reason': f"🔴 紧急释放: 误差{error:.1f}%"
            }

        # ★ 非对称间隔
        if is_release:
            if self.last_adjustment_size > self.large_adj_threshold:
                min_interval = self.large_adj_interval_release
            else:
                min_interval = self.base_min_interval_release
        else:
            if self.last_adjustment_size > self.large_adj_threshold:
                min_interval = self.large_adj_interval_allocate
            else:
                min_interval = self.base_min_interval_allocate

        # 间隔保护（释放几乎不保护）
        if time_since_last < min_interval:
            protection_threshold = 6 if is_release else 10  # 释放：6%才保护，分配：10%
            if abs(error) < protection_threshold:
                return {
                    'should_adjust': False,
                    'ratio': 0,
                    'threshold': min_interval,
                    'benefit': 0,
                    'cost': 999,
                    'reason': f"{'🔴' if is_release else '🟡'}间隔保护: {time_since_last:.1f}s < {min_interval:.1f}s"
                }

        # ★ 非对称收益计算
        if is_release:
            urgency_bonus = max(0, (abs(error) - 5) * 3)  # 释放：5%起，每1%+3
        else:
            urgency_bonus = max(0, (abs(error) - 10) * 1)  # 分配：10%起，每1%+1

        benefit = response_mb / 500 + abs(error) / 3 + urgency_bonus

        # ★ 非对称成本计算
        cost_decay = self.cost_decay_release if is_release else self.cost_decay_allocate

        frequency_cost = math.exp(-time_since_last / cost_decay)
        if is_release:
            frequency_cost *= 1.0  # 释放：正常成本
        else:
            frequency_cost *= 2.5  # 分配：成本更高

        volatility_cost = volatility / 8
        recent_adj_cost = self.last_adjustment_size / 1000

        # 如果是反向操作（释放→分配或分配→释放）
        is_reversal = (is_release != self.last_was_release)
        if is_reversal:
            if is_release:
                # 从分配转释放：成本大幅降低
                frequency_cost *= 0.3
                recent_adj_cost *= 0.3
            else:
                # 从释放转分配：成本略降
                frequency_cost *= 0.6
                recent_adj_cost *= 0.6

        cost = frequency_cost + volatility_cost + recent_adj_cost

        # ★ 非对称阈值
        if is_release:
            # 释放：极低阈值
            if abs(error) > 6:
                threshold = 0.5
            elif time_since_last < min_interval * 1.5:
                threshold = 1.2
            else:
                threshold = 0.8
        else:
            # 分配：较高阈值
            if abs(error) > 10:
                threshold = 0.8
            elif time_since_last < min_interval * 1.5:
                threshold = 2.0
            else:
                threshold = 1.3

        ratio = benefit / max(0.1, cost)
        decision = ratio > threshold

        if decision:
            self.last_adjustment_time = now
            self.last_adjustment_size = response_mb
            self.last_was_release = is_release

        return {
            'should_adjust': decision,
            'ratio': ratio,
            'threshold': threshold,
            'benefit': benefit,
            'cost': cost,
            'reason': f"{'🔴释放' if is_release else '🟡分配'} 收益{benefit:.1f}/成本{cost:.1f}={ratio:.1f} vs {threshold:.1f}"
        }

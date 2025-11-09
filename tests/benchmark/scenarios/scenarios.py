"""具体测试场景"""

import time
import math
import random
from .base import BaseScenario


class StarvationScenario(BaseScenario):
    """内存饥饿测试"""

    def __init__(self):
        super().__init__(
            "内存饥饿测试",
            "memory_starvation",
            30
        )

    def run_test_logic(self, params):
        time.sleep(5)
        print(f"\n[行动] 申请 {params['test_size_mb']:.0f}MB...")
        allocated = self.allocator.allocate_mb(params['test_size_mb'])
        print(f"[行动] 成功申请 {allocated:.0f}MB，等待Holder响应...")
        time.sleep(15)
        print(f"\n[行动] 开始释放...")


class ReleaseScenario(BaseScenario):
    """内存释放测试"""

    def __init__(self):
        super().__init__(
            "内存释放测试",
            "memory_release",
            30
        )

    def run_test_logic(self, params):
        print(f"\n[行动] 先申请 {params['test_size_mb']:.0f}MB...")
        self.allocator.allocate_mb(params['test_size_mb'])
        time.sleep(8)
        print(f"\n[行动] 突然释放...")
        released = self.allocator.release_all()
        print(f"[行动] 释放了 {released:.0f}MB，看Holder能否补充...")
        time.sleep(12)


class FluctuationScenario(BaseScenario):
    """快速波动测试"""

    def __init__(self):
        super().__init__(
            "快速波动测试",
            "rapid_fluctuation",
            45
        )

    def run_test_logic(self, params):
        wave_size = params['test_size_mb']
        wave_count = params.get('wave_count', 6)
        interval = self.base_duration / (wave_count * 2)

        for i in range(wave_count):
            print(f"\n[波动{i+1}] 申请 {wave_size:.0f}MB...")
            self.allocator.allocate_mb(wave_size)
            time.sleep(interval)

            print(f"\n[波动{i+1}] 释放...")
            self.allocator.release_all()
            time.sleep(interval)


class PressureScenario(BaseScenario):
    """渐进压力测试"""

    def __init__(self):
        super().__init__(
            "渐进压力测试",
            "gradual_pressure",
            40
        )

    def run_test_logic(self, params):
        steps = params.get('steps', 6)
        step_size = params['step_size_mb']
        interval = self.base_duration / (steps + 2)

        time.sleep(interval)

        for i in range(steps):
            cumulative = (i+1) * step_size
            print(f"\n[渐进{i+1}] 累计 {cumulative:.0f}MB...")
            self.allocator.allocate_mb(step_size)
            time.sleep(interval)

        print(f"\n[渐进] 保持峰值...")
        time.sleep(interval)


class ExtremeScenario(BaseScenario):
    """极限响应测试"""

    def __init__(self):
        super().__init__(
            "极限响应测试",
            "extreme_response",
            25
        )

    def run_test_logic(self, params):
        time.sleep(5)

        print(f"\n[极限] 瞬间申请 {params['test_size_mb']:.0f}MB...")
        start = time.time()
        allocated = self.allocator.allocate_mb(params['test_size_mb'])
        alloc_time = time.time() - start
        print(f"[极限] 申请完成 {allocated:.0f}MB (耗时{alloc_time:.2f}秒)")
        print(f"[极限] 测量Holder响应延迟...")

        time.sleep(12)

        print(f"\n[极限] 释放...")


class ShockScenario(BaseScenario):
    """瞬间冲击测试"""

    def __init__(self):
        super().__init__(
            "瞬间冲击测试",
            "instant_shock",
            20
        )

    def run_test_logic(self, params):
        time.sleep(5)

        print(f"\n[准备] 申请 {params['test_size_mb']:.0f}MB...")
        self.allocator.allocate_mb(params['test_size_mb'])
        time.sleep(5)

        print(f"\n[冲击] 瞬间释放 {params['test_size_mb']:.0f}MB!")
        start = time.time()
        released = self.allocator.release_all()
        shock_time = time.time() - start
        print(f"[冲击] 释放完成: {released:.0f}MB (耗时{shock_time:.2f}秒)")
        print(f"[冲击] 等待Holder补充...")

        time.sleep(5)


class SustainedScenario(BaseScenario):
    """持续压力测试"""

    def __init__(self):
        super().__init__(
            "持续压力测试",
            "sustained_pressure",
            60
        )

    def run_test_logic(self, params):
        test_size = params['test_size_mb']

        print(f"\n[压力] 申请 {test_size:.0f}MB...")
        self.allocator.allocate_mb(test_size)

        print(f"\n[压力] 保持高压 45秒...")
        time.sleep(45)

        print(f"\n[压力] 释放...")


class BidirectionalScenario(BaseScenario):
    """双向测试"""

    def __init__(self):
        super().__init__(
            "双向测试",
            "bidirectional",
            40
        )

    def run_test_logic(self, params):
        size = params['test_size_mb'] // 2

        print(f"\n[阶段1] 申请 {size:.0f}MB（测试holder释放）...")
        self.allocator.allocate_mb(size)
        time.sleep(10)

        print(f"\n[阶段2] 再申请 {size:.0f}MB（加大压力）...")
        self.allocator.allocate_mb(size)
        time.sleep(8)

        print(f"\n[阶段3] 突然释放全部（测试holder补充）...")
        released = self.allocator.release_all()
        print(f"[阶段3] 释放了 {released:.0f}MB")
        time.sleep(12)


class NonlinearScenario(BaseScenario):
    """非线性变化测试 - 指数、正弦、阶跃、随机组合"""

    def __init__(self):
        super().__init__(
            "非线性变化测试",
            "nonlinear_change",
            50
        )

    def run_test_logic(self, params):
        """执行非线性内存变化模式"""
        base_size = params.get('test_size_mb', 3000)
        pattern = params.get('pattern', 'combined')  # exponential, sine, step, random, combined

        print(f"\n[非线性] 模式: {pattern}")
        print(f"[非线性] 基准大小: {base_size:.0f}MB")
        print()

        if pattern == 'exponential':
            self._exponential_growth(base_size)
        elif pattern == 'sine':
            self._sine_wave(base_size)
        elif pattern == 'step':
            self._step_changes(base_size)
        elif pattern == 'random':
            self._random_noise(base_size)
        else:  # combined
            self._combined_pattern(base_size)

    def _exponential_growth(self, base_size):
        """指数增长模式"""
        print("[模式] 指数增长 - 缓慢开始，快速增长")

        steps = 8
        interval = self.base_duration / (steps + 2)

        for i in range(steps):
            # 指数增长: 2^(i/2)
            factor = math.pow(2, i / 2.5)
            size = base_size * factor / 15  # 归一化

            print(f"  步骤{i+1}: {size:.0f}MB (因子{factor:.2f})")
            self.allocator.allocate_mb(size)
            time.sleep(interval)

        print("\n  保持峰值...")
        time.sleep(interval)

        print("\n  开始释放...")

    def _sine_wave(self, base_size):
        """正弦波动模式"""
        print("[模式] 正弦波 - 周期性波动")

        cycles = 3
        samples_per_cycle = 6
        total_samples = cycles * samples_per_cycle
        interval = self.base_duration / total_samples

        for i in range(total_samples):
            # 正弦波: sin(2π * i / samples_per_cycle)
            phase = 2 * math.pi * i / samples_per_cycle
            amplitude = (math.sin(phase) + 1) / 2  # 归一化到0-1
            size = base_size * amplitude / 2

            action = "增" if amplitude > 0.5 else "减"
            print(f"  周期{i//samples_per_cycle + 1}.{i%samples_per_cycle + 1}: {action} {size:.0f}MB (幅度{amplitude:.2f})")

            if amplitude > 0.5:
                self.allocator.allocate_mb(size)
            else:
                # 部分释放
                current = self.allocator.get_total_mb()
                if current > size:
                    self.allocator.release_mb(current - size)

            time.sleep(interval)

    def _step_changes(self, base_size):
        """阶跃变化模式"""
        print("[模式] 阶跃 - 突然跳跃式变化")

        steps = [
            (0.2, "低位"),
            (0.6, "中位"),
            (0.3, "回落"),
            (0.9, "高位"),
            (0.1, "骤降"),
            (0.7, "恢复")
        ]

        interval = self.base_duration / len(steps)

        for i, (level, desc) in enumerate(steps):
            size = base_size * level
            print(f"  阶跃{i+1}: {desc} {size:.0f}MB (水平{level:.1%})")

            # 全部释放再分配到目标level
            self.allocator.release_all()
            time.sleep(0.5)
            self.allocator.allocate_mb(size)

            time.sleep(interval)

        print("\n  最终释放...")

    def _random_noise(self, base_size):
        """随机噪声模式"""
        print("[模式] 随机噪声 - 不可预测变化")

        samples = 15
        interval = self.base_duration / samples

        for i in range(samples):
            # 随机变化：0.1 - 1.0
            factor = random.uniform(0.1, 1.0)
            size = base_size * factor / 2

            action = random.choice(["申请", "释放"])

            if action == "申请":
                print(f"  随机{i+1}: 申请 {size:.0f}MB")
                self.allocator.allocate_mb(size)
            else:
                current = self.allocator.get_total_mb()
                release_size = min(size, current * 0.6)
                if release_size > 0:
                    print(f"  随机{i+1}: 释放 {release_size:.0f}MB")
                    self.allocator.release_mb(release_size)

            time.sleep(interval)

    def _combined_pattern(self, base_size):
        """组合模式 - 多种非线性模式组合"""
        print("[模式] 组合 - 指数+正弦+阶跃+随机")

        total_time = self.base_duration
        phase_time = total_time / 4

        # 阶段1: 指数增长（快速）
        print("\n=== 阶段1: 指数增长 ===")
        for i in range(4):
            factor = math.pow(1.8, i)
            size = base_size * factor / 10
            print(f"  {size:.0f}MB")
            self.allocator.allocate_mb(size)
            time.sleep(phase_time / 4)

        # 阶段2: 正弦波动
        print("\n=== 阶段2: 正弦波动 ===")
        for i in range(4):
            phase = 2 * math.pi * i / 4
            amplitude = (math.sin(phase) + 1) / 2
            size = base_size * amplitude / 3

            current = self.allocator.get_total_mb()
            target = size

            if target > current:
                print(f"  上升 {target - current:.0f}MB")
                self.allocator.allocate_mb(target - current)
            else:
                print(f"  下降 {current - target:.0f}MB")
                self.allocator.release_mb(current - target)

            time.sleep(phase_time / 4)

        # 阶段3: 阶跃变化
        print("\n=== 阶段3: 阶跃变化 ===")
        levels = [0.8, 0.3, 0.9, 0.2]
        for level in levels:
            size = base_size * level
            print(f"  跳至 {size:.0f}MB")
            self.allocator.release_all()
            time.sleep(0.3)
            self.allocator.allocate_mb(size)
            time.sleep(phase_time / 4)

        # 阶段4: 随机噪声
        print("\n=== 阶段4: 随机收尾 ===")
        for i in range(4):
            factor = random.uniform(0.2, 0.7)
            size = base_size * factor / 2
            print(f"  随机 {size:.0f}MB")

            if random.random() > 0.5:
                self.allocator.allocate_mb(size)
            else:
                current = self.allocator.get_total_mb()
                if current > 0:
                    self.allocator.release_mb(min(size, current * 0.5))

            time.sleep(phase_time / 4)

        print("\n[完成] 组合模式测试结束")

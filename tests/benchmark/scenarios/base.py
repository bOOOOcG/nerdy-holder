"""基础场景类"""

import time
import threading

from ..utils import HolderStatusReader, SmartMonitor
from ..analyzer import SystemAnalyzer
from ..allocator import MemoryAllocator


class BaseScenario:
    """自适应场景基类"""

    def __init__(self, name, scenario_type, base_duration):
        self.name = name
        self.scenario_type = scenario_type
        self.base_duration = base_duration
        self.holder_status = HolderStatusReader()
        self.analyzer = SystemAnalyzer(self.holder_status)
        self.allocator = MemoryAllocator()
        self.monitor = SmartMonitor(self.holder_status)
        self.params = None

    def analyze_and_prepare(self):
        """分析并准备测试参数"""
        self.params = self.analyzer.calculate_test_params(self.scenario_type)
        return self.params

    def run_test_logic(self, params):
        """运行测试逻辑 - 子类实现"""
        raise NotImplementedError

    def run(self):
        """执行场景"""
        print(f"\n{'='*80}")
        print(f"场景: {self.name}")
        print(f"{'='*80}\n")

        print("分析系统状态...")
        analysis = self.analyzer.analyze()

        print(f"   总内存: {analysis['total_gb']:.1f}GB")
        print(f"   系统占用: {analysis['system_used_mb']:.0f}MB ({analysis['system_percent']:.1f}%)")
        print(f"   系统空闲: {analysis['system_free_mb']:.0f}MB")
        print(f"   Holder持有: {analysis['holder_holding_mb']:.0f}MB")
        print(f"   Holder目标: {analysis['holder_target']:.1f}%")

        params = self.analyze_and_prepare()

        if not params or not params['feasible']:
            print(f"\n场景不可行: {params['reason'] if params else '无法分析'}")
            return None

        print(f"\n测试方案: {params.get('description', '自定义')}")
        print(f"   测试量: {params['test_size_mb']:.0f}MB")
        if params.get('expect_holder_delta_mb'):
            print(f"   预期Holder变化: {params['expect_holder_delta_mb']:+.0f}MB")

        print(f"\n开始测试...")

        self.monitor.start()

        test_thread = threading.Thread(target=lambda: self.run_test_logic(params), daemon=True)
        test_thread.start()

        start_time = time.time()
        duration = self.base_duration

        while time.time() - start_time < duration:
            sample = self.monitor.record()

            elapsed = time.time() - start_time
            progress = elapsed / duration * 100

            print(f"\r进度: {progress:5.1f}% | "
                  f"系统: {sample['system_mem_percent']:5.1f}% | "
                  f"Holder: {sample['holder_holding']:6.0f}MB "
                  f"({sample['holder_delta']:+6.0f}MB) | "
                  f"误差: {sample['error']:4.1f}%",
                  end='', flush=True)

            time.sleep(0.5)

        print()

        test_thread.join(timeout=2)
        released = self.allocator.release_all()
        if released > 0:
            print(f"   清理: 释放了{released:.0f}MB")

        metrics = self.monitor.get_metrics()
        metrics['test_size_mb'] = params['test_size_mb']
        metrics['expect_delta'] = params.get('expect_holder_delta_mb', 0)

        return metrics

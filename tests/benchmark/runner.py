"""Benchmark 运行器"""

import time
import psutil
import statistics
from datetime import datetime

from .utils import HolderStatusReader
from .scenarios import *


class BenchmarkRunner:
    """Benchmark运行器"""

    def __init__(self):
        self.scenarios = [
            StarvationScenario(),
            ReleaseScenario(),
            FluctuationScenario(),
            PressureScenario(),
            ExtremeScenario(),
            ShockScenario(),
            SustainedScenario(),
            BidirectionalScenario(),
            NonlinearScenario(),
        ]
        self.results = []
        self.holder_status = HolderStatusReader()

    def check_holder(self):
        """检查holder"""
        if not self.holder_status.is_available():
            print("\n无法检测到Holder运行")
            print("   请先运行: python run_holder.py --fixed-target 80")
            return False

        status = self.holder_status.read_status()
        print(f"\nHolder运行中")
        print(f"   目标: {status['current_target']:.1f}%")
        print(f"   持有: {status['holding_mb']:.0f}MB")
        print(f"   系统: {status['system_memory']:.1f}%")

        return True

    def run_all(self):
        """运行所有测试"""
        print("\n" + "="*80)
        print("🤓 Nerdy Holder Benchmarker")
        print("="*80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"系统内存: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"测试场景: {len(self.scenarios)} 个")
        print("="*80)

        if not self.check_holder():
            return

        print("\n准备就绪")
        print("\n按 Enter 开始...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n取消")
            return

        print("\n开始测试...\n")
        time.sleep(2)

        for i, scenario in enumerate(self.scenarios, 1):
            print(f"\n{'='*80}")
            print(f"测试 {i}/{len(self.scenarios)}")
            print(f"{'='*80}")

            try:
                metrics = scenario.run()

                if metrics:
                    self.results.append({
                        'name': scenario.name,
                        'metrics': metrics
                    })

                    self.print_result(scenario.name, metrics)

                if i < len(self.scenarios):
                    print("\n休息 5 秒...")
                    time.sleep(5)

            except KeyboardInterrupt:
                print("\n\n中断")
                break
            except Exception as e:
                print(f"\n失败: {e}")
                import traceback
                traceback.print_exc()

        if self.results:
            self.print_summary()

    def print_result(self, name, metrics):
        """打印结果"""
        print(f"\n{name} - 结果:")
        print("-" * 80)

        if metrics.get('response_time'):
            print(f"响应速度: {metrics['response_time']:.1f}秒")
        else:
            print(f"响应速度: >场景时长")

        print(f"平均误差: {metrics['avg_error']:.2f}%")
        print(f"最大误差: {metrics['max_error']:.2f}%")
        print(f"稳定性:   {metrics['stability']:.2f}%")
        print(f"调整次数: {metrics['adjustments']}次")
        print(f"调整频率: {metrics['adjustment_rate']:.1f}次/分钟")

        actual = metrics.get('holder_delta', 0)
        expected = metrics.get('expect_delta', 0)
        test_size = metrics.get('test_size_mb', 0)

        print(f"\n测试量: {test_size:.0f}MB")
        if expected != 0:
            print(f"Holder响应: {actual:+.0f}MB (预期{expected:+.0f}MB)")
            response_rate = (abs(actual) / abs(expected) * 100) if expected != 0 else 0
            print(f"响应率: {response_rate:.1f}%")
        else:
            print(f"Holder变化: {actual:+.0f}MB")

        score = self.calculate_score(metrics)
        grade = self.get_grade(score)
        print(f"\n评分: {score:.1f}/100 ({grade})")

    def calculate_score(self, m):
        """计算评分"""
        # 响应速度 (35分)
        if m.get('response_time'):
            if m['response_time'] < 5:
                response_score = 35
            elif m['response_time'] < 10:
                response_score = 30
            elif m['response_time'] < 15:
                response_score = 25
            else:
                response_score = 15
        else:
            response_score = 10

        # 准确度 (30分)
        avg_error = m['avg_error']
        if avg_error < 1:
            accuracy_score = 30
        elif avg_error < 2:
            accuracy_score = 25
        elif avg_error < 3:
            accuracy_score = 20
        else:
            accuracy_score = max(0, 30 - avg_error * 4)

        # 稳定性 (15分)
        stability = m['stability']
        if stability < 1:
            stability_score = 15
        elif stability < 2:
            stability_score = 12
        elif stability < 3:
            stability_score = 10
        else:
            stability_score = max(0, 15 - stability * 2)

        # Holder响应率 (20分)
        actual = abs(m.get('holder_delta', 0))
        expected = abs(m.get('expect_delta', 0))

        if expected > 0:
            response_rate = actual / expected
            if response_rate > 0.8:
                holder_score = 20
            elif response_rate > 0.6:
                holder_score = 15
            elif response_rate > 0.4:
                holder_score = 10
            else:
                holder_score = 5
        else:
            holder_score = 15

        return response_score + accuracy_score + stability_score + holder_score

    def get_grade(self, score):
        """评级"""
        if score >= 90:
            return "S 优秀"
        elif score >= 80:
            return "A 良好"
        elif score >= 70:
            return "B 中等"
        elif score >= 60:
            return "C 及格"
        else:
            return "D 不及格"

    def print_summary(self):
        """总结"""
        print("\n" + "="*80)
        print("测试总结")
        print("="*80)

        print(f"\n完成: {len(self.results)}/{len(self.scenarios)}\n")

        print("场景得分:")
        print("-" * 80)
        print(f"{'场景':<30} {'响应(s)':<10} {'误差':<10} {'Holder响应':<15} {'得分':<10}")
        print("-" * 80)

        scores = []
        for r in self.results:
            m = r['metrics']
            score = self.calculate_score(m)
            scores.append(score)

            resp = f"{m['response_time']:.1f}" if m.get('response_time') else "N/A"

            actual = m.get('holder_delta', 0)
            expected = m.get('expect_delta', 0)
            if expected != 0:
                response_rate = (abs(actual) / abs(expected) * 100) if expected != 0 else 0
                holder_str = f"{response_rate:.0f}%"
            else:
                holder_str = f"{actual:+.0f}MB"

            print(f"{r['name']:<30} {resp:<10} {m['avg_error']:<10.2f} {holder_str:<15} {score:<10.1f}")

        print("-" * 80)
        avg = sum(scores) / len(scores)
        print(f"\n总分: {avg:.1f}/100")
        print(f"评级: {self.get_grade(avg)}")

        # 分析
        print(f"\n关键指标:")
        all_errors = [r['metrics']['avg_error'] for r in self.results]
        all_stabilities = [r['metrics']['stability'] for r in self.results]
        print(f"  平均误差: {statistics.mean(all_errors):.2f}%")
        print(f"  平均稳定性: {statistics.mean(all_stabilities):.2f}%")

        print("\n" + "="*80)

        self.save_report(avg)

    def save_report(self, score):
        """保存报告"""
        filename = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Nerdy Holder Benchmarker 测试报告\n")
                f.write("="*80 + "\n")
                f.write(f"测试时间: {datetime.now()}\n")
                f.write(f"总分: {score:.1f}/100\n\n")

                for r in self.results:
                    f.write(f"\n场景: {r['name']}\n")
                    f.write("-"*80 + "\n")
                    for k, v in r['metrics'].items():
                        f.write(f"{k}: {v}\n")

            print(f"\n报告: {filename}")
        except Exception as e:
            print(f"\n保存失败: {e}")

"""测试追踪器模块"""

import unittest
import time
from nerdy_holder.trackers import PerformanceTracker


class TestPerformanceTracker(unittest.TestCase):
    """测试性能追踪器"""

    def setUp(self):
        """初始化"""
        self.tracker = PerformanceTracker()

    def test_init(self):
        """测试初始化"""
        self.assertEqual(len(self.tracker.metrics_window), 0)
        self.assertEqual(len(self.tracker.adjustment_times), 0)

    def test_record(self):
        """测试记录"""
        self.tracker.record(error=2.5, adjustment_size=1000, was_blocked=False)

        self.assertEqual(len(self.tracker.metrics_window), 1)
        self.assertEqual(len(self.tracker.adjustment_times), 1)

    def test_record_blocked(self):
        """测试记录被阻止的决策"""
        self.tracker.record(error=1.0, adjustment_size=500, was_blocked=True)

        self.assertEqual(len(self.tracker.metrics_window), 1)
        self.assertEqual(len(self.tracker.adjustment_times), 0)  # 被阻止不记录调整时间

    def test_get_stats_insufficient_data(self):
        """测试数据不足时获取统计"""
        # 少于10条数据
        for i in range(5):
            self.tracker.record(error=2.0, adjustment_size=1000, was_blocked=False)

        stats = self.tracker.get_stats()
        self.assertIsNone(stats)

    def test_get_stats_sufficient_data(self):
        """测试数据充足时获取统计"""
        # 记录足够的数据
        for i in range(15):
            self.tracker.record(error=2.0 + i * 0.1, adjustment_size=1000, was_blocked=False)
            time.sleep(0.01)

        stats = self.tracker.get_stats()

        self.assertIsNotNone(stats)
        self.assertIn('avg_error', stats)
        self.assertIn('error_volatility', stats)
        self.assertIn('block_rate', stats)
        self.assertIn('adjustment_rate', stats)
        self.assertIn('interval_volatility', stats)

    def test_stats_calculation(self):
        """测试统计计算"""
        # 记录一些数据
        errors = [2.0, 2.5, 3.0, 2.8, 2.3, 2.1, 2.4, 2.6, 2.9, 2.7, 2.2, 2.5]

        for i, error in enumerate(errors):
            was_blocked = (i % 3 == 0)  # 每3个有1个被阻止
            self.tracker.record(error=error, adjustment_size=1000, was_blocked=was_blocked)
            time.sleep(0.01)

        stats = self.tracker.get_stats()

        # 检查平均误差
        self.assertGreater(stats['avg_error'], 0)

        # 检查阻止率
        self.assertGreaterEqual(stats['block_rate'], 0)
        self.assertLessEqual(stats['block_rate'], 1)


if __name__ == '__main__':
    unittest.main()

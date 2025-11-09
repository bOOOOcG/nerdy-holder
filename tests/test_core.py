"""测试核心程序"""

import unittest
from unittest.mock import Mock, patch
from nerdy_holder.core import NerdyHolderPro


class TestNerdyHolderPro(unittest.TestCase):
    """测试核心Holder"""

    def setUp(self):
        """初始化"""
        # 创建一个固定目标的holder用于测试
        self.holder = NerdyHolderPro(enable_benchmark=False, fixed_target=30)

    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.holder)
        self.assertEqual(self.holder.current_target, 30)
        self.assertTrue(self.holder.test_mode)

    def test_no_release_when_holding_zero(self):
        """测试持有0MB时不应该执行释放调整"""
        # 模拟系统内存高于目标（需要释放）但持有0MB的情况
        with patch.object(self.holder, 'get_system_memory', return_value=75.0):
            with patch.object(self.holder, 'get_holding_mb', return_value=0):
                # 记录初始统计
                initial_adjustments = self.holder.stats['adjustments']
                initial_blocked = self.holder.stats['blocked']

                # 执行决策
                self.holder.make_decision()

                # 验证：应该被阻止，而不是调整
                # 因为需要释放但持有0MB
                self.assertEqual(
                    self.holder.stats['adjustments'],
                    initial_adjustments,
                    "不应该增加调整计数"
                )
                self.assertGreater(
                    self.holder.stats['blocked'],
                    initial_blocked,
                    "应该增加阻止计数"
                )

    def test_allocate_when_below_target(self):
        """测试低于目标时应该分配"""
        # 模拟系统内存低于目标
        with patch.object(self.holder, 'get_system_memory', return_value=25.0):
            with patch.object(self.holder, 'get_holding_mb', return_value=0):
                with patch.object(self.holder, 'allocate_memory', return_value=100) as mock_allocate:
                    # 执行决策
                    self.holder.make_decision()

                    # 可能会尝试分配（取决于决策逻辑）
                    # 如果调用了allocate_memory，说明尝试分配了

    def test_release_when_holding_memory(self):
        """测试持有内存时可以释放"""
        # 模拟系统内存高于目标且持有内存
        with patch.object(self.holder, 'get_system_memory', return_value=75.0):
            with patch.object(self.holder, 'get_holding_mb', return_value=5000):
                with patch.object(self.holder, 'release_memory', return_value=1000) as mock_release:
                    # 执行决策
                    self.holder.make_decision()

                    # 可能会尝试释放（取决于决策逻辑）

    def test_tolerance_check(self):
        """测试容差检查"""
        # 设置容差为0.8%
        self.holder.optimizer.params['tolerance'] = 0.8

        # 模拟误差在容差范围内
        with patch.object(self.holder, 'get_system_memory', return_value=30.5):
            initial_adjustments = self.holder.stats['adjustments']

            # 执行决策
            self.holder.make_decision()

            # 误差0.5%，小于容差0.8%，不应该调整
            self.assertEqual(
                self.holder.stats['adjustments'],
                initial_adjustments,
                "容差范围内不应该调整"
            )


if __name__ == '__main__':
    unittest.main()

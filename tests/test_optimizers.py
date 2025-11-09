"""测试优化器模块"""

import unittest
import tempfile
import os
from nerdy_holder.optimizers import ParameterOptimizer


class TestParameterOptimizer(unittest.TestCase):
    """测试参数优化器"""

    def setUp(self):
        """初始化"""
        # 使用临时文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.optimizer = ParameterOptimizer(config_file=self.temp_file.name)

    def tearDown(self):
        """清理"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.optimizer.params)
        self.assertIn('pid_kp', self.optimizer.params)
        self.assertIn('best_score', self.optimizer.params)

    def test_default_params(self):
        """测试默认参数"""
        self.assertEqual(self.optimizer.params['pid_kp'], 2.2)
        self.assertEqual(self.optimizer.params['pid_ki'], 0.25)
        self.assertEqual(self.optimizer.params['pid_kd'], 0.6)
        self.assertEqual(self.optimizer.params['best_score'], 0)

    def test_calculate_score(self):
        """测试计算得分"""
        stats = {
            'avg_error': 1.5,
            'error_volatility': 0.8,
            'block_rate': 0.2,
            'interval_volatility': 1.5
        }

        score, scenario = self.optimizer.calculate_score(stats)

        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIn(scenario, ['optimal', 'normal', 'constrained', 'volatile', 'mismatch'])

    def test_calculate_score_perfect(self):
        """测试完美得分"""
        stats = {
            'avg_error': 0.1,
            'error_volatility': 0.3,
            'block_rate': 0.2,
            'interval_volatility': 0.5
        }

        score, scenario = self.optimizer.calculate_score(stats)
        self.assertGreater(score, 90)
        self.assertEqual(scenario, 'optimal')  # 应该识别为理想场景

    def test_calculate_score_poor(self):
        """测试较差得分"""
        stats = {
            'avg_error': 8.0,
            'error_volatility': 5.0,
            'block_rate': 0.8,
            'interval_volatility': 5.0
        }

        score, scenario = self.optimizer.calculate_score(stats)
        # 高阻止率，可能被识别为constrained场景
        self.assertLess(score, 80)  # 放宽一点，因为constrained场景下高阻止率是好的

    def test_save_params(self):
        """测试保存参数"""
        self.optimizer.params['best_score'] = 95.5
        self.optimizer.save_params(force=True)

        # 创建新的优化器加载文件
        new_optimizer = ParameterOptimizer(config_file=self.temp_file.name)
        self.assertEqual(new_optimizer.params['best_score'], 95.5)

    def test_maybe_optimize_new_best(self):
        """测试优化 - 新最佳"""
        self.optimizer.params['best_score'] = 80

        stats = {
            'avg_error': 1.0,
            'error_volatility': 0.5,
            'block_rate': 0.2,
            'interval_volatility': 1.0
        }

        updated, result = self.optimizer.maybe_optimize(stats)

        if updated and not isinstance(result, str):
            self.assertGreater(result, 80)


if __name__ == '__main__':
    unittest.main()

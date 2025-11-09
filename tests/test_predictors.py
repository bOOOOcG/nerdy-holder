"""测试预测器模块"""

import unittest
from nerdy_holder.predictors import AdaptiveEMAPredictor


class TestAdaptiveEMAPredictor(unittest.TestCase):
    """测试EMA预测器"""

    def setUp(self):
        """初始化"""
        self.predictor = AdaptiveEMAPredictor(fast_alpha=0.35, slow_alpha=0.08)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.predictor.fast_alpha, 0.35)
        self.assertEqual(self.predictor.slow_alpha, 0.08)
        self.assertIsNone(self.predictor.fast_ema)
        self.assertIsNone(self.predictor.slow_ema)

    def test_update(self):
        """测试更新"""
        self.predictor.update(80.0)

        self.assertIsNotNone(self.predictor.fast_ema)
        self.assertIsNotNone(self.predictor.slow_ema)
        self.assertEqual(self.predictor.fast_ema, 80.0)
        self.assertEqual(self.predictor.slow_ema, 80.0)

    def test_multiple_updates(self):
        """测试多次更新"""
        values = [80.0, 81.0, 82.0, 81.5, 80.5]

        for val in values:
            self.predictor.update(val)

        self.assertIsNotNone(self.predictor.fast_ema)
        self.assertIsNotNone(self.predictor.slow_ema)
        self.assertEqual(len(self.predictor.history), 5)

    def test_predict(self):
        """测试预测"""
        # 未更新时预测应该返回0
        prediction = self.predictor.predict()
        self.assertEqual(prediction, 0)

        # 更新后预测
        self.predictor.update(80.0)
        self.predictor.update(81.0)
        self.predictor.update(82.0)

        prediction = self.predictor.predict(seconds_ahead=5)
        self.assertGreaterEqual(prediction, 0)
        self.assertLessEqual(prediction, 100)

    def test_get_momentum(self):
        """测试获取动量"""
        # 未更新时动量为0
        momentum = self.predictor.get_momentum()
        self.assertEqual(momentum, 0)

        # 更新后获取动量
        self.predictor.update(80.0)
        self.predictor.update(85.0)

        momentum = self.predictor.get_momentum()
        self.assertIsInstance(momentum, float)

    def test_history_limit(self):
        """测试历史记录限制"""
        # 更新超过maxlen次
        for i in range(60):
            self.predictor.update(80 + i * 0.1)

        # 历史记录应该只保留最近50条
        self.assertEqual(len(self.predictor.history), 50)


if __name__ == '__main__':
    unittest.main()

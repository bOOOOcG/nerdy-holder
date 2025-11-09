"""自适应EMA预测器"""

from collections import deque


class AdaptiveEMAPredictor:
    """自适应EMA预测器"""

    def __init__(self, fast_alpha=0.35, slow_alpha=0.08):
        self.fast_alpha = fast_alpha
        self.slow_alpha = slow_alpha
        self.fast_ema = None
        self.slow_ema = None
        self.history = deque(maxlen=50)

    def update(self, value):
        """更新EMA"""
        self.history.append(value)

        if self.fast_ema is None:
            self.fast_ema = self.slow_ema = value
        else:
            self.fast_ema = self.fast_alpha * value + (1 - self.fast_alpha) * self.fast_ema
            self.slow_ema = self.slow_alpha * value + (1 - self.slow_alpha) * self.slow_ema

    def predict(self, seconds_ahead=5):
        """预测未来值"""
        if self.fast_ema is None:
            return 0

        momentum = self.fast_ema - self.slow_ema
        prediction = self.fast_ema + momentum * (seconds_ahead / 5)
        return max(0, min(100, prediction))

    def get_momentum(self):
        """获取动量"""
        if self.fast_ema is None:
            return 0
        return self.fast_ema - self.slow_ema

"""增强型PID控制器 - 非对称策略"""

import time


class EnhancedPIDController:
    """增强型PID控制器 - 非对称策略"""

    def __init__(self, Kp=2.2, Ki=0.25, Kd=0.6, target=80):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.target = target

        self.integral = 0
        self.last_error = 0
        self.last_time = time.time()

        self.integral_max = 40
        self.integral_min = -40

        # 动作追踪
        self.last_action = None
        self.action_change_time = time.time()

    def set_target(self, target):
        """更新目标"""
        self.target = target
        self.integral = 0

    def compute(self, current_value):
        """计算PID输出 - 非对称积分恢复"""
        current_time = time.time()
        dt = max(0.1, current_time - self.last_time)

        error = self.target - current_value

        # 检测动作反转
        current_action = 'allocate' if error < 0 else 'release'
        action_changed = False

        if self.last_action and current_action != self.last_action:
            # ★ 非对称重置
            if current_action == 'release':
                # 转为释放：激进重置（需要快速响应）
                if abs(error) > 8:
                    self.integral = 0  # 完全清零
                else:
                    self.integral *= 0.1  # 重置90%
            else:
                # 转为分配：保守重置（不急着填充）
                if abs(error) > 12:
                    self.integral = 0
                else:
                    self.integral *= 0.4  # 重置60%

            self.action_change_time = current_time
            action_changed = True

        self.last_action = current_action

        # P项
        P = self.Kp * error

        # I项（动态权重）
        self.integral += error * dt
        self.integral = max(self.integral_min, min(self.integral_max, self.integral))

        # ★ 非对称权重恢复
        time_since_change = current_time - self.action_change_time

        if current_action == 'release':
            # 释放：快速恢复（8秒）
            if time_since_change < 8:
                integral_weight = 0.2 + 0.8 * (time_since_change / 8)
            else:
                integral_weight = 1.0
        else:
            # 分配：慢速恢复（18秒）
            if time_since_change < 18:
                integral_weight = 0.05 + 0.95 * (time_since_change / 18)
            else:
                integral_weight = 1.0

        I = self.Ki * self.integral * integral_weight

        # D项
        derivative = (error - self.last_error) / dt if dt > 0 else 0
        D = self.Kd * derivative

        output = P + I + D

        self.last_error = error
        self.last_time = current_time

        return {
            'output': output,
            'P': P,
            'I': I,
            'D': D,
            'error': error,
            'action_changed': action_changed
        }

"""参数优化器 - 带智能探索和回滚"""

import time
import json
import random
from pathlib import Path


class ParameterOptimizer:
    """参数优化器 - 带智能探索和回滚"""

    def __init__(self, config_file='nerdy_params.json'):
        self.config_file = config_file
        self.params = self.load_params()
        self.last_save = time.time()

        # 探索控制
        self.exploration_rate = 0.08
        self.last_params_backup = None
        self.last_score = 0
        self.exploration_start_time = None
        self.consecutive_worse = 0

    def load_params(self):
        """加载参数"""
        defaults = {
            # PID参数
            'pid_kp': 2.2,
            'pid_ki': 0.25,
            'pid_kd': 0.6,

            # 响应参数
            'response_base': 1.6,
            'response_curve': 1.7,
            'urgency_threshold': 3.5,

            # 非对称成本参数
            'cost_decay_release': 0.3,
            'cost_decay_allocate': 0.8,
            'min_interval_release': 1.5,
            'min_interval_allocate': 3.5,

            # EMA参数
            'ema_fast': 0.35,
            'ema_slow': 0.08,

            # 容差
            'tolerance': 0.8,

            # 统计 - 场景感知
            'best_score': 0,  # 综合最佳得分
            'best_scores_by_scenario': {  # 各场景最佳得分
                'optimal': 0,      # 理想场景
                'normal': 0,       # 正常场景
                'constrained': 0,  # 受限场景（无内存可操作）
                'volatile': 0,     # 波动场景
                'mismatch': 0      # 失配场景（参数不匹配）
            },
            'total_runtime_hours': 0,
            'optimization_count': 0
        }

        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
        except Exception:
            pass

        return defaults

    def save_params(self, force=False):
        """保存参数"""
        now = time.time()
        if not force and (now - self.last_save) < 60:
            return

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.params, f, indent=2)
            self.last_save = now
        except Exception:
            pass

    def identify_scenario(self, stats):
        """识别当前场景"""
        avg_error = stats['avg_error']
        block_rate = stats['block_rate']
        error_vol = stats['error_volatility']

        # 场景优先级判断
        if block_rate > 0.8:
            # 高阻止率：无内存可操作（如系统已高于目标但holder持有0MB）
            return 'constrained'
        elif error_vol > 3.0:
            # 高波动：系统负载变化剧烈
            return 'volatile'
        elif avg_error > 10:
            # 高误差：参数明显不匹配当前环境
            return 'mismatch'
        elif avg_error < 2 and error_vol < 1.0 and 0.15 <= block_rate <= 0.3:
            # 理想状态：误差小、稳定、阻止率适中
            return 'optimal'
        else:
            # 正常运行
            return 'normal'

    def calculate_score(self, stats):
        """计算性能得分 - 场景感知"""
        if not stats:
            return 0, 'unknown'

        # 识别场景
        scenario = self.identify_scenario(stats)

        # 基础指标得分
        avg_error = stats['avg_error']
        error_vol = stats['error_volatility']
        block_rate = stats['block_rate']
        interval_vol = stats['interval_volatility']

        # 1. 误差得分
        error_score = max(0, 100 - avg_error * 20)

        # 2. 稳定性得分
        if error_vol < 0.5:
            stability_score = 100
        elif error_vol < 1.0:
            stability_score = 90
        elif error_vol < 2.0:
            stability_score = 70
        else:
            stability_score = max(0, 100 - error_vol * 20)

        # 3. 阻止率得分 - 场景感知
        if scenario == 'constrained':
            # 受限场景：高阻止率反而是好的（正确识别无法操作）
            if block_rate > 0.9:
                block_score = 100
            elif block_rate > 0.7:
                block_score = 90
            elif block_rate > 0.5:
                block_score = 70
            else:
                block_score = 40  # 应该阻止但没阻止
        else:
            # 非受限场景：适度阻止最佳
            if 0.15 <= block_rate <= 0.3:
                block_score = 100
            elif block_rate < 0.15:
                block_score = 70
            elif block_rate < 0.5:
                block_score = max(0, 100 - (block_rate - 0.3) * 150)
            else:
                block_score = 20  # 阻止过多

        # 4. 调整节奏得分
        if interval_vol < 1.0:
            rhythm_score = 100
        elif interval_vol < 2.0:
            rhythm_score = 80
        elif interval_vol < 3.0:
            rhythm_score = 60
        else:
            rhythm_score = max(0, 100 - interval_vol * 10)

        # 场景自适应权重
        if scenario == 'constrained':
            # 受限场景：重点看能否正确阻止
            weights = {'error': 0.20, 'stability': 0.25, 'block': 0.40, 'rhythm': 0.15}
        elif scenario == 'volatile':
            # 波动场景：重点看稳定性
            weights = {'error': 0.25, 'stability': 0.45, 'block': 0.15, 'rhythm': 0.15}
        elif scenario == 'mismatch':
            # 失配场景：重点看能否快速纠正误差
            weights = {'error': 0.50, 'stability': 0.20, 'block': 0.15, 'rhythm': 0.15}
        elif scenario == 'optimal':
            # 理想场景：均衡评估
            weights = {'error': 0.30, 'stability': 0.35, 'block': 0.20, 'rhythm': 0.15}
        else:  # normal
            # 正常场景：默认权重
            weights = {'error': 0.35, 'stability': 0.30, 'block': 0.20, 'rhythm': 0.15}

        # 计算得分
        total_score = (error_score * weights['error'] +
                      stability_score * weights['stability'] +
                      block_score * weights['block'] +
                      rhythm_score * weights['rhythm'])

        return total_score, scenario

    def maybe_optimize(self, stats):
        """尝试优化参数 - 带回滚"""
        if not stats:
            return False, None

        current_score, scenario = self.calculate_score(stats)

        # 检查探索状态
        if self.exploration_start_time:
            time_in_exploration = time.time() - self.exploration_start_time

            if time_in_exploration > 60:
                if current_score < self.last_score - 3:
                    # 探索失败，回滚
                    if self.last_params_backup:
                        self.params.update(self.last_params_backup)
                        self.exploration_start_time = None
                        self.consecutive_worse += 1
                        return False, f"回滚 (得分{current_score:.1f}<{self.last_score:.1f})"
                else:
                    # 探索成功
                    self.last_score = current_score
                    self.exploration_start_time = None
                    self.consecutive_worse = 0
                    return True, f"探索成功 ({self.last_score:.1f}→{current_score:.1f})"

        # 更新场景最佳得分
        scenario_improved = False
        if current_score > self.params['best_scores_by_scenario'].get(scenario, 0):
            self.params['best_scores_by_scenario'][scenario] = current_score
            scenario_improved = True

        # 更新综合最佳得分（各场景加权平均）
        scenario_scores = self.params['best_scores_by_scenario']
        # 权重：optimal和normal更重要（常见场景）
        weighted_score = (
            scenario_scores.get('optimal', 0) * 0.30 +
            scenario_scores.get('normal', 0) * 0.35 +
            scenario_scores.get('constrained', 0) * 0.15 +
            scenario_scores.get('volatile', 0) * 0.15 +
            scenario_scores.get('mismatch', 0) * 0.05
        )

        if weighted_score > self.params['best_score']:
            self.params['best_score'] = weighted_score
            self.params['optimization_count'] += 1
            self.save_params(force=True)
            self.consecutive_worse = 0
            return True, (current_score, scenario, scenario_improved)

        # 连续失败则暂停
        if self.consecutive_worse >= 3:
            return False, None

        # 尝试探索
        if random.random() < self.exploration_rate:
            self.last_params_backup = {
                'response_base': self.params['response_base'],
                'response_curve': self.params['response_curve'],
                'urgency_threshold': self.params['urgency_threshold'],
                'cost_decay_release': self.params['cost_decay_release'],
                'cost_decay_allocate': self.params['cost_decay_allocate'],
            }
            self.last_score = current_score

            self.explore_parameter_smart(stats)
            self.exploration_start_time = time.time()
            return False, "开始探索"

        return False, None

    def explore_parameter_smart(self, stats):
        """智能探索 - 根据瓶颈调整"""
        if stats['avg_error'] > 3:
            # 误差大 → 增强响应
            param = random.choice(['response_base', 'urgency_threshold'])
            change = random.uniform(0.05, 0.15) * self.params[param]
        elif stats['error_volatility'] > 2:
            # 波动大 → 增强阻尼
            param = random.choice(['cost_decay_release', 'cost_decay_allocate'])
            change = random.uniform(0.05, 0.15) * self.params[param]
        elif stats['block_rate'] < 0.1:
            # 阻止太少 → 增强成本
            param = random.choice(['cost_decay_allocate', 'min_interval_allocate'])
            change = random.uniform(0.1, 0.2) * self.params[param]
        else:
            # 状态良好，小幅调整
            param = random.choice(list(self.last_params_backup.keys()))
            change = random.uniform(-0.08, 0.08) * self.params[param]

        # 应用调整
        current = self.params[param]
        limits = {
            'response_base': (1.0, 2.5),
            'response_curve': (1.3, 2.5),
            'urgency_threshold': (2.0, 5.0),
            'cost_decay_release': (0.2, 0.5),
            'cost_decay_allocate': (0.5, 1.2),
            'min_interval_release': (1.0, 3.0),
            'min_interval_allocate': (2.5, 5.0),
        }

        min_val, max_val = limits.get(param, (0.1, 10))
        self.params[param] = max(min_val, min(max_val, current + change))

"""智能评分器 - 场景感知 + 行为分析"""

import statistics
from collections import defaultdict


class IntelligentScorer:
    """智能评分器 - 利用holder的场景感知和性能数据"""

    def __init__(self):
        self.scenario_weights = {
            'optimal': {
                'accuracy': 0.30,      # 理想场景重视准确度
                'stability': 0.35,     # 重视稳定性
                'responsiveness': 0.20,  # 响应速度
                'efficiency': 0.15     # 资源效率
            },
            'normal': {
                'accuracy': 0.35,
                'stability': 0.25,
                'responsiveness': 0.25,
                'efficiency': 0.15
            },
            'constrained': {
                'accuracy': 0.20,      # 受限场景误差大是正常的
                'stability': 0.25,
                'responsiveness': 0.15,
                'efficiency': 0.40     # 重视能否正确识别无法操作
            },
            'volatile': {
                'accuracy': 0.25,      # 波动场景
                'stability': 0.45,     # 最重视稳定性
                'responsiveness': 0.15,
                'efficiency': 0.15
            },
            'mismatch': {
                'accuracy': 0.50,      # 失配场景
                'stability': 0.15,
                'responsiveness': 0.20,  # 重视能否快速纠正
                'efficiency': 0.15
            }
        }

    def calculate_comprehensive_score(self, test_data, holder_snapshots):
        """
        计算综合得分

        Args:
            test_data: benchmark测试数据（误差、稳定性等）
            holder_snapshots: holder在测试期间的状态快照列表

        Returns:
            {
                'total_score': 总分,
                'breakdown': 分项得分,
                'scenario_scores': 各场景得分,
                'behavior_analysis': 行为分析,
                'recommendations': 建议
            }
        """
        # 1. 基础指标得分
        base_scores = self._calculate_base_scores(test_data)

        # 2. 场景感知得分
        scenario_scores = self._calculate_scenario_scores(holder_snapshots)

        # 3. 行为模式分析
        behavior_analysis = self._analyze_behavior_patterns(holder_snapshots)

        # 4. 优化效果评估
        optimization_score = self._evaluate_optimization(holder_snapshots)

        # 5. 综合评分
        total_score = (
            base_scores['weighted_score'] * 0.40 +      # 基础表现
            scenario_scores['avg_score'] * 0.30 +       # 场景适应性
            behavior_analysis['health_score'] * 0.15 +  # 行为健康度
            optimization_score * 0.15                    # 优化能力
        )

        return {
            'total_score': total_score,
            'breakdown': {
                'base': base_scores,
                'scenario': scenario_scores,
                'behavior': behavior_analysis,
                'optimization': optimization_score
            },
            'grade': self._get_grade(total_score),
            'recommendations': self._generate_recommendations(
                base_scores, scenario_scores, behavior_analysis, optimization_score
            )
        }

    def _calculate_base_scores(self, test_data):
        """计算基础指标得分"""
        avg_error = test_data.get('avg_error', 0)
        stability = test_data.get('stability', 0)
        response_time = test_data.get('response_time')
        adjustment_rate = test_data.get('adjustment_rate', 0)

        # 1. 准确度得分 (0-100)
        if avg_error < 0.5:
            accuracy = 100
        elif avg_error < 1.0:
            accuracy = 95
        elif avg_error < 2.0:
            accuracy = 85
        elif avg_error < 3.0:
            accuracy = 70
        else:
            accuracy = max(0, 100 - avg_error * 15)

        # 2. 稳定性得分 (0-100)
        if stability < 0.5:
            stability_score = 100
        elif stability < 1.0:
            stability_score = 90
        elif stability < 2.0:
            stability_score = 75
        elif stability < 3.0:
            stability_score = 60
        else:
            stability_score = max(0, 100 - stability * 12)

        # 3. 响应速度得分 (0-100)
        if response_time is None:
            responsiveness = 20  # 超时
        elif response_time < 3:
            responsiveness = 100
        elif response_time < 5:
            responsiveness = 90
        elif response_time < 10:
            responsiveness = 75
        elif response_time < 15:
            responsiveness = 60
        else:
            responsiveness = max(20, 100 - response_time * 3)

        # 4. 效率得分 (调整频率应适中)
        if 3 <= adjustment_rate <= 8:
            efficiency = 100  # 理想频率
        elif 1 <= adjustment_rate < 3:
            efficiency = 85   # 有点慢
        elif 8 < adjustment_rate <= 12:
            efficiency = 85   # 有点频繁
        elif adjustment_rate < 1:
            efficiency = 60   # 太慢
        else:
            efficiency = max(30, 100 - adjustment_rate * 2)  # 太频繁

        # 加权总分
        weighted_score = (
            accuracy * 0.35 +
            stability_score * 0.30 +
            responsiveness * 0.20 +
            efficiency * 0.15
        )

        return {
            'accuracy': accuracy,
            'stability': stability_score,
            'responsiveness': responsiveness,
            'efficiency': efficiency,
            'weighted_score': weighted_score
        }

    def _calculate_scenario_scores(self, snapshots):
        """场景感知评分 - 分析holder在不同场景下的表现"""
        if not snapshots:
            return {'avg_score': 0, 'by_scenario': {}}

        # 按场景分组（需要从holder的performance数据中获取）
        # 这里简化处理，实际应该从snapshots中提取场景信息
        scenario_performances = defaultdict(list)

        for snap in snapshots:
            perf = snap.get('performance', {})
            # 根据性能指标推断场景
            scenario = self._infer_scenario(perf)
            scenario_performances[scenario].append(perf)

        scenario_scores = {}
        for scenario, perfs in scenario_performances.items():
            if perfs:
                avg_error = statistics.mean([p.get('avg_error', 0) for p in perfs if p.get('avg_error')])
                avg_volatility = statistics.mean([p.get('error_volatility', 0) for p in perfs if p.get('error_volatility')])

                # 使用场景权重评分
                weights = self.scenario_weights.get(scenario, self.scenario_weights['normal'])

                # 简化评分
                error_score = max(0, 100 - avg_error * 20)
                stability_score = max(0, 100 - avg_volatility * 15)

                scenario_scores[scenario] = (
                    error_score * weights['accuracy'] * 100 +
                    stability_score * weights['stability'] * 100
                ) / (weights['accuracy'] + weights['stability'])

        avg_score = statistics.mean(scenario_scores.values()) if scenario_scores else 0

        return {
            'avg_score': avg_score,
            'by_scenario': scenario_scores,
            'scenario_distribution': {s: len(p) for s, p in scenario_performances.items()}
        }

    def _infer_scenario(self, perf):
        """从性能数据推断场景"""
        if not perf:
            return 'unknown'

        avg_error = perf.get('avg_error', 0)
        volatility = perf.get('error_volatility', 0)
        block_rate = perf.get('block_rate', 0)

        if block_rate > 0.8:
            return 'constrained'
        elif volatility > 3.0:
            return 'volatile'
        elif avg_error > 10:
            return 'mismatch'
        elif avg_error < 2 and volatility < 1.0 and 0.15 <= block_rate <= 0.3:
            return 'optimal'
        else:
            return 'normal'

    def _analyze_behavior_patterns(self, snapshots):
        """行为模式分析 - 检测异常和健康状态"""
        if not snapshots or len(snapshots) < 3:
            return {'health_score': 50, 'patterns': [], 'anomalies': []}

        patterns = []
        anomalies = []

        # 1. 检测重复无效调整
        adjustments = [s.get('stats', {}).get('adjustments', 0) for s in snapshots]
        blocked = [s.get('stats', {}).get('blocked', 0) for s in snapshots]

        if len(adjustments) >= 2:
            adj_rate = adjustments[-1] - adjustments[0]
            block_rate_val = blocked[-1] / max(1, adjustments[-1] + blocked[-1])

            if block_rate_val > 0.9:
                anomalies.append("高阻止率 (>90%) - 可能无法有效操作内存")
            elif block_rate_val < 0.05:
                anomalies.append("低阻止率 (<5%) - 可能过度调整")

        # 2. 检测参数波动
        params_history = []
        for s in snapshots:
            params = s.get('params', {})
            if params:
                params_history.append(params)

        if len(params_history) >= 3:
            # 检查PID参数稳定性
            kp_values = [p.get('pid_kp', 0) for p in params_history]
            kp_volatility = statistics.stdev(kp_values) if len(kp_values) > 1 else 0

            if kp_volatility > 0.5:
                patterns.append("参数频繁调整 - 系统在主动探索优化")
            elif kp_volatility < 0.05:
                patterns.append("参数稳定 - 找到合适配置")

        # 3. 检测内存泄漏风险
        holdings = [s.get('holding_mb', 0) for s in snapshots]
        if len(holdings) >= 5:
            # 检查是否持续增长
            if all(holdings[i] <= holdings[i+1] for i in range(len(holdings)-1)):
                if holdings[-1] > holdings[0] * 2:
                    anomalies.append("内存持续增长 - 可能存在问题")

        # 计算健康分数
        health_score = 100
        health_score -= len(anomalies) * 15  # 每个异常扣15分
        health_score = max(0, min(100, health_score))

        return {
            'health_score': health_score,
            'patterns': patterns,
            'anomalies': anomalies
        }

    def _evaluate_optimization(self, snapshots):
        """评估优化效果"""
        if not snapshots or len(snapshots) < 2:
            return 50

        # 提取性能分数
        scores = []
        for s in snapshots:
            perf = s.get('performance', {})
            score = perf.get('score', 0)
            if score > 0:
                scores.append(score)

        if len(scores) < 2:
            return 50

        # 分析分数趋势
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]

        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)

        improvement = avg_second - avg_first

        # 评分
        if improvement > 10:
            return 100  # 显著提升
        elif improvement > 5:
            return 90   # 明显提升
        elif improvement > 0:
            return 75   # 有所提升
        elif improvement > -5:
            return 60   # 基本稳定
        else:
            return 40   # 性能下降

    def _generate_recommendations(self, base, scenario, behavior, optimization):
        """生成优化建议"""
        recommendations = []

        # 基础指标建议
        if base['accuracy'] < 70:
            recommendations.append("准确度较低 - 考虑调整PID参数或响应曲线")

        if base['stability'] < 60:
            recommendations.append("稳定性不足 - 增大cost_decay参数以减少波动")

        if base['responsiveness'] < 50:
            recommendations.append("响应过慢 - 检查urgency_threshold和response_base")

        if base['efficiency'] < 60:
            recommendations.append("调整频率异常 - 检查min_interval参数")

        # 行为模式建议
        if behavior['health_score'] < 70:
            recommendations.append(f"检测到 {len(behavior['anomalies'])} 个异常行为，需要关注")

        # 优化效果建议
        if optimization < 50:
            recommendations.append("参数优化效果不佳 - 可能需要重置或调整探索率")

        if not recommendations:
            recommendations.append("系统运行良好，保持当前配置")

        return recommendations

    def _get_grade(self, score):
        """评级"""
        if score >= 95:
            return "S+ 卓越"
        elif score >= 90:
            return "S 优秀"
        elif score >= 85:
            return "A+ 良好+"
        elif score >= 80:
            return "A 良好"
        elif score >= 75:
            return "B+ 中上"
        elif score >= 70:
            return "B 中等"
        elif score >= 60:
            return "C 及格"
        else:
            return "D 需改进"

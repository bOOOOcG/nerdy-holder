"""场景专用评分器 - 每个测试场景有独立的评分标准"""


class ScenarioScorer:
    """为不同测试场景提供专门的评分标准"""

    def score_starvation(self, metrics, analysis):
        """
        内存饥饿测试评分
        考察点：释放速度、释放完整性、误差恢复
        """
        score_breakdown = {}

        # 1. 释放速度 (40分) - 关键指标
        response_time = metrics.get('response_time')
        if response_time is None:
            speed_score = 0
        elif response_time < 3:
            speed_score = 40
        elif response_time < 5:
            speed_score = 35
        elif response_time < 8:
            speed_score = 28
        elif response_time < 12:
            speed_score = 20
        else:
            speed_score = max(0, 40 - response_time)

        score_breakdown['release_speed'] = speed_score

        # 2. 释放完整性 (30分) - holder是否足够释放
        actual = abs(metrics.get('holder_delta', 0))
        expected = abs(metrics.get('expect_delta', 0))

        if expected > 0:
            release_rate = actual / expected
            if release_rate >= 0.9:
                completeness_score = 30
            elif release_rate >= 0.7:
                completeness_score = 24
            elif release_rate >= 0.5:
                completeness_score = 18
            elif release_rate >= 0.3:
                completeness_score = 10
            else:
                completeness_score = 5
        else:
            completeness_score = 15

        score_breakdown['release_completeness'] = completeness_score

        # 3. 误差控制 (20分) - 释放后误差是否小
        avg_error = metrics.get('avg_error', 0)
        if avg_error < 1.5:
            accuracy_score = 20
        elif avg_error < 3.0:
            accuracy_score = 15
        elif avg_error < 5.0:
            accuracy_score = 10
        else:
            accuracy_score = max(0, 20 - avg_error * 2)

        score_breakdown['accuracy'] = accuracy_score

        # 4. 过程稳定性 (10分) - 释放过程是否平滑
        stability = metrics.get('stability', 0)
        if stability < 2.0:
            stability_score = 10
        elif stability < 4.0:
            stability_score = 7
        else:
            stability_score = max(0, 10 - stability)

        score_breakdown['stability'] = stability_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '释放速度、释放完整性'
        }

    def score_release(self, metrics, analysis):
        """
        内存释放测试评分（holder需要分配内存）
        考察点：分配速度、分配能力、稳定性
        """
        score_breakdown = {}

        # 1. 分配速度 (35分)
        response_time = metrics.get('response_time')
        if response_time is None:
            speed_score = 0
        elif response_time < 5:
            speed_score = 35
        elif response_time < 10:
            speed_score = 28
        elif response_time < 15:
            speed_score = 20
        else:
            speed_score = max(0, 35 - response_time)

        score_breakdown['allocation_speed'] = speed_score

        # 2. 分配能力 (35分) - 能否分配足够内存
        actual = metrics.get('holder_delta', 0)
        expected = metrics.get('expect_delta', 0)

        if expected > 0:
            alloc_rate = actual / expected
            if alloc_rate >= 0.9:
                capacity_score = 35
            elif alloc_rate >= 0.7:
                capacity_score = 28
            elif alloc_rate >= 0.5:
                capacity_score = 20
            else:
                capacity_score = max(0, 35 * alloc_rate)
        else:
            capacity_score = 17

        score_breakdown['allocation_capacity'] = capacity_score

        # 3. 稳定性 (20分) - 分配过程是否稳定
        stability = metrics.get('stability', 0)
        if stability < 1.5:
            stability_score = 20
        elif stability < 3.0:
            stability_score = 15
        elif stability < 5.0:
            stability_score = 10
        else:
            stability_score = max(0, 20 - stability * 2)

        score_breakdown['stability'] = stability_score

        # 4. 准确性 (10分)
        avg_error = metrics.get('avg_error', 0)
        if avg_error < 2.0:
            accuracy_score = 10
        elif avg_error < 4.0:
            accuracy_score = 7
        else:
            accuracy_score = max(0, 10 - avg_error)

        score_breakdown['accuracy'] = accuracy_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '分配速度、分配能力、稳定性'
        }

    def score_fluctuation(self, metrics, analysis):
        """
        快速波动测试评分
        考察点：抗干扰能力、稳定性、不过度反应
        """
        score_breakdown = {}

        # 1. 稳定性 (50分) - 最重要
        stability = metrics.get('stability', 0)
        if stability < 2.0:
            stability_score = 50
        elif stability < 3.0:
            stability_score = 42
        elif stability < 4.0:
            stability_score = 35
        elif stability < 6.0:
            stability_score = 25
        else:
            stability_score = max(0, 50 - stability * 5)

        score_breakdown['stability'] = stability_score

        # 2. 误差控制 (25分) - 波动下仍保持误差小
        avg_error = metrics.get('avg_error', 0)
        if avg_error < 2.0:
            accuracy_score = 25
        elif avg_error < 3.5:
            accuracy_score = 20
        elif avg_error < 5.0:
            accuracy_score = 15
        else:
            accuracy_score = max(0, 25 - avg_error * 3)

        score_breakdown['accuracy'] = accuracy_score

        # 3. 调整节奏 (25分) - 不应过度调整
        adj_rate = metrics.get('adjustment_rate', 0)
        if 2 <= adj_rate <= 6:
            rhythm_score = 25  # 理想频率
        elif 1 <= adj_rate < 2 or 6 < adj_rate <= 10:
            rhythm_score = 18  # 可接受
        elif adj_rate < 1:
            rhythm_score = 10  # 太慢
        else:
            rhythm_score = max(0, 25 - adj_rate)  # 太频繁

        score_breakdown['adjustment_rhythm'] = rhythm_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '稳定性、抗干扰、调整节奏'
        }

    def score_pressure(self, metrics, analysis):
        """
        渐进压力测试评分
        考察点：适应性、持续稳定性、渐进跟踪
        """
        score_breakdown = {}

        # 1. 误差跟踪 (40分) - 能否跟上渐进变化
        avg_error = metrics.get('avg_error', 0)
        if avg_error < 1.0:
            tracking_score = 40
        elif avg_error < 2.0:
            tracking_score = 35
        elif avg_error < 3.0:
            tracking_score = 28
        else:
            tracking_score = max(0, 40 - avg_error * 8)

        score_breakdown['tracking'] = tracking_score

        # 2. 持续稳定性 (30分) - 全程保持稳定
        stability = metrics.get('stability', 0)
        if stability < 1.0:
            stability_score = 30
        elif stability < 2.0:
            stability_score = 25
        elif stability < 3.0:
            stability_score = 18
        else:
            stability_score = max(0, 30 - stability * 5)

        score_breakdown['stability'] = stability_score

        # 3. 响应速度 (20分)
        response_time = metrics.get('response_time')
        if response_time is None:
            speed_score = 5
        elif response_time < 5:
            speed_score = 20
        elif response_time < 10:
            speed_score = 15
        else:
            speed_score = max(5, 20 - response_time)

        score_breakdown['responsiveness'] = speed_score

        # 4. 调整频率 (10分) - 应该渐进调整，不要跳跃
        adj_rate = metrics.get('adjustment_rate', 0)
        if 4 <= adj_rate <= 12:
            rhythm_score = 10
        elif 2 <= adj_rate < 4 or 12 < adj_rate <= 15:
            rhythm_score = 7
        else:
            rhythm_score = 3

        score_breakdown['rhythm'] = rhythm_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '渐进跟踪、持续稳定'
        }

    def score_extreme(self, metrics, analysis):
        """
        极限响应测试评分
        考察点：极限情况下的快速响应和稳定性
        """
        score_breakdown = {}

        # 1. 极限响应速度 (50分) - 最关键
        response_time = metrics.get('response_time')
        if response_time is None:
            speed_score = 0
        elif response_time < 2:
            speed_score = 50
        elif response_time < 5:
            speed_score = 42
        elif response_time < 8:
            speed_score = 32
        elif response_time < 12:
            speed_score = 20
        else:
            speed_score = max(0, 50 - response_time * 2)

        score_breakdown['extreme_response'] = speed_score

        # 2. 应对能力 (30分) - holder响应量
        actual = abs(metrics.get('holder_delta', 0))
        expected = abs(metrics.get('expect_delta', 0))

        if expected > 0:
            response_rate = actual / expected
            if response_rate >= 0.8:
                capacity_score = 30
            elif response_rate >= 0.6:
                capacity_score = 24
            elif response_rate >= 0.4:
                capacity_score = 18
            else:
                capacity_score = max(0, 30 * response_rate)
        else:
            capacity_score = 15

        score_breakdown['capacity'] = capacity_score

        # 3. 恢复稳定性 (20分) - 冲击后能否稳定
        stability = metrics.get('stability', 0)
        if stability < 3.0:
            stability_score = 20
        elif stability < 5.0:
            stability_score = 15
        elif stability < 7.0:
            stability_score = 10
        else:
            stability_score = max(0, 20 - stability)

        score_breakdown['stability'] = stability_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '极限响应速度、应对能力'
        }

    def score_shock(self, metrics, analysis):
        """
        瞬间冲击测试评分
        考察点：突发响应、冲击吸收
        """
        score_breakdown = {}

        # 1. 突发响应 (45分)
        response_time = metrics.get('response_time')
        if response_time is None:
            speed_score = 0
        elif response_time < 3:
            speed_score = 45
        elif response_time < 6:
            speed_score = 38
        elif response_time < 10:
            speed_score = 28
        else:
            speed_score = max(0, 45 - response_time * 2)

        score_breakdown['shock_response'] = speed_score

        # 2. 冲击吸收 (35分) - 能否吸收冲击
        actual = metrics.get('holder_delta', 0)
        expected = metrics.get('expect_delta', 0)

        if expected != 0:
            absorption_rate = abs(actual / expected)
            if absorption_rate >= 0.85:
                absorption_score = 35
            elif absorption_rate >= 0.65:
                absorption_score = 28
            elif absorption_rate >= 0.45:
                absorption_score = 20
            else:
                absorption_score = max(0, 35 * absorption_rate)
        else:
            absorption_score = 17

        score_breakdown['shock_absorption'] = absorption_score

        # 3. 后续稳定 (20分)
        stability = metrics.get('stability', 0)
        if stability < 3.0:
            stability_score = 20
        elif stability < 5.0:
            stability_score = 15
        else:
            stability_score = max(0, 20 - stability)

        score_breakdown['stability'] = stability_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '突发响应、冲击吸收'
        }

    def score_sustained(self, metrics, analysis):
        """
        持续压力测试评分
        考察点：长时间稳定性、耐久性
        """
        score_breakdown = {}

        # 1. 持续稳定性 (50分) - 最重要
        stability = metrics.get('stability', 0)
        if stability < 0.8:
            stability_score = 50
        elif stability < 1.5:
            stability_score = 45
        elif stability < 2.5:
            stability_score = 38
        elif stability < 4.0:
            stability_score = 28
        else:
            stability_score = max(0, 50 - stability * 8)

        score_breakdown['sustained_stability'] = stability_score

        # 2. 误差恒定性 (30分) - 长时间误差小
        avg_error = metrics.get('avg_error', 0)
        if avg_error < 1.0:
            accuracy_score = 30
        elif avg_error < 2.0:
            accuracy_score = 25
        elif avg_error < 3.0:
            accuracy_score = 18
        else:
            accuracy_score = max(0, 30 - avg_error * 6)

        score_breakdown['accuracy'] = accuracy_score

        # 3. 调整效率 (20分) - 应该很少调整
        adj_rate = metrics.get('adjustment_rate', 0)
        if adj_rate < 2:
            efficiency_score = 20
        elif adj_rate < 4:
            efficiency_score = 15
        elif adj_rate < 6:
            efficiency_score = 10
        else:
            efficiency_score = max(0, 20 - adj_rate)

        score_breakdown['efficiency'] = efficiency_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '持续稳定性、耐久性'
        }

    def score_bidirectional(self, metrics, analysis):
        """
        双向测试评分
        考察点：双向调整能力、平衡性
        """
        score_breakdown = {}

        # 1. 双向能力 (40分) - 分配和释放都要好
        actual = metrics.get('holder_delta', 0)
        # 双向测试最终应该接近0
        if abs(actual) < 500:
            balance_score = 40
        elif abs(actual) < 1500:
            balance_score = 32
        elif abs(actual) < 3000:
            balance_score = 24
        else:
            balance_score = max(0, 40 - abs(actual) / 100)

        score_breakdown['bidirectional_balance'] = balance_score

        # 2. 响应速度 (30分)
        response_time = metrics.get('response_time')
        if response_time is None:
            speed_score = 5
        elif response_time < 4:
            speed_score = 30
        elif response_time < 8:
            speed_score = 24
        elif response_time < 12:
            speed_score = 18
        else:
            speed_score = max(5, 30 - response_time)

        score_breakdown['responsiveness'] = speed_score

        # 3. 稳定性 (20分)
        stability = metrics.get('stability', 0)
        if stability < 2.0:
            stability_score = 20
        elif stability < 3.5:
            stability_score = 15
        elif stability < 5.0:
            stability_score = 10
        else:
            stability_score = max(0, 20 - stability * 2)

        score_breakdown['stability'] = stability_score

        # 4. 误差 (10分)
        avg_error = metrics.get('avg_error', 0)
        if avg_error < 2.0:
            accuracy_score = 10
        elif avg_error < 4.0:
            accuracy_score = 7
        else:
            accuracy_score = max(0, 10 - avg_error)

        score_breakdown['accuracy'] = accuracy_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '双向平衡、响应能力'
        }

    def score_nonlinear(self, metrics, analysis):
        """
        非线性变化测试评分
        考察点：复杂模式跟踪、预测能力、适应性
        """
        score_breakdown = {}

        # 1. 跟踪能力 (40分) - 能否跟上非线性变化
        avg_error = metrics.get('avg_error', 0)
        if avg_error < 2.0:
            tracking_score = 40
        elif avg_error < 3.5:
            tracking_score = 32
        elif avg_error < 5.0:
            tracking_score = 24
        elif avg_error < 7.0:
            tracking_score = 16
        else:
            tracking_score = max(0, 40 - avg_error * 4)

        score_breakdown['nonlinear_tracking'] = tracking_score

        # 2. 预测准确性 (30分) - EMA预测是否有效
        # 需要从analysis中获取预测误差
        # 这里简化处理
        stability = metrics.get('stability', 0)
        if stability < 2.5:
            prediction_score = 30
        elif stability < 4.0:
            prediction_score = 22
        elif stability < 6.0:
            prediction_score = 15
        else:
            prediction_score = max(0, 30 - stability * 3)

        score_breakdown['prediction'] = prediction_score

        # 3. 适应速度 (20分) - 模式变化时快速适应
        response_time = metrics.get('response_time')
        if response_time is None:
            adapt_score = 5
        elif response_time < 5:
            adapt_score = 20
        elif response_time < 10:
            adapt_score = 15
        elif response_time < 15:
            adapt_score = 10
        else:
            adapt_score = max(5, 20 - response_time)

        score_breakdown['adaptation'] = adapt_score

        # 4. 调整智能度 (10分) - 不应该振荡
        adj_rate = metrics.get('adjustment_rate', 0)
        if 3 <= adj_rate <= 10:
            intelligence_score = 10
        elif 2 <= adj_rate < 3 or 10 < adj_rate <= 15:
            intelligence_score = 7
        else:
            intelligence_score = max(0, 10 - abs(adj_rate - 6))

        score_breakdown['intelligence'] = intelligence_score

        total = sum(score_breakdown.values())
        return {
            'score': total,
            'breakdown': score_breakdown,
            'key_metrics': '非线性跟踪、预测能力、适应性'
        }

    def score_scenario(self, scenario_name, metrics, analysis=None):
        """根据场景名称选择评分方法"""
        scenario_map = {
            '内存饥饿测试': self.score_starvation,
            '内存释放测试': self.score_release,
            '快速波动测试': self.score_fluctuation,
            '渐进压力测试': self.score_pressure,
            '极限响应测试': self.score_extreme,
            '瞬间冲击测试': self.score_shock,
            '持续压力测试': self.score_sustained,
            '双向测试': self.score_bidirectional,
            '非线性变化测试': self.score_nonlinear,
        }

        scorer = scenario_map.get(scenario_name)
        if scorer:
            return scorer(metrics, analysis)
        else:
            # 默认评分
            return {
                'score': 50,
                'breakdown': {},
                'key_metrics': '未知场景'
            }

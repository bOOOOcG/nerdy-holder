"""系统分析器"""

import psutil


class SystemAnalyzer:
    """系统状态分析器"""

    def __init__(self, holder_status):
        self.holder_status = holder_status
        self.total_memory_gb = psutil.virtual_memory().total / (1024**3)
        self.total_memory_mb = psutil.virtual_memory().total / (1024*1024)

    def analyze(self):
        """分析当前系统状态"""
        mem = psutil.virtual_memory()
        status = self.holder_status.read_status()

        if not status:
            return None

        analysis = {
            'total_mb': self.total_memory_mb,
            'total_gb': self.total_memory_gb,
            'system_used_mb': mem.used / (1024*1024),
            'system_free_mb': mem.available / (1024*1024),
            'system_percent': mem.percent,
            'holder_holding_mb': status.get('holding_mb', 0),
            'holder_target': status.get('current_target', 80),
            'holder_chunks': status.get('chunks_count', 0),
            'holder_can_release': status.get('holding_mb', 0),
            'system_can_allocate': mem.available / (1024*1024),
        }

        target_total_mb = analysis['holder_target'] / 100 * self.total_memory_mb
        analysis['holder_target_mb'] = target_total_mb
        analysis['holder_surplus'] = analysis['holder_holding_mb']
        analysis['holder_shortage'] = max(0, target_total_mb - analysis['system_used_mb'])

        return analysis

    def calculate_test_params(self, scenario_type):
        """为场景计算最优测试参数"""
        analysis = self.analyze()
        if not analysis:
            return None

        params = {
            'scenario_type': scenario_type,
            'feasible': True,
            'reason': '',
            'test_size_mb': 0,
            'expect_holder_delta_mb': 0,
            'safety_margin': 0.8
        }

        if scenario_type == 'memory_starvation':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_test = min(
                holder_can_release * params['safety_margin'],
                system_can_allocate * params['safety_margin']
            )

            if max_test < 1000:
                params['feasible'] = False
                params['reason'] = f"测试量不足: holder仅有{holder_can_release:.0f}MB, 系统空闲{system_can_allocate:.0f}MB"
                return params

            if holder_can_release > 15000:
                params['test_size_mb'] = min(10000, max_test)
                params['description'] = "大规模饥饿测试(10GB)"
            elif holder_can_release > 8000:
                params['test_size_mb'] = min(5000, max_test)
                params['description'] = "中等饥饿测试(5GB)"
            elif holder_can_release > 3000:
                params['test_size_mb'] = min(3000, max_test)
                params['description'] = "小规模饥饿测试(3GB)"
            else:
                params['test_size_mb'] = min(2000, max_test)
                params['description'] = "轻度饥饿测试(2GB)"

            params['expect_holder_delta_mb'] = -params['test_size_mb']

        elif scenario_type == 'memory_release':
            system_can_allocate = analysis['system_can_allocate']

            max_test = system_can_allocate * params['safety_margin']

            if max_test < 1000:
                params['feasible'] = False
                params['reason'] = f"系统空闲不足: 仅{system_can_allocate:.0f}MB"
                return params

            if system_can_allocate > 15000:
                params['test_size_mb'] = min(10000, max_test)
                params['description'] = "大规模释放测试(10GB)"
            elif system_can_allocate > 8000:
                params['test_size_mb'] = min(5000, max_test)
                params['description'] = "中等释放测试(5GB)"
            elif system_can_allocate > 3000:
                params['test_size_mb'] = min(3000, max_test)
                params['description'] = "小规模释放测试(3GB)"
            else:
                params['test_size_mb'] = min(2000, max_test)
                params['description'] = "轻度释放测试(2GB)"

            params['expect_holder_delta_mb'] = params['test_size_mb']

        elif scenario_type == 'rapid_fluctuation':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_wave = min(
                holder_can_release * 0.5,
                system_can_allocate * 0.6
            )

            if max_wave < 1000:
                params['feasible'] = False
                params['reason'] = f"可用空间不足以波动"
                return params

            if max_wave > 8000:
                params['test_size_mb'] = 5000
                params['wave_count'] = 6
                params['description'] = "大幅度波动(5GB × 6次)"
            elif max_wave > 4000:
                params['test_size_mb'] = 3000
                params['wave_count'] = 6
                params['description'] = "中等波动(3GB × 6次)"
            else:
                params['test_size_mb'] = 2000
                params['wave_count'] = 5
                params['description'] = "小幅度波动(2GB × 5次)"

        elif scenario_type == 'gradual_pressure':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_total = min(
                holder_can_release * 0.7,
                system_can_allocate * 0.7
            )

            if max_total < 2000:
                params['feasible'] = False
                params['reason'] = f"空间不足以渐进测试"
                return params

            if max_total > 15000:
                params['test_size_mb'] = 12000
                params['step_size_mb'] = 2000
                params['steps'] = 6
                params['description'] = "高压渐进(12GB，6步)"
            elif max_total > 8000:
                params['test_size_mb'] = 8000
                params['step_size_mb'] = 1500
                params['steps'] = 5
                params['description'] = "中压渐进(8GB，5步)"
            else:
                params['test_size_mb'] = 5000
                params['step_size_mb'] = 1000
                params['steps'] = 5
                params['description'] = "低压渐进(5GB，5步)"

        elif scenario_type == 'extreme_response':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_extreme = min(
                holder_can_release * 0.9,
                system_can_allocate * 0.9
            )

            if max_extreme < 3000:
                params['feasible'] = False
                params['reason'] = f"空间不足以极限测试"
                return params

            if max_extreme > 20000:
                params['test_size_mb'] = 20000
                params['description'] = "超大极限冲击(20GB)"
            elif max_extreme > 15000:
                params['test_size_mb'] = 15000
                params['description'] = "大型极限冲击(15GB)"
            elif max_extreme > 10000:
                params['test_size_mb'] = 10000
                params['description'] = "中型极限冲击(10GB)"
            else:
                params['test_size_mb'] = 5000
                params['description'] = "小型极限冲击(5GB)"

            params['expect_holder_delta_mb'] = -params['test_size_mb']

        elif scenario_type == 'instant_shock':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_shock = min(
                holder_can_release * 0.7,
                system_can_allocate * 0.7
            )

            if max_shock < 2000:
                params['feasible'] = False
                params['reason'] = f"空间不足"
                return params

            params['test_size_mb'] = min(8000, max_shock)
            params['description'] = f"瞬间冲击测试({params['test_size_mb']/1000:.0f}GB)"
            params['expect_holder_delta_mb'] = params['test_size_mb']

        elif scenario_type == 'sustained_pressure':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_sustained = min(
                holder_can_release * 0.6,
                system_can_allocate * 0.6
            )

            if max_sustained < 3000:
                params['feasible'] = False
                params['reason'] = f"空间不足"
                return params

            params['test_size_mb'] = min(10000, max_sustained)
            params['description'] = f"持续压力测试({params['test_size_mb']/1000:.0f}GB)"
            params['expect_holder_delta_mb'] = -params['test_size_mb']

        elif scenario_type == 'bidirectional':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_bidir = min(
                holder_can_release * 0.5,
                system_can_allocate * 0.5
            )

            if max_bidir < 2000:
                params['feasible'] = False
                params['reason'] = f"空间不足"
                return params

            params['test_size_mb'] = min(8000, max_bidir)
            params['description'] = f"双向测试({params['test_size_mb']/1000:.0f}GB)"

        elif scenario_type == 'nonlinear_change':
            holder_can_release = analysis['holder_can_release']
            system_can_allocate = analysis['system_can_allocate']

            max_nonlinear = min(
                holder_can_release * 0.4,
                system_can_allocate * 0.4
            )

            if max_nonlinear < 1500:
                params['feasible'] = False
                params['reason'] = f"空间不足以进行非线性测试"
                return params

            if max_nonlinear > 10000:
                params['test_size_mb'] = 5000
                params['description'] = "大规模非线性测试(5GB)"
            elif max_nonlinear > 5000:
                params['test_size_mb'] = 3000
                params['description'] = "中等非线性测试(3GB)"
            else:
                params['test_size_mb'] = 2000
                params['description'] = "小规模非线性测试(2GB)"

            params['pattern'] = 'combined'  # 默认组合模式

        return params

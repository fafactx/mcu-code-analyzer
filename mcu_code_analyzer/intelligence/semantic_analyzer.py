"""
语义分析器 - 深度理解代码语义和业务逻辑
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
from utils.logger import logger, log_decorator, performance_monitor
from utils.file_utils import FileUtils
from intelligence.llm_manager import llm_manager
from intelligence.prompt_generator import PromptGenerator, PromptContext


@dataclass
class BusinessLogic:
    """业务逻辑数据类"""
    name: str
    description: str = ""
    functions: List[str] = field(default_factory=list)
    data_flow: List[str] = field(default_factory=list)
    state_transitions: List[str] = field(default_factory=list)
    timing_requirements: List[str] = field(default_factory=list)
    error_handling: List[str] = field(default_factory=list)


@dataclass
class ArchitecturalPattern:
    """架构模式数据类"""
    pattern_type: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class SemanticAnalysisResult:
    """语义分析结果数据类"""
    business_logics: List[BusinessLogic] = field(default_factory=list)
    architectural_patterns: List[ArchitecturalPattern] = field(default_factory=list)
    control_flows: Dict[str, str] = field(default_factory=dict)
    data_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    performance_bottlenecks: List[str] = field(default_factory=list)
    security_concerns: List[str] = field(default_factory=list)
    maintainability_score: float = 0.0
    complexity_metrics: Dict[str, float] = field(default_factory=dict)


class SemanticAnalyzer:
    """语义分析器"""
    
    def __init__(self):
        self.prompt_generator = PromptGenerator()
        self.analysis_cache = {}
        
        # 预定义的架构模式
        self.known_patterns = {
            'state_machine': {
                'keywords': ['state', 'transition', 'switch', 'case', 'enum'],
                'functions': ['state_handler', 'transition', 'state_machine']
            },
            'observer': {
                'keywords': ['callback', 'notify', 'observer', 'listener'],
                'functions': ['register', 'unregister', 'notify']
            },
            'interrupt_driven': {
                'keywords': ['interrupt', 'irq', 'handler', 'isr'],
                'functions': ['handler', 'irq', 'isr']
            },
            'polling': {
                'keywords': ['poll', 'check', 'status', 'flag'],
                'functions': ['poll', 'check_status', 'wait_for']
            },
            'producer_consumer': {
                'keywords': ['queue', 'buffer', 'producer', 'consumer'],
                'functions': ['enqueue', 'dequeue', 'put', 'get']
            }
        }
    
    @log_decorator
    @performance_monitor
    def analyze_project_semantics(self, project_path: Path, analysis_result: Dict,
                                 chip_info: Dict = None) -> SemanticAnalysisResult:
        """分析项目语义"""
        logger.info(f"开始语义分析: {project_path}")
        
        result = SemanticAnalysisResult()
        
        # 1. 识别业务逻辑模块
        result.business_logics = self._identify_business_logics(analysis_result)
        
        # 2. 检测架构模式
        result.architectural_patterns = self._detect_architectural_patterns(analysis_result)
        
        # 3. 分析控制流
        result.control_flows = self._analyze_control_flows(analysis_result)
        
        # 4. 分析数据依赖
        result.data_dependencies = self._analyze_data_dependencies(analysis_result)
        
        # 5. 识别性能瓶颈
        result.performance_bottlenecks = self._identify_performance_bottlenecks(analysis_result)
        
        # 6. 安全性分析
        result.security_concerns = self._analyze_security_concerns(analysis_result)
        
        # 7. 计算可维护性评分
        result.maintainability_score = self._calculate_maintainability_score(analysis_result)
        
        # 8. 复杂度度量
        result.complexity_metrics = self._calculate_complexity_metrics(analysis_result)
        
        logger.info("语义分析完成")
        return result
    
    @log_decorator
    def analyze_business_intent(self, main_code: str, context: PromptContext) -> str:
        """分析业务意图"""
        logger.info("分析业务意图")
        
        prompt = f"""作为嵌入式系统专家，请分析以下main函数的业务意图和应用场景：

```c
{main_code}
```

项目上下文：
- 芯片：{getattr(context.chip_info, 'device_name', '未知') if context.chip_info else '未知'}
- 使用的接口：{self._format_interfaces(context.interface_usage)}

请分析：
1. 这个项目最可能的应用场景是什么？
2. 主要解决什么业务问题？
3. 目标用户群体是谁？
4. 核心价值是什么？

请用中文简洁回答，重点突出业务价值。"""
        
        response = llm_manager.generate(prompt, temperature=0.2)
        
        if response.success:
            return response.content.strip()
        else:
            logger.warning(f"业务意图分析失败: {response.error_message}")
            return self._infer_business_intent_fallback(main_code, context)
    
    @log_decorator
    def analyze_code_quality(self, functions: Dict, call_relations: List) -> Dict[str, any]:
        """分析代码质量"""
        logger.info("分析代码质量")
        
        quality_metrics = {
            'function_complexity': {},
            'coupling_analysis': {},
            'cohesion_analysis': {},
            'naming_quality': {},
            'overall_score': 0.0
        }
        
        # 分析函数复杂度
        for func_name, func_info in functions.items():
            complexity = self._calculate_function_complexity(func_info)
            quality_metrics['function_complexity'][func_name] = complexity
        
        # 分析耦合度
        coupling_scores = self._analyze_coupling(functions, call_relations)
        quality_metrics['coupling_analysis'] = coupling_scores
        
        # 分析内聚性
        cohesion_scores = self._analyze_cohesion(functions)
        quality_metrics['cohesion_analysis'] = cohesion_scores
        
        # 分析命名质量
        naming_scores = self._analyze_naming_quality(functions)
        quality_metrics['naming_quality'] = naming_scores
        
        # 计算总体评分
        quality_metrics['overall_score'] = self._calculate_overall_quality_score(quality_metrics)
        
        return quality_metrics
    
    def _identify_business_logics(self, analysis_result: Dict) -> List[BusinessLogic]:
        """识别业务逻辑模块"""
        business_logics = []
        
        # 基于函数名和调用关系推断业务逻辑
        functions = analysis_result.get('functions', {})
        call_graph = analysis_result.get('call_graph', {})
        
        # 按功能分组函数
        function_groups = self._group_functions_by_purpose(functions)
        
        for group_name, group_functions in function_groups.items():
            if len(group_functions) >= 2:  # 至少2个函数才算一个业务逻辑模块
                logic = BusinessLogic(
                    name=group_name,
                    description=f"{group_name}相关的业务逻辑",
                    functions=group_functions
                )
                business_logics.append(logic)
        
        return business_logics
    
    def _detect_architectural_patterns(self, analysis_result: Dict) -> List[ArchitecturalPattern]:
        """检测架构模式"""
        patterns = []
        functions = analysis_result.get('functions', {})
        
        for pattern_name, pattern_info in self.known_patterns.items():
            confidence = self._calculate_pattern_confidence(functions, pattern_info)
            
            if confidence > 0.3:  # 置信度阈值
                evidence = self._collect_pattern_evidence(functions, pattern_info)
                pattern = ArchitecturalPattern(
                    pattern_type=pattern_name,
                    confidence=confidence,
                    evidence=evidence,
                    description=self._get_pattern_description(pattern_name)
                )
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda p: p.confidence, reverse=True)
    
    def _analyze_control_flows(self, analysis_result: Dict) -> Dict[str, str]:
        """分析控制流"""
        control_flows = {}
        call_graph = analysis_result.get('call_graph', {})
        
        # 分析主要的控制流路径
        if 'main' in call_graph:
            main_flow = self._trace_control_flow('main', call_graph, set(), 0)
            control_flows['main_flow'] = main_flow
        
        # 分析中断处理流程
        interrupt_handlers = self._find_interrupt_handlers(analysis_result.get('functions', {}))
        for handler in interrupt_handlers:
            if handler in call_graph:
                flow = self._trace_control_flow(handler, call_graph, set(), 0)
                control_flows[f'{handler}_flow'] = flow
        
        return control_flows
    
    def _analyze_data_dependencies(self, analysis_result: Dict) -> Dict[str, List[str]]:
        """分析数据依赖"""
        dependencies = {}
        functions = analysis_result.get('functions', {})
        
        # 基于函数调用关系推断数据依赖
        for func_name, func_info in functions.items():
            deps = []
            
            # 分析函数调用的其他函数
            if hasattr(func_info, 'calls'):
                for called_func in func_info.calls:
                    if called_func in functions:
                        deps.append(called_func)
            
            if deps:
                dependencies[func_name] = deps
        
        return dependencies
    
    def _identify_performance_bottlenecks(self, analysis_result: Dict) -> List[str]:
        """识别性能瓶颈"""
        bottlenecks = []
        functions = analysis_result.get('functions', {})
        call_graph = analysis_result.get('call_graph', {})
        
        # 检查深度嵌套的函数调用
        for func_name in call_graph:
            depth = self._calculate_call_depth(func_name, call_graph, set())
            if depth > 5:
                bottlenecks.append(f"深度调用链: {func_name} (深度: {depth})")
        
        # 检查高频调用的函数
        call_counts = {}
        for caller, callees in call_graph.items():
            for callee in callees:
                call_counts[callee] = call_counts.get(callee, 0) + 1
        
        high_frequency_funcs = [func for func, count in call_counts.items() if count > 10]
        for func in high_frequency_funcs:
            bottlenecks.append(f"高频调用函数: {func} (调用次数: {call_counts[func]})")
        
        return bottlenecks
    
    def _analyze_security_concerns(self, analysis_result: Dict) -> List[str]:
        """分析安全性问题"""
        concerns = []
        functions = analysis_result.get('functions', {})
        
        # 检查潜在的安全风险函数
        risky_functions = ['strcpy', 'strcat', 'sprintf', 'gets', 'scanf']
        
        for func_name, func_info in functions.items():
            if hasattr(func_info, 'calls'):
                for called_func in func_info.calls:
                    if any(risky in called_func for risky in risky_functions):
                        concerns.append(f"使用了潜在不安全的函数: {called_func} 在 {func_name}")
        
        # 检查缓冲区操作
        buffer_functions = [func for func in functions.keys() if 'buffer' in func.lower() or 'buf' in func.lower()]
        if buffer_functions:
            concerns.append(f"发现缓冲区操作函数，需要检查边界: {', '.join(buffer_functions[:3])}")
        
        return concerns
    
    def _calculate_maintainability_score(self, analysis_result: Dict) -> float:
        """计算可维护性评分"""
        score = 100.0  # 基础分数
        
        function_stats = analysis_result.get('function_stats', {})
        
        # 函数数量影响
        total_functions = function_stats.get('total_functions', 0)
        if total_functions > 100:
            score -= 10
        elif total_functions > 200:
            score -= 20
        
        # 静态函数比例（好的封装）
        static_functions = function_stats.get('static_functions', 0)
        if total_functions > 0:
            static_ratio = static_functions / total_functions
            score += static_ratio * 10
        
        # 函数定义比例
        defined_functions = function_stats.get('defined_functions', 0)
        if total_functions > 0:
            definition_ratio = defined_functions / total_functions
            score += definition_ratio * 5
        
        return max(0.0, min(100.0, score))
    
    def _calculate_complexity_metrics(self, analysis_result: Dict) -> Dict[str, float]:
        """计算复杂度度量"""
        metrics = {}
        
        function_stats = analysis_result.get('function_stats', {})
        call_stats = analysis_result.get('call_stats', {})
        
        # 函数复杂度
        total_functions = function_stats.get('total_functions', 1)
        total_calls = call_stats.get('total_calls', 0)
        
        metrics['average_calls_per_function'] = total_calls / total_functions
        metrics['function_density'] = function_stats.get('defined_functions', 0) / total_functions
        metrics['static_function_ratio'] = function_stats.get('static_functions', 0) / total_functions
        
        # 调用复杂度
        unique_callers = call_stats.get('unique_callers', 1)
        unique_callees = call_stats.get('unique_callees', 1)
        
        metrics['call_diversity'] = unique_callees / unique_callers
        metrics['reusability_index'] = unique_callees / total_functions
        
        return metrics
    
    def _group_functions_by_purpose(self, functions: Dict) -> Dict[str, List[str]]:
        """按用途分组函数"""
        groups = {
            'initialization': [],
            'configuration': [],
            'communication': [],
            'control': [],
            'data_processing': [],
            'interrupt_handling': [],
            'utility': []
        }
        
        for func_name in functions.keys():
            func_lower = func_name.lower()
            
            if any(keyword in func_lower for keyword in ['init', 'setup', 'begin']):
                groups['initialization'].append(func_name)
            elif any(keyword in func_lower for keyword in ['config', 'set', 'configure']):
                groups['configuration'].append(func_name)
            elif any(keyword in func_lower for keyword in ['send', 'receive', 'transmit', 'uart', 'spi', 'i2c']):
                groups['communication'].append(func_name)
            elif any(keyword in func_lower for keyword in ['control', 'start', 'stop', 'enable', 'disable']):
                groups['control'].append(func_name)
            elif any(keyword in func_lower for keyword in ['process', 'calculate', 'convert', 'filter']):
                groups['data_processing'].append(func_name)
            elif any(keyword in func_lower for keyword in ['irq', 'handler', 'isr', 'interrupt']):
                groups['interrupt_handling'].append(func_name)
            else:
                groups['utility'].append(func_name)
        
        # 移除空组
        return {k: v for k, v in groups.items() if v}
    
    def _calculate_pattern_confidence(self, functions: Dict, pattern_info: Dict) -> float:
        """计算模式置信度"""
        keyword_matches = 0
        function_matches = 0
        total_functions = len(functions)
        
        if total_functions == 0:
            return 0.0
        
        # 检查关键字匹配
        for func_name in functions.keys():
            func_lower = func_name.lower()
            for keyword in pattern_info['keywords']:
                if keyword.lower() in func_lower:
                    keyword_matches += 1
                    break
        
        # 检查函数名模式匹配
        for func_name in functions.keys():
            func_lower = func_name.lower()
            for pattern_func in pattern_info['functions']:
                if pattern_func.lower() in func_lower:
                    function_matches += 1
                    break
        
        # 计算置信度
        keyword_confidence = keyword_matches / total_functions
        function_confidence = function_matches / total_functions
        
        return (keyword_confidence + function_confidence) / 2
    
    def _collect_pattern_evidence(self, functions: Dict, pattern_info: Dict) -> List[str]:
        """收集模式证据"""
        evidence = []
        
        for func_name in functions.keys():
            func_lower = func_name.lower()
            for keyword in pattern_info['keywords']:
                if keyword.lower() in func_lower:
                    evidence.append(f"函数 {func_name} 包含关键字 '{keyword}'")
                    break
        
        return evidence[:5]  # 只返回前5个证据
    
    def _get_pattern_description(self, pattern_name: str) -> str:
        """获取模式描述"""
        descriptions = {
            'state_machine': '状态机模式：使用状态转换来控制程序流程',
            'observer': '观察者模式：使用回调函数实现事件通知',
            'interrupt_driven': '中断驱动模式：基于硬件中断的事件处理',
            'polling': '轮询模式：定期检查状态或条件',
            'producer_consumer': '生产者消费者模式：使用队列或缓冲区传递数据'
        }
        return descriptions.get(pattern_name, f'{pattern_name}模式')
    
    def _format_interfaces(self, interface_usage: Dict) -> str:
        """格式化接口信息"""
        if not interface_usage:
            return "无"
        
        enabled = [name for name, info in interface_usage.items() 
                  if getattr(info, 'enabled', False)]
        return ', '.join(enabled[:3])  # 只显示前3个
    
    def _infer_business_intent_fallback(self, main_code: str, context: PromptContext) -> str:
        """业务意图降级推断"""
        intents = []
        
        # 基于接口使用推断
        if context.interface_usage:
            enabled_interfaces = [name for name, info in context.interface_usage.items() 
                                if getattr(info, 'enabled', False)]
            
            if 'UART' in enabled_interfaces:
                intents.append("串口通信")
            if 'GPIO' in enabled_interfaces:
                intents.append("GPIO控制")
            if 'ADC' in enabled_interfaces:
                intents.append("模拟信号采集")
            if 'TIMER' in enabled_interfaces:
                intents.append("定时控制")
        
        # 基于代码内容推断
        if 'while' in main_code:
            intents.append("循环控制")
        if 'delay' in main_code.lower() or 'wait' in main_code.lower():
            intents.append("时序控制")
        
        if intents:
            return f"这是一个嵌入式控制项目，主要功能包括：{', '.join(intents)}"
        else:
            return "这是一个标准的嵌入式系统项目，具体业务逻辑需要进一步分析"

    def _trace_control_flow(self, func_name: str, call_graph: Dict, visited: Set, depth: int) -> str:
        """追踪控制流"""
        if depth > 3 or func_name in visited:  # 限制深度和避免循环
            return f"{func_name}..."

        visited.add(func_name)
        flow = func_name

        if func_name in call_graph and call_graph[func_name]:
            callees = list(call_graph[func_name])[:2]  # 只追踪前2个调用
            sub_flows = []
            for callee in callees:
                sub_flow = self._trace_control_flow(callee, call_graph, visited.copy(), depth + 1)
                sub_flows.append(sub_flow)

            if sub_flows:
                flow += f" -> [{', '.join(sub_flows)}]"

        return flow

    def _find_interrupt_handlers(self, functions: Dict) -> List[str]:
        """查找中断处理函数"""
        handlers = []
        for func_name in functions.keys():
            func_lower = func_name.lower()
            if any(keyword in func_lower for keyword in ['irq', 'handler', 'isr', 'interrupt']):
                handlers.append(func_name)
        return handlers

    def _calculate_call_depth(self, func_name: str, call_graph: Dict, visited: Set) -> int:
        """计算调用深度"""
        if func_name in visited or func_name not in call_graph:
            return 0

        visited.add(func_name)
        max_depth = 0

        for callee in call_graph[func_name]:
            depth = 1 + self._calculate_call_depth(callee, call_graph, visited.copy())
            max_depth = max(max_depth, depth)

        return max_depth

    def _calculate_function_complexity(self, func_info) -> str:
        """计算函数复杂度"""
        # 基于函数签名长度和调用数量估算复杂度
        signature_length = len(getattr(func_info, 'signature', ''))
        call_count = len(getattr(func_info, 'calls', set()))

        if signature_length > 100 or call_count > 10:
            return "high"
        elif signature_length > 50 or call_count > 5:
            return "medium"
        else:
            return "low"

    def _analyze_coupling(self, functions: Dict, call_relations: List) -> Dict[str, float]:
        """分析耦合度"""
        coupling_scores = {}

        for func_name in functions.keys():
            # 计算该函数的入度和出度
            in_degree = sum(1 for relation in call_relations if relation.callee == func_name)
            out_degree = sum(1 for relation in call_relations if relation.caller == func_name)

            # 耦合度 = (入度 + 出度) / 总函数数
            total_functions = len(functions)
            coupling = (in_degree + out_degree) / total_functions if total_functions > 0 else 0
            coupling_scores[func_name] = coupling

        return coupling_scores

    def _analyze_cohesion(self, functions: Dict) -> Dict[str, float]:
        """分析内聚性"""
        cohesion_scores = {}

        # 基于函数名的相似性分析内聚性
        for func_name in functions.keys():
            # 简化的内聚性计算：基于函数名的一致性
            name_parts = func_name.lower().split('_')

            # 计算与其他函数名的相似度
            similarity_sum = 0
            for other_func in functions.keys():
                if other_func != func_name:
                    other_parts = other_func.lower().split('_')
                    common_parts = set(name_parts) & set(other_parts)
                    similarity = len(common_parts) / max(len(name_parts), len(other_parts))
                    similarity_sum += similarity

            cohesion = similarity_sum / (len(functions) - 1) if len(functions) > 1 else 0
            cohesion_scores[func_name] = cohesion

        return cohesion_scores

    def _analyze_naming_quality(self, functions: Dict) -> Dict[str, float]:
        """分析命名质量"""
        naming_scores = {}

        for func_name in functions.keys():
            score = 1.0  # 基础分数

            # 检查命名约定
            if func_name.islower():
                score += 0.2  # 小写命名

            if '_' in func_name:
                score += 0.2  # 使用下划线分隔

            # 检查长度
            if 5 <= len(func_name) <= 20:
                score += 0.2  # 合适的长度
            elif len(func_name) < 3:
                score -= 0.3  # 太短
            elif len(func_name) > 30:
                score -= 0.2  # 太长

            # 检查是否包含动词
            verbs = ['init', 'set', 'get', 'start', 'stop', 'send', 'receive', 'process', 'handle']
            if any(verb in func_name.lower() for verb in verbs):
                score += 0.3  # 包含动词

            # 检查缩写
            if len([part for part in func_name.split('_') if len(part) <= 2]) > 1:
                score -= 0.2  # 过多缩写

            naming_scores[func_name] = max(0.0, min(2.0, score))

        return naming_scores

    def _calculate_overall_quality_score(self, quality_metrics: Dict) -> float:
        """计算总体质量评分"""
        scores = []

        # 复杂度评分
        complexity_scores = quality_metrics.get('function_complexity', {})
        if complexity_scores:
            low_count = sum(1 for score in complexity_scores.values() if score == 'low')
            complexity_score = (low_count / len(complexity_scores)) * 100
            scores.append(complexity_score)

        # 耦合度评分（低耦合更好）
        coupling_scores = quality_metrics.get('coupling_analysis', {})
        if coupling_scores:
            avg_coupling = sum(coupling_scores.values()) / len(coupling_scores)
            coupling_score = max(0, 100 - avg_coupling * 100)
            scores.append(coupling_score)

        # 内聚性评分
        cohesion_scores = quality_metrics.get('cohesion_analysis', {})
        if cohesion_scores:
            avg_cohesion = sum(cohesion_scores.values()) / len(cohesion_scores)
            cohesion_score = avg_cohesion * 100
            scores.append(cohesion_score)

        # 命名质量评分
        naming_scores = quality_metrics.get('naming_quality', {})
        if naming_scores:
            avg_naming = sum(naming_scores.values()) / len(naming_scores)
            naming_score = (avg_naming / 2.0) * 100  # 标准化到100分
            scores.append(naming_score)

        return sum(scores) / len(scores) if scores else 0.0

    def get_analysis_summary(self, result: SemanticAnalysisResult) -> Dict[str, any]:
        """获取分析摘要"""
        return {
            'business_logic_count': len(result.business_logics),
            'detected_patterns': [p.pattern_type for p in result.architectural_patterns],
            'top_pattern': result.architectural_patterns[0].pattern_type if result.architectural_patterns else None,
            'maintainability_score': result.maintainability_score,
            'performance_bottleneck_count': len(result.performance_bottlenecks),
            'security_concern_count': len(result.security_concerns),
            'complexity_metrics': result.complexity_metrics
        }

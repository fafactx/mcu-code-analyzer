"""
代码总结器 - 基于LLM的智能代码理解和总结
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from utils.logger import logger, log_decorator, performance_monitor
from utils.file_utils import FileUtils
from intelligence.llm_manager import llm_manager, LLMResponse
from intelligence.prompt_generator import PromptGenerator, PromptContext


@dataclass
class CodeSummary:
    """代码总结数据类"""
    project_overview: str = ""
    main_functionality: str = ""
    key_algorithms: List[str] = None
    data_structures: List[str] = None
    control_flow: str = ""
    performance_characteristics: str = ""
    dependencies: List[str] = None
    complexity_analysis: str = ""
    optimization_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.key_algorithms is None:
            self.key_algorithms = []
        if self.data_structures is None:
            self.data_structures = []
        if self.dependencies is None:
            self.dependencies = []
        if self.optimization_suggestions is None:
            self.optimization_suggestions = []


@dataclass
class FunctionSummary:
    """函数总结数据类"""
    name: str
    purpose: str = ""
    parameters: str = ""
    return_value: str = ""
    complexity: str = ""
    dependencies: List[str] = None
    side_effects: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.side_effects is None:
            self.side_effects = []


class CodeSummarizer:
    """代码总结器"""

    def __init__(self):
        self.prompt_generator = PromptGenerator()
        self.function_summaries: Dict[str, FunctionSummary] = {}
        self.project_summary: Optional[CodeSummary] = None
        self.llm_log_callback = None  # LLM交互日志回调

    def set_llm_log_callback(self, callback):
        """设置LLM交互日志回调"""
        self.llm_log_callback = callback

    def _log_llm_interaction(self, interaction_type: str, content: str):
        """记录LLM交互"""
        if self.llm_log_callback:
            self.llm_log_callback(interaction_type, content)

    @log_decorator
    @performance_monitor
    def summarize_project(self, project_path: Path, analysis_result: Dict,
                         chip_info: Dict = None) -> CodeSummary:
        """总结整个项目"""
        logger.info(f"开始总结项目: {project_path}")
        
        # 准备上下文
        context = self._prepare_project_context(project_path, analysis_result, chip_info)
        
        # 生成项目分析提示词
        prompt = self.prompt_generator.generate_project_analysis_prompt(context)

        # 记录发送给LLM的提示词
        self._log_llm_interaction("prompt", prompt)
        self._log_llm_interaction("status", "正在调用LLM进行项目分析...")

        # 调用LLM进行分析
        response = llm_manager.generate(prompt)

        if response.success:
            # 记录LLM回复
            self._log_llm_interaction("response", response.content)
            self._log_llm_interaction("status", "LLM分析成功，正在解析结果...")

            # 解析LLM响应
            summary = self._parse_project_analysis_response(response.content)
            self.project_summary = summary
            logger.info("项目总结完成")
            self._log_llm_interaction("status", "项目总结完成")
            return summary
        else:
            # 记录错误
            error_msg = f"LLM调用失败: {response.error_message}"
            self._log_llm_interaction("error", error_msg)
            logger.error(f"项目总结失败: {response.error_message}")
            return self._create_fallback_summary(analysis_result)
    
    @log_decorator
    def summarize_main_function(self, main_code: str, context: PromptContext) -> str:
        """总结main函数的主要逻辑"""
        logger.info("总结main函数逻辑")
        
        prompt = f"""请分析以下main函数的主要业务逻辑和执行流程：

```c
{main_code}
```

项目上下文：
- 芯片：{context.chip_info.get('device', '未知') if context.chip_info else '未知'}
- 使用的接口：{self._format_interfaces_brief(context.interface_usage)}

请简洁地描述：
1. 主要的初始化步骤
2. 核心业务逻辑
3. 主循环或事件处理
4. 关键的控制流程

用中文回答，控制在200字以内。"""

        # 记录main函数分析提示词
        self._log_llm_interaction("prompt", prompt)
        self._log_llm_interaction("status", "正在分析main函数...")

        response = llm_manager.generate(prompt)

        if response.success:
            # 记录LLM回复
            self._log_llm_interaction("response", response.content)
            self._log_llm_interaction("status", "main函数分析完成")
            return response.content.strip()
        else:
            # 记录错误
            error_msg = f"main函数分析失败: {response.error_message}"
            self._log_llm_interaction("error", error_msg)
            logger.warning(f"main函数总结失败: {response.error_message}")
            return self._analyze_main_function_fallback(main_code)
    
    @log_decorator
    def summarize_function(self, func_name: str, func_code: str, 
                          context: PromptContext = None) -> FunctionSummary:
        """总结单个函数"""
        logger.debug(f"总结函数: {func_name}")
        
        prompt = f"""请分析以下C函数的功能和特性：

```c
{func_code}
```

请分析：
1. 函数的主要用途
2. 参数说明
3. 返回值说明
4. 算法复杂度
5. 可能的副作用

以JSON格式返回：
{{
    "purpose": "函数用途",
    "parameters": "参数说明",
    "return_value": "返回值说明",
    "complexity": "时间/空间复杂度",
    "side_effects": ["副作用1", "副作用2"]
}}"""
        
        response = llm_manager.generate(prompt, temperature=0.1)
        
        if response.success:
            try:
                import json
                result = json.loads(response.content)
                summary = FunctionSummary(
                    name=func_name,
                    purpose=result.get('purpose', ''),
                    parameters=result.get('parameters', ''),
                    return_value=result.get('return_value', ''),
                    complexity=result.get('complexity', ''),
                    side_effects=result.get('side_effects', [])
                )
                self.function_summaries[func_name] = summary
                return summary
            except json.JSONDecodeError:
                logger.warning(f"函数{func_name}总结响应解析失败")
        
        # 降级处理
        return self._analyze_function_fallback(func_name, func_code)
    
    @log_decorator
    def analyze_code_patterns(self, source_files: List[Path]) -> Dict[str, List[str]]:
        """分析代码模式和设计模式"""
        logger.info("分析代码模式")
        
        patterns = {
            'state_machines': [],
            'interrupt_handlers': [],
            'callback_functions': [],
            'data_structures': [],
            'algorithms': []
        }
        
        for file_path in source_files[:5]:  # 只分析前5个文件
            content = FileUtils.read_file_safe(file_path)
            if not content:
                continue
            
            # 检测状态机模式
            if self._detect_state_machine(content):
                patterns['state_machines'].append(str(file_path.name))
            
            # 检测中断处理函数
            interrupt_handlers = self._detect_interrupt_handlers(content)
            patterns['interrupt_handlers'].extend(interrupt_handlers)
            
            # 检测回调函数
            callbacks = self._detect_callback_functions(content)
            patterns['callback_functions'].extend(callbacks)
            
            # 检测数据结构
            data_structs = self._detect_data_structures(content)
            patterns['data_structures'].extend(data_structs)
        
        return patterns
    
    def _prepare_project_context(self, project_path: Path, analysis_result: Dict,
                                chip_info: Dict) -> PromptContext:
        """准备项目上下文"""
        # 获取主要函数列表
        main_functions = []
        if 'main_reachable_functions' in analysis_result:
            main_functions = list(analysis_result['main_reachable_functions'])[:20]

        # 获取接口使用情况
        interface_usage = analysis_result.get('interface_usage', {})

        # 获取流程图代码
        flowchart_code = analysis_result.get('mermaid_code', '无流程图数据')

        context = PromptContext(
            project_name=project_path.name,
            chip_info=chip_info,
            interface_usage=interface_usage,
            main_functions=main_functions
        )

        # 添加流程图代码到上下文
        context.flowchart_code = flowchart_code

        return context
    
    def _parse_project_analysis_response(self, response_content: str) -> CodeSummary:
        """解析项目分析响应"""
        try:
            import json
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                return CodeSummary(
                    project_overview=result.get('project_type', ''),
                    main_functionality=result.get('application_domain', ''),
                    complexity_analysis=result.get('complexity_level', ''),
                    optimization_suggestions=result.get('optimization_suggestions', []),
                    dependencies=result.get('main_modules', [])
                )
        except (json.JSONDecodeError, AttributeError):
            logger.warning("项目分析响应解析失败，使用文本解析")
        
        # 文本解析降级
        return CodeSummary(
            project_overview="基于LLM分析的STM32项目",
            main_functionality=response_content[:200] + "..." if len(response_content) > 200 else response_content
        )
    
    def _create_fallback_summary(self, analysis_result: Dict) -> CodeSummary:
        """创建降级总结"""
        logger.info("创建降级项目总结")
        
        # 基于分析结果创建基础总结
        function_stats = analysis_result.get('function_stats', {})
        call_stats = analysis_result.get('call_stats', {})
        
        overview = f"STM32嵌入式项目，包含{function_stats.get('total_functions', 0)}个函数"
        
        complexity = "medium"
        if function_stats.get('total_functions', 0) > 100:
            complexity = "high"
        elif function_stats.get('total_functions', 0) < 20:
            complexity = "low"
        
        return CodeSummary(
            project_overview=overview,
            main_functionality="嵌入式控制系统",
            complexity_analysis=complexity,
            dependencies=["STM32 HAL库", "标准C库"]
        )
    
    def _format_interfaces_brief(self, interface_usage: Dict) -> str:
        """简要格式化接口信息"""
        if not interface_usage:
            return "无"
        
        enabled = [name for name, info in interface_usage.items() 
                  if getattr(info, 'enabled', False)]
        return ', '.join(enabled[:5])  # 只显示前5个
    
    def _analyze_main_function_fallback(self, main_code: str) -> str:
        """main函数降级分析"""
        analysis = []
        
        # 检测初始化函数
        if 'HAL_Init' in main_code or 'SystemInit' in main_code:
            analysis.append("系统初始化")
        
        # 检测时钟配置
        if 'SystemClock' in main_code or 'RCC_' in main_code:
            analysis.append("时钟配置")
        
        # 检测外设初始化
        if 'MX_' in main_code or '_Init' in main_code:
            analysis.append("外设初始化")
        
        # 检测主循环
        if 'while' in main_code:
            analysis.append("主循环处理")
        
        if analysis:
            return "主要功能包括：" + "、".join(analysis)
        else:
            return "标准的嵌入式主函数，负责系统初始化和主循环控制"
    
    def _analyze_function_fallback(self, func_name: str, func_code: str) -> FunctionSummary:
        """函数降级分析"""
        purpose = "功能待分析"
        
        # 基于函数名推断用途
        if 'init' in func_name.lower():
            purpose = "初始化函数"
        elif 'config' in func_name.lower():
            purpose = "配置函数"
        elif 'handler' in func_name.lower() or 'irq' in func_name.lower():
            purpose = "中断处理函数"
        elif 'callback' in func_name.lower():
            purpose = "回调函数"
        
        return FunctionSummary(
            name=func_name,
            purpose=purpose,
            complexity="O(1)" if len(func_code) < 100 else "O(n)"
        )
    
    def _detect_state_machine(self, content: str) -> bool:
        """检测状态机模式"""
        state_indicators = ['state', 'STATE', 'switch', 'case', 'enum.*state']
        return any(re.search(indicator, content, re.IGNORECASE) for indicator in state_indicators)
    
    def _detect_interrupt_handlers(self, content: str) -> List[str]:
        """检测中断处理函数"""
        pattern = r'void\s+(\w*(?:IRQ|Handler|ISR)\w*)\s*\('
        matches = re.findall(pattern, content, re.IGNORECASE)
        return matches
    
    def _detect_callback_functions(self, content: str) -> List[str]:
        """检测回调函数"""
        pattern = r'void\s+(\w*(?:Callback|callback)\w*)\s*\('
        matches = re.findall(pattern, content, re.IGNORECASE)
        return matches
    
    def _detect_data_structures(self, content: str) -> List[str]:
        """检测数据结构"""
        patterns = [
            r'typedef\s+struct\s+(\w+)',
            r'struct\s+(\w+)\s*\{',
            r'typedef\s+enum\s+(\w+)',
            r'enum\s+(\w+)\s*\{'
        ]
        
        structures = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            structures.extend(matches)
        
        return structures
    
    def get_project_summary(self) -> Optional[CodeSummary]:
        """获取项目总结"""
        return self.project_summary
    
    def get_function_summary(self, func_name: str) -> Optional[FunctionSummary]:
        """获取函数总结"""
        return self.function_summaries.get(func_name)
    
    def get_all_function_summaries(self) -> Dict[str, FunctionSummary]:
        """获取所有函数总结"""
        return self.function_summaries.copy()

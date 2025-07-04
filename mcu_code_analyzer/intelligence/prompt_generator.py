"""
智能提示词生成器 - 基于项目分析结果生成上下文相关的LLM提示词
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from pathlib import Path
from utils.logger import logger, log_decorator
from utils.config import config


@dataclass
class PromptContext:
    """提示词上下文数据类"""
    project_name: str = ""
    chip_info: Dict = None
    interface_usage: Dict = None
    main_functions: List[str] = None
    code_summary: str = ""
    target_platform: str = ""
    conversion_type: str = ""
    user_requirements: str = ""


class PromptTemplate:
    """提示词模板类"""
    
    @staticmethod
    def project_analysis_template() -> str:
        """项目分析提示词模板"""
        return """{system_prompt}

请分析以下MCU项目的具体功能和实现逻辑：

## 项目基本信息
- 项目名称：{project_name}
- 芯片型号：{chip_model}
- 芯片系列：{chip_series}
- CPU内核：{cpu_core}
- Flash大小：{flash_size}
- RAM大小：{ram_size}

## 使用的硬件接口
{interface_list}

## 代码执行流程图
以下是从main函数开始的代码执行流程：
```mermaid
{flowchart_code}
```

## 主要函数列表
{main_functions}

## 分析要求
请基于上述流程图和项目信息，详细分析：

1. **项目具体功能**：这个项目到底做了什么？实现了什么功能？
2. **执行逻辑分析**：根据流程图，分析代码的执行逻辑和控制流程
3. **硬件交互**：项目如何与硬件外设交互？使用了哪些接口？
4. **应用场景**：这个项目可能用于什么应用场景？
5. **技术特点**：项目有什么技术特点或亮点？

请用中文详细回答，重点说明项目的具体功能和实现方式。"""

    @staticmethod
    def code_conversion_template() -> str:
        """代码转换提示词模板"""
        return """你是一位专业的嵌入式代码转换专家，擅长STM32到NXP平台的代码迁移。

源平台信息：
- 芯片：{source_chip}
- 系列：{source_series}
- 使用的库：{source_libraries}

目标平台信息：
- 芯片：{target_chip}
- 系列：{target_series}
- SDK：{target_sdk}

需要转换的代码：
```c
{source_code}
```

接口映射参考：
{interface_mapping}

转换要求：
1. 保持完全相同的功能逻辑
2. 使用目标平台的最佳实践
3. 优化性能和可读性
4. 添加必要的错误处理
5. 包含详细的注释说明

请返回转换后的代码，格式如下：
```c
// 转换后的代码
{converted_code}
```

转换说明：
- 主要变更：{main_changes}
- 注意事项：{notes}
- 测试建议：{test_suggestions}"""

    @staticmethod
    def interface_mapping_template() -> str:
        """接口映射提示词模板"""
        return """你是一位嵌入式接口映射专家，请为以下STM32接口找到对应的NXP SDK接口。

STM32接口使用情况：
{stm32_interfaces}

NXP目标平台：{target_platform}

请为每个STM32接口提供对应的NXP接口映射：

格式要求：
```json
{{
    "interface_mappings": {{
        "STM32_Function": {{
            "nxp_equivalent": "NXP_Function",
            "parameters_mapping": {{"param1": "new_param1"}},
            "usage_notes": "使用说明",
            "example": "示例代码"
        }}
    }},
    "header_mappings": {{
        "stm32_header.h": ["nxp_header1.h", "nxp_header2.h"]
    }},
    "initialization_changes": "初始化代码变更说明",
    "compatibility_notes": "兼容性注意事项"
}}
```"""

    @staticmethod
    def documentation_template() -> str:
        """文档生成提示词模板"""
        return """你是一位技术文档专家，请为以下STM32项目生成详细的技术文档。

项目概况：
- 名称：{project_name}
- 芯片：{chip_info}
- 功能：{project_functions}

代码分析结果：
{code_analysis}

接口使用情况：
{interface_usage}

请生成以下文档内容：

# {project_name} 技术文档

## 1. 项目概述
- 项目简介
- 硬件平台
- 主要功能

## 2. 系统架构
- 整体架构图
- 模块划分
- 数据流图

## 3. 硬件接口
- 使用的外设
- 引脚配置
- 时序要求

## 4. 软件设计
- 主要函数说明
- 调用关系
- 状态机设计

## 5. 移植指南
- 平台差异
- 移植步骤
- 注意事项

请使用Markdown格式，内容要详细且专业。"""


class PromptGenerator:
    """智能提示词生成器"""
    
    def __init__(self):
        self.templates = PromptTemplate()
        self.context_cache = {}
    
    @log_decorator
    def generate_project_analysis_prompt(self, context: PromptContext) -> str:
        """生成项目分析提示词"""
        logger.info("生成项目分析提示词")
        
        # 格式化芯片信息
        chip_info = context.chip_info or {}
        if hasattr(chip_info, 'device_name'):
            # ChipInfo对象
            chip_model = getattr(chip_info, 'device_name', '未知')
            chip_series = getattr(chip_info, 'series', '未知')
            cpu_core = getattr(chip_info, 'core', '未知')
            flash_size = getattr(chip_info, 'flash_size', '未知')
            ram_size = getattr(chip_info, 'ram_size', '未知')
        else:
            # 字典格式
            chip_model = chip_info.get('device', '未知') if isinstance(chip_info, dict) else '未知'
            chip_series = chip_info.get('series', '未知') if isinstance(chip_info, dict) else '未知'
            cpu_core = chip_info.get('core', '未知') if isinstance(chip_info, dict) else '未知'
            flash_size = chip_info.get('flash_size', '未知') if isinstance(chip_info, dict) else '未知'
            ram_size = chip_info.get('ram_size', '未知') if isinstance(chip_info, dict) else '未知'
        
        # 格式化接口列表
        interface_list = self._format_interface_list(context.interface_usage)
        
        # 格式化主要函数
        main_functions = self._format_function_list(context.main_functions)
        
        # 获取系统提示词
        try:
            from config.config_manager import config
            system_prompt = config.get('llm.system_prompt', '你是一位资深的嵌入式系统工程师。')
        except ImportError:
            # 降级处理
            system_prompt = '你是一位资深的嵌入式系统工程师，专门分析MCU项目的功能和实现。请基于提供的代码流程图和项目信息，详细分析项目的具体功能和实现逻辑。'

        # 获取流程图代码
        flowchart_code = getattr(context, 'flowchart_code', '无流程图数据')

        prompt = self.templates.project_analysis_template().format(
            system_prompt=system_prompt,
            project_name=context.project_name,
            chip_model=chip_model,
            chip_series=chip_series,
            cpu_core=cpu_core,
            flash_size=flash_size,
            ram_size=ram_size,
            interface_list=interface_list,
            main_functions=main_functions,
            flowchart_code=flowchart_code
        )
        
        return prompt
    
    @log_decorator
    def generate_code_conversion_prompt(self, source_code: str, context: PromptContext) -> str:
        """生成代码转换提示词"""
        logger.info("生成代码转换提示词")
        
        # 获取源平台信息
        chip_info = context.chip_info or {}
        source_chip = chip_info.get('device', 'STM32')
        source_series = chip_info.get('series', 'STM32系列')
        
        # 分析使用的库
        source_libraries = self._analyze_source_libraries(context.interface_usage)
        
        # 生成接口映射
        interface_mapping = self._generate_interface_mapping(context.interface_usage)
        
        prompt = self.templates.code_conversion_template().format(
            source_chip=source_chip,
            source_series=source_series,
            source_libraries=source_libraries,
            target_chip=context.target_platform or "NXP MCXA153",
            target_series="NXP MCXA系列",
            target_sdk="NXP MCUXpresso SDK",
            source_code=source_code,
            interface_mapping=interface_mapping
        )
        
        return prompt
    
    @log_decorator
    def generate_interface_mapping_prompt(self, context: PromptContext) -> str:
        """生成接口映射提示词"""
        logger.info("生成接口映射提示词")
        
        # 格式化STM32接口使用情况
        stm32_interfaces = self._format_stm32_interfaces(context.interface_usage)
        
        prompt = self.templates.interface_mapping_template().format(
            stm32_interfaces=stm32_interfaces,
            target_platform=context.target_platform or "NXP MCXA系列"
        )
        
        return prompt
    
    @log_decorator
    def generate_documentation_prompt(self, context: PromptContext) -> str:
        """生成文档提示词"""
        logger.info("生成文档提示词")
        
        # 格式化项目信息
        chip_info_str = self._format_chip_info(context.chip_info)
        code_analysis_str = self._format_code_analysis(context)
        interface_usage_str = self._format_interface_usage(context.interface_usage)
        
        prompt = self.templates.documentation_template().format(
            project_name=context.project_name,
            chip_info=chip_info_str,
            project_functions=context.code_summary or "待分析",
            code_analysis=code_analysis_str,
            interface_usage=interface_usage_str
        )
        
        return prompt
    
    def generate_custom_prompt(self, template: str, context: PromptContext, **kwargs) -> str:
        """生成自定义提示词"""
        logger.info("生成自定义提示词")
        
        # 准备格式化参数
        format_params = {
            'project_name': context.project_name,
            'chip_info': self._format_chip_info(context.chip_info),
            'interface_usage': self._format_interface_usage(context.interface_usage),
            'main_functions': self._format_function_list(context.main_functions),
            'code_summary': context.code_summary,
            'target_platform': context.target_platform,
            **kwargs
        }
        
        try:
            return template.format(**format_params)
        except KeyError as e:
            logger.error(f"模板格式化失败，缺少参数: {e}")
            return template
    
    def _format_interface_list(self, interface_usage: Dict) -> str:
        """格式化接口列表"""
        if not interface_usage:
            return "无接口使用信息"
        
        enabled_interfaces = [
            (name, info) for name, info in interface_usage.items() 
            if getattr(info, 'enabled', False)
        ]
        
        if not enabled_interfaces:
            return "未检测到接口使用"
        
        lines = []
        for name, info in enabled_interfaces:
            func_count = len(getattr(info, 'functions', set()))
            description = getattr(info, 'description', name)
            lines.append(f"- {name}: {description} ({func_count}个函数)")
        
        return '\n'.join(lines)
    
    def _format_function_list(self, functions: List[str]) -> str:
        """格式化函数列表"""
        if not functions:
            return "无函数信息"
        
        # 只显示前10个函数
        display_functions = functions[:10]
        result = '\n'.join([f"- {func}" for func in display_functions])
        
        if len(functions) > 10:
            result += f"\n- ... 还有{len(functions) - 10}个函数"
        
        return result
    
    def _analyze_source_libraries(self, interface_usage: Dict) -> str:
        """分析源代码使用的库"""
        if not interface_usage:
            return "未知库"
        
        libraries = set()
        for name, info in interface_usage.items():
            if getattr(info, 'enabled', False):
                vendor = getattr(info, 'vendor', '')
                if 'STM32' in vendor:
                    libraries.add('STM32 HAL')
                elif 'ARM' in vendor:
                    libraries.add('ARM CMSIS')
        
        return ', '.join(libraries) if libraries else "标准C库"
    
    def _generate_interface_mapping(self, interface_usage: Dict) -> str:
        """生成接口映射信息"""
        if not interface_usage:
            return "无接口映射信息"
        
        mappings = []
        for name, info in interface_usage.items():
            if getattr(info, 'enabled', False):
                functions = getattr(info, 'functions', set())
                if functions:
                    sample_func = list(functions)[0]
                    mappings.append(f"{name}: {sample_func} -> 对应的NXP函数")
        
        return '\n'.join(mappings[:5])  # 只显示前5个映射
    
    def _format_stm32_interfaces(self, interface_usage: Dict) -> str:
        """格式化STM32接口信息"""
        if not interface_usage:
            return "{}"
        
        interfaces = {}
        for name, info in interface_usage.items():
            if getattr(info, 'enabled', False) and 'STM32' in getattr(info, 'vendor', ''):
                functions = list(getattr(info, 'functions', set()))[:3]  # 只取前3个函数
                interfaces[name] = {
                    'functions': functions,
                    'description': getattr(info, 'description', name)
                }
        
        import json
        return json.dumps(interfaces, ensure_ascii=False, indent=2)
    
    def _format_chip_info(self, chip_info: Dict) -> str:
        """格式化芯片信息"""
        if not chip_info:
            return "芯片信息未知"
        
        info_parts = []
        if chip_info.get('device'):
            info_parts.append(f"型号: {chip_info['device']}")
        if chip_info.get('series'):
            info_parts.append(f"系列: {chip_info['series']}")
        if chip_info.get('core'):
            info_parts.append(f"内核: {chip_info['core']}")
        
        return ', '.join(info_parts) if info_parts else "芯片信息不完整"
    
    def _format_code_analysis(self, context: PromptContext) -> str:
        """格式化代码分析结果"""
        if context.code_summary:
            return context.code_summary
        
        parts = []
        if context.main_functions:
            parts.append(f"主要函数数量: {len(context.main_functions)}")
        if context.interface_usage:
            enabled_count = sum(1 for info in context.interface_usage.values() 
                              if getattr(info, 'enabled', False))
            parts.append(f"使用的接口: {enabled_count}个")
        
        return ', '.join(parts) if parts else "代码分析结果待生成"
    
    def _format_interface_usage(self, interface_usage: Dict) -> str:
        """格式化接口使用情况"""
        return self._format_interface_list(interface_usage)
    
    def cache_context(self, key: str, context: PromptContext):
        """缓存上下文"""
        self.context_cache[key] = context
        logger.debug(f"缓存上下文: {key}")
    
    def get_cached_context(self, key: str) -> Optional[PromptContext]:
        """获取缓存的上下文"""
        return self.context_cache.get(key)

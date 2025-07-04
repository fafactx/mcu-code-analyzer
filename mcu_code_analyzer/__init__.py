"""
STM32工程分析器 v2.0
智能分析STM32项目，助力代码理解与平台迁移

Copyright (c) 2024 STM32 Analyzer Team
License: MIT
"""

__version__ = '0.1.0'
__author__ = "STM32 Analyzer Team"
__email__ = "support@stm32analyzer.com"
__description__ = "智能STM32工程分析器 - 深度代码分析与平台迁移助手"

def get_version():
    """获取版本字符串"""
    return __version__

def print_banner():
    """打印启动横幅"""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    STM32工程分析器 v{__version__}                     ║
║                                                              ║
║  🚀 智能分析STM32项目，助力代码理解与平台迁移                      ║
║                                                              ║
║  特性: 深度代码分析 | LLM智能理解 | 多厂商支持 | 现代化界面        ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

__version__ = '0.1.0'
__author__ = "AI Assistant"
__description__ = "STM32工程智能分析工具"

from core import *
from intelligence import *
from ui import *
from utils import *

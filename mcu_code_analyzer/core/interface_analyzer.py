"""
接口分析器 - 分析项目中使用的硬件接口和库函数
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from utils.logger import logger, log_decorator, performance_monitor
from utils.file_utils import FileUtils
from utils.config import config


@dataclass
class InterfaceUsage:
    """接口使用信息数据类"""
    interface_name: str
    functions: Set[str] = field(default_factory=set)
    files: Set[str] = field(default_factory=set)
    call_count: int = 0
    enabled: bool = False
    description: str = ""
    vendor: str = ""  # STM32, NXP, ARM等


@dataclass
class LibraryInfo:
    """库信息数据类"""
    name: str
    vendor: str
    version: str = ""
    header_files: Set[str] = field(default_factory=set)
    interfaces: Set[str] = field(default_factory=set)


class InterfaceAnalyzer:
    """接口分析器"""
    
    def __init__(self):
        self.interface_usage: Dict[str, InterfaceUsage] = {}
        self.library_info: Dict[str, LibraryInfo] = {}
        self.interface_patterns = self._load_interface_patterns()
        self.vendor_libraries = self._load_vendor_libraries()
    
    def _load_interface_patterns(self) -> Dict[str, Dict[str, any]]:
        """加载接口识别模式"""
        patterns = config.get_interface_patterns()
        
        # 扩展模式定义，添加描述和厂商信息
        extended_patterns = {}
        for interface, pattern_list in patterns.items():
            extended_patterns[interface] = {
                'patterns': pattern_list,
                'description': self._get_interface_description(interface),
                'vendor': self._get_interface_vendor(interface, pattern_list)
            }
        
        return extended_patterns
    
    def _get_interface_description(self, interface: str) -> str:
        """获取接口描述"""
        descriptions = {
            'GPIO': '通用输入输出接口',
            'UART': '串行通信接口',
            'SPI': 'SPI串行外设接口',
            'I2C': 'I2C总线接口',
            'TIMER': '定时器接口',
            'ADC': '模数转换器接口',
            'DMA': '直接内存访问接口',
            'CLOCK': '时钟管理接口',
            'NVIC': '嵌套向量中断控制器',
            'SYSTICK': '系统滴答定时器',
            'CAN': 'CAN总线接口',
            'USB': 'USB接口',
            'ETH': '以太网接口',
            'FLASH': 'Flash存储器接口',
            'RTC': '实时时钟接口',
            'WATCHDOG': '看门狗定时器接口'
        }
        return descriptions.get(interface, f'{interface}接口')
    
    def _get_interface_vendor(self, interface: str, patterns: List[str]) -> str:
        """根据模式推断接口厂商"""
        if any('HAL_' in p for p in patterns):
            return 'STM32'
        elif any(p.startswith(('LP', 'FLEX', 'MCX')) for p in patterns):
            return 'NXP'
        elif any('Chip_' in p for p in patterns):
            return 'NXP LPC'
        elif any(p in ['NVIC_', 'SysTick_'] for p in patterns):
            return 'ARM CMSIS'
        else:
            return 'Generic'
    
    def _load_vendor_libraries(self) -> Dict[str, Dict[str, any]]:
        """加载厂商库信息"""
        return {
            'STM32_HAL': {
                'vendor': 'STMicroelectronics',
                'name': 'STM32 HAL Library',
                'header_pattern': r'stm32[a-z0-9]+_hal.*\.h',
                'function_prefix': ['HAL_', '__HAL_'],
                'interfaces': ['GPIO', 'UART', 'SPI', 'I2C', 'TIMER', 'ADC', 'DMA', 'CLOCK']
            },
            'STM32_LL': {
                'vendor': 'STMicroelectronics', 
                'name': 'STM32 Low Layer Library',
                'header_pattern': r'stm32[a-z0-9]+_ll.*\.h',
                'function_prefix': ['LL_'],
                'interfaces': ['GPIO', 'UART', 'SPI', 'I2C', 'TIMER', 'ADC', 'DMA']
            },
            'NXP_SDK': {
                'vendor': 'NXP',
                'name': 'NXP MCUXpresso SDK',
                'header_pattern': r'fsl_.*\.h',
                'function_prefix': ['GPIO_', 'LPUART_', 'LPSPI_', 'LPI2C_', 'CTIMER_'],
                'interfaces': ['GPIO', 'UART', 'SPI', 'I2C', 'TIMER', 'ADC', 'DMA', 'CLOCK']
            },
            'ARM_CMSIS': {
                'vendor': 'ARM',
                'name': 'ARM CMSIS',
                'header_pattern': r'core_cm[0-9]+\.h|cmsis_.*\.h',
                'function_prefix': ['NVIC_', 'SysTick_', '__'],
                'interfaces': ['NVIC', 'SYSTICK']
            }
        }
    
    @log_decorator
    @performance_monitor
    def analyze_interfaces(self, project_path: Path, main_reachable_functions: Set[str] = None,
                          call_relations: List = None) -> Dict[str, InterfaceUsage]:
        """分析项目中的接口使用情况"""
        logger.info(f"开始分析接口使用情况: {project_path}")
        
        # 初始化接口使用统计
        for interface, info in self.interface_patterns.items():
            self.interface_usage[interface] = InterfaceUsage(
                interface_name=interface,
                description=info['description'],
                vendor=info['vendor']
            )
        
        # 获取源文件
        c_files = FileUtils.find_files(project_path)
        logger.info(f"分析 {len(c_files)} 个源文件")
        
        # 分析头文件包含
        self._analyze_header_includes(c_files)
        
        # 分析函数调用
        if call_relations and main_reachable_functions:
            self._analyze_function_calls(call_relations, main_reachable_functions)
        else:
            self._analyze_source_code(c_files)
        
        # 识别使用的库
        self._identify_libraries(c_files)
        
        # 生成统计信息
        enabled_interfaces = [name for name, usage in self.interface_usage.items() if usage.enabled]
        logger.info(f"检测到使用的接口: {', '.join(enabled_interfaces) if enabled_interfaces else '无'}")
        
        return self.interface_usage
    
    def _analyze_header_includes(self, c_files: List[Path]):
        """分析头文件包含情况"""
        logger.info("分析头文件包含...")
        
        all_includes = set()
        for file_path in c_files:
            content = FileUtils.read_file_safe(file_path)
            if content:
                includes = FileUtils.extract_includes(content)
                all_includes.update(includes)
        
        logger.info(f"找到 {len(all_includes)} 个头文件包含")
        
        # 根据头文件推断使用的库和接口
        for include_file in all_includes:
            self._analyze_header_file(include_file)
    
    def _analyze_header_file(self, header_file: str):
        """分析单个头文件"""
        header_lower = header_file.lower()
        
        # 检查是否匹配已知的库模式
        for lib_name, lib_info in self.vendor_libraries.items():
            if re.match(lib_info['header_pattern'], header_lower):
                if lib_name not in self.library_info:
                    self.library_info[lib_name] = LibraryInfo(
                        name=lib_info['name'],
                        vendor=lib_info['vendor']
                    )
                
                self.library_info[lib_name].header_files.add(header_file)
                self.library_info[lib_name].interfaces.update(lib_info['interfaces'])
                
                # 标记相关接口为可能使用
                for interface in lib_info['interfaces']:
                    if interface in self.interface_usage:
                        self.interface_usage[interface].files.add(header_file)
        
        # 基于头文件名推断接口类型
        interface_hints = {
            'gpio': 'GPIO',
            'uart': 'UART',
            'usart': 'UART', 
            'spi': 'SPI',
            'i2c': 'I2C',
            'tim': 'TIMER',
            'timer': 'TIMER',
            'adc': 'ADC',
            'dma': 'DMA',
            'rcc': 'CLOCK',
            'clock': 'CLOCK',
            'can': 'CAN',
            'usb': 'USB',
            'eth': 'ETH',
            'flash': 'FLASH',
            'rtc': 'RTC',
            'iwdg': 'WATCHDOG',
            'wwdg': 'WATCHDOG'
        }
        
        for hint, interface in interface_hints.items():
            if hint in header_lower and interface in self.interface_usage:
                self.interface_usage[interface].files.add(header_file)
    
    def _analyze_function_calls(self, call_relations: List, main_reachable_functions: Set[str]):
        """基于函数调用关系分析接口使用"""
        logger.info("基于调用关系分析接口使用...")
        
        # 只分析从main函数可达的调用
        relevant_calls = [
            relation for relation in call_relations 
            if relation.caller in main_reachable_functions
        ]
        
        logger.info(f"分析 {len(relevant_calls)} 个相关函数调用")
        
        for relation in relevant_calls:
            callee = relation.callee
            
            # 检查函数名是否匹配接口模式
            for interface, info in self.interface_patterns.items():
                for pattern in info['patterns']:
                    if pattern in callee:
                        usage = self.interface_usage[interface]
                        usage.functions.add(callee)
                        usage.files.add(relation.file_path)
                        usage.call_count += 1
                        usage.enabled = True
                        break
    
    def _analyze_source_code(self, c_files: List[Path]):
        """直接分析源代码中的接口使用"""
        logger.info("直接分析源代码...")
        
        for file_path in c_files:
            content = FileUtils.read_file_safe(file_path)
            if not content:
                continue
            
            # 查找函数调用
            for interface, info in self.interface_patterns.items():
                for pattern in info['patterns']:
                    # 使用正则表达式查找函数调用
                    call_pattern = rf'\b{re.escape(pattern)}\w*\s*\('
                    matches = re.finditer(call_pattern, content)
                    
                    for match in matches:
                        func_call = match.group(0).rstrip('(').strip()
                        usage = self.interface_usage[interface]
                        usage.functions.add(func_call)
                        usage.files.add(str(file_path))
                        usage.call_count += 1
                        usage.enabled = True
    
    def _identify_libraries(self, c_files: List[Path]):
        """识别项目使用的库"""
        logger.info("识别使用的库...")
        
        # 统计各库的使用情况
        library_scores = defaultdict(int)
        
        for lib_name, lib_info in self.vendor_libraries.items():
            if lib_name in self.library_info:
                # 基于头文件数量评分
                library_scores[lib_name] += len(self.library_info[lib_name].header_files) * 10
                
                # 基于接口使用情况评分
                for interface in self.library_info[lib_name].interfaces:
                    if interface in self.interface_usage and self.interface_usage[interface].enabled:
                        library_scores[lib_name] += self.interface_usage[interface].call_count
        
        # 记录识别结果
        for lib_name, score in library_scores.items():
            if score > 0:
                logger.info(f"识别到库: {self.vendor_libraries[lib_name]['name']} (评分: {score})")
    
    def get_interface_summary(self) -> Dict[str, any]:
        """获取接口使用摘要"""
        enabled_interfaces = {
            name: usage for name, usage in self.interface_usage.items() 
            if usage.enabled
        }
        
        summary = {
            'total_interfaces': len(self.interface_usage),
            'enabled_interfaces': len(enabled_interfaces),
            'interface_details': {},
            'library_info': self.library_info,
            'vendor_distribution': defaultdict(int)
        }
        
        # 详细接口信息
        for name, usage in enabled_interfaces.items():
            summary['interface_details'][name] = {
                'description': usage.description,
                'vendor': usage.vendor,
                'function_count': len(usage.functions),
                'file_count': len(usage.files),
                'call_count': usage.call_count,
                'functions': list(usage.functions)[:10]  # 只显示前10个函数
            }
            
            # 厂商分布统计
            summary['vendor_distribution'][usage.vendor] += 1
        
        return summary
    
    def get_vendor_interfaces(self, vendor: str) -> Dict[str, InterfaceUsage]:
        """获取指定厂商的接口"""
        return {
            name: usage for name, usage in self.interface_usage.items()
            if usage.vendor == vendor and usage.enabled
        }
    
    def is_interface_used(self, interface_name: str) -> bool:
        """检查接口是否被使用"""
        return (interface_name in self.interface_usage and 
                self.interface_usage[interface_name].enabled)
    
    def get_interface_functions(self, interface_name: str) -> Set[str]:
        """获取接口使用的函数列表"""
        if interface_name in self.interface_usage:
            return self.interface_usage[interface_name].functions
        return set()

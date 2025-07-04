"""
芯片识别器 - 支持多厂商芯片型号识别和特性分析
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from utils.logger import logger, log_decorator
from utils.file_utils import FileUtils
from utils.config import config


@dataclass
class ChipInfo:
    """芯片信息数据类"""
    device_name: str = ""
    vendor: str = ""
    series: str = ""
    family: str = ""
    core: str = ""
    frequency: str = ""
    flash_size: str = ""
    ram_size: str = ""
    package: str = ""
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []


class ChipDetector:
    """芯片识别器"""
    
    def __init__(self):
        self.chip_info = ChipInfo()
        self._vendor_patterns = self._load_vendor_patterns()
        self._series_mapping = config.get_chip_series_mapping()
    
    def _load_vendor_patterns(self) -> Dict[str, Dict[str, str]]:
        """加载厂商识别模式"""
        return {
            'STMicroelectronics': {
                'patterns': [r'^STM32[A-Z]\d+', r'^STM8[A-Z]\d+'],
                'series_prefix': 'STM32',
                'core_mapping': {
                    'STM32F0': 'Cortex-M0',
                    'STM32F1': 'Cortex-M3',
                    'STM32F2': 'Cortex-M3',
                    'STM32F3': 'Cortex-M4',
                    'STM32F4': 'Cortex-M4',
                    'STM32F7': 'Cortex-M7',
                    'STM32H7': 'Cortex-M7',
                    'STM32L0': 'Cortex-M0+',
                    'STM32L1': 'Cortex-M3',
                    'STM32L4': 'Cortex-M4',
                    'STM32L5': 'Cortex-M33',
                    'STM32G0': 'Cortex-M0+',
                    'STM32G4': 'Cortex-M4',
                    'STM32WB': 'Cortex-M4',
                    'STM32WL': 'Cortex-M4'
                }
            },
            'NXP': {
                'patterns': [r'^MCX[A-Z]\d+', r'^LPC\d+', r'^MK\d+', r'^KINETIS'],
                'series_prefix': 'MCX',
                'core_mapping': {
                    'MCXA': 'Cortex-M33',
                    'MCXN': 'Cortex-M33',
                    'LPC11': 'Cortex-M0',
                    'LPC13': 'Cortex-M3',
                    'LPC15': 'Cortex-M3',
                    'LPC17': 'Cortex-M3',
                    'LPC18': 'Cortex-M3',
                    'LPC40': 'Cortex-M4',
                    'LPC43': 'Cortex-M4',
                    'LPC54': 'Cortex-M4',
                    'LPC55': 'Cortex-M33'
                }
            },
            'Microchip': {
                'patterns': [r'^PIC\d+', r'^ATSAM[A-Z]\d+', r'^ATMEGA\d+'],
                'series_prefix': 'PIC',
                'core_mapping': {
                    'SAMD': 'Cortex-M0+',
                    'SAME': 'Cortex-M4',
                    'SAMV': 'Cortex-M7'
                }
            },
            'Texas Instruments': {
                'patterns': [r'^MSP\d+', r'^TM4C\d+', r'^CC\d+'],
                'series_prefix': 'MSP',
                'core_mapping': {
                    'MSP430': 'MSP430',
                    'TM4C': 'Cortex-M4',
                    'CC13': 'Cortex-M3',
                    'CC26': 'Cortex-M3'
                }
            }
        }
    
    @log_decorator
    def detect_from_project_file(self, project_path: Path) -> ChipInfo:
        """从项目文件中检测芯片信息"""
        from localization import loc
        logger.info(f"{loc.get_text('detecting_chip_info')}: {project_path}")
        
        # 查找项目文件
        project_files = FileUtils.find_project_files(project_path)
        
        # 优先处理Keil项目文件
        if project_files['keil']:
            for keil_file in project_files['keil']:
                chip_info = self._parse_keil_project(keil_file)
                if chip_info.device_name:
                    logger.info(f"{loc.get_text('detected_chip_from_keil', chip_info.device_name)}")
                    return chip_info
        
        # 处理其他项目文件
        for project_type, files in project_files.items():
            if files and project_type != 'keil':
                chip_info = self._parse_other_project(files[0], project_type)
                if chip_info.device_name:
                    logger.info(f"Detected chip from {project_type} project file: {chip_info.device_name}")
                    return chip_info
        
        # 如果没有找到项目文件，尝试从源代码中推断
        chip_info = self._detect_from_source_code(project_path)
        if chip_info.device_name:
            logger.info(f"Inferred chip from source code: {chip_info.device_name}")
            return chip_info
        
        logger.warning("Failed to detect chip information")
        return ChipInfo()
    
    def _parse_keil_project(self, project_file: Path) -> ChipInfo:
        """解析Keil项目文件"""
        try:
            tree = ET.parse(project_file)
            root = tree.getroot()
            
            chip_info = ChipInfo()
            
            # 查找Device标签
            device_elem = root.find(".//Device")
            if device_elem is not None and device_elem.text:
                chip_info.device_name = device_elem.text.strip()
                logger.debug(f"检测到设备: {chip_info.device_name}")
            
            # 查找Vendor标签
            vendor_elem = root.find(".//Vendor")
            if vendor_elem is not None and vendor_elem.text:
                chip_info.vendor = vendor_elem.text.strip()
                logger.debug(f"检测到厂商: {chip_info.vendor}")
            
            # 查找CPU信息
            cpu_elem = root.find(".//Cpu")
            if cpu_elem is not None and cpu_elem.text:
                cpu_info = cpu_elem.text
                chip_info = self._parse_cpu_info(chip_info, cpu_info)
            
            # 查找PackID获取更多信息
            pack_elem = root.find(".//PackID")
            if pack_elem is not None and pack_elem.text:
                pack_id = pack_elem.text
                chip_info = self._parse_pack_id(chip_info, pack_id)
            
            # 补充芯片系列和特性信息
            chip_info = self._enrich_chip_info(chip_info)
            
            return chip_info
            
        except Exception as e:
            logger.error(f"解析Keil项目文件失败: {project_file}, 错误: {e}")
            return ChipInfo()
    
    def _parse_cpu_info(self, chip_info: ChipInfo, cpu_info: str) -> ChipInfo:
        """解析CPU信息字符串"""
        # 解析内存信息
        # 格式示例: "IRAM(0x20000000,0x20000) IROM(0x8000000,0x100000) CPUTYPE(\"Cortex-M4\") FPU2 CLOCK(12000000)"
        
        # 提取RAM信息
        ram_match = re.search(r'IRAM\([^,]+,\s*0x([0-9A-Fa-f]+)\)', cpu_info)
        if ram_match:
            ram_hex = ram_match.group(1)
            ram_bytes = int(ram_hex, 16)
            chip_info.ram_size = self._format_memory_size(ram_bytes)
        
        # 提取Flash信息
        flash_match = re.search(r'IROM\([^,]+,\s*0x([0-9A-Fa-f]+)\)', cpu_info)
        if flash_match:
            flash_hex = flash_match.group(1)
            flash_bytes = int(flash_hex, 16)
            chip_info.flash_size = self._format_memory_size(flash_bytes)
        
        # 提取CPU类型
        cpu_match = re.search(r'CPUTYPE\("([^"]+)"\)', cpu_info)
        if cpu_match:
            chip_info.core = cpu_match.group(1)
        
        # 提取时钟频率
        clock_match = re.search(r'CLOCK\((\d+)\)', cpu_info)
        if clock_match:
            clock_hz = int(clock_match.group(1))
            chip_info.frequency = self._format_frequency(clock_hz)
        
        # 检测FPU
        if 'FPU' in cpu_info:
            chip_info.features.append('FPU')
        
        return chip_info
    
    def _parse_pack_id(self, chip_info: ChipInfo, pack_id: str) -> ChipInfo:
        """解析Pack ID获取厂商信息"""
        # 格式示例: "STMicroelectronics.STM32F4xx_DFP.2.17.1"
        parts = pack_id.split('.')
        if len(parts) >= 2:
            vendor_part = parts[0]
            device_part = parts[1]
            
            if not chip_info.vendor:
                chip_info.vendor = vendor_part
            
            # 从device part推断系列信息
            if 'STM32' in device_part:
                series_match = re.search(r'STM32([A-Z]\d+)', device_part)
                if series_match:
                    chip_info.family = f"STM32{series_match.group(1)}"
        
        return chip_info
    
    def _parse_other_project(self, project_file: Path, project_type: str) -> ChipInfo:
        """解析其他类型的项目文件"""
        # 这里可以扩展支持CMake、Makefile等项目文件的解析
        # 目前返回空的芯片信息
        logger.debug(f"暂不支持解析 {project_type} 项目文件: {project_file}")
        return ChipInfo()
    
    def _detect_from_source_code(self, project_path: Path) -> ChipInfo:
        """从源代码中推断芯片信息"""
        c_files = FileUtils.find_files(project_path, ['.c', '.h'])
        
        device_patterns = []
        vendor_hints = []
        
        for file_path in c_files[:10]:  # 只检查前10个文件
            content = FileUtils.read_file_safe(file_path)
            if not content:
                continue
            
            # 查找设备定义
            device_matches = re.findall(r'#define\s+([A-Z0-9_]+)\s*1', content)
            for match in device_matches:
                if any(pattern in match for pattern in ['STM32', 'MCX', 'LPC', 'PIC']):
                    device_patterns.append(match)
            
            # 查找包含的头文件
            includes = FileUtils.extract_includes(content)
            for include in includes:
                if 'stm32' in include.lower():
                    vendor_hints.append('STMicroelectronics')
                elif 'nxp' in include.lower() or 'mcx' in include.lower():
                    vendor_hints.append('NXP')
        
        # 分析收集到的信息
        if device_patterns:
            # 选择最可能的设备名
            device_name = max(device_patterns, key=len)
            chip_info = ChipInfo(device_name=device_name)
            
            if vendor_hints:
                chip_info.vendor = max(set(vendor_hints), key=vendor_hints.count)
            
            return self._enrich_chip_info(chip_info)
        
        return ChipInfo()
    
    def _enrich_chip_info(self, chip_info: ChipInfo) -> ChipInfo:
        """补充芯片信息"""
        if not chip_info.device_name:
            return chip_info
        
        device_upper = chip_info.device_name.upper()
        
        # 识别厂商
        if not chip_info.vendor:
            chip_info.vendor = self._identify_vendor(device_upper)
        
        # 识别系列
        if not chip_info.series:
            chip_info.series = self._identify_series(device_upper)
        
        # 识别内核
        if not chip_info.core:
            chip_info.core = self._identify_core(device_upper)
        
        # 识别封装
        if not chip_info.package:
            chip_info.package = self._identify_package(chip_info.device_name)
        
        return chip_info
    
    def _identify_vendor(self, device_name: str) -> str:
        """识别芯片厂商"""
        for vendor, info in self._vendor_patterns.items():
            for pattern in info['patterns']:
                if re.match(pattern, device_name):
                    return vendor
        return "Unknown"
    
    def _identify_series(self, device_name: str) -> str:
        """识别芯片系列"""
        # STM32系列识别
        for prefix, series_name in self._series_mapping.items():
            if device_name.startswith(prefix.upper()):
                return series_name
        
        # NXP系列识别
        if device_name.startswith('MCXA'):
            return f'NXP MCXA系列 ({device_name})'
        elif device_name.startswith('MCXN'):
            return f'NXP MCXN系列 ({device_name})'
        elif device_name.startswith('LPC'):
            return f'NXP LPC系列 ({device_name})'
        
        return f'未知系列 ({device_name})'
    
    def _identify_core(self, device_name: str) -> str:
        """识别CPU内核"""
        for vendor, info in self._vendor_patterns.items():
            core_mapping = info.get('core_mapping', {})
            for prefix, core in core_mapping.items():
                if device_name.startswith(prefix.upper()):
                    return core
        return "Unknown"
    
    def _identify_package(self, device_name: str) -> str:
        """识别封装类型"""
        # 从设备名称后缀推断封装
        package_mapping = {
            'T6': 'LQFP-36',
            'C6': 'WLCSP-36', 
            'U6': 'UFQFPN-32',
            'K6': 'UFQFPN-32',
            'H6': 'TFBGA-64',
            'VLH': 'LQFP-64',
            'VLT': 'LQFP-100',
            'ZGT': 'LQFP-144',
            'ZIT': 'LQFP-176'
        }
        
        for suffix, package in package_mapping.items():
            if device_name.endswith(suffix):
                return package
        
        return "Unknown"
    
    @staticmethod
    def _format_memory_size(size_bytes: int) -> str:
        """格式化内存大小"""
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes // (1024 * 1024)}MB"
        elif size_bytes >= 1024:
            return f"{size_bytes // 1024}KB"
        else:
            return f"{size_bytes}B"
    
    @staticmethod
    def _format_frequency(freq_hz: int) -> str:
        """格式化频率"""
        if freq_hz >= 1000000:
            return f"{freq_hz // 1000000}MHz"
        elif freq_hz >= 1000:
            return f"{freq_hz // 1000}KHz"
        else:
            return f"{freq_hz}Hz"
    
    @staticmethod
    def get_chip_summary(chip_info: ChipInfo) -> Dict[str, str]:
        """获取芯片信息摘要"""
        return {
            '设备型号': chip_info.device_name or '未知',
            '厂商': chip_info.vendor or '未知',
            '系列': chip_info.series or '未知',
            'CPU内核': chip_info.core or '未知',
            'Flash大小': chip_info.flash_size or '未知',
            'RAM大小': chip_info.ram_size or '未知',
            '主频': chip_info.frequency or '未知',
            '封装': chip_info.package or '未知',
            '特性': ', '.join(chip_info.features) if chip_info.features else '无'
        }

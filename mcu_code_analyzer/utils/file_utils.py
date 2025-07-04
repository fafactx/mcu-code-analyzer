"""
文件工具模块 - 提供文件操作、编码检测和路径处理功能
"""

import os
import re
import chardet
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple
from utils.logger import logger, performance_monitor
from utils.config import config


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10240)  # 读取前10KB用于检测
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')
                confidence = result.get('confidence', 0)
                
                # 如果置信度太低，使用默认编码
                if confidence < 0.7:
                    encoding = 'utf-8'
                
                logger.debug(f"文件编码检测: {file_path.name} -> {encoding} (置信度: {confidence:.2f})")
                return encoding
                
        except Exception as e:
            logger.warning(f"编码检测失败: {file_path}, 使用默认编码 utf-8")
            return 'utf-8'
    
    @staticmethod
    def read_file_safe(file_path: Path) -> Optional[str]:
        """安全读取文件内容，自动处理编码问题"""
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return None
        
        # 检查文件大小
        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
        max_size = config.analyzer.max_file_size
        if file_size > max_size:
            logger.warning(f"文件过大，跳过: {file_path} ({file_size:.1f}MB > {max_size}MB)")
            return None
        
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp1252']
        
        # 首先尝试自动检测的编码
        detected_encoding = FileUtils.detect_encoding(file_path)
        if detected_encoding not in encodings:
            encodings.insert(0, detected_encoding)
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    logger.debug(f"成功读取文件: {file_path} (编码: {encoding})")
                    return content
            except Exception as e:
                logger.debug(f"编码 {encoding} 读取失败: {file_path}")
                continue
        
        logger.error(f"无法读取文件: {file_path}")
        return None
    
    @staticmethod
    def write_file_safe(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
        """安全写入文件"""
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.debug(f"文件写入成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件写入失败: {file_path}, 错误: {e}")
            return False
    
    @staticmethod
    @performance_monitor
    def find_files(root_path: Path, extensions: List[str] = None, 
                   exclude_dirs: List[str] = None) -> List[Path]:
        """递归查找指定扩展名的文件"""
        if extensions is None:
            extensions = config.analyzer.supported_extensions
        
        if exclude_dirs is None:
            exclude_dirs = config.analyzer.exclude_dirs
        
        found_files = []
        exclude_dirs_lower = [d.lower() for d in exclude_dirs]
        
        try:
            for file_path in root_path.rglob('*'):
                # 跳过目录
                if file_path.is_dir():
                    continue
                
                # 检查是否在排除目录中
                if any(excluded in str(file_path).lower() for excluded in exclude_dirs_lower):
                    continue
                
                # 检查文件扩展名
                if file_path.suffix.lower() in [ext.lower() for ext in extensions]:
                    found_files.append(file_path)
        
        except Exception as e:
            logger.error(f"文件搜索失败: {root_path}, 错误: {e}")
        
        logger.info(f"找到 {len(found_files)} 个文件 (扩展名: {extensions})")
        return found_files
    
    @staticmethod
    def find_project_files(root_path: Path) -> Dict[str, List[Path]]:
        """查找项目文件（Keil、CMake等）"""
        project_files = {
            'keil': [],
            'cmake': [],
            'makefile': [],
            'vs': [],
            'codeblocks': []
        }
        
        patterns = {
            'keil': ['*.uvproj', '*.uvprojx'],
            'cmake': ['CMakeLists.txt', '*.cmake'],
            'makefile': ['Makefile', 'makefile', '*.mk'],
            'vs': ['*.vcxproj', '*.sln'],
            'codeblocks': ['*.cbp']
        }
        
        try:
            for project_type, file_patterns in patterns.items():
                for pattern in file_patterns:
                    files = list(root_path.rglob(pattern))
                    project_files[project_type].extend(files)
        
        except Exception as e:
            logger.error(f"项目文件搜索失败: {root_path}, 错误: {e}")
        
        # 记录找到的项目文件
        for project_type, files in project_files.items():
            if files:
                logger.info(f"找到 {project_type.upper()} 项目文件: {len(files)} 个")
                for file in files[:3]:  # 只显示前3个
                    logger.debug(f"  - {file.relative_to(root_path)}")
                if len(files) > 3:
                    logger.debug(f"  - ... 还有 {len(files) - 3} 个文件")
        
        return project_files
    
    @staticmethod
    def clean_code_content(content: str) -> str:
        """清理代码内容，移除注释和空行"""
        if not content:
            return ""
        
        # 移除单行注释
        content = re.sub(r'//.*', '', content)
        
        # 移除多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # 移除预处理器指令（可选）
        # content = re.sub(r'^\s*#.*$', '', content, flags=re.MULTILINE)
        
        # 移除多余的空行
        content = re.sub(r'\n\s*\n', '\n', content)
        
        return content.strip()
    
    @staticmethod
    def extract_includes(content: str) -> List[str]:
        """提取头文件包含"""
        includes = []
        include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
        
        for match in re.finditer(include_pattern, content):
            include_file = match.group(1)
            includes.append(include_file)
        
        return includes
    
    @staticmethod
    def get_relative_path(file_path: Path, base_path: Path) -> str:
        """获取相对路径"""
        try:
            return str(file_path.relative_to(base_path))
        except ValueError:
            return str(file_path)
    
    @staticmethod
    def ensure_output_dir(base_path: Path) -> Path:
        """确保输出目录存在"""
        output_dir = config.get_output_dir(base_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出目录: {output_dir}")
        return output_dir
    
    @staticmethod
    def backup_file(file_path: Path) -> Optional[Path]:
        """备份文件"""
        if not file_path.exists():
            return None
        
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        counter = 1
        
        while backup_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{counter}")
            counter += 1
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f"文件备份: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"文件备份失败: {e}")
            return None
    
    @staticmethod
    def get_file_stats(file_path: Path) -> Dict[str, any]:
        """获取文件统计信息"""
        if not file_path.exists():
            return {}
        
        try:
            stat = file_path.stat()
            content = FileUtils.read_file_safe(file_path)
            
            stats = {
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified_time': stat.st_mtime,
                'line_count': len(content.splitlines()) if content else 0,
                'char_count': len(content) if content else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取文件统计失败: {file_path}, 错误: {e}")
            return {}
    
    @staticmethod
    def validate_path(path_str: str) -> Tuple[bool, str]:
        """验证路径有效性"""
        if not path_str:
            return False, "路径不能为空"
        
        try:
            path = Path(path_str)
            if not path.exists():
                return False, f"路径不存在: {path_str}"
            
            if not path.is_dir():
                return False, f"不是有效的目录: {path_str}"
            
            # 检查读取权限
            if not os.access(path, os.R_OK):
                return False, f"没有读取权限: {path_str}"
            
            return True, "路径有效"
            
        except Exception as e:
            return False, f"路径验证失败: {e}"

"""
工程文件解析器 - 支持多种项目文件格式的解析
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from utils.logger import logger, log_decorator
from utils.file_utils import FileUtils
from utils.config import config


@dataclass
class ProjectInfo:
    """项目信息数据类"""
    name: str = ""
    type: str = ""  # keil, cmake, makefile, vs, codeblocks
    root_path: Path = None
    source_files: List[str] = field(default_factory=list)
    header_files: List[str] = field(default_factory=list)
    include_paths: List[str] = field(default_factory=list)
    defines: Dict[str, str] = field(default_factory=dict)
    compiler: str = ""
    target_name: str = ""
    output_dir: str = ""
    libraries: List[str] = field(default_factory=list)
    linker_script: str = ""
    
    def __post_init__(self):
        if self.root_path is None:
            self.root_path = Path.cwd()


class ProjectParser:
    """项目文件解析器"""
    
    def __init__(self):
        self.project_info = ProjectInfo()
        self._supported_types = ['keil', 'cmake', 'makefile', 'vs', 'codeblocks']
    
    @log_decorator
    def parse_project(self, project_path: Path) -> ProjectInfo:
        """解析项目文件"""
        logger.info(f"开始解析项目: {project_path}")
        
        self.project_info.root_path = project_path
        
        # 查找项目文件
        project_files = FileUtils.find_project_files(project_path)
        
        # 按优先级解析项目文件
        for project_type in self._supported_types:
            if project_files[project_type]:
                project_file = project_files[project_type][0]
                logger.info(f"找到{project_type.upper()}项目文件: {project_file.name}")
                
                if project_type == 'keil':
                    return self._parse_keil_project(project_file)
                elif project_type == 'cmake':
                    return self._parse_cmake_project(project_file)
                elif project_type == 'makefile':
                    return self._parse_makefile_project(project_file)
                elif project_type == 'vs':
                    return self._parse_vs_project(project_file)
                elif project_type == 'codeblocks':
                    return self._parse_codeblocks_project(project_file)
        
        # 如果没有找到特定项目文件，创建通用项目信息
        logger.info("未找到特定项目文件，创建通用项目信息")
        return self._create_generic_project(project_path)
    
    def _parse_keil_project(self, project_file: Path) -> ProjectInfo:
        """解析Keil项目文件"""
        try:
            tree = ET.parse(project_file)
            root = tree.getroot()
            
            project_info = ProjectInfo(
                name=project_file.stem,
                type='keil',
                root_path=project_file.parent,
                compiler='armcc'
            )
            
            # 解析目标配置
            target_elem = root.find(".//TargetName")
            if target_elem is not None and target_elem.text:
                project_info.target_name = target_elem.text.strip()
            
            # 解析输出目录
            output_elem = root.find(".//OutputDirectory")
            if output_elem is not None and output_elem.text:
                project_info.output_dir = output_elem.text.strip()
            
            # 解析包含路径
            include_paths = set()
            for include_elem in root.findall(".//IncludePath"):
                if include_elem.text:
                    paths = include_elem.text.split(';')
                    for path in paths:
                        path = path.strip()
                        if path:
                            include_paths.add(path)
            project_info.include_paths = list(include_paths)
            
            # 解析预定义宏
            defines = {}
            for define_elem in root.findall(".//Define"):
                if define_elem.text:
                    for def_item in define_elem.text.split(','):
                        def_item = def_item.strip()
                        if '=' in def_item:
                            key, value = def_item.split('=', 1)
                            defines[key.strip()] = value.strip()
                        else:
                            defines[def_item] = '1'
            project_info.defines = defines
            
            # 解析源文件
            source_files = []
            header_files = []

            # uvprojx文件所在目录作为相对路径的基准
            uvprojx_dir = project_file.parent

            for file_elem in root.findall(".//FilePath"):
                if file_elem.text:
                    file_path = file_elem.text.strip()

                    # 如果是相对路径，基于uvprojx文件目录解析
                    if not Path(file_path).is_absolute():
                        # 将相对路径转换为基于项目根目录的相对路径
                        resolved_path = (uvprojx_dir / file_path).resolve()
                        try:
                            # 转换为相对于项目根目录的路径
                            relative_to_project = resolved_path.relative_to(project_info.root_path)
                            file_path = str(relative_to_project)
                        except ValueError:
                            # 如果无法转换为相对路径，使用绝对路径
                            file_path = str(resolved_path)

                    if file_path.endswith(('.c', '.cpp', '.cc', '.cxx')):
                        source_files.append(file_path)
                    elif file_path.endswith(('.h', '.hpp', '.hxx')):
                        header_files.append(file_path)
            
            project_info.source_files = source_files
            project_info.header_files = header_files
            
            # 解析库文件
            libraries = []
            for lib_elem in root.findall(".//Lib"):
                if lib_elem.text:
                    libraries.append(lib_elem.text.strip())
            project_info.libraries = libraries
            
            # 解析链接脚本
            scatter_elem = root.find(".//ScatterFile")
            if scatter_elem is not None and scatter_elem.text:
                project_info.linker_script = scatter_elem.text.strip()
            
            logger.info(f"Keil项目解析完成: {len(source_files)} 个源文件, {len(header_files)} 个头文件")
            return project_info
            
        except Exception as e:
            logger.error(f"解析Keil项目失败: {project_file}, 错误: {e}")
            return self._create_generic_project(project_file.parent)
    
    def _parse_cmake_project(self, project_file: Path) -> ProjectInfo:
        """解析CMake项目文件"""
        try:
            content = FileUtils.read_file_safe(project_file)
            if not content:
                return self._create_generic_project(project_file.parent)
            
            project_info = ProjectInfo(
                name=project_file.parent.name,
                type='cmake',
                root_path=project_file.parent,
                compiler='gcc'
            )
            
            # 解析项目名称
            project_match = self._extract_cmake_value(content, 'project')
            if project_match:
                project_info.name = project_match
            
            # 解析源文件
            sources = self._extract_cmake_sources(content)
            project_info.source_files = [s for s in sources if s.endswith(('.c', '.cpp', '.cc', '.cxx'))]
            project_info.header_files = [s for s in sources if s.endswith(('.h', '.hpp', '.hxx'))]
            
            # 解析包含目录
            include_dirs = self._extract_cmake_include_dirs(content)
            project_info.include_paths = include_dirs
            
            # 解析编译定义
            definitions = self._extract_cmake_definitions(content)
            project_info.defines = definitions
            
            logger.info(f"CMake项目解析完成: {len(project_info.source_files)} 个源文件")
            return project_info
            
        except Exception as e:
            logger.error(f"解析CMake项目失败: {project_file}, 错误: {e}")
            return self._create_generic_project(project_file.parent)
    
    def _parse_makefile_project(self, project_file: Path) -> ProjectInfo:
        """解析Makefile项目文件"""
        try:
            content = FileUtils.read_file_safe(project_file)
            if not content:
                return self._create_generic_project(project_file.parent)
            
            project_info = ProjectInfo(
                name=project_file.parent.name,
                type='makefile',
                root_path=project_file.parent,
                compiler='gcc'
            )
            
            # 解析源文件变量
            sources = self._extract_makefile_sources(content)
            project_info.source_files = [s for s in sources if s.endswith(('.c', '.cpp', '.cc', '.cxx'))]
            project_info.header_files = [s for s in sources if s.endswith(('.h', '.hpp', '.hxx'))]
            
            # 解析包含路径
            include_paths = self._extract_makefile_includes(content)
            project_info.include_paths = include_paths
            
            # 解析编译定义
            definitions = self._extract_makefile_definitions(content)
            project_info.defines = definitions
            
            logger.info(f"Makefile项目解析完成: {len(project_info.source_files)} 个源文件")
            return project_info
            
        except Exception as e:
            logger.error(f"解析Makefile项目失败: {project_file}, 错误: {e}")
            return self._create_generic_project(project_file.parent)
    
    def _parse_vs_project(self, project_file: Path) -> ProjectInfo:
        """解析Visual Studio项目文件"""
        # 简化实现，主要解析.vcxproj文件
        try:
            tree = ET.parse(project_file)
            root = tree.getroot()
            
            project_info = ProjectInfo(
                name=project_file.stem,
                type='vs',
                root_path=project_file.parent,
                compiler='msvc'
            )
            
            # 解析源文件
            source_files = []
            header_files = []
            
            # Visual Studio项目文件使用命名空间
            ns = {'': 'http://schemas.microsoft.com/developer/msbuild/2003'}
            
            for compile_elem in root.findall(".//ClCompile", ns):
                include_attr = compile_elem.get('Include')
                if include_attr:
                    source_files.append(include_attr)
            
            for include_elem in root.findall(".//ClInclude", ns):
                include_attr = include_elem.get('Include')
                if include_attr:
                    header_files.append(include_attr)
            
            project_info.source_files = source_files
            project_info.header_files = header_files
            
            logger.info(f"Visual Studio项目解析完成: {len(source_files)} 个源文件")
            return project_info
            
        except Exception as e:
            logger.error(f"解析Visual Studio项目失败: {project_file}, 错误: {e}")
            return self._create_generic_project(project_file.parent)
    
    def _parse_codeblocks_project(self, project_file: Path) -> ProjectInfo:
        """解析Code::Blocks项目文件"""
        try:
            tree = ET.parse(project_file)
            root = tree.getroot()
            
            project_info = ProjectInfo(
                name=project_file.stem,
                type='codeblocks',
                root_path=project_file.parent,
                compiler='gcc'
            )
            
            # 解析源文件
            source_files = []
            header_files = []
            
            for unit_elem in root.findall(".//Unit"):
                filename_attr = unit_elem.get('filename')
                if filename_attr:
                    if filename_attr.endswith(('.c', '.cpp', '.cc', '.cxx')):
                        source_files.append(filename_attr)
                    elif filename_attr.endswith(('.h', '.hpp', '.hxx')):
                        header_files.append(filename_attr)
            
            project_info.source_files = source_files
            project_info.header_files = header_files
            
            logger.info(f"Code::Blocks项目解析完成: {len(source_files)} 个源文件")
            return project_info
            
        except Exception as e:
            logger.error(f"解析Code::Blocks项目失败: {project_file}, 错误: {e}")
            return self._create_generic_project(project_file.parent)
    
    def _create_generic_project(self, project_path: Path) -> ProjectInfo:
        """创建通用项目信息"""
        logger.info("创建通用项目信息")
        
        project_info = ProjectInfo(
            name=project_path.name,
            type='generic',
            root_path=project_path,
            compiler='gcc'
        )
        
        # 扫描所有源文件
        all_files = FileUtils.find_files(project_path)
        
        source_files = []
        header_files = []
        
        for file_path in all_files:
            relative_path = str(file_path.relative_to(project_path))
            if file_path.suffix.lower() in ['.c', '.cpp', '.cc', '.cxx']:
                source_files.append(relative_path)
            elif file_path.suffix.lower() in ['.h', '.hpp', '.hxx']:
                header_files.append(relative_path)
        
        project_info.source_files = source_files
        project_info.header_files = header_files
        
        # 自动推断包含路径
        include_paths = set()
        for header_file in header_files[:20]:  # 只检查前20个头文件
            header_path = project_path / header_file
            include_paths.add(str(header_path.parent.relative_to(project_path)))
        
        project_info.include_paths = list(include_paths)
        
        logger.info(f"通用项目创建完成: {len(source_files)} 个源文件, {len(header_files)} 个头文件")
        return project_info

    def _extract_cmake_value(self, content: str, command: str) -> Optional[str]:
        """从CMake内容中提取命令值"""
        import re
        pattern = rf'{command}\s*\(\s*([^)]+)\s*\)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip('"\'')
        return None

    def _extract_cmake_sources(self, content: str) -> List[str]:
        """从CMake内容中提取源文件"""
        import re
        sources = []

        # 查找add_executable和add_library中的源文件
        patterns = [
            r'add_executable\s*\([^)]*\s+([^)]+)\)',
            r'add_library\s*\([^)]*\s+([^)]+)\)',
            r'target_sources\s*\([^)]*\s+([^)]+)\)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # 分割文件列表
                files = re.split(r'\s+', match.strip())
                for file in files:
                    file = file.strip().strip('"\'')
                    if file and '.' in file:
                        sources.append(file)

        return sources

    def _extract_cmake_include_dirs(self, content: str) -> List[str]:
        """从CMake内容中提取包含目录"""
        import re
        include_dirs = []

        patterns = [
            r'include_directories\s*\(\s*([^)]+)\s*\)',
            r'target_include_directories\s*\([^)]*\s+([^)]+)\)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                dirs = re.split(r'\s+', match.strip())
                for dir_path in dirs:
                    dir_path = dir_path.strip().strip('"\'')
                    if dir_path and not dir_path.startswith('$'):
                        include_dirs.append(dir_path)

        return include_dirs

    def _extract_cmake_definitions(self, content: str) -> Dict[str, str]:
        """从CMake内容中提取编译定义"""
        import re
        definitions = {}

        patterns = [
            r'add_definitions\s*\(\s*([^)]+)\s*\)',
            r'target_compile_definitions\s*\([^)]*\s+([^)]+)\)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                defs = re.split(r'\s+', match.strip())
                for def_item in defs:
                    def_item = def_item.strip().strip('"\'')
                    if def_item.startswith('-D'):
                        def_item = def_item[2:]

                    if '=' in def_item:
                        key, value = def_item.split('=', 1)
                        definitions[key.strip()] = value.strip()
                    else:
                        definitions[def_item] = '1'

        return definitions

    def _extract_makefile_sources(self, content: str) -> List[str]:
        """从Makefile内容中提取源文件"""
        import re
        sources = []

        # 查找常见的源文件变量
        patterns = [
            r'SOURCES?\s*[+:=]\s*([^\n]+)',
            r'SRCS?\s*[+:=]\s*([^\n]+)',
            r'C_SOURCES?\s*[+:=]\s*([^\n]+)',
            r'CPP_SOURCES?\s*[+:=]\s*([^\n]+)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                files = re.split(r'\s+', match.strip())
                for file in files:
                    file = file.strip().strip('\\')
                    if file and '.' in file and not file.startswith('$'):
                        sources.append(file)

        return sources

    def _extract_makefile_includes(self, content: str) -> List[str]:
        """从Makefile内容中提取包含路径"""
        import re
        include_paths = []

        # 查找-I选项
        pattern = r'-I\s*([^\s]+)'
        matches = re.findall(pattern, content)

        for match in matches:
            path = match.strip()
            if path and not path.startswith('$'):
                include_paths.append(path)

        return include_paths

    def _extract_makefile_definitions(self, content: str) -> Dict[str, str]:
        """从Makefile内容中提取编译定义"""
        import re
        definitions = {}

        # 查找-D选项
        pattern = r'-D\s*([^\s]+)'
        matches = re.findall(pattern, content)

        for match in matches:
            def_item = match.strip()
            if '=' in def_item:
                key, value = def_item.split('=', 1)
                definitions[key.strip()] = value.strip()
            else:
                definitions[def_item] = '1'

        return definitions

    def get_project_summary(self) -> Dict[str, any]:
        """获取项目信息摘要"""
        return {
            '项目名称': self.project_info.name,
            '项目类型': self.project_info.type.upper(),
            '编译器': self.project_info.compiler,
            '源文件数量': len(self.project_info.source_files),
            '头文件数量': len(self.project_info.header_files),
            '包含路径数量': len(self.project_info.include_paths),
            '预定义宏数量': len(self.project_info.defines),
            '库文件数量': len(self.project_info.libraries),
            '目标名称': self.project_info.target_name or '未指定',
            '输出目录': self.project_info.output_dir or '未指定'
        }

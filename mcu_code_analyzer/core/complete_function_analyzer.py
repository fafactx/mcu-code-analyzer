"""
完整的函数分析器 - 先全量分析所有函数，再进行调用关系分析
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from utils.logger import logger
from utils.file_utils import FileUtils


@dataclass
class FunctionInfo:
    """函数信息数据类"""
    name: str
    file_path: str
    line_number: int
    signature: str
    return_type: str
    parameters: str
    is_static: bool = False
    is_inline: bool = False
    is_main: bool = False
    calls: List[str] = None  # 调用的其他函数
    called_by: List[str] = None  # 被哪些函数调用
    
    def __post_init__(self):
        if self.calls is None:
            self.calls = []
        if self.called_by is None:
            self.called_by = []


class CompleteFunctionAnalyzer:
    """完整的函数分析器"""
    
    def __init__(self):
        self.all_functions: Dict[str, FunctionInfo] = {}
        self.main_functions: List[FunctionInfo] = []
        self.analysis_cache = {}
        self.should_cancel = False  # 取消标志
        
    def analyze_project(self, project_path: Path, source_files: List[str] = None) -> Dict:
        """完整分析项目的所有函数 - 使用文件搜索，不依赖配置文件"""
        # 重置取消标志
        self.should_cancel = False

        logger.info("🔍 开始完整函数分析...")

        # 第一步：搜索所有源文件（忽略传入的source_files，直接遍历目录）
        self.update_status("🔍 搜索项目中的所有源文件...")
        actual_source_files = self._search_source_files(project_path)
        logger.info(f"找到 {len(actual_source_files)} 个源文件")

        # 第二步：提取所有函数定义
        self.update_status("📋 提取所有函数定义...")
        self._extract_all_functions_from_files(actual_source_files)

        # 第三步：分析函数调用关系
        self.update_status("🔗 分析函数调用关系...")
        self._analyze_function_calls_from_files(actual_source_files)

        # 第四步：识别main函数
        self.update_status("🎯 识别main函数...")
        self._identify_main_functions()

        # 第五步：保存分析结果
        self.update_status("💾 保存函数分析结果...")
        output_path = project_path / "Analyzer_Output"
        output_path.mkdir(parents=True, exist_ok=True)
        self._save_analysis_results(output_path)

        logger.info(f"✅ 函数分析完成: {len(self.all_functions)} 个函数, {len(self.main_functions)} 个main函数")

        return {
            'all_functions': self.all_functions,
            'main_functions': self.main_functions,
            'total_functions': len(self.all_functions),
            'actual_source_files': actual_source_files,
            'analysis_file': output_path / "all_functions.json"
        }

    def _search_source_files(self, project_path: Path) -> List[Path]:
        """搜索项目目录中的所有源文件"""
        source_files = []

        # 支持的源文件扩展名
        source_extensions = {'.c', '.cpp', '.cc', '.cxx', '.C', '.CPP'}

        # 需要排除的目录
        exclude_dirs = {
            'build', 'Build', 'BUILD',
            'debug', 'Debug', 'DEBUG',
            'release', 'Release', 'RELEASE',
            'output', 'Output', 'OUTPUT',
            'obj', 'Obj', 'OBJ',
            'bin', 'Bin', 'BIN',
            '.git', '.svn', '.hg',
            'node_modules', '__pycache__',
            'Analyzer_Output'  # 排除我们自己的输出目录
        }

        logger.info(f"开始搜索源文件: {project_path}")

        try:
            # 递归搜索所有源文件
            for file_path in project_path.rglob('*'):
                # 跳过目录
                if file_path.is_dir():
                    continue

                # 检查是否在排除目录中
                if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                    continue

                # 检查文件扩展名
                if file_path.suffix in source_extensions:
                    source_files.append(file_path)
                    logger.debug(f"找到源文件: {file_path}")

            logger.info(f"搜索完成，找到 {len(source_files)} 个源文件")
            return source_files

        except Exception as e:
            logger.error(f"搜索源文件失败: {e}")
            return []

    def _extract_all_functions_from_files(self, source_files: List[Path]):
        """从文件列表中提取所有函数定义"""
        logger.info("开始提取所有函数定义...")

        total_files = len(source_files)
        processed_files = 0

        for source_file in source_files:
            # 检查是否需要取消
            if self.should_cancel:
                logger.info("函数提取被取消")
                return

            try:
                processed_files += 1

                # 更新进度
                if processed_files % 5 == 0 or processed_files == total_files:
                    progress_msg = f"📋 提取函数定义... ({processed_files}/{total_files}) - {source_file.name}"
                    self.update_status(progress_msg)
                    logger.info(progress_msg)

                self._extract_functions_from_file(source_file)
            except Exception as e:
                logger.warning(f"提取函数失败 {source_file}: {e}")

    def _analyze_function_calls_from_files(self, source_files: List[Path]):
        """从文件列表分析函数调用关系"""
        logger.info("开始分析函数调用关系...")

        total_functions = len(self.all_functions)
        processed = 0

        # 为每个函数分析其调用的其他函数
        for func_name, func_info in self.all_functions.items():
            # 检查是否需要取消
            if self.should_cancel:
                logger.info("函数调用分析被取消")
                return

            processed += 1

            # 更新进度
            if processed % 10 == 0 or processed == total_functions:
                progress_msg = f"🔗 分析函数调用关系... ({processed}/{total_functions})"
                self.update_status(progress_msg)
                logger.info(progress_msg)

            called_functions = self._find_function_calls_in_function(func_info, None)
            func_info.calls = called_functions

            # 更新被调用关系
            for called_func in called_functions:
                if called_func in self.all_functions:
                    if func_name not in self.all_functions[called_func].called_by:
                        self.all_functions[called_func].called_by.append(func_name)

    def _extract_all_functions(self, project_path: Path, source_files: List[str]):
        """提取所有函数定义"""
        logger.info("开始提取所有函数定义...")
        
        for source_file_str in source_files:
            # 转换路径
            if isinstance(source_file_str, str):
                if not Path(source_file_str).is_absolute():
                    # 处理相对路径，特别是 ../ 路径
                    source_file = (project_path / source_file_str).resolve()
                else:
                    source_file = Path(source_file_str)
            else:
                source_file = source_file_str
            
            # 检查文件
            if not source_file.suffix.lower() in ['.c', '.cpp', '.h', '.hpp']:
                continue
            
            if not source_file.exists():
                logger.warning(f"文件不存在: {source_file}")
                continue
            
            # 分析文件中的函数
            self._extract_functions_from_file(source_file)
    
    def _extract_functions_from_file(self, file_path: Path):
        """从单个文件中提取函数"""
        content = FileUtils.read_file_safe(file_path)
        if not content:
            return
        
        # 增强的函数定义模式
        function_patterns = [
            # 标准函数定义: 返回类型 函数名(参数) {
            r'(?P<static>static\s+)?(?P<inline>inline\s+)?(?P<return>\w+(?:\s*\*)*)\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*{',
            
            # 指针返回类型: 类型* 函数名(参数) {
            r'(?P<static>static\s+)?(?P<inline>inline\s+)?(?P<return>\w+)\s*\*\s*(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*{',
            
            # void函数: void 函数名(参数) {
            r'(?P<static>static\s+)?(?P<inline>inline\s+)?void\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*{',
            
            # main函数特殊处理: int main(...) 或 void main(...) 或 main(...)
            r'(?P<return>int|void)?\s*(?P<name>main)\s*\((?P<params>[^)]*)\)\s*{',
            
            # 无返回类型声明的函数 (老式C)
            r'(?P<static>static\s+)?(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*{',
        ]
        
        lines = content.split('\n')
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                func_name = match.group('name')
                
                # 过滤关键字
                if func_name in ['if', 'for', 'while', 'switch', 'do', 'else', 'case', 'default']:
                    continue
                
                # 计算行号
                line_number = content[:match.start()].count('\n') + 1
                
                # 提取函数信息
                return_type = match.groupdict().get('return', 'void') or 'void'
                parameters = match.groupdict().get('params', '') or ''
                is_static = bool(match.groupdict().get('static'))
                is_inline = bool(match.groupdict().get('inline'))
                is_main = (func_name == 'main')
                
                # 创建函数信息
                func_info = FunctionInfo(
                    name=func_name,
                    file_path=str(file_path),
                    line_number=line_number,
                    signature=match.group(0).strip(),
                    return_type=return_type.strip(),
                    parameters=parameters.strip(),
                    is_static=is_static,
                    is_inline=is_inline,
                    is_main=is_main
                )
                
                # 避免重复（同名函数取第一个）
                if func_name not in self.all_functions:
                    self.all_functions[func_name] = func_info
                    logger.debug(f"发现函数: {func_name} 在 {file_path.name}:{line_number}")
    
    def _analyze_function_calls(self, project_path: Path, source_files: List[str]):
        """分析函数调用关系"""
        logger.info("开始分析函数调用关系...")
        
        # 为每个函数分析其调用的其他函数
        for func_name, func_info in self.all_functions.items():
            called_functions = self._find_function_calls_in_function(func_info, project_path)
            func_info.calls = called_functions
            
            # 更新被调用关系
            for called_func in called_functions:
                if called_func in self.all_functions:
                    if func_name not in self.all_functions[called_func].called_by:
                        self.all_functions[called_func].called_by.append(func_name)
    
    def _find_function_calls_in_function(self, func_info: FunctionInfo, project_path: Path = None) -> List[str]:
        """查找函数内部调用的其他函数"""
        file_path = Path(func_info.file_path)
        content = FileUtils.read_file_safe(file_path)
        if not content:
            return []

        # 找到函数体
        func_start = content.find(func_info.signature)
        if func_start == -1:
            return []

        # 提取函数体（简单的大括号匹配）
        func_body = self._extract_function_body(content, func_start)
        if not func_body:
            return []

        # 优化：使用正则表达式一次性查找所有可能的函数调用
        # 匹配模式：标识符后跟左括号
        call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        potential_calls = re.findall(call_pattern, func_body)

        # 过滤出真正存在的函数调用
        called_functions = []
        for call_name in potential_calls:
            if call_name != func_info.name and call_name in self.all_functions:
                if call_name not in called_functions:  # 避免重复
                    called_functions.append(call_name)

        return called_functions
    
    def _extract_function_body(self, content: str, func_start: int) -> str:
        """提取函数体内容"""
        # 找到第一个 {
        brace_start = content.find('{', func_start)
        if brace_start == -1:
            return ""
        
        # 匹配大括号
        brace_count = 0
        brace_end = brace_start
        
        for i, char in enumerate(content[brace_start:], brace_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    brace_end = i
                    break
        
        return content[brace_start:brace_end + 1]
    
    def _identify_main_functions(self):
        """识别main函数"""
        self.main_functions = []
        
        for func_name, func_info in self.all_functions.items():
            if func_info.is_main or func_name == 'main':
                self.main_functions.append(func_info)
                logger.info(f"发现main函数: {func_info.file_path}:{func_info.line_number}")
    
    def _save_analysis_results(self, output_path: Path):
        """保存分析结果到文件"""
        # 转换为可序列化的格式
        serializable_functions = {}
        for name, func_info in self.all_functions.items():
            serializable_functions[name] = asdict(func_info)
        
        # 保存所有函数信息
        all_functions_file = output_path / "all_functions.json"
        with open(all_functions_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_functions': len(self.all_functions),
                'main_functions_count': len(self.main_functions),
                'main_functions': [func.name for func in self.main_functions],
                'functions': serializable_functions
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"函数分析结果已保存: {all_functions_file}")
    
    def update_status(self, message: str):
        """更新状态（可被UI重写）"""
        logger.info(message)

    def cancel_analysis(self):
        """取消分析"""
        self.should_cancel = True
        logger.info("收到取消分析请求")
    
    def get_main_function(self) -> Optional[FunctionInfo]:
        """获取main函数"""
        if self.main_functions:
            return self.main_functions[0]  # 返回第一个main函数
        return None
    
    def trace_function_calls_from_main(self, max_depth: int = 5) -> Dict:
        """从main函数开始追踪调用关系"""
        main_func = self.get_main_function()
        if not main_func:
            raise Exception("未找到main函数")
        
        call_graph = {
            'main_function': asdict(main_func),
            'call_relations': {},
            'reachable_functions': [],
            'depth_map': {}
        }
        
        # 从main开始递归追踪
        visited = set()
        to_visit = [(main_func.name, 0)]
        
        while to_visit:
            current_func, depth = to_visit.pop(0)
            
            if current_func in visited or depth >= max_depth:
                continue
            
            visited.add(current_func)
            call_graph['reachable_functions'].append(current_func)
            call_graph['depth_map'][current_func] = depth
            
            # 获取调用的函数
            if current_func in self.all_functions:
                called_functions = self.all_functions[current_func].calls
                call_graph['call_relations'][current_func] = called_functions
                
                # 添加到待访问列表
                for called_func in called_functions:
                    if called_func not in visited:
                        to_visit.append((called_func, depth + 1))
        
        return call_graph

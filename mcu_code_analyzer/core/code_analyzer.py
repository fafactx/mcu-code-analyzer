"""
代码分析器 - 负责C代码的函数提取和调用关系分析
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
from utils.logger import logger, log_decorator, performance_monitor
from utils.file_utils import FileUtils
from utils.config import config


@dataclass
class FunctionInfo:
    """函数信息数据类"""
    name: str
    file_path: str
    line_number: int
    return_type: str = ""
    parameters: str = ""
    signature: str = ""
    is_definition: bool = False
    is_static: bool = False
    is_inline: bool = False
    calls: Set[str] = field(default_factory=set)
    called_by: Set[str] = field(default_factory=set)


@dataclass
class CallRelation:
    """函数调用关系数据类"""
    caller: str
    callee: str
    file_path: str
    line_number: int
    call_type: str = "direct"  # direct, indirect, conditional


class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self):
        self.functions: Dict[str, FunctionInfo] = {}
        self.call_relations: List[CallRelation] = []
        self.main_call_tree: Dict[str, Set[str]] = defaultdict(set)
        self.analysis_stats = {
            'total_files': 0,
            'parsed_files': 0,
            'total_functions': 0,
            'total_calls': 0,
            'main_reachable_functions': 0
        }
    
    @log_decorator
    @performance_monitor
    def analyze_project(self, project_path: Path, source_files: List[str] = None) -> Dict[str, any]:
        """分析整个项目的代码"""
        logger.info(f"开始分析项目代码: {project_path}")
        
        # 获取源文件列表
        if source_files is None:
            c_files = FileUtils.find_files(project_path)
        else:
            c_files = [project_path / file for file in source_files if Path(project_path / file).exists()]
        
        self.analysis_stats['total_files'] = len(c_files)
        logger.info(f"找到 {len(c_files)} 个源文件")
        
        # 第一阶段：提取所有函数定义
        logger.info("第一阶段：提取函数定义")
        for i, file_path in enumerate(c_files):
            logger.log_analysis_progress(i + 1, len(c_files), file_path.name)
            self._extract_functions_from_file(file_path)
        
        logger.info(f"提取到 {len(self.functions)} 个函数")
        self.analysis_stats['total_functions'] = len(self.functions)
        
        # 第二阶段：分析函数调用关系
        logger.info("第二阶段：分析调用关系")
        for i, file_path in enumerate(c_files):
            logger.log_analysis_progress(i + 1, len(c_files), file_path.name)
            self._extract_calls_from_file(file_path)
        
        logger.info(f"分析到 {len(self.call_relations)} 个函数调用")
        self.analysis_stats['total_calls'] = len(self.call_relations)
        
        # 第三阶段：构建调用树
        logger.info("第三阶段：构建调用树")
        self._build_call_tree()
        
        # 第四阶段：分析从main函数可达的函数
        logger.info("第四阶段：分析main函数调用链")
        main_reachable = self._analyze_main_call_chain()
        self.analysis_stats['main_reachable_functions'] = len(main_reachable)
        
        logger.info("代码分析完成")
        return self._generate_analysis_result()
    
    def _extract_functions_from_file(self, file_path: Path):
        """从文件中提取函数定义"""
        content = FileUtils.read_file_safe(file_path)
        if not content:
            return
        
        # 清理代码内容
        clean_content = FileUtils.clean_code_content(content)
        lines = clean_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # 检测函数定义
            if '(' in line and not any(keyword in line for keyword in ['if', 'while', 'for', 'switch', 'return']):
                func_info = self._parse_function_definition(lines, i, file_path)
                if func_info:
                    self.functions[func_info.name] = func_info
                    logger.debug(f"找到函数: {func_info.name} 在 {file_path.name}:{func_info.line_number}")
                    # 跳过已处理的行
                    i += 5  # 跳过函数头部分
                else:
                    i += 1
            else:
                i += 1
        
        self.analysis_stats['parsed_files'] += 1
    
    def _parse_function_definition(self, lines: List[str], start_line: int, file_path: Path) -> Optional[FunctionInfo]:
        """解析函数定义"""
        # 收集完整的函数签名（可能跨多行）
        signature_lines = []
        i = start_line
        paren_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            signature_lines.append(line)
            paren_count += line.count('(') - line.count(')')
            
            if paren_count <= 0 and '(' in ''.join(signature_lines):
                break
            i += 1
            if i - start_line > 10:  # 防止无限循环
                break
        
        full_signature = ' '.join(signature_lines).strip()
        
        # 使用正则表达式解析函数签名
        # 匹配模式：[修饰符] 返回类型 函数名(参数)
        pattern = r'(?:(static|extern|inline)\s+)*([a-zA-Z_]\w*(?:\s*\*)*)\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)'
        match = re.search(pattern, full_signature)
        
        if not match:
            return None
        
        modifiers = match.group(1) or ""
        return_type = match.group(2).strip()
        func_name = match.group(3).strip()
        parameters = match.group(4).strip()
        
        # 过滤掉不是函数的情况
        if (func_name in ['if', 'while', 'for', 'switch', 'return', 'sizeof'] or
            func_name.isdigit() or len(func_name) < 2):
            return None
        
        # 检查是否是函数定义（有函数体）
        is_definition = False
        check_line = i + 1
        while check_line < min(i + 5, len(lines)):
            if '{' in lines[check_line]:
                is_definition = True
                break
            if ';' in lines[check_line]:
                break
            check_line += 1
        
        return FunctionInfo(
            name=func_name,
            file_path=str(file_path),
            line_number=start_line + 1,
            return_type=return_type,
            parameters=parameters,
            signature=full_signature,
            is_definition=is_definition,
            is_static='static' in modifiers,
            is_inline='inline' in modifiers
        )
    
    def _extract_calls_from_file(self, file_path: Path):
        """从文件中提取函数调用关系"""
        content = FileUtils.read_file_safe(file_path)
        if not content:
            return
        
        clean_content = FileUtils.clean_code_content(content)
        lines = clean_content.split('\n')
        
        current_function = None
        brace_count = 0
        in_function_body = False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line:
                continue
            
            # 检测函数定义开始
            if '{' in line and current_function is None:
                # 查找这行或前几行中的函数名
                for func_name in self.functions:
                    if func_name in line or (line_num > 1 and func_name in lines[line_num - 2]):
                        if self.functions[func_name].file_path == str(file_path):
                            current_function = func_name
                            in_function_body = True
                            brace_count = line.count('{') - line.count('}')
                            break
            
            # 更新大括号计数
            if in_function_body:
                brace_count += line.count('{') - line.count('}')
                
                if brace_count <= 0:
                    in_function_body = False
                    current_function = None
                    continue
            
            # 在函数体内查找函数调用
            if current_function and in_function_body:
                calls = self._find_function_calls_in_line(line)
                for called_func in calls:
                    if called_func in self.functions:
                        call_relation = CallRelation(
                            caller=current_function,
                            callee=called_func,
                            file_path=str(file_path),
                            line_number=line_num
                        )
                        self.call_relations.append(call_relation)
                        
                        # 更新函数信息
                        self.functions[current_function].calls.add(called_func)
                        self.functions[called_func].called_by.add(current_function)
    
    def _find_function_calls_in_line(self, line: str) -> List[str]:
        """在代码行中查找函数调用"""
        calls = []
        
        # 查找函数调用模式：函数名(
        call_pattern = r'([a-zA-Z_]\w*)\s*\('
        matches = re.finditer(call_pattern, line)
        
        for match in matches:
            func_name = match.group(1)
            
            # 过滤掉关键字和明显不是函数的情况
            if (func_name not in ['if', 'while', 'for', 'switch', 'sizeof', 'return', 
                                 'case', 'default', 'else', 'do', 'typedef'] and
                not func_name.isdigit() and len(func_name) >= 2):
                calls.append(func_name)
        
        return calls
    
    def _build_call_tree(self):
        """构建函数调用树"""
        for relation in self.call_relations:
            self.main_call_tree[relation.caller].add(relation.callee)
    
    def _analyze_main_call_chain(self) -> Set[str]:
        """分析从main函数开始的调用链"""
        if 'main' not in self.functions:
            logger.warning("未找到main函数")
            return set()
        
        # 使用广度优先搜索遍历调用树
        visited = set()
        queue = deque(['main'])
        
        while queue:
            current_func = queue.popleft()
            if current_func in visited:
                continue
            
            visited.add(current_func)
            
            # 添加当前函数调用的所有函数
            if current_func in self.main_call_tree:
                for called_func in self.main_call_tree[current_func]:
                    if called_func not in visited:
                        queue.append(called_func)
        
        logger.info(f"从main函数可达的函数数量: {len(visited)}")
        return visited
    
    def _generate_analysis_result(self) -> Dict[str, any]:
        """生成分析结果"""
        main_reachable = self._analyze_main_call_chain()
        
        # 统计信息
        function_stats = {
            'total_functions': len(self.functions),
            'defined_functions': sum(1 for f in self.functions.values() if f.is_definition),
            'declared_functions': sum(1 for f in self.functions.values() if not f.is_definition),
            'static_functions': sum(1 for f in self.functions.values() if f.is_static),
            'inline_functions': sum(1 for f in self.functions.values() if f.is_inline),
            'main_reachable': len(main_reachable)
        }
        
        # 调用关系统计
        call_stats = {
            'total_calls': len(self.call_relations),
            'unique_callers': len(set(r.caller for r in self.call_relations)),
            'unique_callees': len(set(r.callee for r in self.call_relations))
        }
        
        # 生成调用图数据
        call_graph = {}
        for func_name in main_reachable:
            if func_name in self.main_call_tree:
                call_graph[func_name] = list(self.main_call_tree[func_name])
        
        return {
            'functions': self.functions,
            'call_relations': self.call_relations,
            'call_graph': call_graph,
            'main_reachable_functions': main_reachable,
            'function_stats': function_stats,
            'call_stats': call_stats,
            'analysis_stats': self.analysis_stats
        }
    
    def get_function_by_name(self, func_name: str) -> Optional[FunctionInfo]:
        """根据名称获取函数信息"""
        return self.functions.get(func_name)
    
    def get_callers(self, func_name: str) -> Set[str]:
        """获取调用指定函数的所有函数"""
        if func_name in self.functions:
            return self.functions[func_name].called_by
        return set()
    
    def get_callees(self, func_name: str) -> Set[str]:
        """获取指定函数调用的所有函数"""
        if func_name in self.functions:
            return self.functions[func_name].calls
        return set()
    
    def is_main_reachable(self, func_name: str) -> bool:
        """检查函数是否从main函数可达"""
        main_reachable = self._analyze_main_call_chain()
        return func_name in main_reachable

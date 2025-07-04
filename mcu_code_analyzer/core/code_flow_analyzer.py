"""
代码流程分析器 - 分析真正的代码执行流程
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from utils.logger import logger
from utils.file_utils import FileUtils


@dataclass
class FlowNode:
    """流程节点"""
    node_id: str
    node_type: str  # 'start', 'declaration', 'function_call', 'condition', 'loop_body', 'statement', 'end'
    content: str
    line_number: int
    original_code: str = ""
    children: List[str] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class CodeBlock:
    """代码块"""
    block_type: str  # 'sequence', 'if', 'else', 'while', 'for'
    start_line: int
    end_line: int
    content: str
    nested_blocks: List['CodeBlock'] = None
    
    def __post_init__(self):
        if self.nested_blocks is None:
            self.nested_blocks = []


class CodeFlowAnalyzer:
    """代码流程分析器"""

    def __init__(self):
        self.flow_nodes = {}
        self.node_counter = 0
        self.analysis_depth = 1  # 分析深度
        self.statement_processor = None  # 延迟初始化
        
    def analyze_main_function_flow(self, main_function_info, depth: int = 1) -> Dict:
        """分析main函数的执行流程"""
        logger.info("🔄 开始分析main函数执行流程...")

        # 重置分析器状态（修复硬编码问题）
        self.flow_nodes = {}
        self.node_counter = 0
        self.analysis_depth = depth
        logger.info(f"设置分析深度: {depth}")

        # 初始化语句处理器
        if self.statement_processor is None:
            from .statement_processor import StatementProcessor
            self.statement_processor = StatementProcessor(self)

        # 读取main函数所在文件
        file_path = Path(main_function_info.file_path)
        logger.info(f"分析文件: {file_path}")
        content = FileUtils.read_file_safe(file_path)
        if not content:
            logger.warning(f"无法读取文件: {file_path}")
            return {}

        # 提取main函数体
        main_body = self._extract_main_function_body(content, main_function_info)
        if not main_body:
            logger.warning(f"无法提取main函数体，签名: {main_function_info.signature}")
            return {}

        logger.info(f"提取到main函数体，长度: {len(main_body)} 字符")

        # 分析函数体的执行流程
        flow_graph = self._analyze_function_body_flow(main_body, main_function_info)

        node_count = len(flow_graph.get('nodes', {}))
        edge_count = len(flow_graph.get('edges', []))
        logger.info(f"✅ 流程分析完成，生成 {node_count} 个节点, {edge_count} 个连接")

        return flow_graph
    
    def _extract_main_function_body(self, content: str, main_function_info) -> str:
        """提取main函数体"""
        # 找到main函数的开始位置
        func_start = content.find(main_function_info.signature)
        if func_start == -1:
            return ""
        
        # 找到函数体开始的大括号
        brace_start = content.find('{', func_start)
        if brace_start == -1:
            return ""
        
        # 匹配大括号找到函数体结束
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
        
        return content[brace_start + 1:brace_end]  # 不包含大括号
    
    def _analyze_function_body_flow(self, function_body: str, main_function_info) -> Dict:
        """分析函数体的执行流程"""
        logger.info("开始分析函数体流程...")
        flow_graph = {
            'nodes': {},
            'edges': [],
            'start_node': None,
            'main_function': main_function_info
        }

        # 创建程序开始节点
        start_node = self._create_start_node()
        flow_graph['nodes'][start_node.node_id] = start_node
        flow_graph['start_node'] = start_node.node_id
        previous_node = start_node.node_id

        # 按行分析代码，生成真正的执行流程
        statements = self._parse_statements(function_body)
        logger.info(f"解析到 {len(statements)} 个语句")

        # 生成执行流程节点
        for stmt in statements:
            nodes, edges = self.statement_processor.process_statement(stmt, previous_node)

            # 添加节点
            for node in nodes:
                flow_graph['nodes'][node.node_id] = node

            # 添加边
            flow_graph['edges'].extend(edges)

            # 更新前一个节点
            if nodes:
                previous_node = nodes[-1].node_id

        return flow_graph

    def _parse_statements(self, function_body: str) -> List[Dict]:
        """解析函数体中的语句，按执行顺序返回"""
        statements = []
        lines = function_body.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 跳过空行和注释
            if not line or line.startswith('//') or line.startswith('/*'):
                i += 1
                continue

            # 识别不同类型的语句
            if self._is_variable_declaration(line):
                statements.append({
                    'type': 'declaration',
                    'content': line,
                    'line_number': i,
                    'original_code': line
                })
                i += 1

            elif line.startswith('while'):
                # while循环
                loop_content, end_line = self._extract_loop_content(lines, i)
                statements.append({
                    'type': 'while_loop',
                    'content': line,
                    'loop_body': loop_content,
                    'line_number': i,
                    'end_line': end_line,
                    'original_code': '\n'.join(lines[i:end_line+1])
                })
                i = end_line + 1

            elif line.startswith('for'):
                # for循环
                loop_content, end_line = self._extract_loop_content(lines, i)
                statements.append({
                    'type': 'for_loop',
                    'content': line,
                    'loop_body': loop_content,
                    'line_number': i,
                    'end_line': end_line,
                    'original_code': '\n'.join(lines[i:end_line+1])
                })
                i = end_line + 1

            elif line.startswith('if'):
                # if条件
                if_content, end_line = self._extract_if_content(lines, i)
                statements.append({
                    'type': 'if_condition',
                    'content': line,
                    'if_body': if_content,
                    'line_number': i,
                    'end_line': end_line,
                    'original_code': '\n'.join(lines[i:end_line+1])
                })
                i = end_line + 1

            else:
                # 普通语句（函数调用、赋值等）
                statements.append({
                    'type': 'statement',
                    'content': line,
                    'line_number': i,
                    'original_code': line
                })
                i += 1

        return statements

    def _is_variable_declaration(self, line: str) -> bool:
        """判断是否是变量声明"""
        # 简单的变量声明识别
        var_types = ['char', 'int', 'float', 'double', 'long', 'short', 'unsigned', 'signed']
        line_clean = line.strip()
        return any(line_clean.startswith(vtype + ' ') for vtype in var_types)

    def _extract_loop_content(self, lines: List[str], start_index: int) -> Tuple[str, int]:
        """提取循环内容"""
        # 找到开始的大括号
        brace_line = start_index
        while brace_line < len(lines) and '{' not in lines[brace_line]:
            brace_line += 1

        if brace_line >= len(lines):
            return "", start_index

        # 匹配大括号
        brace_count = 0
        end_line = brace_line

        for i in range(brace_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{')
            brace_count -= line.count('}')

            if brace_count == 0:
                end_line = i
                break

        # 提取循环体内容（不包含大括号）
        body_lines = []
        for i in range(brace_line + 1, end_line):
            body_lines.append(lines[i])

        return '\n'.join(body_lines), end_line

    def _extract_if_content(self, lines: List[str], start_index: int) -> Tuple[str, int]:
        """提取if内容"""
        return self._extract_loop_content(lines, start_index)

    def _create_start_node(self) -> FlowNode:
        """创建程序开始节点"""
        self.node_counter += 1
        node_id = f"start_{self.node_counter}"

        return FlowNode(
            node_id=node_id,
            node_type='start',
            content='程序开始',
            line_number=0
        )

    def _create_node(self, node_type: str, content: str, line_number: int, original_code: str = "") -> FlowNode:
        """创建流程节点"""
        self.node_counter += 1
        node_id = f"{node_type}_{self.node_counter}"

        return FlowNode(
            node_id=node_id,
            node_type=node_type,
            content=content,
            line_number=line_number,
            original_code=original_code
        )

    def _parse_code_blocks(self, function_body: str) -> List[CodeBlock]:
        """解析代码块结构"""
        blocks = []
        lines = function_body.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('while'):
                # while循环
                block_content, block_end = self._extract_block_content(lines, i)
                blocks.append(CodeBlock('while', i, block_end, block_content))
                i = block_end + 1
                
            elif line.startswith('for'):
                # for循环
                block_content, block_end = self._extract_block_content(lines, i)
                blocks.append(CodeBlock('for', i, block_end, block_content))
                i = block_end + 1
                
            elif line.startswith('if'):
                # if条件
                block_content, block_end = self._extract_block_content(lines, i)
                blocks.append(CodeBlock('if', i, block_end, block_content))
                i = block_end + 1
                
            else:
                # 顺序执行的语句
                seq_lines = []
                start_line = i
                while i < len(lines) and not self._is_control_statement(lines[i].strip()):
                    if lines[i].strip():  # 跳过空行
                        seq_lines.append(lines[i])
                    i += 1
                
                if seq_lines:
                    blocks.append(CodeBlock('sequence', start_line, i-1, '\n'.join(seq_lines)))
        
        return blocks
    
    def _extract_block_content(self, lines: List[str], start_index: int) -> Tuple[str, int]:
        """提取代码块内容"""
        # 找到开始的大括号
        brace_line = start_index
        while brace_line < len(lines) and '{' not in lines[brace_line]:
            brace_line += 1
        
        if brace_line >= len(lines):
            return lines[start_index], start_index
        
        # 匹配大括号
        brace_count = 0
        end_line = brace_line
        
        for i in range(brace_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            if brace_count == 0:
                end_line = i
                break
        
        block_lines = lines[start_index:end_line + 1]
        return '\n'.join(block_lines), end_line
    
    def _is_control_statement(self, line: str) -> bool:
        """判断是否是控制语句"""
        control_keywords = ['if', 'else', 'while', 'for', 'switch', 'do']
        return any(line.startswith(keyword) for keyword in control_keywords)
    
    def _extract_statements(self, content: str) -> List[str]:
        """提取语句"""
        statements = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                # 提取函数调用
                func_calls = re.findall(r'(\w+)\s*\(', line)
                for func_call in func_calls:
                    if func_call not in ['if', 'while', 'for', 'switch']:
                        statements.append(f"{func_call}()")
        
        return statements
    
    def _create_flow_node(self, content: str, line_number: int) -> FlowNode:
        """创建流程节点"""
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"
        
        return FlowNode(
            node_id=node_id,
            node_type='function',
            content=content,
            line_number=line_number
        )
    
    def _create_condition_node(self, content: str, line_number: int) -> FlowNode:
        """创建条件节点"""
        self.node_counter += 1
        node_id = f"cond_{self.node_counter}"
        
        # 提取条件表达式
        condition = self._extract_condition(content)
        
        return FlowNode(
            node_id=node_id,
            node_type='condition',
            content=condition,
            line_number=line_number
        )
    
    def _create_loop_body_node(self, content: str, line_number: int) -> FlowNode:
        """创建循环体节点"""
        self.node_counter += 1
        node_id = f"loop_{self.node_counter}"
        
        # 提取循环体中的函数调用
        statements = self._extract_statements(content)
        loop_content = " → ".join(statements) if statements else "循环体"
        
        return FlowNode(
            node_id=node_id,
            node_type='loop',
            content=loop_content,
            line_number=line_number
        )
    
    def _extract_condition(self, content: str) -> str:
        """提取条件表达式"""
        # 提取while或if后面的条件
        match = re.search(r'(while|if)\s*\(([^)]+)\)', content)
        if match:
            return match.group(2).strip()
        return "条件"
    
    def generate_execution_flowchart(self, flow_graph: Dict) -> str:
        """生成真正的执行流程图"""
        if not flow_graph or 'nodes' not in flow_graph:
            return ""

        mermaid_lines = ["flowchart TD"]

        # 添加节点定义
        for node_id, node in flow_graph['nodes'].items():
            if node.node_type == 'start':
                # 程序开始节点（椭圆）
                mermaid_lines.append(f'    {node_id}(("{node.content}"))')
            elif node.node_type == 'declaration':
                # 变量声明节点（矩形，浅紫色）
                mermaid_lines.append(f'    {node_id}["{node.content}"]')
            elif node.node_type in ['function_call', 'statement']:
                # 函数调用/语句节点（矩形，蓝色）
                mermaid_lines.append(f'    {node_id}["{node.content}"]')
            elif node.node_type in ['output', 'input']:
                # 输入输出节点（矩形，绿色）
                mermaid_lines.append(f'    {node_id}["{node.content}"]')
            elif node.node_type == 'condition':
                # 条件判断节点（菱形，橙色）
                mermaid_lines.append(f'    {node_id}{{{node.content}}}')
            elif node.node_type == 'loop_body':
                # 循环体节点（矩形，浅绿色）
                mermaid_lines.append(f'    {node_id}["{node.content}"]')
            else:
                # 默认节点
                mermaid_lines.append(f'    {node_id}["{node.content}"]')

        # 添加连接关系
        for edge in flow_graph['edges']:
            if len(edge) == 2:
                # 普通连接
                mermaid_lines.append(f'    {edge[0]} --> {edge[1]}')
            elif len(edge) == 3:
                # 带标签的连接
                if edge[2] == 'true':
                    mermaid_lines.append(f'    {edge[0]} -->|是| {edge[1]}')
                elif edge[2] == 'false':
                    mermaid_lines.append(f'    {edge[0]} -->|否| {edge[1]}')
                elif edge[2] == 'loop':
                    mermaid_lines.append(f'    {edge[0]} --> {edge[1]}')

        # 添加样式
        mermaid_lines.extend([
            "",
            "    classDef startNode fill:#E1F5FE,stroke:#0277BD,stroke-width:3px",
            "    classDef declarationNode fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px",
            "    classDef functionNode fill:#E3F2FD,stroke:#1976D2,stroke-width:2px",
            "    classDef conditionNode fill:#FFF3E0,stroke:#F57C00,stroke-width:2px",
            "    classDef loopNode fill:#E8F5E8,stroke:#388E3C,stroke-width:2px",
            "    classDef ioNode fill:#E0F2F1,stroke:#00695C,stroke-width:2px",
            ""
        ])

        # 应用样式
        for node_id, node in flow_graph['nodes'].items():
            if node.node_type == 'start':
                mermaid_lines.append(f"    class {node_id} startNode")
            elif node.node_type == 'declaration':
                mermaid_lines.append(f"    class {node_id} declarationNode")
            elif node.node_type in ['function_call', 'statement']:
                mermaid_lines.append(f"    class {node_id} functionNode")
            elif node.node_type in ['output', 'input']:
                mermaid_lines.append(f"    class {node_id} ioNode")
            elif node.node_type == 'condition':
                mermaid_lines.append(f"    class {node_id} conditionNode")
            elif node.node_type == 'loop_body':
                mermaid_lines.append(f"    class {node_id} loopNode")

        return "\n".join(mermaid_lines)

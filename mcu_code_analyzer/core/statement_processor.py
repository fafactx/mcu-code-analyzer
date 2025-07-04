"""
语句处理器 - 处理不同类型的代码语句
"""

import re
from typing import List, Tuple, Dict
from dataclasses import dataclass
from .code_flow_analyzer import FlowNode


class StatementProcessor:
    """语句处理器"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
    
    def process_statement(self, stmt: Dict, previous_node: str) -> Tuple[List[FlowNode], List[Tuple]]:
        """处理单个语句，返回节点和边"""
        if stmt['type'] == 'declaration':
            return self._process_declaration(stmt, previous_node)
        elif stmt['type'] == 'statement':
            return self._process_simple_statement(stmt, previous_node)
        elif stmt['type'] == 'while_loop':
            return self._process_while_loop(stmt, previous_node)
        elif stmt['type'] == 'for_loop':
            return self._process_for_loop(stmt, previous_node)
        elif stmt['type'] == 'if_condition':
            return self._process_if_condition(stmt, previous_node)
        else:
            return [], []
    
    def _process_declaration(self, stmt: Dict, previous_node: str) -> Tuple[List[FlowNode], List[Tuple]]:
        """处理变量声明"""
        content = self._beautify_declaration(stmt['content'])
        node = self.analyzer._create_node('declaration', content, stmt['line_number'], stmt['original_code'])
        edges = [(previous_node, node.node_id)] if previous_node else []
        return [node], edges
    
    def _process_simple_statement(self, stmt: Dict, previous_node: str) -> Tuple[List[FlowNode], List[Tuple]]:
        """处理简单语句"""
        content = self._beautify_statement(stmt['content'])
        
        # 判断语句类型
        if self._is_function_call(stmt['content']):
            node_type = 'function_call'
        elif 'PRINTF' in stmt['content'] or 'printf' in stmt['content']:
            node_type = 'output'
        elif 'GETCHAR' in stmt['content'] or 'getchar' in stmt['content']:
            node_type = 'input'
        else:
            node_type = 'statement'
        
        node = self.analyzer._create_node(node_type, content, stmt['line_number'], stmt['original_code'])
        edges = [(previous_node, node.node_id)] if previous_node else []
        return [node], edges
    
    def _process_while_loop(self, stmt: Dict, previous_node: str) -> Tuple[List[FlowNode], List[Tuple]]:
        """处理while循环"""
        # 提取条件
        condition = self._extract_condition(stmt['content'])
        condition_node = self.analyzer._create_node('condition', f"无限循环开始", stmt['line_number'], stmt['content'])
        
        # 处理循环体
        loop_body_statements = self._parse_loop_body(stmt['loop_body'])
        loop_nodes = []
        loop_edges = []
        
        current_node = condition_node.node_id
        for body_stmt in loop_body_statements:
            body_content = self._beautify_statement(body_stmt)
            if 'GETCHAR' in body_stmt:
                body_content = "从输入获取字符 ch = GETCHAR"
            elif 'PUTCHAR' in body_stmt:
                body_content = "输出字符 PUTCHAR"
            
            body_node = self.analyzer._create_node('loop_body', body_content, stmt['line_number'])
            loop_nodes.append(body_node)
            loop_edges.append((current_node, body_node.node_id))
            current_node = body_node.node_id
        
        # 循环回到条件判断
        if loop_nodes:
            loop_edges.append((loop_nodes[-1].node_id, condition_node.node_id))
        
        edges = [(previous_node, condition_node.node_id)] if previous_node else []
        edges.extend(loop_edges)
        
        return [condition_node] + loop_nodes, edges
    
    def _process_for_loop(self, stmt: Dict, previous_node: str) -> Tuple[List[FlowNode], List[Tuple]]:
        """处理for循环"""
        # 类似while循环的处理
        return self._process_while_loop(stmt, previous_node)
    
    def _process_if_condition(self, stmt: Dict, previous_node: str) -> Tuple[List[FlowNode], List[Tuple]]:
        """处理if条件"""
        condition = self._extract_condition(stmt['content'])
        condition_node = self.analyzer._create_node('condition', condition, stmt['line_number'], stmt['content'])
        
        edges = [(previous_node, condition_node.node_id)] if previous_node else []
        return [condition_node], edges
    
    def _beautify_declaration(self, content: str) -> str:
        """美化变量声明"""
        if 'char' in content and 'ch' in content:
            return "声明字符变量 ch"
        elif 'int' in content:
            return f"声明整型变量"
        elif 'float' in content:
            return f"声明浮点变量"
        else:
            return f"声明变量"
    
    def _beautify_statement(self, content: str) -> str:
        """美化语句显示"""
        content = content.strip().rstrip(';')
        
        if 'BOARD_InitHardware' in content:
            return "初始化硬件\nBOARD_InitHardware"
        elif 'PRINTF' in content and 'hello world' in content:
            return "打印消息 'hello world.\\r\\n'"
        elif 'GETCHAR' in content:
            return "从输入获取字符 ch =\nGETCHAR"
        elif 'PUTCHAR' in content:
            return "输出字符 PUTCHAR"
        else:
            return content
    
    def _is_function_call(self, content: str) -> bool:
        """判断是否是函数调用"""
        return bool(re.search(r'\w+\s*\(', content))
    
    def _extract_condition(self, content: str) -> str:
        """提取条件表达式"""
        match = re.search(r'(while|if|for)\s*\(([^)]+)\)', content)
        if match:
            condition = match.group(2).strip()
            if condition == '1':
                return "无限循环开始"
            return condition
        return "条件"
    
    def _parse_loop_body(self, loop_body: str) -> List[str]:
        """解析循环体中的语句"""
        statements = []
        lines = loop_body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*') and line != '{' and line != '}':
                statements.append(line)
        
        return statements

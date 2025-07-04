"""
结果查看器 - 显示分析结果的详细界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
from typing import Dict, Any
from pathlib import Path
from utils.logger import logger
from utils.config import config


class ResultViewer:
    """结果查看器类"""
    
    def __init__(self, parent, analysis_result: Dict[str, Any]):
        self.parent = parent
        self.analysis_result = analysis_result
        self.window = tk.Toplevel(parent)
        self.setup_window()
        self.create_widgets()
        self.setup_layout()
        self.load_results()
        self.bind_events()
    
    def setup_window(self):
        """设置窗口属性"""
        self.window.title("分析结果查看器")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # 居中显示
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"1000x700+{x}+{y}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.window, padding="10")
        
        # 标题框架
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_label = ttk.Label(
            self.title_frame,
            text="STM32工程分析结果",
            font=("Microsoft YaHei", 16, "bold")
        )
        
        # 导出按钮
        self.export_btn = ttk.Button(
            self.title_frame,
            text="📄 导出报告",
            command=self.export_report
        )
        
        # 选项卡控件
        self.notebook = ttk.Notebook(self.main_frame)
        
        # 项目概览选项卡
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="📋 项目概览")
        
        # 芯片信息选项卡
        self.chip_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chip_frame, text="🔧 芯片信息")
        
        # 代码分析选项卡
        self.code_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.code_frame, text="💻 代码分析")
        
        # 接口分析选项卡
        self.interface_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.interface_frame, text="🔌 接口分析")
        
        # 智能分析选项卡
        self.ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_frame, text="🤖 智能分析")
        
        # 创建各选项卡内容
        self.create_overview_tab()
        self.create_chip_tab()
        self.create_code_tab()
        self.create_interface_tab()
        self.create_ai_tab()
    
    def create_overview_tab(self):
        """创建项目概览选项卡"""
        # 滚动框架
        canvas = tk.Canvas(self.overview_frame)
        scrollbar = ttk.Scrollbar(self.overview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 项目基本信息
        info_frame = ttk.LabelFrame(scrollable_frame, text="项目基本信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.project_info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.project_info_text.pack(fill=tk.BOTH, expand=True)
        
        # 统计信息
        stats_frame = ttk.LabelFrame(scrollable_frame, text="统计信息", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=10, wrap=tk.WORD, font=("Consolas", 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # 分析摘要
        summary_frame = ttk.LabelFrame(scrollable_frame, text="分析摘要", padding="10")
        summary_frame.pack(fill=tk.BOTH, expand=True)
        
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame, 
            wrap=tk.WORD, 
            font=("Microsoft YaHei", 10)
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_chip_tab(self):
        """创建芯片信息选项卡"""
        # 芯片详细信息
        chip_info_frame = ttk.LabelFrame(self.chip_frame, text="芯片详细信息", padding="10")
        chip_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.chip_info_text = tk.Text(chip_info_frame, height=12, wrap=tk.WORD, font=("Consolas", 10))
        self.chip_info_text.pack(fill=tk.BOTH, expand=True)
        
        # 芯片特性
        chip_features_frame = ttk.LabelFrame(self.chip_frame, text="芯片特性", padding="10")
        chip_features_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chip_features_text = scrolledtext.ScrolledText(
            chip_features_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 10)
        )
        self.chip_features_text.pack(fill=tk.BOTH, expand=True)
    
    def create_code_tab(self):
        """创建代码分析选项卡"""
        # 上部分：函数统计
        functions_frame = ttk.LabelFrame(self.code_frame, text="函数统计", padding="10")
        functions_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.functions_text = tk.Text(functions_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.functions_text.pack(fill=tk.BOTH, expand=True)
        
        # 下部分：调用关系
        calls_frame = ttk.LabelFrame(self.code_frame, text="主要函数调用关系", padding="10")
        calls_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图显示调用关系
        self.calls_tree = ttk.Treeview(calls_frame, columns=("caller", "callee", "file"), show="tree headings")
        self.calls_tree.heading("#0", text="调用关系")
        self.calls_tree.heading("caller", text="调用者")
        self.calls_tree.heading("callee", text="被调用者")
        self.calls_tree.heading("file", text="文件")
        
        calls_scrollbar = ttk.Scrollbar(calls_frame, orient="vertical", command=self.calls_tree.yview)
        self.calls_tree.configure(yscrollcommand=calls_scrollbar.set)
        
        self.calls_tree.pack(side="left", fill="both", expand=True)
        calls_scrollbar.pack(side="right", fill="y")
    
    def create_interface_tab(self):
        """创建接口分析选项卡"""
        # 上部分：接口使用统计
        interface_stats_frame = ttk.LabelFrame(self.interface_frame, text="接口使用统计", padding="10")
        interface_stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.interface_stats_text = tk.Text(
            interface_stats_frame, 
            height=8, 
            wrap=tk.WORD, 
            font=("Consolas", 10)
        )
        self.interface_stats_text.pack(fill=tk.BOTH, expand=True)
        
        # 下部分：详细接口信息
        interface_details_frame = ttk.LabelFrame(self.interface_frame, text="接口详细信息", padding="10")
        interface_details_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图显示接口详情
        self.interface_tree = ttk.Treeview(
            interface_details_frame, 
            columns=("description", "vendor", "functions", "calls"), 
            show="tree headings"
        )
        self.interface_tree.heading("#0", text="接口名称")
        self.interface_tree.heading("description", text="描述")
        self.interface_tree.heading("vendor", text="厂商")
        self.interface_tree.heading("functions", text="函数数量")
        self.interface_tree.heading("calls", text="调用次数")
        
        interface_scrollbar = ttk.Scrollbar(
            interface_details_frame, 
            orient="vertical", 
            command=self.interface_tree.yview
        )
        self.interface_tree.configure(yscrollcommand=interface_scrollbar.set)
        
        self.interface_tree.pack(side="left", fill="both", expand=True)
        interface_scrollbar.pack(side="right", fill="y")
    
    def create_ai_tab(self):
        """创建智能分析选项卡"""
        # 代码总结
        summary_frame = ttk.LabelFrame(self.ai_frame, text="代码总结", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ai_summary_text = scrolledtext.ScrolledText(
            summary_frame,
            height=8,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 10)
        )
        self.ai_summary_text.pack(fill=tk.BOTH, expand=True)
        
        # 语义分析结果
        semantic_frame = ttk.LabelFrame(self.ai_frame, text="语义分析", padding="10")
        semantic_frame.pack(fill=tk.BOTH, expand=True)
        
        self.semantic_text = scrolledtext.ScrolledText(
            semantic_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 10)
        )
        self.semantic_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_layout(self):
        """设置布局"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题框架
        self.title_frame.pack(fill=tk.X, pady=(0, 10))
        self.title_label.pack(side=tk.LEFT)
        self.export_btn.pack(side=tk.RIGHT)
        
        # 选项卡
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def bind_events(self):
        """绑定事件"""
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_results(self):
        """加载分析结果"""
        try:
            self.load_overview_data()
            self.load_chip_data()
            self.load_code_data()
            self.load_interface_data()
            self.load_ai_data()
        except Exception as e:
            logger.error(f"加载分析结果失败: {e}")
            messagebox.showerror("错误", f"加载分析结果失败: {e}")
    
    def load_overview_data(self):
        """加载项目概览数据"""
        project_info = self.analysis_result.get('project_info')
        if project_info:
            info_text = f"""项目名称: {project_info.name}
项目类型: {project_info.type.upper()}
编译器: {project_info.compiler}
源文件数量: {len(project_info.source_files)}
头文件数量: {len(project_info.header_files)}
包含路径数量: {len(project_info.include_paths)}
预定义宏数量: {len(project_info.defines)}
目标名称: {project_info.target_name or '未指定'}"""
            
            self.project_info_text.insert(tk.END, info_text)
            self.project_info_text.config(state=tk.DISABLED)
        
        # 统计信息
        code_analysis = self.analysis_result.get('code_analysis', {})
        function_stats = code_analysis.get('function_stats', {})
        call_stats = code_analysis.get('call_stats', {})
        
        stats_text = f"""=== 函数统计 ===
总函数数量: {function_stats.get('total_functions', 0)}
已定义函数: {function_stats.get('defined_functions', 0)}
声明函数: {function_stats.get('declared_functions', 0)}
静态函数: {function_stats.get('static_functions', 0)}
内联函数: {function_stats.get('inline_functions', 0)}
main可达函数: {function_stats.get('main_reachable', 0)}

=== 调用统计 ===
总调用次数: {call_stats.get('total_calls', 0)}
调用者数量: {call_stats.get('unique_callers', 0)}
被调用者数量: {call_stats.get('unique_callees', 0)}"""
        
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)
        
        # 分析摘要
        summary = "项目分析已完成。这是一个STM32嵌入式项目，包含了完整的代码结构分析、接口使用分析和智能语义分析。"
        if 'code_summary' in self.analysis_result:
            code_summary = self.analysis_result['code_summary']
            if hasattr(code_summary, 'project_overview'):
                summary = code_summary.project_overview or summary
        
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)
    
    def load_chip_data(self):
        """加载芯片数据"""
        chip_info = self.analysis_result.get('chip_info')
        if chip_info:
            chip_summary = chip_info.get_chip_summary()
            
            chip_text = ""
            for key, value in chip_summary.items():
                chip_text += f"{key}: {value}\n"
            
            self.chip_info_text.insert(tk.END, chip_text)
            self.chip_info_text.config(state=tk.DISABLED)
            
            # 芯片特性
            features_text = f"""该芯片是{chip_summary.get('厂商', '未知')}生产的{chip_summary.get('系列', '未知')}系列微控制器。

主要特性：
• CPU内核：{chip_summary.get('CPU内核', '未知')}
• Flash容量：{chip_summary.get('Flash大小', '未知')}
• RAM容量：{chip_summary.get('RAM大小', '未知')}
• 工作频率：{chip_summary.get('主频', '未知')}
• 封装类型：{chip_summary.get('封装', '未知')}

适用场景：
• 嵌入式控制系统
• 物联网设备
• 工业自动化
• 消费电子产品"""
            
            self.chip_features_text.insert(tk.END, features_text)
            self.chip_features_text.config(state=tk.DISABLED)
    
    def load_code_data(self):
        """加载代码分析数据"""
        code_analysis = self.analysis_result.get('code_analysis', {})
        
        # 函数统计详情
        functions = code_analysis.get('functions', {})
        if functions:
            func_text = "主要函数列表：\n\n"
            for i, (func_name, func_info) in enumerate(list(functions.items())[:20]):
                func_text += f"{i+1:2d}. {func_name}\n"
                func_text += f"    文件: {Path(func_info.file_path).name}\n"
                func_text += f"    行号: {func_info.line_number}\n"
                func_text += f"    类型: {'定义' if func_info.is_definition else '声明'}\n"
                if func_info.is_static:
                    func_text += f"    修饰: static\n"
                func_text += "\n"
            
            if len(functions) > 20:
                func_text += f"... 还有 {len(functions) - 20} 个函数\n"
            
            self.functions_text.insert(tk.END, func_text)
            self.functions_text.config(state=tk.DISABLED)
        
        # 调用关系树
        call_relations = code_analysis.get('call_relations', [])
        main_calls = [rel for rel in call_relations if rel.caller == 'main'][:20]
        
        for i, relation in enumerate(main_calls):
            item_id = self.calls_tree.insert(
                "", 
                tk.END, 
                text=f"调用 {i+1}",
                values=(relation.caller, relation.callee, Path(relation.file_path).name)
            )
    
    def load_interface_data(self):
        """加载接口分析数据"""
        interface_usage = self.analysis_result.get('interface_usage', {})
        
        # 接口统计
        enabled_interfaces = {
            name: info for name, info in interface_usage.items() 
            if getattr(info, 'enabled', False)
        }
        
        stats_text = f"检测到 {len(enabled_interfaces)} 个启用的接口：\n\n"
        
        vendor_count = {}
        for name, info in enabled_interfaces.items():
            vendor = getattr(info, 'vendor', 'Unknown')
            vendor_count[vendor] = vendor_count.get(vendor, 0) + 1
            
            func_count = len(getattr(info, 'functions', set()))
            call_count = getattr(info, 'call_count', 0)
            stats_text += f"• {name}: {func_count} 个函数, {call_count} 次调用\n"
        
        stats_text += f"\n厂商分布：\n"
        for vendor, count in vendor_count.items():
            stats_text += f"• {vendor}: {count} 个接口\n"
        
        self.interface_stats_text.insert(tk.END, stats_text)
        self.interface_stats_text.config(state=tk.DISABLED)
        
        # 接口详情树
        for name, info in enabled_interfaces.items():
            func_count = len(getattr(info, 'functions', set()))
            call_count = getattr(info, 'call_count', 0)
            description = getattr(info, 'description', name)
            vendor = getattr(info, 'vendor', 'Unknown')
            
            self.interface_tree.insert(
                "",
                tk.END,
                text=name,
                values=(description, vendor, func_count, call_count)
            )
    
    def load_ai_data(self):
        """加载AI分析数据"""
        # 代码总结
        code_summary = self.analysis_result.get('code_summary')
        if code_summary:
            summary_text = f"""项目概述：{getattr(code_summary, 'project_overview', '待分析')}

主要功能：{getattr(code_summary, 'main_functionality', '待分析')}

复杂度分析：{getattr(code_summary, 'complexity_analysis', '待分析')}

优化建议：
"""
            suggestions = getattr(code_summary, 'optimization_suggestions', [])
            for i, suggestion in enumerate(suggestions, 1):
                summary_text += f"{i}. {suggestion}\n"
            
            self.ai_summary_text.insert(tk.END, summary_text)
            self.ai_summary_text.config(state=tk.DISABLED)
        
        # 语义分析
        semantic_analysis = self.analysis_result.get('semantic_analysis')
        if semantic_analysis:
            semantic_text = f"""可维护性评分：{semantic_analysis.maintainability_score:.1f}/100

检测到的架构模式：
"""
            for pattern in semantic_analysis.architectural_patterns:
                semantic_text += f"• {pattern.pattern_type} (置信度: {pattern.confidence:.2f})\n"
                semantic_text += f"  {pattern.description}\n\n"
            
            if semantic_analysis.performance_bottlenecks:
                semantic_text += "性能瓶颈：\n"
                for bottleneck in semantic_analysis.performance_bottlenecks:
                    semantic_text += f"• {bottleneck}\n"
            
            if semantic_analysis.security_concerns:
                semantic_text += "\n安全性问题：\n"
                for concern in semantic_analysis.security_concerns:
                    semantic_text += f"• {concern}\n"
            
            self.semantic_text.insert(tk.END, semantic_text)
            self.semantic_text.config(state=tk.DISABLED)
    
    def export_report(self):
        """导出报告"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="导出分析报告",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if file_path:
                if file_path.endswith('.json'):
                    self.export_json_report(file_path)
                else:
                    self.export_text_report(file_path)
                
                messagebox.showinfo("成功", f"报告已导出到：{file_path}")
                
        except Exception as e:
            logger.error(f"导出报告失败: {e}")
            messagebox.showerror("错误", f"导出报告失败: {e}")
    
    def export_text_report(self, file_path: str):
        """导出文本报告"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("STM32工程分析报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 项目信息
            f.write("项目信息\n")
            f.write("-" * 20 + "\n")
            f.write(self.project_info_text.get(1.0, tk.END))
            f.write("\n")
            
            # 统计信息
            f.write("统计信息\n")
            f.write("-" * 20 + "\n")
            f.write(self.stats_text.get(1.0, tk.END))
            f.write("\n")
            
            # 其他内容...
    
    def export_json_report(self, file_path: str):
        """导出JSON报告"""
        # 简化的JSON导出
        report_data = {
            'project_name': self.analysis_result.get('project_info', {}).name if self.analysis_result.get('project_info') else 'Unknown',
            'analysis_timestamp': str(Path().cwd()),
            'summary': 'Analysis completed'
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    def update_results(self, new_results: Dict[str, Any]):
        """更新结果"""
        self.analysis_result = new_results
        # 清空现有内容并重新加载
        # 这里可以实现更精细的更新逻辑
        self.load_results()
    
    def on_closing(self):
        """窗口关闭事件"""
        self.window.destroy()

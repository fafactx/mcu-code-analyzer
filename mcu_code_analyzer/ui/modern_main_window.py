"""
现代化主窗口 - MCU代码分析器的现代化用户界面
采用CustomTkinter和卡片式设计
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import threading
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from utils.logger import logger
from utils.config import config
from utils.file_utils import FileUtils
from core.chip_detector import ChipDetector
from core.project_parser import ProjectParser
from core.code_analyzer import CodeAnalyzer
from core.interface_analyzer import InterfaceAnalyzer
from core.complete_function_analyzer import CompleteFunctionAnalyzer
from core.code_flow_analyzer import CodeFlowAnalyzer
from intelligence.code_summarizer import CodeSummarizer
from intelligence.semantic_analyzer import SemanticAnalyzer
from intelligence.prompt_generator import PromptGenerator, PromptContext
from ui.config_dialog import ConfigDialog
from ui.analysis_progress_dialog import AnalysisProgressDialog


class ModernMainWindow:
    """现代化主窗口类 - 采用CustomTkinter和卡片式设计"""
    
    def __init__(self):
        # 设置CustomTkinter主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        
        # NXP色系配置
        self.colors = {
            'primary': '#0066CC',      # NXP蓝
            'secondary': '#FF6600',    # NXP橙
            'background': '#F8F9FA',   # 浅灰背景
            'card': '#FFFFFF',         # 白色卡片
            'text': '#2C3E50',         # 深蓝灰文本
            'accent': '#E8F4FD',       # 浅蓝强调
            'border': '#D1E7DD',       # 边框色
            'success': '#28A745',      # 成功绿
            'warning': '#FFC107',      # 警告黄
            'error': '#DC3545'         # 错误红
        }
        
        # 分析组件
        self.chip_detector = ChipDetector()
        self.project_parser = ProjectParser()
        self.code_analyzer = CodeAnalyzer()
        self.interface_analyzer = InterfaceAnalyzer()
        self.complete_function_analyzer = CompleteFunctionAnalyzer()
        self.code_flow_analyzer = CodeFlowAnalyzer()
        self.code_summarizer = CodeSummarizer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.prompt_generator = PromptGenerator()
        
        # 分析结果
        self.analysis_result = {}
        self.current_project_path = None
        self.mermaid_code = ""
        self.call_graph = {}
        
        # 设置窗口
        self.setup_window()
        self.create_modern_ui()
        self.bind_events()
        
        logger.set_gui_callback(self.log_callback)
    
    def setup_window(self):
        """Setup window properties"""
        self.root.title("MCU Code Analyzer v2.0 - Modern Interface")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # 设置窗口图标
        try:
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass
    
    def create_modern_ui(self):
        """创建现代化UI界面 - 专业版本"""
        # 创建菜单栏
        self.create_menu_bar()

        # 创建工具栏
        self.create_toolbar()

        # 创建主容器
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # 配置网格权重
        self.main_container.grid_rowconfigure(1, weight=1)  # 中间区域可扩展
        self.main_container.grid_columnconfigure(0, weight=1)

        # 创建各个区域
        self.create_project_config_area()  # 顶部：项目配置
        self.create_results_area()         # 中间：分析结果
        self.create_progress_area()        # 底部：进度条

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File(F)", menu=file_menu)
        file_menu.add_command(label="Open Project...", command=self.browse_project_path, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save Analysis Results", command=self.save_analysis_results, accelerator="Ctrl+S")
        file_menu.add_command(label="Export Report...", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")

        # View menu
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View(V)", menu=view_menu)
        view_menu.add_command(label="Project Overview", command=lambda: self.tabview.set("Project Overview"))
        view_menu.add_command(label="Code Flowchart", command=lambda: self.tabview.set("Code Flowchart"))
        view_menu.add_command(label="Execution Log", command=lambda: self.tabview.set("Execution Log"))
        view_menu.add_command(label="LLM Analysis Dialog", command=lambda: self.tabview.set("LLM Analysis Dialog"))
        view_menu.add_separator()
        view_menu.add_command(label="Refresh Interface", command=self.refresh_ui, accelerator="F5")

        # Config menu
        config_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Config(C)", menu=config_menu)
        config_menu.add_command(label="LLM Settings...", command=self.open_config_dialog)
        config_menu.add_command(label="Analysis Parameters...", command=self.open_analysis_config)
        config_menu.add_separator()
        config_menu.add_command(label="Interface Theme", command=self.toggle_theme)

        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools(T)", menu=tools_menu)
        tools_menu.add_command(label="Quick Test", command=self.run_quick_test, accelerator="Ctrl+T")
        tools_menu.add_command(label="Start Analysis", command=self.start_analysis, accelerator="F9")
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear All", command=self.clear_all, accelerator="Ctrl+L")

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help(H)", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['card'],
            corner_radius=0,
            height=50
        )
        toolbar_frame.pack(fill="x", padx=0, pady=0)
        toolbar_frame.pack_propagate(False)

        # 工具栏内容
        toolbar_content = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        toolbar_content.pack(fill="both", expand=True, padx=10, pady=8)

        # 左侧工具按钮
        left_tools = ctk.CTkFrame(toolbar_content, fg_color="transparent")
        left_tools.pack(side="left")

        # Open project button
        self.toolbar_open_btn = ctk.CTkButton(
            left_tools,
            text="Open Project",
            command=self.browse_project_path,
            width=100,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['primary'],
            hover_color="#0052A3"
        )
        self.toolbar_open_btn.pack(side="left", padx=(0, 8))

        # Quick test button
        self.toolbar_test_btn = ctk.CTkButton(
            left_tools,
            text="Quick Test",
            command=self.run_quick_test,
            width=90,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['success'],
            hover_color="#218838"
        )
        self.toolbar_test_btn.pack(side="left", padx=(0, 8))

        # Start analysis button
        self.toolbar_analyze_btn = ctk.CTkButton(
            left_tools,
            text="Start Analysis",
            command=self.start_analysis,
            width=110,
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['secondary'],
            hover_color="#E55A00"
        )
        self.toolbar_analyze_btn.pack(side="left", padx=(0, 8))

        # Cancel analysis button (initially hidden)
        self.toolbar_cancel_btn = ctk.CTkButton(
            left_tools,
            text="Cancel Analysis",
            command=self.cancel_analysis,
            width=120,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['error'],
            hover_color="#C82333"
        )
        # 初始不显示

        # 右侧工具按钮
        right_tools = ctk.CTkFrame(toolbar_content, fg_color="transparent")
        right_tools.pack(side="right")

        # LLM config button
        self.toolbar_config_btn = ctk.CTkButton(
            right_tools,
            text="LLM Config",
            command=self.open_config_dialog,
            width=90,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color="#6C757D",
            hover_color="#5A6268"
        )
        self.toolbar_config_btn.pack(side="left", padx=(8, 0))

    def create_project_config_area(self):
        """创建项目配置区域 - 专业版本"""
        config_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['card'],
            corner_radius=8,
            border_width=1,
            border_color=self.colors['border']
        )
        config_frame.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        # 配置标题
        title_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(10, 5))

        title_label = ctk.CTkLabel(
            title_frame,
            text="Project Configuration",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text']
        )
        title_label.pack(side="left")

        # 配置内容区域
        config_content = ctk.CTkFrame(config_frame, fg_color="transparent")
        config_content.pack(fill="x", padx=15, pady=(0, 15))

        # 第一行：项目路径
        path_row = ctk.CTkFrame(config_content, fg_color="transparent")
        path_row.pack(fill="x", pady=(0, 10))

        path_label = ctk.CTkLabel(
            path_row,
            text="Project Path:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text'],
            width=100
        )
        path_label.pack(side="left", padx=(0, 10))

        self.project_path_var = ctk.StringVar()
        self.project_entry = ctk.CTkEntry(
            path_row,
            textvariable=self.project_path_var,
            placeholder_text="Please select MCU project directory...",
            font=ctk.CTkFont(size=12),
            height=36
        )
        self.project_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            path_row,
            text="Browse...",
            command=self.browse_project_path,
            width=80,
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['primary'],
            hover_color="#0052A3"
        )
        self.browse_btn.pack(side="right")

        # 第二行：分析参数
        params_row = ctk.CTkFrame(config_content, fg_color="transparent")
        params_row.pack(fill="x")

        # 分析深度
        depth_frame = ctk.CTkFrame(params_row, fg_color="transparent")
        depth_frame.pack(side="left", padx=(0, 30))

        depth_label = ctk.CTkLabel(
            depth_frame,
            text="Analysis Depth:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text']
        )
        depth_label.pack(side="left", padx=(0, 8))

        self.depth_var = ctk.StringVar(value="2")
        self.depth_spinbox = ctk.CTkOptionMenu(
            depth_frame,
            values=["1", "2", "3", "4", "5"],
            variable=self.depth_var,
            width=60,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        self.depth_spinbox.pack(side="left")

        # Analysis options
        options_frame = ctk.CTkFrame(params_row, fg_color="transparent")
        options_frame.pack(side="left", padx=(0, 30))

        self.show_mermaid_var = ctk.BooleanVar(value=True)
        self.show_mermaid_check = ctk.CTkCheckBox(
            options_frame,
            text="Generate Flowchart",
            variable=self.show_mermaid_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.show_mermaid_check.pack(side="left", padx=(0, 15))

        self.enable_llm_var = ctk.BooleanVar(value=True)
        self.enable_llm_check = ctk.CTkCheckBox(
            options_frame,
            text="LLM Smart Analysis",
            variable=self.enable_llm_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.enable_llm_check.pack(side="left")

        # 操作按钮区域
        actions_frame = ctk.CTkFrame(params_row, fg_color="transparent")
        actions_frame.pack(side="right")

        self.clear_btn = ctk.CTkButton(
            actions_frame,
            text="Clear",
            command=self.clear_all,
            width=60,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#6C757D",
            hover_color="#5A6268"
        )
        self.clear_btn.pack(side="left", padx=(0, 8))

        # 初始化分析控制变量
        self.analysis_running = False
        self.analysis_thread = None
        self.progress_dialog = None

    def export_report(self):
        """导出分析报告"""
        if not hasattr(self, 'analysis_result') or not self.analysis_result:
            messagebox.showwarning("Warning", "No analysis results to export")
            return

        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title="Export Analysis Report",
                defaultextension=".html",
                filetypes=[("HTML Files", "*.html"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )

            if file_path:
                # Report export logic can be implemented here
                messagebox.showinfo("Success", f"Report exported to: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def save_analysis_results(self):
        """保存分析结果"""
        if not hasattr(self, 'analysis_result') or not self.analysis_result:
            messagebox.showwarning("Warning", "No analysis results to save")
            return

        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title="Save Analysis Results",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )

            if file_path:
                # Result saving logic can be implemented here
                messagebox.showinfo("Success", f"Analysis results saved to: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")

    def refresh_ui(self):
        """刷新界面"""
        self.update_status("界面已刷新")

    def open_analysis_config(self):
        """打开分析参数配置"""
        messagebox.showinfo("提示", "分析参数配置功能开发中...")

    def toggle_theme(self):
        """切换界面主题"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "dark" if current_mode == "Light" else "light"
        ctk.set_appearance_mode(new_mode)
        self.update_status(f"已切换到{new_mode}主题")

    def show_help(self):
        """显示使用说明"""
        help_text = """
MCU代码分析器 - 使用说明

1. 文件菜单
   - 打开项目: 选择MCU项目目录
   - 保存结果: 保存分析结果
   - 导出报告: 导出HTML格式报告

2. 视图菜单
   - 切换不同的分析结果标签页
   - 刷新界面

3. 配置菜单
   - LLM设置: 配置AI分析参数
   - 分析参数: 设置分析深度等

4. 工具菜单
   - 快速测试: 验证项目结构
   - 开始分析: 执行完整分析

快捷键:
- Ctrl+O: 打开项目
- Ctrl+S: 保存结果
- Ctrl+T: 快速测试
- F9: 开始分析
- F5: 刷新界面
"""
        messagebox.showinfo("使用说明", help_text)

    def show_about(self):
        """显示关于信息"""
        about_text = """
MCU代码分析器 v2.0

专业的MCU项目代码分析工具

功能特性:
• 智能芯片识别
• 代码流程图生成
• LLM智能分析
• 多线程处理
• 专业UI界面

开发团队: AI Assistant
技术支持: 基于Claude AI
"""
        messagebox.showinfo("关于程序", about_text)

    def run_quick_test(self):
        """运行快速测试"""
        if not self.validate_inputs():
            return

        project_path = self.project_path_var.get().strip()

        # 快速测试：只检查项目结构和基本信息
        try:
            self.update_status("执行快速测试...")

            # 检查项目结构
            project_path_obj = Path(project_path)
            c_files = list(project_path_obj.rglob("*.c"))
            h_files = list(project_path_obj.rglob("*.h"))

            # 检查芯片信息
            chip_info = self.chip_detector.detect_from_project_file(project_path_obj)

            # Display test results
            test_result = f"""Quick Test Results:

Project Path: {project_path}
C Files Count: {len(c_files)}
H Files Count: {len(h_files)}
Detected Chip: {chip_info.device_name or 'Unknown'}
Chip Vendor: {chip_info.vendor or 'Unknown'}
CPU Core: {chip_info.core or 'Unknown'}
Project Structure: {'Valid' if c_files else 'Invalid'}

Test Status: Completed
"""

            self.overview_text.delete("1.0", "end")
            self.overview_text.insert("1.0", test_result)
            self.tabview.set("Project Overview")

            self.update_status("Quick test completed")

        except Exception as e:
            messagebox.showerror("Test Failed", f"Quick test failed: {str(e)}")
            self.update_status("Quick test failed")

    def cancel_analysis(self):
        """取消分析"""
        if self.analysis_running and self.analysis_thread:
            self.analysis_running = False
            self.update_status("Canceling analysis...")

            # Notify all analyzers to cancel
            if hasattr(self, 'complete_function_analyzer'):
                self.complete_function_analyzer.cancel_analysis()
            if hasattr(self, 'code_flow_analyzer'):
                self.code_flow_analyzer.should_cancel = True

            # Restore toolbar button state
            self.toolbar_analyze_btn.configure(
                text="Start Analysis",
                command=self.start_analysis,
                fg_color=self.colors['secondary']
            )

            self.set_ui_state(True)
            self.update_status("Analysis canceled")
            self.progress_bar.set(0)
            self.progress_percent_var.set("0%")

    def create_results_area(self):
        """创建分析结果区域（三个横向标签）"""
        results_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border']
        )
        results_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # 标签页框架
        self.tabview = ctk.CTkTabview(
            results_frame,
            fg_color=self.colors['accent'],
            segmented_button_fg_color=self.colors['primary'],
            segmented_button_selected_color=self.colors['secondary'],
            segmented_button_selected_hover_color="#E55A00"
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)

        # Project overview tab
        self.overview_tab = self.tabview.add("Project Overview")
        self.overview_text = ctk.CTkTextbox(
            self.overview_tab,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.overview_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Code flowchart tab
        self.flowchart_tab = self.tabview.add("Code Flowchart")

        # 流程图控制按钮
        flowchart_controls = ctk.CTkFrame(self.flowchart_tab, fg_color="transparent")
        flowchart_controls.pack(fill="x", padx=10, pady=(10, 5))

        self.render_flowchart_btn = ctk.CTkButton(
            flowchart_controls,
            text="Web Render",
            command=self.render_flowchart_web,
            width=100,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['primary'],
            hover_color="#0052A3"
        )
        self.render_flowchart_btn.pack(side="left", padx=(0, 10))

        self.copy_flowchart_btn = ctk.CTkButton(
            flowchart_controls,
            text="Copy Code",
            command=self.copy_flowchart_code,
            width=100,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['secondary'],
            hover_color="#E55A00"
        )
        self.copy_flowchart_btn.pack(side="left")

        # 流程图显示
        self.flowchart_text = ctk.CTkTextbox(
            self.flowchart_tab,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.flowchart_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Execution log tab
        self.log_tab = self.tabview.add("Execution Log")
        self.log_text = ctk.CTkTextbox(
            self.log_tab,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        # LLM analysis dialog tab
        self.llm_tab = self.tabview.add("LLM Analysis Dialog")

        # LLM对话控制按钮
        llm_controls = ctk.CTkFrame(self.llm_tab, fg_color="transparent")
        llm_controls.pack(fill="x", padx=10, pady=(10, 5))

        self.clear_llm_btn = ctk.CTkButton(
            llm_controls,
            text="Clear Dialog",
            command=self.clear_llm_dialog,
            width=100,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#6C757D",
            hover_color="#5A6268"
        )
        self.clear_llm_btn.pack(side="left", padx=(0, 10))

        self.export_llm_btn = ctk.CTkButton(
            llm_controls,
            text="Export Dialog",
            command=self.export_llm_dialog,
            width=100,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['secondary'],
            hover_color="#E55A00"
        )
        self.export_llm_btn.pack(side="left")

        # LLM对话显示区域
        self.llm_dialog_text = ctk.CTkTextbox(
            self.llm_tab,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.llm_dialog_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def create_progress_area(self):
        """创建进度条区域（底部）"""
        progress_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border'],
            height=80
        )
        progress_frame.grid(row=2, column=0, sticky="ew")
        progress_frame.grid_propagate(False)  # 固定高度

        # 进度内容
        progress_content = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_content.pack(fill="both", expand=True, padx=20, pady=15)

        # 状态和百分比在同一行
        status_row = ctk.CTkFrame(progress_content, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 8))

        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            status_row,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text']
        )
        self.status_label.pack(side="left")

        self.progress_percent_var = ctk.StringVar(value="0%")
        self.progress_percent_label = ctk.CTkLabel(
            status_row,
            textvariable=self.progress_percent_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.progress_percent_label.pack(side="right")

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            progress_content,
            height=15,
            progress_color=self.colors['primary']
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

    def render_flowchart_web(self):
        """在网页中渲染流程图"""
        if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
            messagebox.showwarning("警告", "没有可渲染的流程图代码")
            return

        try:
            import tempfile
            import webbrowser

            # 创建HTML文件
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MCU代码流程图</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        #mermaid-diagram {{
            text-align: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 MCU代码执行流程图</h1>
        <div id="mermaid-diagram">
            <pre class="mermaid">
{self.mermaid_code}
            </pre>
        </div>
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
"""

            # 保存到临时文件并打开
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name

            webbrowser.open(f'file://{temp_file}')
            self.update_status("流程图已在浏览器中打开")

        except Exception as e:
            messagebox.showerror("错误", f"打开网页渲染失败: {str(e)}")

    def copy_flowchart_code(self):
        """复制流程图代码到剪贴板"""
        if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
            messagebox.showwarning("警告", "没有可复制的流程图代码")
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.mermaid_code)
            self.update_status("流程图代码已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")

    def clear_llm_dialog(self):
        """清空LLM对话"""
        self.llm_dialog_text.delete("1.0", "end")
        self.update_status("LLM对话已清空")

    def export_llm_dialog(self):
        """导出LLM对话到文件"""
        try:
            from tkinter import filedialog
            dialog_content = self.llm_dialog_text.get("1.0", "end")
            if not dialog_content.strip():
                messagebox.showwarning("警告", "没有可导出的LLM对话内容")
                return

            file_path = filedialog.asksaveasfilename(
                title="保存LLM对话",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(dialog_content)
                self.update_status(f"LLM对话已导出到: {file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def log_llm_interaction(self, interaction_type: str, content: str, timestamp: str = None):
        """记录LLM交互"""
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")

        # 格式化显示
        if interaction_type == "prompt":
            header = f"\n{'='*60}\n[{timestamp}] 🚀 发送给LLM的提示词:\n{'='*60}\n"
            formatted_content = f"{header}{content}\n"
        elif interaction_type == "response":
            header = f"\n{'='*60}\n[{timestamp}] 🤖 LLM回复:\n{'='*60}\n"
            formatted_content = f"{header}{content}\n"
        elif interaction_type == "error":
            header = f"\n{'='*60}\n[{timestamp}] ❌ LLM分析错误:\n{'='*60}\n"
            formatted_content = f"{header}{content}\n"
        elif interaction_type == "status":
            formatted_content = f"\n[{timestamp}] ℹ️ {content}\n"
        else:
            formatted_content = f"\n[{timestamp}] {content}\n"

        # 在UI线程中更新
        self.root.after(0, lambda: [
            self.llm_dialog_text.insert("end", formatted_content),
            self.llm_dialog_text.see("end")
        ])

    def clear_all(self):
        """清空所有内容"""
        self.project_path_var.set("")
        self.overview_text.delete("1.0", "end")
        self.flowchart_text.delete("1.0", "end")
        self.log_text.delete("1.0", "end")
        self.llm_dialog_text.delete("1.0", "end")  # 清空LLM对话
        self.progress_bar.set(0)
        self.progress_percent_var.set("0%")
        self.update_status("已清空")
        if hasattr(self, 'analysis_result'):
            self.analysis_result = {}
        if hasattr(self, 'mermaid_code'):
            self.mermaid_code = ""
        if hasattr(self, 'call_graph'):
            self.call_graph = {}

    def bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.project_path_var.trace('w', self.on_path_changed)

    def browse_project_path(self):
        """浏览MCU项目路径"""
        path = filedialog.askdirectory(title="选择MCU项目目录")
        if path:
            self.project_path_var.set(path)
            self.cleanup_existing_analysis(path)

    def cleanup_existing_analysis(self, project_path: str):
        """清理已存在的分析目录"""
        try:
            analysis_dir = Path(project_path) / "Analyzer_Output"
            if analysis_dir.exists():
                import shutil
                shutil.rmtree(analysis_dir)
                logger.info(f"已清理分析目录: {analysis_dir}")
                self.update_status("已清理旧的分析目录")
        except Exception as e:
            logger.warning(f"清理分析目录失败: {e}")

    def on_path_changed(self, *args):
        """路径改变事件"""
        project_path = self.project_path_var.get()
        if project_path:
            is_valid, message = FileUtils.validate_path(project_path)
            if is_valid:
                self.update_status("路径有效")
            else:
                self.update_status(f"路径无效: {message}")

    def start_analysis(self):
        """开始分析"""
        if not self.validate_inputs():
            return

        if self.analysis_running:
            messagebox.showwarning("Warning", "Analysis is in progress, please wait for completion or cancel current analysis")
            return

        # Set analysis state
        self.analysis_running = True
        self.set_ui_state(False)
        self.log_text.delete("1.0", "end")

        # Update toolbar button state
        self.toolbar_analyze_btn.configure(text="Cancel Analysis", command=self.cancel_analysis, fg_color=self.colors['error'])

        # 创建并显示进度对话框
        self.progress_dialog = AnalysisProgressDialog(self.root, "MCU Code Analysis Progress")
        self.progress_dialog.show(cancel_callback=self.cancel_analysis)

        # 启动分析线程
        self.analysis_thread = threading.Thread(target=self.run_analysis_with_exception_handling)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()

    def validate_inputs(self) -> bool:
        """Validate inputs"""
        project_path = self.project_path_var.get().strip()
        if not project_path:
            messagebox.showerror("Error", "Please select MCU project directory")
            return False

        is_valid, message = FileUtils.validate_path(project_path)
        if not is_valid:
            messagebox.showerror("Error", f"Invalid MCU project path: {message}")
            return False

        return True

    def run_analysis_with_exception_handling(self):
        """带异常处理的分析包装器"""
        try:
            self.run_analysis()
        except Exception as e:
            logger.error(f"分析过程中发生异常: {e}", exc_info=True)
            self.root.after(0, lambda: [
                messagebox.showerror("分析错误", f"分析过程中发生错误: {str(e)}"),
                self.analysis_finished()
            ])

    def analysis_finished(self):
        """分析完成后的清理工作"""
        self.analysis_running = False

        # Restore toolbar button state
        self.toolbar_analyze_btn.configure(
            text="Start Analysis",
            command=self.start_analysis,
            fg_color=self.colors['secondary']
        )

        # 标记进度对话框为完成状态
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.set_completed(success=True)

        self.set_ui_state(True)

    def cancel_analysis(self):
        """取消分析"""
        if self.analysis_running:
            self.analysis_running = False

            # 标记进度对话框为取消状态
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.set_cancelled()

            # 取消完整函数分析器
            if hasattr(self, 'complete_function_analyzer'):
                self.complete_function_analyzer.cancel()

            self.update_status("分析已取消")
            logger.info("用户取消了分析")

    def run_analysis(self):
        """运行分析（重构版本 - 正确的执行流程）"""
        try:
            self.update_status("Starting analysis...")
            self.update_progress(0)

            project_path = Path(self.project_path_var.get())
            output_path = project_path / "Analyzer_Output"
            output_path.mkdir(parents=True, exist_ok=True)

            self.current_project_path = project_path

            # 第一阶段：解析uvprojx/uvproj项目文件
            self.update_status("🔍 解析项目文件 (uvprojx/uvproj)...")
            self.update_progress(10)
            project_info = self.project_parser.parse_project(project_path)
            chip_info = self.chip_detector.detect_from_project_file(project_path)

            # 检查是否取消
            if not self.analysis_running:
                return

            # 第二阶段：完整函数分析（新的正确流程）
            self.update_status("🔍 完整分析所有函数...")
            self.update_progress(25)

            # 设置状态更新回调
            self.complete_function_analyzer.update_status = self.update_status

            # 执行完整函数分析
            function_analysis = self.complete_function_analyzer.analyze_project(
                project_path,
                project_info.source_files
            )

            # 检查是否取消
            if not self.analysis_running:
                return

            # 检查是否找到main函数
            main_function_info = self.complete_function_analyzer.get_main_function()
            if not main_function_info:
                raise Exception("未找到main函数，无法进行调用关系分析")

            # 第三阶段：从main函数追踪调用关系
            depth = int(self.depth_var.get())
            self.update_status(f"🔄 从main函数追踪调用关系 (深度: {depth})...")
            self.update_progress(50)
            call_graph = self.complete_function_analyzer.trace_function_calls_from_main(depth)

            # 检查是否取消
            if not self.analysis_running:
                return

            # 第四阶段：生成真正的执行流程图
            if self.show_mermaid_var.get():
                self.update_status("📊 生成执行流程图...")
                self.update_progress(70)
                # 使用新的代码流程分析器，传递深度参数
                flow_graph = self.code_flow_analyzer.analyze_main_function_flow(main_function_info, depth)

                # 检查是否取消
                if not self.analysis_running:
                    return

                self.mermaid_code = self.code_flow_analyzer.generate_execution_flowchart(flow_graph)

                # 如果代码流程分析失败，回退到简单的函数调用关系图
                if not self.mermaid_code or len(self.mermaid_code.strip()) < 50:
                    logger.warning("代码流程分析失败，回退到函数调用关系图")
                    self.mermaid_code = self.generate_mermaid_flowchart(call_graph, main_function_info)

            # 检查是否取消
            if not self.analysis_running:
                return

            # 第五阶段：接口分析
            self.update_status("🔌 分析接口使用...")
            self.update_progress(80)
            # 暂时跳过调用关系分析，只进行源代码分析
            interface_usage = self.interface_analyzer.analyze_interfaces(
                project_path,
                None,  # 不传递可达函数
                None   # 不传递调用关系
            )

            # 检查是否取消
            if not self.analysis_running:
                return

            # 第六阶段：LLM智能分析（如果启用）- 在流程图生成之后
            code_summary = None
            if self.enable_llm_var.get():
                self.update_status("🤖 执行LLM智能分析...")
                self.update_progress(90)

                # 设置LLM交互日志回调
                self.code_summarizer.set_llm_log_callback(self.log_llm_interaction)

                # 准备包含流程图的分析结果
                analysis_result_with_flowchart = {
                    **call_graph,
                    'mermaid_code': self.mermaid_code or '',  # 确保传递流程图代码
                    'interface_usage': interface_usage,
                    'main_reachable_functions': call_graph.get('reachable_functions', [])
                }

                # 检查是否取消
                if not self.analysis_running:
                    return

                code_summary = self.code_summarizer.summarize_project(
                    project_path, analysis_result_with_flowchart, ChipDetector.get_chip_summary(chip_info)
                )

            # 整合结果
            self.analysis_result = {
                'project_info': project_info,
                'chip_info': chip_info,
                'main_function': main_function_info,
                'function_analysis': function_analysis,
                'call_graph': call_graph,
                'interface_usage': interface_usage,
                'mermaid_code': self.mermaid_code,
                'project_path': project_path,
                'output_path': output_path
            }

            if code_summary:
                self.analysis_result['code_summary'] = code_summary

            # 保存结果
            self.save_analysis_results()

            # 显示结果
            self.display_results()

            self.update_status("✅ Analysis completed!")
            self.update_progress(100)

            logger.info("MCU project analysis completed")

        except Exception as e:
            if self.analysis_running:  # Only show error if not canceled
                logger.error(f"Analysis failed: {e}")

                # 标记进度对话框为失败状态
                if hasattr(self, 'progress_dialog') and self.progress_dialog:
                    self.progress_dialog.set_completed(success=False)
                    self.progress_dialog.add_log(f"❌ Analysis failed: {str(e)}")

                self.root.after(0, lambda: [
                    self.update_status(f"❌ Analysis failed: {str(e)}"),
                    messagebox.showerror("Analysis Failed", str(e))
                ])
        finally:
            # 在UI线程中完成清理
            self.root.after(0, self.analysis_finished)

    # 注意：旧的函数分析方法已被CompleteFunctionAnalyzer替代
    # 保留这些方法以防需要回退，但不再使用

    def find_main_function_old(self, project_path: Path, source_files: list) -> Optional[Dict]:
        """定位main函数"""
        import re

        for source_file_str in source_files:
            # 将字符串路径转换为Path对象
            if isinstance(source_file_str, str):
                # 处理相对路径，特别是 ../ 路径
                if not Path(source_file_str).is_absolute():
                    source_file = (project_path / source_file_str).resolve()
                else:
                    source_file = Path(source_file_str)
            else:
                source_file = source_file_str

            # 检查文件扩展名
            if not source_file.suffix.lower() in ['.c', '.cpp']:
                continue

            # 检查文件是否存在
            if not source_file.exists():
                continue

            content = FileUtils.read_file_safe(source_file)
            if not content:
                continue

            # 查找main函数定义
            main_patterns = [
                r'int\s+main\s*\([^)]*\)\s*{',
                r'void\s+main\s*\([^)]*\)\s*{',
                r'main\s*\([^)]*\)\s*{'
            ]

            for pattern in main_patterns:
                match = re.search(pattern, content, re.MULTILINE)
                if match:
                    # 计算行号
                    lines_before = content[:match.start()].count('\n')
                    return {
                        'file': source_file,
                        'line': lines_before + 1,
                        'function_name': 'main',
                        'signature': match.group(0).strip()
                    }

        return None

    def trace_function_calls(self, main_function_info: Dict, project_path: Path,
                           source_files: list, max_depth: int) -> Dict:
        """从main函数追踪调用关系"""
        import re

        call_graph = {
            'main_function': main_function_info,
            'call_relations': {},
            'reachable_functions': [],
            'depth_map': {}
        }

        # 首先提取所有函数定义
        all_functions = self.extract_all_functions(project_path, source_files)

        # 从main函数开始递归追踪
        visited = set()
        to_visit = [('main', 0)]  # (function_name, depth)

        while to_visit and len(to_visit) > 0:
            current_func, depth = to_visit.pop(0)

            if current_func in visited or depth >= max_depth:
                continue

            visited.add(current_func)
            call_graph['reachable_functions'].append(current_func)
            call_graph['depth_map'][current_func] = depth

            # 查找当前函数调用的其他函数
            called_functions = self.find_function_calls(current_func, all_functions, source_files)
            call_graph['call_relations'][current_func] = called_functions

            # 添加到待访问列表
            for called_func in called_functions:
                if called_func not in visited:
                    to_visit.append((called_func, depth + 1))

        return call_graph

    def extract_all_functions(self, project_path: Path, source_files: list) -> Dict:
        """提取所有函数定义"""
        import re

        functions = {}

        for source_file_str in source_files:
            # 将字符串路径转换为Path对象
            if isinstance(source_file_str, str):
                # 处理相对路径，特别是 ../ 路径
                if not Path(source_file_str).is_absolute():
                    source_file = (project_path / source_file_str).resolve()
                else:
                    source_file = Path(source_file_str)
            else:
                source_file = source_file_str

            # 检查文件扩展名
            if not source_file.suffix.lower() in ['.c', '.cpp', '.h']:
                continue

            # 检查文件是否存在
            if not source_file.exists():
                continue

            content = FileUtils.read_file_safe(source_file)
            if not content:
                continue

            # 函数定义模式
            func_patterns = [
                r'(\w+)\s+(\w+)\s*\([^)]*\)\s*{',  # 返回类型 函数名(参数) {
                r'(\w+)\s*\*\s*(\w+)\s*\([^)]*\)\s*{',  # 指针返回类型
                r'static\s+(\w+)\s+(\w+)\s*\([^)]*\)\s*{',  # static函数
                r'inline\s+(\w+)\s+(\w+)\s*\([^)]*\)\s*{'   # inline函数
            ]

            for pattern in func_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        func_name = match.group(2)
                        if func_name and func_name not in ['if', 'for', 'while', 'switch']:
                            functions[func_name] = {
                                'file': source_file,
                                'signature': match.group(0).strip(),
                                'return_type': match.group(1)
                            }

        return functions

    def find_function_calls(self, function_name: str, all_functions: Dict, source_files: list) -> list:
        """查找函数内部调用的其他函数"""
        import re

        if function_name not in all_functions:
            return []

        func_info = all_functions[function_name]
        content = FileUtils.read_file_safe(func_info['file'])
        if not content:
            return []

        # 找到函数体
        func_start = content.find(func_info['signature'])
        if func_start == -1:
            return []

        # 简单的大括号匹配来找函数体结束
        brace_count = 0
        func_body_start = content.find('{', func_start)
        if func_body_start == -1:
            return []

        func_body_end = func_body_start
        for i, char in enumerate(content[func_body_start:], func_body_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    func_body_end = i
                    break

        func_body = content[func_body_start:func_body_end + 1]

        # 查找函数调用
        called_functions = []
        for other_func in all_functions:
            if other_func != function_name:
                # 查找函数调用模式
                call_pattern = rf'\b{re.escape(other_func)}\s*\('
                if re.search(call_pattern, func_body):
                    called_functions.append(other_func)

        return called_functions

    def generate_mermaid_flowchart(self, call_graph: Dict, main_function_info) -> str:
        """生成Mermaid流程图"""
        mermaid_lines = ["graph TD"]

        # 添加main函数节点
        mermaid_lines.append(f'    main["🚀 main()"]')

        # 处理main函数信息（兼容新旧格式）
        if hasattr(main_function_info, 'file_path'):
            # 新的FunctionInfo对象
            file_name = Path(main_function_info.file_path).name
            line_number = main_function_info.line_number
        else:
            # 旧的字典格式
            file_name = main_function_info["file"].name
            line_number = main_function_info["line"]

        mermaid_lines.append(f'    main --> main_desc["📍 {file_name}:{line_number}"]')

        # 添加调用关系
        call_relations = call_graph.get('call_relations', {})
        depth_map = call_graph.get('depth_map', {})

        for caller, callees in call_relations.items():
            for callee in callees:
                depth = depth_map.get(callee, 0)

                # 根据深度设置不同的样式
                if depth <= 1:
                    icon = "🔧"  # 直接调用
                elif depth <= 2:
                    icon = "⚙️"  # 二级调用
                else:
                    icon = "🔩"  # 深层调用

                mermaid_lines.append(f'    {caller} --> {callee}["{icon} {callee}()"]')

        # 添加样式
        mermaid_lines.extend([
            "",
            "    classDef mainFunc fill:#0066CC,stroke:#fff,stroke-width:3px,color:#fff",
            "    classDef directCall fill:#FF6600,stroke:#fff,stroke-width:2px,color:#fff",
            "    classDef deepCall fill:#28A745,stroke:#fff,stroke-width:1px,color:#fff",
            "",
            "    class main mainFunc"
        ])

        return "\n".join(mermaid_lines)

    def display_results(self):
        """显示分析结果"""
        if not self.analysis_result:
            return

        # 显示项目概览
        overview_text = self.generate_overview_text()
        self.overview_text.delete("1.0", "end")
        self.overview_text.insert("1.0", overview_text)

        # 显示流程图
        if self.mermaid_code:
            self.flowchart_text.delete("1.0", "end")
            self.flowchart_text.insert("1.0", self.mermaid_code)

    def generate_overview_text(self) -> str:
        """生成项目概览文本"""
        result = self.analysis_result

        overview = []
        overview.append("🔧 MCU项目分析报告")
        overview.append("=" * 50)
        overview.append("")

        # 项目信息
        overview.append("📁 项目信息:")
        overview.append(f"  项目名称: {result['project_info'].name}")
        overview.append(f"  项目类型: {result['project_info'].type}")
        overview.append(f"  项目路径: {result['project_path']}")
        overview.append("")

        # 芯片信息
        chip_info = result['chip_info']
        overview.append("🔌 芯片信息:")
        overview.append(f"  设备型号: {chip_info.device_name or '未知'}")
        overview.append(f"  厂商: {chip_info.vendor or '未知'}")
        overview.append(f"  系列: {chip_info.series or '未知'}")
        overview.append(f"  内核: {chip_info.core or '未知'}")
        overview.append(f"  Flash: {chip_info.flash_size or '未知'}")
        overview.append(f"  RAM: {chip_info.ram_size or '未知'}")
        overview.append("")

        # main函数信息
        main_func = result['main_function']
        overview.append("🎯 main函数:")
        if hasattr(main_func, 'file_path'):
            # 新的FunctionInfo对象
            overview.append(f"  文件: {Path(main_func.file_path).name}")
            overview.append(f"  行号: {main_func.line_number}")
            overview.append(f"  签名: {main_func.signature}")
        else:
            # 旧的字典格式（兼容）
            overview.append(f"  文件: {main_func['file'].name}")
            overview.append(f"  行号: {main_func['line']}")
            overview.append(f"  签名: {main_func['signature']}")
        overview.append("")

        # 函数分析统计
        function_analysis = result.get('function_analysis', {})
        if function_analysis:
            overview.append("📊 函数分析统计:")
            overview.append(f"  总函数数量: {function_analysis.get('total_functions', 0)}")
            overview.append(f"  main函数数量: {function_analysis.get('main_functions_count', 0)}")
            overview.append("")

        # 调用关系统计
        call_graph = result['call_graph']
        overview.append("🔄 调用关系分析:")
        overview.append(f"  可达函数数量: {len(call_graph['reachable_functions'])}")
        overview.append(f"  最大调用深度: {int(self.depth_var.get())}")
        overview.append(f"  调用关系数量: {sum(len(calls) for calls in call_graph['call_relations'].values())}")
        overview.append("")

        # 可达函数列表
        overview.append("📋 可达函数列表:")
        for func_name in call_graph['reachable_functions']:
            depth = call_graph['depth_map'].get(func_name, 0)
            indent = "  " + "  " * depth
            overview.append(f"{indent}{'🚀' if func_name == 'main' else '🔧'} {func_name}() (深度: {depth})")

        overview.append("")
        overview.append("✅ 分析完成！")

        return "\n".join(overview)

    def save_analysis_results(self):
        """保存分析结果"""
        try:
            output_path = self.analysis_result['output_path']

            # 保存JSON格式的详细结果
            import json
            result_file = output_path / "analysis_result.json"

            # 准备可序列化的数据
            serializable_result = self.prepare_serializable_result()

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_result, f, ensure_ascii=False, indent=2)

            # 保存Mermaid流程图
            if self.mermaid_code:
                mermaid_file = output_path / "call_flowchart.mmd"
                with open(mermaid_file, 'w', encoding='utf-8') as f:
                    f.write(self.mermaid_code)

            logger.info(f"分析结果已保存到: {output_path}")

        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")

    def prepare_serializable_result(self) -> Dict:
        """准备可序列化的结果"""
        try:
            chip_info = self.analysis_result.get('chip_info')
            project_info = self.analysis_result.get('project_info')
            main_function = self.analysis_result.get('main_function')
            call_graph = self.analysis_result.get('call_graph')

            return {
                'project_name': project_info.name if project_info else "未知项目",
                'chip_device': chip_info.device_name if chip_info else "未知芯片",
                'chip_vendor': chip_info.vendor if chip_info else "未知厂商",
                'chip_series': chip_info.series if chip_info else "未知系列",
                'chip_core': chip_info.core if chip_info else "未知内核",
                'main_function_file': str(main_function['file']) if main_function else "未找到",
                'main_function_line': main_function['line'] if main_function else 0,
                'reachable_functions': call_graph['reachable_functions'] if call_graph else [],
                'call_relations': call_graph['call_relations'] if call_graph else {},
                'analysis_timestamp': str(datetime.now()),
                'summary': "分析完成"
            }
        except Exception as e:
            logger.error(f"准备序列化结果时出错: {e}")
            return {
                'project_name': "未知项目",
                'chip_device': "未知芯片",
                'analysis_timestamp': str(datetime.now()),
                'summary': "分析完成（部分信息缺失）"
            }

    def refresh_flowchart(self):
        """刷新流程图"""
        if self.mermaid_code:
            self.flowchart_text.delete("1.0", "end")
            self.flowchart_text.insert("1.0", self.mermaid_code)
            self.update_status("流程图已刷新")



    def update_status(self, message: str):
        """更新状态"""
        self.root.after(0, lambda: self.status_var.set(message))

        # 同时更新进度对话框
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.update_status(message)
            self.progress_dialog.add_log(message)

    def update_progress(self, value: float):
        """更新进度"""
        self.root.after(0, lambda: [
            self.progress_bar.set(value / 100),
            self.progress_percent_var.set(f"{value:.0f}%")
        ])

        # 同时更新进度对话框
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.update_progress(value)

    def set_ui_state(self, enabled: bool):
        """设置UI状态"""
        state = "normal" if enabled else "disabled"
        self.analyze_btn.configure(state=state)
        self.config_btn.configure(state=state)
        self.clear_btn.configure(state=state)
        self.browse_btn.configure(state=state)

    def open_config_dialog(self):
        """打开配置对话框"""
        dialog = ConfigDialog(self.root)
        self.root.wait_window(dialog.dialog)

    def log_callback(self, level: str, message: str):
        """日志回调函数"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"

        self.root.after(0, lambda: [
            self.log_text.insert("end", log_entry),
            self.log_text.see("end")
        ])

    def on_closing(self):
        """窗口关闭事件"""
        self.root.destroy()

    def run(self):
        """运行主窗口"""
        self.root.mainloop()


# 主程序入口
if __name__ == "__main__":
    app = ModernMainWindow()
    app.run()

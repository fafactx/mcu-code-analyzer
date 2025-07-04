"""
主窗口 - MCU代码分析器的现代化用户界面
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
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
from intelligence.llm_manager import llm_manager
from intelligence.code_summarizer import CodeSummarizer
from intelligence.semantic_analyzer import SemanticAnalyzer
from intelligence.prompt_generator import PromptGenerator, PromptContext
from ui.config_dialog import ConfigDialog
from ui.result_viewer import ResultViewer


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.setup_layout()
        self.bind_events()
        
        # 分析组件
        self.chip_detector = ChipDetector()
        self.project_parser = ProjectParser()
        self.code_analyzer = CodeAnalyzer()
        self.interface_analyzer = InterfaceAnalyzer()
        self.code_summarizer = CodeSummarizer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.prompt_generator = PromptGenerator()
        
        # 分析结果
        self.analysis_result = {}
        self.current_project_path = None
        
        # 结果查看器
        self.result_viewer = None
        
        logger.set_gui_callback(self.log_callback)
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title(config.ui.window_title)
        self.root.geometry(f"{config.ui.window_width}x{config.ui.window_height}")
        self.root.minsize(800, 600)
        
        # 设置图标（如果有的话）
        try:
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass
        
        # 设置NXP风格主题
        self.setup_nxp_theme()

    def setup_nxp_theme(self):
        """设置NXP风格主题"""
        style = ttk.Style()
        style.theme_use('clam')

        # NXP品牌色系
        nxp_blue = "#0066CC"
        nxp_orange = "#FF6600"
        nxp_light_blue = "#E8F4FD"
        nxp_gray = "#F8F9FA"
        nxp_dark = "#2C3E50"

        # 配置样式
        style.configure('TLabel',
                       background=nxp_gray,
                       foreground=nxp_dark,
                       font=(config.ui.font_default, 10))

        style.configure('TLabelFrame',
                       background=nxp_gray,
                       foreground=nxp_dark,
                       borderwidth=2,
                       relief='solid')

        style.configure('TLabelFrame.Label',
                       background=nxp_gray,
                       foreground=nxp_blue,
                       font=(config.ui.font_default, 10, 'bold'))

        style.configure('TButton',
                       background=nxp_light_blue,
                       foreground=nxp_dark,
                       borderwidth=1,
                       focuscolor='none',
                       font=(config.ui.font_default, 9))

        style.map('TButton',
                 background=[('active', nxp_blue),
                           ('pressed', nxp_blue)])

        style.configure('Accent.TButton',
                       background=nxp_blue,
                       foreground='white',
                       font=(config.ui.font_default, 10, 'bold'))

        style.map('Accent.TButton',
                 background=[('active', nxp_orange),
                           ('pressed', nxp_orange)])

        style.configure('TCheckbutton',
                       background=nxp_gray,
                       foreground=nxp_dark,
                       font=(config.ui.font_default, 9))

        style.configure('TNotebook',
                       background=nxp_gray,
                       borderwidth=0)

        style.configure('TNotebook.Tab',
                       background=nxp_light_blue,
                       foreground=nxp_dark,
                       padding=[12, 8],
                       font=(config.ui.font_default, 9))

        style.map('TNotebook.Tab',
                 background=[('selected', nxp_blue),
                           ('active', nxp_orange)],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])

        # 设置根窗口背景
        self.root.configure(bg=nxp_gray)

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # 标题
        self.title_label = ttk.Label(
            self.main_frame,
            text="MCU代码分析器 v2.0",
            font=(config.ui.font_default, 16, "bold")
        )

        # 目录选择框架
        self.path_frame = ttk.LabelFrame(self.main_frame, text="项目设置", padding="10")

        # MCU项目路径
        self.project_frame = ttk.Frame(self.path_frame)
        self.project_label = ttk.Label(self.project_frame, text="MCU项目目录:")
        self.project_path_var = tk.StringVar()
        self.project_entry = ttk.Entry(self.project_frame, textvariable=self.project_path_var, width=60)
        self.project_browse_btn = ttk.Button(self.project_frame, text="📁 浏览", command=self.browse_project_path)
        
        # 分析选项框架
        self.options_frame = ttk.LabelFrame(self.main_frame, text="分析选项", padding="10")

        # 第一行选项
        self.options_row1 = ttk.Frame(self.options_frame)

        self.deep_analysis_var = tk.BooleanVar(value=True)
        self.deep_analysis_check = ttk.Checkbutton(
            self.options_row1,
            text="🔍 深度代码分析",
            variable=self.deep_analysis_var
        )

        self.call_analysis_var = tk.BooleanVar(value=True)
        self.call_analysis_check = ttk.Checkbutton(
            self.options_row1,
            text="🔄 main函数调用分析",
            variable=self.call_analysis_var
        )

        self.enable_llm_var = tk.BooleanVar(value=True)
        self.enable_llm_check = ttk.Checkbutton(
            self.options_row1,
            text="🤖 LLM智能分析",
            variable=self.enable_llm_var
        )

        # 第二行选项
        self.options_row2 = ttk.Frame(self.options_frame)

        self.depth_label = ttk.Label(self.options_row2, text="调用深度:")
        self.depth_var = tk.StringVar(value="3")
        self.depth_spinbox = ttk.Spinbox(
            self.options_row2,
            from_=1,
            to=10,
            width=5,
            textvariable=self.depth_var
        )

        self.show_mermaid_var = tk.BooleanVar(value=True)
        self.show_mermaid_check = ttk.Checkbutton(
            self.options_row2,
            text="📊 显示调用流程图",
            variable=self.show_mermaid_var
        )

        self.generate_report_var = tk.BooleanVar(value=True)
        self.generate_report_check = ttk.Checkbutton(
            self.options_row2,
            text="📄 生成分析报告",
            variable=self.generate_report_var
        )
        
        # 控制按钮框架
        self.control_frame = ttk.Frame(self.main_frame)

        self.analyze_btn = ttk.Button(
            self.control_frame,
            text="🚀 开始分析",
            command=self.start_analysis,
            style="Accent.TButton"
        )

        self.config_btn = ttk.Button(
            self.control_frame,
            text="⚙️ LLM配置",
            command=self.open_config_dialog
        )

        self.clear_btn = ttk.Button(
            self.control_frame,
            text="🗑️ 清空",
            command=self.clear_all
        )
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            variable=self.progress_var,
            maximum=100
        )
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        
        # 结果显示区域
        self.result_frame = ttk.LabelFrame(self.main_frame, text="分析结果", padding="5")

        # 创建Notebook用于多标签页
        self.notebook = ttk.Notebook(self.result_frame)

        # 概览标签页
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="📋 项目概览")
        self.overview_text = scrolledtext.ScrolledText(
            self.overview_frame,
            height=15,
            font=(config.ui.font_code, 10),
            wrap=tk.WORD
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True)

        # 调用流程图标签页
        self.flowchart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.flowchart_frame, text="🔄 调用流程图")

        # 流程图控制框架
        self.flowchart_control_frame = ttk.Frame(self.flowchart_frame)
        self.flowchart_control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.refresh_flowchart_btn = ttk.Button(
            self.flowchart_control_frame,
            text="🔄 刷新流程图",
            command=self.refresh_flowchart
        )
        self.refresh_flowchart_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.render_flowchart_btn = ttk.Button(
            self.flowchart_control_frame,
            text="🎨 渲染图形",
            command=self.render_flowchart
        )
        self.render_flowchart_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Mermaid流程图显示
        self.flowchart_text = scrolledtext.ScrolledText(
            self.flowchart_frame,
            height=15,
            font=(config.ui.font_code, 9),
            wrap=tk.WORD
        )
        self.flowchart_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # 日志标签页
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="📝 执行日志")
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=15,
            font=(config.ui.font_code, 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 配置日志文本颜色
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("DEBUG", foreground="gray")

        # 初始化变量
        self.mermaid_code = ""
        self.call_graph = {}
    
    def setup_layout(self):
        """设置布局"""
        # 主框架
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        self.title_label.pack(pady=(0, 10))
        
        # 路径选择区域
        self.path_frame.pack(fill=tk.X, pady=(0, 10))

        # MCU项目路径
        self.project_frame.pack(fill=tk.X, pady=(0, 5))
        self.project_label.pack(side=tk.LEFT)
        self.project_browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.project_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 5))
        
        # 分析选项
        self.options_frame.pack(fill=tk.X, pady=(0, 10))

        # 第一行选项
        self.options_row1.pack(fill=tk.X, pady=(0, 5))
        self.deep_analysis_check.pack(side=tk.LEFT, padx=(0, 20))
        self.call_analysis_check.pack(side=tk.LEFT, padx=(0, 20))
        self.enable_llm_check.pack(side=tk.LEFT)

        # 第二行选项
        self.options_row2.pack(fill=tk.X)
        self.depth_label.pack(side=tk.LEFT, padx=(0, 5))
        self.depth_spinbox.pack(side=tk.LEFT, padx=(0, 20))
        self.show_mermaid_check.pack(side=tk.LEFT, padx=(0, 20))
        self.generate_report_check.pack(side=tk.LEFT)

        # 控制按钮
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.config_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_btn.pack(side=tk.RIGHT)

        # 进度条和状态
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.status_label.pack(anchor=tk.W)

        # 结果区域
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 路径输入框变化事件
        self.project_path_var.trace('w', self.on_path_changed)
    
    def browse_project_path(self):
        """浏览MCU项目路径"""
        path = filedialog.askdirectory(title="选择MCU项目目录")
        if path:
            self.project_path_var.set(path)
            # 自动清理已存在的分析目录
            self.cleanup_existing_analysis(path)
    
    def cleanup_existing_analysis(self, project_path: str):
        """清理已存在的分析目录"""
        try:
            analysis_dir = Path(project_path) / "Analyzer_Output"
            if analysis_dir.exists():
                import shutil
                shutil.rmtree(analysis_dir)
                logger.info(f"已清理分析目录: {analysis_dir}")
                self.status_var.set("已清理旧的分析目录")
        except Exception as e:
            logger.warning(f"清理分析目录失败: {e}")

    def on_path_changed(self, *args):
        """路径改变事件"""
        project_path = self.project_path_var.get()
        if project_path:
            # 验证路径
            is_valid, message = FileUtils.validate_path(project_path)
            if is_valid:
                self.status_var.set("路径有效")
            else:
                self.status_var.set(f"路径无效: {message}")
    
    def start_analysis(self):
        """开始分析"""
        # 验证输入
        if not self.validate_inputs():
            return
        
        # 禁用按钮
        self.set_ui_state(False)
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中执行分析
        analysis_thread = threading.Thread(target=self.run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def validate_inputs(self) -> bool:
        """验证输入"""
        project_path = self.project_path_var.get().strip()
        if not project_path:
            messagebox.showerror("错误", "请选择MCU项目目录")
            return False

        is_valid, message = FileUtils.validate_path(project_path)
        if not is_valid:
            messagebox.showerror("错误", f"MCU项目路径无效: {message}")
            return False

        return True
    
    def run_analysis(self):
        """运行分析（在后台线程中）"""
        try:
            self.update_status("开始分析...")
            self.update_progress(0)

            project_path = Path(self.project_path_var.get())
            # 自动设置输出路径为项目路径下的Analyzer_Output目录
            output_path = project_path / "Analyzer_Output"

            # 确保输出目录存在
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.current_project_path = project_path
            
            # 第一阶段：项目解析
            self.update_status("解析项目文件...")
            self.update_progress(10)
            project_info = self.project_parser.parse_project(project_path)
            
            # 第二阶段：芯片识别
            self.update_status("识别芯片信息...")
            self.update_progress(20)
            chip_info = self.chip_detector.detect_from_project_file(project_path)
            
            # 第三阶段：代码分析
            self.update_status("分析代码结构...")
            self.update_progress(30)
            code_result = self.code_analyzer.analyze_project(
                project_path, 
                project_info.source_files
            )
            
            # 第四阶段：接口分析
            self.update_status("分析接口使用...")
            self.update_progress(50)
            interface_usage = self.interface_analyzer.analyze_interfaces(
                project_path,
                code_result.get('main_reachable_functions'),
                code_result.get('call_relations')
            )
            
            # 第五阶段：智能分析（如果启用）
            if self.enable_llm_var.get():
                self.update_status("执行智能分析...")
                self.update_progress(70)
                
                # 代码总结
                code_summary = self.code_summarizer.summarize_project(
                    project_path, code_result, self.chip_detector.get_chip_summary()
                )
                
                # 语义分析（如果启用）
                semantic_result = None
                if self.enable_semantic_var.get():
                    semantic_result = self.semantic_analyzer.analyze_project_semantics(
                        project_path, code_result, self.chip_detector.get_chip_summary()
                    )
            
            # 整合结果
            self.update_status("整合分析结果...")
            self.update_progress(90)
            
            self.analysis_result = {
                'project_info': project_info,
                'chip_info': chip_info,
                'code_analysis': code_result,
                'interface_usage': interface_usage,
                'project_path': project_path,
                'output_path': output_path
            }
            
            if self.enable_llm_var.get():
                self.analysis_result['code_summary'] = code_summary
                if self.enable_semantic_var.get():
                    self.analysis_result['semantic_analysis'] = semantic_result
            
            # 保存结果
            self.save_analysis_results()
            
            self.update_status("分析完成！")
            self.update_progress(100)
            
            # 启用查看结果按钮
            self.root.after(0, lambda: self.view_results_btn.config(state="normal"))
            
            logger.info("项目分析完成")
            
        except Exception as e:
            logger.exception(f"分析过程中发生错误: {e}")
            self.update_status(f"分析失败: {e}")
            messagebox.showerror("错误", f"分析过程中发生错误:\n{e}")
        
        finally:
            # 恢复UI状态
            self.root.after(0, lambda: self.set_ui_state(True))
    
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
            
            logger.info(f"分析结果已保存到: {result_file}")
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
    
    def prepare_serializable_result(self) -> Dict:
        """准备可序列化的结果"""
        # 这里需要将复杂对象转换为可序列化的字典
        try:
            chip_info = self.analysis_result.get('chip_info')
            project_info = self.analysis_result.get('project_info')

            return {
                'project_name': project_info.name if project_info else "未知项目",
                'chip_device': chip_info.device_name if chip_info else "未知芯片",
                'chip_vendor': chip_info.vendor if chip_info else "未知厂商",
                'chip_series': chip_info.series if chip_info else "未知系列",
                'chip_core': chip_info.core if chip_info else "未知内核",
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

    def open_config_dialog(self):
        """打开配置对话框"""
        dialog = ConfigDialog(self.root)
        self.root.wait_window(dialog.dialog)

    def view_results(self):
        """查看分析结果"""
        if not self.analysis_result:
            messagebox.showwarning("警告", "没有可查看的分析结果")
            return

        if self.result_viewer is None or not self.result_viewer.window.winfo_exists():
            self.result_viewer = ResultViewer(self.root, self.analysis_result)
        else:
            self.result_viewer.update_results(self.analysis_result)
            self.result_viewer.window.lift()

    def clear_all(self):
        """清空所有内容"""
        if messagebox.askyesno("确认", "确定要清空所有内容吗？"):
            self.project_path_var.set("")
            self.log_text.delete(1.0, tk.END)
            self.analysis_result = {}
            self.current_project_path = None
            self.view_results_btn.config(state="disabled")
            self.update_progress(0)
            self.update_status("就绪")

    def set_ui_state(self, enabled: bool):
        """设置UI状态"""
        state = "normal" if enabled else "disabled"

        self.project_browse_btn.config(state=state)
        self.analyze_btn.config(state=state)
        self.config_btn.config(state=state)
        self.clear_btn.config(state=state)

        self.deep_analysis_check.config(state=state)
        self.call_analysis_check.config(state=state)
        self.enable_llm_check.config(state=state)
        self.show_mermaid_check.config(state=state)
        self.generate_report_check.config(state=state)
        self.depth_spinbox.config(state=state)

    def update_status(self, message: str):
        """更新状态"""
        self.root.after(0, lambda: self.status_var.set(message))

    def update_progress(self, value: float):
        """更新进度"""
        self.root.after(0, lambda: self.progress_var.set(value))

    def log_callback(self, message: str, level: str = "info"):
        """日志回调函数"""
        def append_log():
            # 添加时间戳
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_line = f"[{timestamp}] {message}\n"

            # 根据级别设置颜色
            tag = level.upper()
            self.log_text.insert(tk.END, log_line, tag)
            self.log_text.see(tk.END)

        self.root.after(0, append_log)

    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出MCU代码分析器吗？"):
            logger.info("应用程序退出")
            self.root.destroy()

    def refresh_flowchart(self):
        """刷新流程图"""
        if hasattr(self, 'call_graph') and self.call_graph:
            self.generate_mermaid_flowchart(self.call_graph)
        else:
            self.flowchart_text.delete(1.0, tk.END)
            self.flowchart_text.insert(tk.END, "暂无调用关系数据，请先进行分析")

    def render_flowchart(self):
        """渲染流程图"""
        if not self.mermaid_code:
            messagebox.showwarning("警告", "暂无流程图数据，请先进行分析")
            return

        try:
            # 创建临时HTML文件
            import tempfile
            import webbrowser

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MCU项目调用流程图</title>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            </head>
            <body>
                <div class="mermaid">
                {self.mermaid_code}
                </div>
                <script>
                    mermaid.initialize({{startOnLoad:true}});
                </script>
            </body>
            </html>
            """

            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name

            webbrowser.open(f'file://{temp_file}')

        except Exception as e:
            messagebox.showerror("错误", f"渲染流程图失败:\n{e}")

    def generate_mermaid_flowchart(self, call_analysis):
        """生成Mermaid流程图"""
        if not call_analysis or 'call_tree' not in call_analysis:
            return

        mermaid_lines = ["graph TD"]
        node_counter = 0

        def add_node_to_mermaid(tree_node, parent_id=None):
            nonlocal node_counter

            if not tree_node:
                return

            func_name = tree_node['name']
            node_id = f"node{node_counter}"
            node_counter += 1

            # 根据函数类型设置样式
            if func_name == 'main':
                mermaid_lines.append(f"    {node_id}[🔴 {func_name}]")
                mermaid_lines.append(f"    {node_id} --> {node_id}")
            elif any(pattern in func_name for pattern in ['HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_']):
                mermaid_lines.append(f"    {node_id}[🟢 {func_name}]")
            else:
                mermaid_lines.append(f"    {node_id}[🔵 {func_name}]")

            # 添加连接
            if parent_id:
                mermaid_lines.append(f"    {parent_id} --> {node_id}")

            # 递归处理子节点
            for child in tree_node.get('children', []):
                add_node_to_mermaid(child, node_id)

        # 从根节点开始构建
        call_tree = call_analysis.get('call_tree')
        if call_tree:
            add_node_to_mermaid(call_tree)

        self.mermaid_code = "\n".join(mermaid_lines)

        # 显示在UI中
        self.flowchart_text.delete(1.0, tk.END)
        explanation = """# MCU项目调用流程图 (Mermaid格式)

## 图例说明
- 🔴 main函数 (程序入口)
- 🟢 接口函数 (HAL/GPIO/UART等)
- 🔵 用户自定义函数

## Mermaid代码
"""
        self.flowchart_text.insert(tk.END, explanation)
        self.flowchart_text.insert(tk.END, self.mermaid_code)

    def run(self):
        """运行主窗口"""
        logger.info("MCU代码分析器启动")
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        logger.exception(f"应用程序启动失败: {e}")
        messagebox.showerror("错误", f"应用程序启动失败:\n{e}")


if __name__ == "__main__":
    main()

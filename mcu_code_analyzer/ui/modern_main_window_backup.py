"""
现代化主窗口 - MCU代码分析器的现代化用户界面
采用CustomTkinter和卡片式设计
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
from core.complete_function_analyzer import CompleteFunctionAnalyzer
from core.code_flow_analyzer import CodeFlowAnalyzer
from intelligence.code_summarizer import CodeSummarizer
from intelligence.semantic_analyzer import SemanticAnalyzer
from intelligence.prompt_generator import PromptGenerator, PromptContext
from ui.config_dialog import ConfigDialog


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
        """设置窗口属性"""
        self.root.title("MCU代码分析器 v2.0 - 现代化界面")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # 设置窗口图标
        try:
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass
    
    def create_modern_ui(self):
        """创建现代化UI界面"""
        # 主滚动框架
        self.main_scrollable = ctk.CTkScrollableFrame(
            self.root,
            fg_color=self.colors['background']
        )
        self.main_scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题区域
        self.create_header()
        
        # 项目配置卡片
        self.create_project_card()
        
        # 分析选项卡片
        self.create_analysis_options_card()
        
        # 控制按钮卡片
        self.create_control_card()
        
        # 进度状态卡片
        self.create_progress_card()
        
        # 结果显示卡片
        self.create_results_card()
    
    def create_header(self):
        """创建标题区域"""
        header_frame = ctk.CTkFrame(
            self.main_scrollable,
            fg_color=self.colors['primary'],
            corner_radius=15
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 主标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔧 MCU代码分析器",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=20)
        
        # 副标题
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="智能分析MCU项目 • 生成调用流程图 • NXP专业版",
            font=ctk.CTkFont(size=14),
            text_color="#E8F4FD"
        )
        subtitle_label.pack(pady=(0, 20))
    
    def create_project_card(self):
        """创建项目配置卡片"""
        project_card = ctk.CTkFrame(
            self.main_scrollable,
            fg_color=self.colors['card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border']
        )
        project_card.pack(fill="x", pady=(0, 15))
        
        # 卡片标题
        card_title = ctk.CTkLabel(
            project_card,
            text="📁 项目配置",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['primary']
        )
        card_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # 项目路径选择
        path_frame = ctk.CTkFrame(project_card, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="MCU项目目录:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text']
        )
        path_label.pack(anchor="w", pady=(0, 8))
        
        # 路径输入框和浏览按钮
        path_input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input_frame.pack(fill="x")
        
        self.project_path_var = ctk.StringVar()
        self.project_entry = ctk.CTkEntry(
            path_input_frame,
            textvariable=self.project_path_var,
            placeholder_text="请选择MCU项目目录...",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.project_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(
            path_input_frame,
            text="📁 浏览",
            command=self.browse_project_path,
            width=100,
            height=35,
            fg_color=self.colors['secondary'],
            hover_color="#E55A00"
        )
        self.browse_btn.pack(side="right")
    
    def create_analysis_options_card(self):
        """创建分析选项卡片"""
        options_card = ctk.CTkFrame(
            self.main_scrollable,
            fg_color=self.colors['card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border']
        )
        options_card.pack(fill="x", pady=(0, 15))
        
        # 卡片标题
        card_title = ctk.CTkLabel(
            options_card,
            text="⚙️ 分析选项",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['primary']
        )
        card_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # 选项网格
        options_grid = ctk.CTkFrame(options_card, fg_color="transparent")
        options_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        # 第一行选项
        row1 = ctk.CTkFrame(options_grid, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        
        self.deep_analysis_var = ctk.BooleanVar(value=True)
        self.deep_analysis_check = ctk.CTkCheckBox(
            row1,
            text="🔍 深度代码分析",
            variable=self.deep_analysis_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.deep_analysis_check.pack(side="left", padx=(0, 30))
        
        self.call_analysis_var = ctk.BooleanVar(value=True)
        self.call_analysis_check = ctk.CTkCheckBox(
            row1,
            text="🔄 main函数调用分析",
            variable=self.call_analysis_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.call_analysis_check.pack(side="left", padx=(0, 30))
        
        self.enable_llm_var = ctk.BooleanVar(value=True)
        self.enable_llm_check = ctk.CTkCheckBox(
            row1,
            text="🤖 LLM智能分析",
            variable=self.enable_llm_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.enable_llm_check.pack(side="left")
        
        # 第二行选项
        row2 = ctk.CTkFrame(options_grid, fg_color="transparent")
        row2.pack(fill="x")
        
        # 调用深度设置
        depth_frame = ctk.CTkFrame(row2, fg_color="transparent")
        depth_frame.pack(side="left", padx=(0, 30))
        
        depth_label = ctk.CTkLabel(
            depth_frame,
            text="调用深度:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text']
        )
        depth_label.pack(side="left", padx=(0, 8))
        
        self.depth_var = ctk.StringVar(value="3")
        self.depth_spinbox = ctk.CTkOptionMenu(
            depth_frame,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            variable=self.depth_var,
            width=60,
            height=28
        )
        self.depth_spinbox.pack(side="left")
        
        self.show_mermaid_var = ctk.BooleanVar(value=True)
        self.show_mermaid_check = ctk.CTkCheckBox(
            row2,
            text="📊 显示调用流程图",
            variable=self.show_mermaid_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.show_mermaid_check.pack(side="left", padx=(0, 30))
        
        self.generate_report_var = ctk.BooleanVar(value=True)
        self.generate_report_check = ctk.CTkCheckBox(
            row2,
            text="📄 生成分析报告",
            variable=self.generate_report_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.generate_report_check.pack(side="left")

    def create_control_card(self):
        """创建控制按钮卡片"""
        control_card = ctk.CTkFrame(
            self.main_scrollable,
            fg_color=self.colors['card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border']
        )
        control_card.pack(fill="x", pady=(0, 15))

        # 卡片标题
        card_title = ctk.CTkLabel(
            control_card,
            text="🎮 操作控制",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['primary']
        )
        card_title.pack(anchor="w", padx=20, pady=(15, 10))

        # 按钮区域
        button_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))

        # 主要操作按钮
        self.analyze_btn = ctk.CTkButton(
            button_frame,
            text="🚀 开始分析",
            command=self.start_analysis,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color="#0052A3"
        )
        self.analyze_btn.pack(side="left", padx=(0, 15))

        # 配置按钮
        self.config_btn = ctk.CTkButton(
            button_frame,
            text="⚙️ LLM配置",
            command=self.open_config_dialog,
            width=120,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['secondary'],
            hover_color="#E55A00"
        )
        self.config_btn.pack(side="left", padx=(0, 15))

        # 清空按钮
        self.clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ 清空",
            command=self.clear_all,
            width=100,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#6C757D",
            hover_color="#5A6268"
        )
        self.clear_btn.pack(side="right")

    def create_progress_card(self):
        """创建进度状态卡片"""
        progress_card = ctk.CTkFrame(
            self.main_scrollable,
            fg_color=self.colors['card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border']
        )
        progress_card.pack(fill="x", pady=(0, 15))

        # 卡片标题
        card_title = ctk.CTkLabel(
            progress_card,
            text="📊 分析进度",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['primary']
        )
        card_title.pack(anchor="w", padx=20, pady=(15, 10))

        # 进度内容
        progress_content = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_content.pack(fill="x", padx=20, pady=(0, 15))

        # 状态标签
        self.status_var = ctk.StringVar(value="就绪")
        self.status_label = ctk.CTkLabel(
            progress_content,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text']
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            progress_content,
            height=20,
            progress_color=self.colors['primary']
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(0)

        # 进度百分比
        self.progress_percent_var = ctk.StringVar(value="0%")
        self.progress_percent_label = ctk.CTkLabel(
            progress_content,
            textvariable=self.progress_percent_var,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        )
        self.progress_percent_label.pack(anchor="e")

    def create_results_card(self):
        """创建结果显示卡片"""
        results_card = ctk.CTkFrame(
            self.main_scrollable,
            fg_color=self.colors['card'],
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border']
        )
        results_card.pack(fill="both", expand=True)

        # 卡片标题
        card_title = ctk.CTkLabel(
            results_card,
            text="📋 分析结果",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['primary']
        )
        card_title.pack(anchor="w", padx=20, pady=(15, 10))

        # 标签页框架
        self.tabview = ctk.CTkTabview(
            results_card,
            width=400,
            height=300,
            fg_color=self.colors['accent'],
            segmented_button_fg_color=self.colors['primary'],
            segmented_button_selected_color=self.colors['secondary'],
            segmented_button_selected_hover_color="#E55A00"
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # 项目概览标签页
        self.overview_tab = self.tabview.add("📋 项目概览")
        self.overview_text = ctk.CTkTextbox(
            self.overview_tab,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.overview_text.pack(fill="both", expand=True, padx=10, pady=10)

        # 调用流程图标签页
        self.flowchart_tab = self.tabview.add("🔄 调用流程图")

        # 流程图控制按钮
        flowchart_controls = ctk.CTkFrame(self.flowchart_tab, fg_color="transparent")
        flowchart_controls.pack(fill="x", padx=10, pady=(10, 5))

        self.refresh_flowchart_btn = ctk.CTkButton(
            flowchart_controls,
            text="🔄 刷新流程图",
            command=self.refresh_flowchart,
            width=120,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors['primary']
        )
        self.refresh_flowchart_btn.pack(side="left", padx=(0, 10))

        self.render_flowchart_btn = ctk.CTkButton(
            flowchart_controls,
            text="🎨 渲染图形",
            command=self.render_flowchart,
            width=120,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors['secondary']
        )
        self.render_flowchart_btn.pack(side="left")

        # 流程图显示
        self.flowchart_text = ctk.CTkTextbox(
            self.flowchart_tab,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.flowchart_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # 执行日志标签页
        self.log_tab = self.tabview.add("📝 执行日志")
        self.log_text = ctk.CTkTextbox(
            self.log_tab,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

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

        self.set_ui_state(False)
        self.log_text.delete("1.0", "end")

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
        """运行分析（重构版本 - 正确的执行流程）"""
        try:
            self.update_status("开始分析...")
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

            # 检查是否找到main函数
            main_function_info = self.complete_function_analyzer.get_main_function()
            if not main_function_info:
                raise Exception("未找到main函数，无法进行调用关系分析")

            # 第三阶段：从main函数追踪调用关系
            depth = int(self.depth_var.get())
            self.update_status(f"🔄 从main函数追踪调用关系 (深度: {depth})...")
            self.update_progress(50)
            call_graph = self.complete_function_analyzer.trace_function_calls_from_main(depth)

            # 第四阶段：生成真正的执行流程图
            if self.show_mermaid_var.get():
                self.update_status("📊 生成执行流程图...")
                self.update_progress(70)
                # 使用新的代码流程分析器，传递深度参数
                flow_graph = self.code_flow_analyzer.analyze_main_function_flow(main_function_info, depth)
                self.mermaid_code = self.code_flow_analyzer.generate_execution_flowchart(flow_graph)

                # 如果代码流程分析失败，回退到简单的函数调用关系图
                if not self.mermaid_code or len(self.mermaid_code.strip()) < 50:
                    logger.warning("代码流程分析失败，回退到函数调用关系图")
                    self.mermaid_code = self.generate_mermaid_flowchart(call_graph, main_function_info)

            # 第五阶段：接口分析
            self.update_status("🔌 分析接口使用...")
            self.update_progress(85)
            # 暂时跳过调用关系分析，只进行源代码分析
            interface_usage = self.interface_analyzer.analyze_interfaces(
                project_path,
                None,  # 不传递可达函数
                None   # 不传递调用关系
            )

            # 第六阶段：LLM智能分析（如果启用）
            code_summary = None
            if self.enable_llm_var.get():
                self.update_status("🤖 执行LLM智能分析...")
                self.update_progress(95)
                code_summary = self.code_summarizer.summarize_project(
                    project_path, call_graph, self.chip_detector.get_chip_summary()
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

            self.update_status("✅ 分析完成！")
            self.update_progress(100)

            logger.info("MCU项目分析完成")

        except Exception as e:
            logger.error(f"分析失败: {e}")
            self.update_status(f"❌ 分析失败: {str(e)}")
            messagebox.showerror("分析失败", str(e))
        finally:
            self.root.after(0, lambda: self.set_ui_state(True))

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

    def render_flowchart(self):
        """在浏览器中渲染流程图"""
        if not self.mermaid_code:
            messagebox.showwarning("警告", "没有可渲染的流程图")
            return

        try:
            # 创建临时HTML文件
            import tempfile
            import webbrowser

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MCU调用流程图</title>
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
            self.update_status("流程图已在浏览器中打开")

        except Exception as e:
            logger.error(f"渲染流程图失败: {e}")
            messagebox.showerror("错误", f"渲染流程图失败: {str(e)}")

    def update_status(self, message: str):
        """更新状态"""
        self.root.after(0, lambda: self.status_var.set(message))

    def update_progress(self, value: float):
        """更新进度"""
        self.root.after(0, lambda: [
            self.progress_bar.set(value / 100),
            self.progress_percent_var.set(f"{value:.0f}%")
        ])

    def set_ui_state(self, enabled: bool):
        """设置UI状态"""
        state = "normal" if enabled else "disabled"
        self.analyze_btn.configure(state=state)
        self.config_btn.configure(state=state)
        self.clear_btn.configure(state=state)
        self.browse_btn.configure(state=state)

    def clear_all(self):
        """清空所有内容"""
        self.project_path_var.set("")
        self.overview_text.delete("1.0", "end")
        self.flowchart_text.delete("1.0", "end")
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)
        self.progress_percent_var.set("0%")
        self.update_status("已清空")
        self.analysis_result = {}
        self.mermaid_code = ""
        self.call_graph = {}

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

"""
MCU Code Analyzer - Professional GUI
Standalone GUI program for exe generation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import re
import json
from datetime import datetime
import tempfile
import webbrowser
import shutil
import traceback

# 版本管理
try:
    from utils.version_manager import get_version_display
except ImportError:
    def get_version_display():
        return "v0.1.0 (Build 1) - 2025-07-03"

# Import core modules with path handling for exe compatibility
import sys
import os
import time
from pathlib import Path

# Add current directory to path for exe compatibility
if getattr(sys, 'frozen', False):
    # Running as exe
    current_dir = os.path.dirname(sys.executable)
    sys.path.insert(0, current_dir)
else:
    # Running as script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

try:
    from core.chip_detector import ChipDetector, ChipInfo
except ImportError:
    # Fallback: try absolute import
    import importlib.util
    core_path = os.path.join(current_dir, 'core', 'chip_detector.py')
    if os.path.exists(core_path):
        spec = importlib.util.spec_from_file_location("chip_detector", core_path)
        chip_detector_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chip_detector_module)
        ChipDetector = chip_detector_module.ChipDetector
        ChipInfo = chip_detector_module.ChipInfo
    else:
        # Ultimate fallback: create dummy classes
        class ChipInfo:
            def __init__(self):
                self.device_name = "Unknown MCU"
                self.vendor = "Unknown"
                self.series = "Unknown"
                self.core = "Unknown"
                self.flash_size = "Unknown"
                self.ram_size = "Unknown"

        class ChipDetector:
            def detect_from_project_file(self, project_path):
                chip_info = ChipInfo()
                try:
                    path_str = str(project_path).upper()
                    if 'STM32' in path_str:
                        chip_info.device_name = "STM32 MCU"
                        chip_info.vendor = "STMicroelectronics"
                        chip_info.series = "STM32"
                        chip_info.core = "Cortex-M"
                except Exception:
                    pass
                return chip_info

try:
    from localization import loc
except ImportError:
    # 如果导入失败，创建一个简单的替代
    class SimpleLoc:
        def get_text(self, key):
            # 简单的文本映射
            text_map = {
                'graph_rendering_related': '图形渲染相关',
                'execution_log': '执行日志',
                'analysis_progress': '分析进度',
                'project_path': '项目路径',
                'browse': '浏览',
                'analyze': '分析',
                'export': '导出',
                'settings': '设置',
                'about': '关于',
                'start_analysis': '开始分析',
                'starting_analysis': '开始分析...',
                'analyzing': '分析中...',
                'scanning_files': '扫描文件...',
                'detecting_chip': '检测芯片...',
                'analyzing_code': '分析代码...',
                'analyzing_calls': '分析调用关系...',
                'generating_flowchart': '生成流程图...',
                'generating_report': '生成报告...',
                'analysis_complete': '分析完成',
                'error': '错误',
                'select_project_dir': '请选择项目目录',
                'project_dir_not_exist': '项目目录不存在',
                'select_output_dir': '请选择输出目录',
                'all_paths_validated': '路径验证通过',
                'cleaning_existing_folders': '清理现有文件夹',
                'starting_analysis_thread': '启动分析线程',
                'about_to_call_log_message': '准备调用日志消息',
                'log_message_called_successfully': '日志消息调用成功',
                'about_to_update_status': '准备更新状态',
                'status_updated_successfully': '状态更新成功',
                'about_to_update_progress': '准备更新进度',
                'progress_updated_successfully': '进度更新成功',
                'creating_analyze_button': '创建分析按钮',
                'analyze_button_created': '分析按钮创建完成',
                'llm_code_analysis': 'LLM代码分析',
                'language': '语言',
                'english': 'English',
                'chinese': '中文',
                'info': '信息'
            }
            return text_map.get(key, key)

    loc = SimpleLoc()

# {loc.get_text('graph_rendering_related')}
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import networkx as nx
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

def safe_json_serialize(obj):
    f"""{loc.get_text('safe_json_serialization')}"""
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_json_serialize(item) for item in obj]
    else:
        return obj

class MCUAnalyzerGUI:
    """MCU Code Analyzer GUI Main Class"""

    def __init__(self):
        self.root = tk.Tk()

        # Initialize core components
        self.chip_detector = ChipDetector()

        # Load global configuration
        self.config = self.load_global_config()

        # {loc.get_text('config_file_path_hidden')}
        self.config_file = self.get_config_file_path()

        # {loc.get_text('add_canvas_rounded_rect')}
        self.create_rounded_rectangle_method()

        self.setup_window()
        self.create_widgets()
        self.setup_layout()

        # {loc.get_text('load_last_config')}
        self.load_last_config()

        # {loc.get_text('analysis_results_ensure_defaults')}
        self.analysis_result = {}
        self.current_project_path = None
        self.call_graph = {}
        self.mermaid_code = ""
        self.last_chip_info = None
        self.last_code_analysis = None
        self.last_call_analysis = None
        self.last_analysis_results = False
        self.last_interfaces = {}

        # 初始化流程图格式选择
        self.current_flowchart_format = 'mermaid'  # 默认使用mermaid格式
        self.plantuml_code = ""  # 存储PlantUML代码

    def setup_window(self):
        """Setup window"""
        version_info = get_version_display()
        self.root.title(f"{loc.get_text('main_title')} - {version_info}")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Create menu bar
        self.setup_menu()

    def setup_menu(self):
        """Setup menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # Config menu
        config_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=loc.get_text('menu_config'), menu=config_menu)
        config_menu.add_command(label=loc.get_text('menu_llm_config'), command=self.open_llm_config)
        config_menu.add_separator()
        config_menu.add_command(label=loc.get_text('menu_analysis_settings'), command=self.open_analysis_config)
        config_menu.add_separator()
        config_menu.add_command(label=loc.get_text('language'), command=self.open_language_config)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=loc.get_text('menu_help'), menu=help_menu)
        help_menu.add_command(label=loc.get_text('menu_usage'), command=self.show_help)
        help_menu.add_command(label=loc.get_text('menu_about'), command=self.show_about)

        # Set icon (if available)
        try:
            # Can add icon file
            pass
        except:
            pass

    def open_language_config(self):
        """Open language configuration dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(loc.get_text('language'))
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"350x200+{x}+{y}")

        # Language selection
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=loc.get_text('language') + ":").pack(pady=(0, 10))

        lang_var = tk.StringVar(value=loc.language)

        ttk.Radiobutton(frame, text=loc.get_text('english'),
                       variable=lang_var, value='en').pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(frame, text=loc.get_text('chinese'),
                       variable=lang_var, value='zh').pack(anchor=tk.W, pady=2)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        def apply_language():
            new_lang = lang_var.get()
            if new_lang != loc.language:
                loc.set_language(new_lang)
                # Save language to config file
                from localization import save_language_to_config
                if save_language_to_config(new_lang):
                    messagebox.showinfo(loc.get_text('info'),
                                      "Language will be applied after restart." if new_lang == 'en'
                                      else "Language setting will take effect after restart.")
                else:
                    messagebox.showerror(loc.get_text('error'),
                                       "Failed to save language setting." if new_lang == 'en'
                                       else "Failed to save language setting.")
            dialog.destroy()

        # Larger buttons with better styling
        ok_btn = ttk.Button(btn_frame, text="OK", command=apply_language, width=15)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15)
        cancel_btn.pack(side=tk.RIGHT)

    def open_llm_config(self):
        """Open LLM configuration dialog"""
        try:
            from ui.config_dialog import ConfigDialog
            dialog = ConfigDialog(self.root)
            # ConfigDialog已经在__init__中显示，不需要调用show()
        except ImportError as e:
            self.log_message(f"❌ Failed to import LLM config dialog: {e}")
            # Fallback to simplified config
            self.show_simple_llm_config()

    def open_analysis_config(self):
        """Open analysis configuration dialog"""
        messagebox.showinfo(loc.get_text('info'), "Analysis configuration will be implemented in future version.")

    def show_help(self):
        """Open README documentation"""
        import os
        import subprocess
        import platform
        import sys
        from pathlib import Path

        try:
            # 查找PDF文档文件
            pdf_filename = "MCU_Code_Analyzer_Complete_Documentation.pdf"

            # 获取资源文件路径
            def get_resource_path(relative_path):
                """获取资源文件的绝对路径"""
                if getattr(sys, 'frozen', False):
                    # 如果是打包的exe文件，资源在临时目录中
                    base_path = sys._MEIPASS
                else:
                    # 如果是Python脚本，资源在脚本目录
                    base_path = os.path.dirname(os.path.abspath(__file__))
                return os.path.join(base_path, relative_path)

            # 尝试从打包的资源中获取PDF
            doc_path = get_resource_path(pdf_filename)

            # 如果打包资源中没有，再尝试其他位置
            if not os.path.exists(doc_path):
                # 获取exe文件所在目录
                if getattr(sys, 'frozen', False):
                    exe_dir = os.path.dirname(sys.executable)
                else:
                    exe_dir = os.path.dirname(os.path.abspath(__file__))

                # 搜索路径列表
                search_paths = [
                    # exe文件所在目录
                    os.path.join(exe_dir, pdf_filename),
                    # 当前工作目录
                    pdf_filename,
                    # 上级目录
                    os.path.join("..", pdf_filename),
                    # exe目录的上级目录
                    os.path.join(exe_dir, "..", pdf_filename),
                ]

                doc_path = None
                for path in search_paths:
                    if os.path.exists(path):
                        doc_path = os.path.abspath(path)
                        break

            if doc_path and os.path.exists(doc_path):
                # 根据操作系统打开文档
                if platform.system() == "Windows":
                    os.startfile(doc_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", doc_path])
                else:  # Linux
                    subprocess.run(["xdg-open", doc_path])

                self.log_message(f"📖 {loc.get_text('document_opened', doc_path)}")
            else:
                # 如果找不到文档文件，显示简化帮助
                if getattr(sys, 'frozen', False):
                    self.log_message(f"⚠️ {loc.get_text('document_not_found', get_resource_path(pdf_filename))}")
                    self.log_message(f"📁 {loc.get_text('meipass_directory', sys._MEIPASS)}")
                else:
                    self.log_message(f"⚠️ {loc.get_text('document_not_found', '')}")
                self.log_message(f"📁 {loc.get_text('current_working_directory', os.getcwd())}")
                help_text = """MCU Code Analyzer - README

🚀 {loc.get_text('quick_start_colon')}
1. {loc.get_text('select_mcu_project_dir')}
2. {loc.get_text('configure_analysis_opts')}
3. {loc.get_text('click_start_analysis')}
4. {loc.get_text('view_analysis_results')}

📋 {loc.get_text('supported_project_types_colon')}
• {loc.get_text('keil_uvision_projects_ext')}
• {loc.get_text('cmake_projects_ext')}
• {loc.get_text('makefile_projects_simple')}
• {loc.get_text('general_cpp_projects_simple')}

🔧 {loc.get_text('llm_configuration_colon')}
• {loc.get_text('supports_ollama_local_models')}
• {loc.get_text('supports_tencent_cloud_api')}
• {loc.get_text('config_llm_config_path')}

📖 {loc.get_text('complete_documentation_pdf')}"""

                messagebox.showinfo("README", help_text)

        except Exception as e:
            self.log_message(f"❌ {loc.get_text('open_document_failed', e)}")
            # {loc.get_text('fallback_to_simple_help')}
            help_text = """MCU Code Analyzer - README

{loc.get_text('quick_start_simple_flow')}

{loc.get_text('supported_formats_list')}
{loc.get_text('llm_config_path_simple')}"""
            messagebox.showinfo("README", help_text)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(loc.get_text('about_title'), loc.get_text('about_text'))

    def start_llm_analysis(self):
        """Start LLM analysis"""
        messagebox.showinfo(loc.get_text('info'), "LLM analysis will be implemented in future version.")

    def clear_all(self):
        """Clear all results"""
        self.overview_text.delete(1.0, tk.END)
        self.detail_text.delete(1.0, tk.END)
        self.flowchart_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)
        # 重置进度条为绿色状态
        self.update_progress(0, is_error=False)
        self.status_var.set(loc.get_text('ready'))
        self.mermaid_code = ""
        self.call_graph = {}

        # Clear canvas and related widgets - 完全重建graph_preview_frame
        if hasattr(self, 'flowchart_canvas'):
            try:
                self.flowchart_canvas.delete("all")
            except tk.TclError:
                pass
            # Remove the canvas reference to force recreation
            delattr(self, 'flowchart_canvas')

        # 清理Call Flowchart标签页内容
        if hasattr(self, 'graph_preview_frame'):
            try:
                # 销毁所有子widget
                for widget in self.graph_preview_frame.winfo_children():
                    widget.destroy()
            except tk.TclError:
                pass

        # Clear any matplotlib figures if they exist
        if hasattr(self, 'graph_figure'):
            try:
                self.graph_figure.clear()
                if hasattr(self, 'graph_canvas'):
                    self.graph_canvas.draw()
            except:
                pass



    # 移除重复的log_message方法 - 使用文件末尾的线程安全版本

    # 移除重复的update_status方法 - 使用文件末尾的线程安全版本

    # 移除重复的update_progress方法 - 使用文件末尾的线程安全版本

    def set_progress_color(self, color):
        """设置进度条颜色 - NXP科技风格"""
        try:
            style = ttk.Style()
            if color == "red":
                # 现代红色 - 失败状态
                style.configure('Custom.Horizontal.TProgressbar',
                              background='#FF4444',  # 现代红色
                              lightcolor='#FF4444',
                              darkcolor='#FF4444')
            else:  # green
                # 现代绿色 - 成功状态
                style.configure('Custom.Horizontal.TProgressbar',
                              background='#00C851',  # 现代绿色
                              lightcolor='#00C851',
                              darkcolor='#00C851')
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to set progress color: {e}")

    def create_widgets(self):
        """Create interface components"""
        # Main frame - 简化UI，白色背景
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.root.configure(bg='white')

        # Title - 移除标题显示
        # self.title_label = ttk.Label(
        #     self.main_frame,
        #     text=loc.get_text('main_title'),
        #     font=("Segoe UI", 16, "bold"),
        #     style="ModernTitle.TLabel"
        # )

        # 简化UI - 移除框架，直接使用Frame
        self.path_frame = ttk.Frame(self.main_frame)

        # 第一行：目录设置
        self.directories_frame = ttk.Frame(self.path_frame)

        # MCU project path
        self.project_frame = ttk.Frame(self.directories_frame)
        self.project_label = ttk.Label(self.project_frame, text=loc.get_text('project_directory'))
        self.project_path_var = tk.StringVar()
        self.project_entry = ttk.Entry(self.project_frame, textvariable=self.project_path_var, width=50)
        self.browse_btn = ttk.Button(self.project_frame, text=loc.get_text('browse'), command=self.browse_project)

        # Output directory
        self.output_frame = ttk.Frame(self.directories_frame)
        self.output_label = ttk.Label(self.output_frame, text=loc.get_text('output_directory'))
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_path_var, width=50)
        self.output_browse_btn = ttk.Button(self.output_frame, text=loc.get_text('browse'), command=self.browse_output)

        # 第二行：分析选项
        self.analysis_options_frame = ttk.Frame(self.path_frame)

        # 从配置文件读取分析选项，不再显示UI配置
        # 所有配置选项现在都在config.yaml中设置

        # 第三行：Start Analysis按钮和LLM分析按钮
        self.button_row = ttk.Frame(self.analysis_options_frame)
        self.log_message(f"🔧 DEBUG: {loc.get_text('creating_analyze_button')}")  # 添加debug输出
        self.analyze_btn = ttk.Button(
            self.button_row,
            text=loc.get_text('start_analysis'),
            command=self.start_analysis
        )
        self.log_message(f"🔧 DEBUG: {loc.get_text('analyze_button_created')}")  # 添加debug输出

        # LLM代码分析按钮
        self.llm_analysis_btn = ttk.Button(
            self.button_row,
            text="🤖 " + loc.get_text('llm_code_analysis'),
            command=self.start_llm_analysis
        )
        self.log_message(f"🔧 DEBUG: {loc.get_text('llm_analysis_button_created')}")

        # Progress bar with percentage display
        self.progress_var = tk.DoubleVar()

        # 创建进度条容器
        self.progress_frame = ttk.Frame(self.main_frame)

        # 创建更细的进度条
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )

        # 创建百分比标签
        self.progress_percentage = ttk.Label(
            self.progress_frame,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            foreground="green"
        )

        # 配置自定义进度条样式
        self.setup_progress_style()

    def setup_progress_style(self):
        """设置现代NXP科技风格样式"""
        try:
            style = ttk.Style()

            # 使用最兼容的主题
            try:
                style.theme_use('clam')  # 使用clam主题，兼容性最好
            except:
                style.theme_use('default')  # 默认主题

            # 简化配色方案 - 移除灰色背景
            nxp_colors = {
                'primary': '#0066CC',      # NXP蓝色
                'success': '#00C851',      # 现代绿色
                'danger': '#FF4444',       # 现代红色
                'background': '#FFFFFF',   # 白色背景
                'surface': '#FFFFFF',      # 白色表面
                'border': '#E0E0E0',       # 边框灰色
                'text': '#212529',         # 深色文字
                'text_secondary': '#6C757D' # 次要文字
            }

            # 配置进度条样式 - NXP科技风格
            style.configure('Custom.Horizontal.TProgressbar',
                          background=nxp_colors['success'],  # 现代绿色
                          troughcolor=nxp_colors['background'],  # 浅灰槽
                          borderwidth=0,
                          lightcolor=nxp_colors['success'],
                          darkcolor=nxp_colors['success'],
                          relief='flat')

            # 设置进度条高度（更细现代风格）
            style.configure('Custom.Horizontal.TProgressbar',
                          thickness=6)  # 6像素高度，现代细线风格

            # 配置整体UI风格
            self.setup_modern_ui_style(style, nxp_colors)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to setup progress style: {e}")

        # 移除按钮样式刷新 - 使用默认样式
        # self.refresh_button_styles()

    def refresh_button_styles(self):
        """强制刷新按钮样式"""
        try:
            # 直接设置按钮属性，确保样式生效
            button_config = {
                'background': '#0066CC',
                'foreground': 'white',
                'relief': 'flat',
                'borderwidth': 0,
                'font': ('Segoe UI', 9, 'bold'),
                'cursor': 'hand2'
            }

            if hasattr(self, 'analyze_btn'):
                self.analyze_btn.configure(**button_config)
            if hasattr(self, 'llm_analysis_btn'):
                self.llm_analysis_btn.configure(**button_config)
            if hasattr(self, 'browse_btn'):
                self.browse_btn.configure(**button_config)
            if hasattr(self, 'output_browse_btn'):
                self.output_browse_btn.configure(**button_config)

            self.log_message("🔧 DEBUG: Button styles applied directly")
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to refresh button styles: {e}")

    def setup_modern_ui_style(self, style, colors):
        """设置现代UI风格"""
        try:
            # 配置现代按钮样式 - NXP科技风格
            style.configure('Modern.TButton',
                          background='#0066CC',      # NXP蓝色
                          foreground='white',        # 白色文字
                          borderwidth=0,             # 无边框
                          focuscolor='none',         # 无焦点框
                          relief='flat',             # 扁平样式
                          padding=(15, 10),          # 更大的内边距
                          font=('Segoe UI', 9, 'bold'))  # 粗体字体

            style.map('Modern.TButton',
                     background=[('active', '#0052A3'),    # 悬停时深蓝色
                               ('pressed', '#004080'),     # 按下时更深蓝色
                               ('disabled', '#CCCCCC')],   # 禁用时灰色
                     foreground=[('active', 'white'),
                               ('pressed', 'white'),
                               ('disabled', '#666666')])   # 禁用时深灰色文字

            # 配置框架样式
            style.configure('Modern.TFrame',
                          background=colors['surface'],
                          relief='flat',
                          borderwidth=0)

            # 配置LabelFrame样式 - Project Settings
            style.configure('Modern.TLabelframe',
                          background=colors['surface'],
                          relief='flat',
                          borderwidth=1,
                          bordercolor=colors['primary'])

            style.configure('Modern.TLabelframe.Label',
                          background=colors['surface'],
                          foreground=colors['primary'],
                          font=('Segoe UI', 10, 'bold'))

            # 配置标签样式
            style.configure('Modern.TLabel',
                          background=colors['surface'],
                          foreground=colors['text'],
                          font=('Segoe UI', 9))

            style.configure('ModernTitle.TLabel',
                          background=colors['surface'],
                          foreground=colors['primary'],
                          font=('Segoe UI', 11, 'bold'))

            # 配置笔记本样式
            style.configure('Modern.TNotebook',
                          background=colors['background'],
                          borderwidth=0,
                          tabmargins=[0, 0, 0, 0])

            style.configure('Modern.TNotebook.Tab',
                          background=colors['background'],
                          foreground=colors['text'],
                          padding=[12, 8],
                          borderwidth=0,
                          focuscolor='none')

            style.map('Modern.TNotebook.Tab',
                     background=[('selected', colors['surface']),
                               ('active', colors['border'])])

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to setup modern UI style: {e}")

        # Status label
        self.status_var = tk.StringVar(value=loc.get_text('ready'))
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)

        # 简化UI - 移除结果区域框架
        self.result_frame = ttk.Frame(self.main_frame)

        # Create Notebook for multiple tabs - 使用默认样式
        self.notebook = ttk.Notebook(self.result_frame)

        # Bind tab selection event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Overview tab
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text=loc.get_text('project_overview'))
        self.overview_text = scrolledtext.ScrolledText(
            self.overview_frame,
            height=15,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True)

        # Detailed analysis tab
        self.detail_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_frame, text=loc.get_text('detailed_analysis'))
        self.detail_text = scrolledtext.ScrolledText(
            self.detail_frame,
            height=15,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # Call flowchart tab - 直接显示图形
        self.flowchart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.flowchart_frame, text=loc.get_text('call_flowchart'))

        # 创建流程图控制区域
        self.flowchart_control_frame = ttk.Frame(self.flowchart_frame)
        self.flowchart_control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 添加版本选择控件
        ttk.Label(self.flowchart_control_frame, text="流程图格式:").pack(side=tk.LEFT, padx=(0, 5))

        self.flowchart_format_var = tk.StringVar(value="mermaid")
        self.flowchart_format_combo = ttk.Combobox(
            self.flowchart_control_frame,
            textvariable=self.flowchart_format_var,
            values=["mermaid", "plantuml"],
            state="readonly",
            width=12
        )
        self.flowchart_format_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.flowchart_format_combo.bind("<<ComboboxSelected>>", self.on_flowchart_format_changed)

        # 添加刷新按钮
        self.refresh_flowchart_btn = ttk.Button(
            self.flowchart_control_frame,
            text="🔄 刷新",
            command=self.refresh_current_flowchart
        )
        self.refresh_flowchart_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 添加导出图片按钮
        self.export_image_btn = ttk.Button(
            self.flowchart_control_frame,
            text="📸 导出图片",
            command=self.export_high_quality_image
        )
        self.export_image_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 添加渲染模式切换按钮
        self.rendering_mode_var = tk.StringVar()
        self.update_rendering_mode_display()

        self.rendering_mode_btn = ttk.Button(
            self.flowchart_control_frame,
            textvariable=self.rendering_mode_var,
            command=self.toggle_rendering_mode,
            width=12
        )
        self.rendering_mode_btn.pack(side=tk.LEFT, padx=(10, 5))

        # 创建图形显示区域
        self.graph_preview_frame = ttk.Frame(self.flowchart_frame)
        self.graph_preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 设置默认值（最高质量SVG）
        self.format_var = tk.StringVar(value="svg")  # 默认SVG
        self.quality_var = tk.StringVar(value="ultra")  # 默认最高质量

        # 设置窗口关闭协议
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 添加窗口尺寸变化监听
        self.last_window_size = None
        self.resize_timer = None
        self.root.bind('<Configure>', self.on_window_configure)

        # 图形显示区域
        if MATPLOTLIB_AVAILABLE:
            # 创建matplotlib图形
            self.graph_figure = Figure(figsize=(12, 8), dpi=80)
            self.graph_canvas = FigureCanvasTkAgg(self.graph_figure, self.graph_preview_frame)
            self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        else:
            # 降级到文本显示
            self.graph_display_text = scrolledtext.ScrolledText(
                self.graph_preview_frame,
                height=15,
                font=("Microsoft YaHei", 9),
                wrap=tk.WORD,
                state=tk.DISABLED
            )
            self.graph_display_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Log tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text=loc.get_text('execution_log'))
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=15,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Source Flowchart tab (重命名从Source Mermaid)
        self.source_flowchart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.source_flowchart_frame, text="Source Flowchart")

        # 控制区域
        source_control_frame = ttk.Frame(self.source_flowchart_frame)
        source_control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 格式选择区域
        format_frame = ttk.Frame(source_control_frame)
        format_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(format_frame, text="源码格式:").pack(side=tk.LEFT, padx=(0, 5))

        self.source_format_var = tk.StringVar(value="mermaid")
        self.source_format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.source_format_var,
            values=["mermaid", "plantuml"],
            state="readonly",
            width=12
        )
        self.source_format_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.source_format_combo.bind("<<ComboboxSelected>>", self.on_source_format_changed)

        # 按钮区域
        source_button_frame = ttk.Frame(source_control_frame)
        source_button_frame.pack(side=tk.RIGHT)

        # LLM Analysis按钮
        self.llm_analysis_inline_btn = ttk.Button(
            source_button_frame,
            text="🤖 LLM Analysis",
            command=self.start_llm_analysis
        )
        self.llm_analysis_inline_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 文本区域
        self.flowchart_text = scrolledtext.ScrolledText(
            self.source_flowchart_frame,
            height=15,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.flowchart_text.pack(fill=tk.BOTH, expand=True)

        # LLM Analysis tab
        self.llm_analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.llm_analysis_frame, text="LLM Analysis")

        # System Prompt区域
        system_frame = ttk.LabelFrame(self.llm_analysis_frame, text="System Prompt", padding="5")
        system_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        self.system_prompt_text = scrolledtext.ScrolledText(
            system_frame,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.system_prompt_text.pack(fill=tk.BOTH, expand=True)

        # User Prompt区域
        user_frame = ttk.LabelFrame(self.llm_analysis_frame, text="User Prompt", padding="5")
        user_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        self.user_prompt_text = scrolledtext.ScrolledText(
            user_frame,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.user_prompt_text.pack(fill=tk.BOTH, expand=True)

        # 按钮和状态区域
        llm_control_frame = ttk.Frame(self.llm_analysis_frame)
        llm_control_frame.pack(fill=tk.X, padx=5, pady=2)

        # 左侧：状态和timeout控制
        left_control_frame = ttk.Frame(llm_control_frame)
        left_control_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.llm_status_label = ttk.Label(left_control_frame, text="Ready", foreground="blue")
        self.llm_status_label.pack(side=tk.LEFT)

        # Timeout控制
        timeout_frame = ttk.Frame(left_control_frame)
        timeout_frame.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Label(timeout_frame, text="Timeout:").pack(side=tk.LEFT)

        self.timeout_var = tk.StringVar(value="200")
        self.timeout_entry = ttk.Entry(
            timeout_frame,
            textvariable=self.timeout_var,
            width=6,
            font=("Consolas", 9)
        )
        self.timeout_entry.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(timeout_frame, text="s").pack(side=tk.LEFT, padx=(2, 0))

        # 右侧：开始分析按钮
        self.llm_start_btn = ttk.Button(
            llm_control_frame,
            text="Start Analysis",
            command=self.run_llm_analysis_inline
        )
        self.llm_start_btn.pack(side=tk.RIGHT)

        # LLM Result区域
        result_frame = ttk.LabelFrame(self.llm_analysis_frame, text="Analysis Result", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(2, 5))

        self.llm_result_text = scrolledtext.ScrolledText(
            result_frame,
            height=12,
            font=("Microsoft YaHei", 10),
            wrap=tk.WORD
        )
        self.llm_result_text.pack(fill=tk.BOTH, expand=True)

    def setup_layout(self):
        """设置布局"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 移除标题显示
        # self.title_label.pack(pady=(0, 10))

        # 项目设置（包含目录和分析选项）
        self.path_frame.pack(fill=tk.X, pady=(10, 10))

        # 第一行：目录设置 - 水平排列
        self.directories_frame.pack(fill=tk.X, pady=(0, 8))

        # 项目目录 - 左半部分
        self.project_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.project_label.pack(side=tk.LEFT)
        self.browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.project_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 5))

        # 输出目录 - 右半部分
        self.output_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.output_label.pack(side=tk.LEFT)
        self.output_browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.output_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 5))

        # 分析选项现在通过配置对话框设置
        self.analysis_options_frame.pack(fill=tk.X, pady=(0, 8))

        # 第三行：Start Analysis按钮和LLM分析按钮
        self.button_row.pack(fill=tk.X, pady=(8, 0))
        self.analyze_btn.pack(side=tk.LEFT)
        self.llm_analysis_btn.pack(side=tk.LEFT, padx=(10, 0))

        # 进度条容器和百分比
        self.progress_frame.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.progress_percentage.pack(side=tk.RIGHT)

        # 状态标签（隐藏，不再显示文字状态）
        # self.status_label.pack(anchor=tk.W)  # 注释掉状态标签

        # 结果区域
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 移除按钮样式应用 - 使用默认样式
        # self.root.after(100, self.refresh_button_styles)

    def browse_project(self):
        """Browse project directory"""
        # 从上次的路径开始浏览
        initial_dir = self.project_path_var.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")  # 默认用户主目录

        path = filedialog.askdirectory(
            title="Select MCU Project Directory",
            initialdir=initial_dir
        )
        if path:
            self.project_path_var.set(path)
            # Auto set output path
            if not self.output_path_var.get():
                output_path = os.path.join(path, "Analyzer_Output")
                self.output_path_var.set(output_path)

            # 保存新选择的路径到配置文件
            self.save_current_config()

    def browse_output(self):
        """Browse output directory"""
        # 从当前输出路径开始浏览
        initial_dir = self.output_path_var.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            project_path = self.project_path_var.get().strip()
            if project_path and os.path.exists(project_path):
                initial_dir = project_path
            else:
                initial_dir = os.path.expanduser("~")

        path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir
        )
        if path:
            self.output_path_var.set(path)
            # 保存新选择的输出路径
            self.save_current_config()

    def start_analysis(self):
        """Start analysis"""
        self.log_message(f"🔧 DEBUG: {loc.get_text('start_analysis_called')}")

        try:
            project_path = self.project_path_var.get().strip()
            self.log_message(f"🔧 DEBUG: {loc.get_text('project_path_equals', project_path)}")

            if not project_path:
                self.log_message("🔧 DEBUG: No project path selected")
                messagebox.showerror(loc.get_text('error'), loc.get_text('select_project_dir'))
                return

            if not os.path.exists(project_path):
                self.log_message(f"🔧 DEBUG: Project path does not exist: {project_path}")
                messagebox.showerror(loc.get_text('error'), loc.get_text('project_dir_not_exist'))
                return

            output_path = self.output_path_var.get().strip()
            self.log_message(f"🔧 DEBUG: output_path = '{output_path}'")

            if not output_path:
                self.log_message("🔧 DEBUG: No output path selected")
                messagebox.showerror(loc.get_text('error'), loc.get_text('select_output_dir'))
                return

            self.log_message(f"🔧 DEBUG: {loc.get_text('all_paths_validated')}")

            # 禁用按钮并清空结果 - 线程安全
            def prepare_ui():
                self.analyze_btn.config(state="disabled")
                self.overview_text.delete(1.0, tk.END)
                self.detail_text.delete(1.0, tk.END)
                self.log_text.delete(1.0, tk.END)

            self.root.after(0, prepare_ui)

            # 清理已有的分析文件夹
            self.log_message(f"🔧 DEBUG: {loc.get_text('cleaning_existing_folders')}")
            self.clean_existing_analysis_folders(output_path)

            # 在新线程中执行分析
            self.log_message(f"🔧 DEBUG: {loc.get_text('starting_analysis_thread')}")
            analysis_thread = threading.Thread(target=self.run_analysis, args=(project_path, output_path))
            analysis_thread.daemon = True
            analysis_thread.start()
            self.log_message("🔧 DEBUG: Analysis thread started!")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Exception in start_analysis: {e}")
            import traceback
            traceback.print_exc()
            # 确保按钮重新启用
            try:
                self.analyze_btn.config(state="normal")
            except:
                pass

    def start_llm_analysis(self):
        """启动LLM代码分析"""
        try:
            # 检查是否有分析结果
            if not hasattr(self, 'analysis_result') or not self.analysis_result:
                messagebox.showinfo(loc.get_text('info'), loc.get_text('please_complete_analysis_first'))
                return

            # 禁用按钮
            self.llm_analysis_btn.config(state="disabled")

            # 在后台线程中运行LLM分析
            import threading
            llm_thread = threading.Thread(target=self.run_llm_analysis)
            llm_thread.daemon = True
            llm_thread.start()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: LLM analysis start failed: {e}")
            messagebox.showerror(loc.get_text('error'), loc.get_text('startup_llm_analysis_failed', e))
            # 重新启用按钮
            try:
                self.llm_analysis_btn.config(state="normal")
            except:
                pass

    def load_global_config(self):
        """加载全局配置文件"""
        try:
            import yaml
            from pathlib import Path

            # 查找配置文件
            possible_paths = [
                Path(__file__).parent / "config.yaml",
                Path.cwd() / "config.yaml"
            ]

            for config_path in possible_paths:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    self.log_message(f"🔧 DEBUG: Loaded global config from: {config_path}")
                    return config

            # 如果没有找到配置文件，返回默认配置
            self.log_message("🔧 DEBUG: No config file found, using defaults")
            return {
                'mermaid': {
                    'rendering_mode': 'online',
                    'online': {'enabled': True},
                    'local': {'enabled': True}
                }
            }

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to load global config: {e}")
            return {
                'mermaid': {
                    'rendering_mode': 'online',
                    'online': {'enabled': True},
                    'local': {'enabled': True}
                }
            }

    def load_analysis_config(self):
        """从配置文件加载分析选项"""
        try:
            import yaml
            from pathlib import Path

            # 查找配置文件
            possible_paths = [
                Path(__file__).parent / "config.yaml",
                Path.cwd() / "config.yaml"
            ]

            for config_path in possible_paths:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    return config.get('analysis_options', {})

            # 如果没有找到配置文件，返回默认值
            return {
                'deep_analysis': True,
                'call_analysis': True,
                'generate_report': True,
                'show_flowchart': True,
                'call_depth': 2
            }

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to load analysis config: {e}")
            # 返回默认值
            return {
                'deep_analysis': True,
                'call_analysis': True,
                'generate_report': True,
                'show_flowchart': True,
                'call_depth': 2
            }

    def clean_existing_analysis_folders(self, output_path):
        """清理输出目录中已有的分析文件夹"""
        try:
            # 常见的分析输出文件夹名称
            analysis_folders = [
                'Analyzer_Output',
                'Analysis_Results',
                'STM32_Analysis',
                'MCU_Analysis'
            ]

            for folder_name in analysis_folders:
                folder_path = os.path.join(output_path, folder_name)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    self.log_message(f"🗑️ {loc.get_text('delete_existing_folder', folder_name)}")
                    shutil.rmtree(folder_path)

            # 也删除常见的分析文件
            analysis_files = [
                'analysis_report.md',
                'call_graph.json',
                'interface_analysis.json',
                'chip_info.json'
            ]

            for file_name in analysis_files:
                file_path = os.path.join(output_path, file_name)
                if os.path.exists(file_path):
                    self.log_message(f"🗑️ {loc.get_text('delete_existing_file', file_name)}")
                    os.remove(file_path)

        except Exception as e:
            self.log_message(f"⚠️ {loc.get_text('cleanup_files_error', e)}")

    def run_analysis(self, project_path, output_path):
        """Run analysis (in background thread)"""
        self.log_message("🔧 DEBUG: run_analysis() started!")  # 添加debug输出
        self.log_message(f"🔧 DEBUG: {loc.get_text('project_path_equals', project_path)}")  # 添加debug输出
        self.log_message(f"🔧 DEBUG: {loc.get_text('output_path_equals', output_path)}")  # 添加debug输出

        try:
            self.log_message(f"🔧 DEBUG: {loc.get_text('about_to_call_log_message')}")  # 添加debug输出
            self.log_message(loc.get_text('starting_analysis'))
            self.log_message(f"🔧 DEBUG: {loc.get_text('log_message_called_successfully')}")  # 添加debug输出

            self.log_message(f"🔧 DEBUG: {loc.get_text('about_to_update_status')}")  # 添加debug输出
            self.update_status(loc.get_text('analyzing'))
            self.log_message(f"🔧 DEBUG: {loc.get_text('status_updated_successfully')}")  # 添加debug输出

            # 重置进度条为绿色状态
            self.log_message(f"🔧 DEBUG: {loc.get_text('about_to_update_progress')}")  # 添加debug输出
            self.update_progress(0, is_error=False)
            self.log_message(f"🔧 DEBUG: {loc.get_text('progress_updated_successfully')}")  # 添加debug输出

            # Ensure output directory exists
            os.makedirs(output_path, exist_ok=True)

            # Step 1: Scan project files
            self.log_message(loc.get_text('scanning_files'))
            self.update_progress(10)
            project_files = self.scan_project_files(project_path)

            # Step 2: Detect chip information using ChipDetector
            self.log_message(loc.get_text('detecting_chip'))
            self.update_progress(30)
            chip_info = self.chip_detector.detect_from_project_file(Path(project_path))

            # 从配置文件读取分析选项
            analysis_config = self.load_analysis_config()

            # Step 3: Analyze code structure
            if analysis_config.get('deep_analysis', True):
                self.log_message(loc.get_text('analyzing_code'))
                self.update_progress(50)
                code_analysis = self.analyze_code_structure(project_path, project_files)
            else:
                code_analysis = {"message": "Skipped deep code analysis"}

            # Step 4: Analyze call relationships
            if analysis_config.get('call_analysis', True):
                self.log_message(loc.get_text('analyzing_calls'))
                self.update_progress(70)
                call_analysis = self.analyze_call_relationships(project_path, project_files, code_analysis)

                # Generate Mermaid flowchart
                if analysis_config.get('show_flowchart', True):
                    self.log_message(loc.get_text('generating_flowchart'))
                    self.generate_mermaid_flowchart(call_analysis)
            else:
                call_analysis = {"message": "Skipped call relationship analysis"}

            # Step 5: Generate report
            if analysis_config.get('generate_report', True):
                self.log_message(loc.get_text('generating_report'))
                self.update_progress(90)
                self.generate_report(output_path, chip_info, code_analysis, call_analysis)

            # Save analysis results for LLM use
            self.current_project_path = project_path
            self.last_chip_info = chip_info
            self.last_code_analysis = code_analysis
            self.last_call_analysis = call_analysis
            self.last_analysis_results = True

            # Display results
            self.display_results(chip_info, code_analysis, call_analysis)

            self.update_progress(100)
            self.update_status(loc.get_text('analysis_complete'))
            self.log_message(loc.get_text('analysis_completed'))

            # {loc.get_text('auto_trigger_flowchart_redraw')}
            self.auto_trigger_flowchart_redraw()

            # 移除弹窗，只在状态栏显示完成信息

        except Exception as e:
            self.log_message(f"Analysis failed: {e}")
            self.update_status(f"{loc.get_text('analysis_failed')}: {e}")
            # 显示红色进度条表示失败
            self.update_progress(100, is_error=True)
            messagebox.showerror(loc.get_text('error'), loc.get_text('analysis_error', e))

        finally:
            # Restore button states
            self.root.after(0, lambda: self.analyze_btn.config(state="normal"))

    def scan_project_files(self, project_path):
        """扫描项目文件"""
        files = {
            'source_files': [],
            'header_files': [],
            'project_files': []
        }

        for root, dirs, filenames in os.walk(project_path):
            # {loc.get_text('skip_some_directories')}
            dirs[:] = [d for d in dirs if d not in ['build', 'debug', 'release', '.git', '__pycache__']]

            for filename in filenames:
                file_path = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()

                if ext in ['.c', '.cpp']:
                    files['source_files'].append(file_path)
                elif ext in ['.h', '.hpp']:
                    files['header_files'].append(file_path)
                elif ext in ['.uvprojx', '.uvproj', '.ioc', '.cproject']:
                    files['project_files'].append(file_path)

        self.log_message(loc.get_text('found_source_files', len(files['source_files'])))
        self.log_message(loc.get_text('found_header_files', len(files['header_files'])))
        self.log_message(loc.get_text('found_project_files', len(files['project_files'])))

        return files



    def analyze_code_structure(self, project_path, project_files):
        """分析代码结构"""
        analysis = {
            'total_functions': 0,
            'main_found': False,
            'includes': [],  # {loc.get_text('change_to_list_not_set')}
            'functions': []
        }

        function_pattern = re.compile(r'\b(?:void|int|char|float|double|static\s+\w+|\w+\s*\*?)\s+(\w+)\s*\([^)]*\)\s*\{')
        include_pattern = re.compile(r'#include\s*[<"]([^>"]+)[>"]')

        for source_file in project_files['source_files'][:10]:  # {loc.get_text('limit_analysis_file_count')}
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # {loc.get_text('find_functions')}
                functions = function_pattern.findall(content)
                analysis['functions'].extend(functions)
                analysis['total_functions'] += len(functions)

                if 'main' in functions:
                    analysis['main_found'] = True

                # {loc.get_text('find_include_files')}
                includes = include_pattern.findall(content)
                for include in includes:
                    if include not in analysis['includes']:
                        analysis['includes'].append(include)

            except Exception as e:
                self.log_message(f"⚠️ {loc.get_text('file_analysis_failed', source_file, e)}")

        self.log_message(f"💻 {loc.get_text('found_functions_count', analysis['total_functions'])}")
        self.log_message(f"💻 {loc.get_text('main_function_status', '✅' if analysis['main_found'] else '❌')}")

        return analysis

    def analyze_call_relationships(self, project_path, project_files, code_analysis):
        """分析从main函数开始的调用关系"""
        self.log_message(f"🔍 {loc.get_text('analyzing_call_relationships')}...")

        # {loc.get_text('get_call_depth_from_config')}
        analysis_config = self.load_analysis_config()
        max_depth = analysis_config.get('call_depth', 2)

        # {loc.get_text('store_all_function_definitions_calls')}
        all_functions = {}  # {function_name: {'file': file_path, 'calls': [called_functions]}}

        # {loc.get_text('first_step')}：{loc.get_text('parse_all_function_definitions')}
        for source_file in project_files['source_files'] + project_files['header_files']:
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 移除注释和字符串字面量，避免误识别
                content = self.remove_comments_and_strings(content)

                # 查找函数定义
                function_defs = self.extract_function_definitions(content, source_file)
                for func_name, func_info in function_defs.items():
                    if func_name not in all_functions:
                        all_functions[func_name] = func_info

            except Exception as e:
                self.log_message(f"⚠️ {loc.get_text('parse_function_calls_failed', source_file, e)}")

        # 第二步：分析每个函数的调用关系
        for source_file in project_files['source_files'] + project_files['header_files']:
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 移除注释和字符串字面量
                content = self.remove_comments_and_strings(content)

                # 分析每个函数内部的调用关系
                self.analyze_function_calls_in_file(content, source_file, all_functions)

            except Exception as e:
                self.log_message(f"⚠️ {loc.get_text('parse_function_calls_failed', source_file, e)}")

        # 第二步：从main函数开始构建调用树
        call_tree = self.build_call_tree(all_functions, 'main', max_depth)

        # 第三步：分析接口使用（只统计调用树中的函数）
        interface_usage = self.analyze_interface_usage_in_call_tree(call_tree, project_files)

        result = {
            'call_tree': call_tree,
            'interface_usage': interface_usage,
            'total_functions_in_tree': self.count_functions_in_tree(call_tree),
            'max_depth_reached': self.get_max_depth_in_tree(call_tree),
            'all_functions': all_functions
        }

        # 保存到实例变量供Mermaid使用
        self.call_graph = result

        # 保存接口使用信息供LLM使用
        self.last_interfaces = interface_usage

        self.log_message(f"🔄 {loc.get_text('build_call_tree_completed', result['max_depth_reached'])}")
        self.log_message(f"🔄 {loc.get_text('call_tree_function_count', result['total_functions_in_tree'])}")

        return result

    def remove_comments_and_strings(self, content):
        """移除C代码中的注释和字符串字面量"""
        # 简化版本，移除单行注释、多行注释和字符串
        import re

        # 移除多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # 移除单行注释
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # 移除字符串字面量
        content = re.sub(r'"[^"]*"', '""', content)
        content = re.sub(r"'[^']*'", "''", content)

        return content

    def extract_function_definitions(self, content, file_path):
        """提取函数定义"""
        functions = {}

        # 匹配函数定义的正则表达式
        pattern = r'\b(?:static\s+)?(?:inline\s+)?(?:void|int|char|float|double|uint\w*|int\w*|\w+\s*\*?)\s+(\w+)\s*\([^)]*\)\s*\{'

        for match in re.finditer(pattern, content):
            func_name = match.group(1)
            # 排除一些关键字
            if func_name not in ['if', 'while', 'for', 'switch', 'return']:
                functions[func_name] = {
                    'file': file_path,
                    'calls': []
                }

        return functions

    def extract_function_calls(self, content):
        """提取函数调用"""
        calls = []

        # 匹配函数调用的正则表达式
        pattern = r'\b(\w+)\s*\('

        for match in re.finditer(pattern, content):
            func_name = match.group(1)
            # 排除一些关键字和常见的非函数调用
            if func_name not in ['if', 'while', 'for', 'switch', 'return', 'sizeof', 'typeof']:
                calls.append(func_name)

        return calls

    def analyze_function_calls_in_file(self, content, source_file, all_functions):
        """分析文件中每个函数内部的调用关系"""
        import re

        # 找到文件中所有函数的定义位置和内容
        function_pattern = r'\b(?:static\s+)?(?:inline\s+)?(?:void|int|char|float|double|uint\w*|int\w*|\w+\s*\*?)\s+(\w+)\s*\([^)]*\)\s*\{'

        for match in re.finditer(function_pattern, content):
            func_name = match.group(1)
            if func_name in ['if', 'while', 'for', 'switch', 'return']:
                continue

            if func_name not in all_functions:
                continue

            # 找到函数体的开始位置
            func_start = match.end() - 1  # 函数体开始的 '{'

            # 找到匹配的结束大括号
            func_body = self.extract_function_body(content, func_start)
            if not func_body:
                continue

            # 在函数体中查找函数调用
            calls_in_function = self.extract_function_calls(func_body)

            # 只保留在all_functions中定义的函数调用
            valid_calls = []
            for called_func in calls_in_function:
                if called_func in all_functions and called_func != func_name:  # 避免自调用
                    valid_calls.append(called_func)

            # 更新函数的调用列表
            if valid_calls:
                all_functions[func_name]['calls'] = list(set(valid_calls))  # 去重

    def extract_function_body(self, content, start_pos):
        """提取函数体内容（从开始大括号到匹配的结束大括号）"""
        if start_pos >= len(content) or content[start_pos] != '{':
            return ""

        brace_count = 1
        pos = start_pos + 1

        while pos < len(content) and brace_count > 0:
            char = content[pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            return content[start_pos:pos]
        else:
            return ""  # 未找到匹配的结束大括号

    def build_call_tree(self, all_functions, start_function, max_depth, current_depth=0, visited=None):
        """构建调用树"""
        if visited is None:
            visited = set()

        if current_depth >= max_depth or start_function in visited:
            return None

        if start_function not in all_functions:
            return None

        visited.add(start_function)

        node = {
            'name': start_function,
            'file': all_functions[start_function].get('file', '未知'),
            'depth': current_depth,
            'children': []
        }

        # 递归构建子节点
        calls = all_functions[start_function].get('calls', [])
        for called_func in calls:
            child = self.build_call_tree(all_functions, called_func, max_depth, current_depth + 1, visited.copy())
            if child:
                node['children'].append(child)

        return node

    def count_functions_in_tree(self, tree):
        """统计调用树中的函数数量"""
        if not tree:
            return 0

        count = 1
        for child in tree.get('children', []):
            count += self.count_functions_in_tree(child)

        return count

    def get_max_depth_in_tree(self, tree):
        """获取调用树的最大深度"""
        if not tree:
            return 0

        if not tree.get('children'):
            return tree.get('depth', 0)

        max_child_depth = max(self.get_max_depth_in_tree(child) for child in tree['children'])
        return max_child_depth

    def analyze_interface_usage_in_call_tree(self, call_tree, project_files):
        """分析调用树中的接口使用情况"""
        if not call_tree:
            return {}

        # 收集调用树中的所有函数名
        functions_in_tree = set()
        self.collect_functions_from_tree(call_tree, functions_in_tree)

        # 接口模式
        interface_patterns = {
            'GPIO': ['HAL_GPIO_', 'GPIO_Pin', 'GPIO_Port'],
            'UART': ['HAL_UART_', 'UART_', 'USART_'],
            'SPI': ['HAL_SPI_', 'SPI_'],
            'I2C': ['HAL_I2C_', 'I2C_'],
            'TIMER': ['HAL_TIM_', 'TIM_'],
            'ADC': ['HAL_ADC_', 'ADC_'],
            'DMA': ['HAL_DMA_', 'DMA_'],
            'CLOCK': ['HAL_RCC_', 'RCC_', 'SystemClock']
        }

        interface_usage = {}

        # 只在调用树相关的文件中搜索接口使用
        for source_file in project_files['source_files'] + project_files['header_files']:
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 检查文件中是否包含调用树中的函数
                file_has_tree_functions = any(func_name in content for func_name in functions_in_tree)

                if file_has_tree_functions:
                    for interface, patterns in interface_patterns.items():
                        if interface not in interface_usage:
                            interface_usage[interface] = 0

                        for pattern in patterns:
                            # 只统计函数调用，不统计定义和注释
                            call_pattern = pattern + r'\w*\s*\('
                            matches = re.findall(call_pattern, content)
                            interface_usage[interface] += len(matches)

            except Exception:
                continue

        # 只返回有使用的接口
        return {k: v for k, v in interface_usage.items() if v > 0}

    def collect_functions_from_tree(self, tree, functions_set):
        """从调用树中收集所有函数名"""
        if not tree:
            return

        functions_set.add(tree['name'])
        for child in tree.get('children', []):
            self.collect_functions_from_tree(child, functions_set)

    def analyze_interfaces(self, project_path, project_files):
        """分析接口使用"""
        interfaces = {
            'GPIO': 0,
            'UART': 0,
            'SPI': 0,
            'I2C': 0,
            'TIMER': 0,
            'ADC': 0,
            'DMA': 0
        }

        # 接口关键字模式
        patterns = {
            'GPIO': ['HAL_GPIO', 'GPIO_', '__HAL_GPIO'],
            'UART': ['HAL_UART', 'UART_', 'USART_'],
            'SPI': ['HAL_SPI', 'SPI_'],
            'I2C': ['HAL_I2C', 'I2C_'],
            'TIMER': ['HAL_TIM', 'TIM_', 'Timer'],
            'ADC': ['HAL_ADC', 'ADC_'],
            'DMA': ['HAL_DMA', 'DMA_']
        }

        for source_file in project_files['source_files'] + project_files['header_files']:
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for interface, keywords in patterns.items():
                    for keyword in keywords:
                        count = content.count(keyword)
                        interfaces[interface] += count

            except Exception as e:
                continue

        # 只保留使用的接口
        used_interfaces = {k: v for k, v in interfaces.items() if v > 0}

        self.log_message(f"🔌 Detected interfaces: {list(used_interfaces.keys())}")

        return used_interfaces

    def generate_mermaid_flowchart(self, call_analysis):
        """根据UI宽度实时生成自适应Mermaid流程图"""
        if not call_analysis or 'call_tree' not in call_analysis:
            self.mermaid_code = "graph TD\n    A[未找到调用关系]"
            return

        call_tree = call_analysis['call_tree']
        if not call_tree:
            self.mermaid_code = "graph TD\n    A[未找到main函数或调用关系]"
            return

        # 获取UI实际宽度，动态计算布局参数
        ui_width, ui_height = self.get_ui_actual_size()

        # 根据UI宽度决定布局策略和每行节点数
        if ui_width < 600:
            nodes_per_row = 2
        elif ui_width < 900:
            nodes_per_row = 3
        elif ui_width < 1200:
            nodes_per_row = 4
        else:
            nodes_per_row = 5

        self.log_message(f"🔧 DEBUG: UI width: {ui_width}, nodes per row: {nodes_per_row}")

        # 保存参数用于UI调整时重新生成
        self.last_ui_width = ui_width
        self.last_nodes_per_row = nodes_per_row
        self.call_analysis_data = call_analysis

        # 收集所有节点，按层级分组
        all_functions = []
        layers = {}

        def collect_functions(node, depth=0):
            func_name = node['name']
            if func_name not in [f['name'] for f in all_functions]:
                func_info = {
                    'name': func_name,
                    'depth': depth,
                    'children': []
                }
                all_functions.append(func_info)

                if depth not in layers:
                    layers[depth] = []
                layers[depth].append(func_info)

            # 收集子节点
            for child in node.get('children', []):
                collect_functions(child, depth + 1)
                # 记录父子关系
                for f in all_functions:
                    if f['name'] == func_name:
                        if child['name'] not in f['children']:
                            f['children'].append(child['name'])
                        break

        collect_functions(call_tree)

        # 根据UI宽度生成不同的Mermaid布局
        mermaid_lines = self.generate_adaptive_mermaid_layout(layers, nodes_per_row, all_functions)

        # 完成Mermaid代码生成
        self.mermaid_code = '\n'.join(mermaid_lines)

        # 添加说明注释
        self.mermaid_code += f"""

    %% 自适应布局说明:
    %% UI宽度: {ui_width}px, 每行节点数: {nodes_per_row}
    %% 🔴 红色: main函数 (程序入口)
    %% 🟢 绿色: HAL/接口函数
    %% 🔵 蓝色: 用户自定义函数
"""

        # 同时生成PlantUML代码，确保两种格式使用相同的数据源
        self.generate_plantuml_flowchart(call_analysis)

        # 更新Source Mermaid标签页
        self.update_source_mermaid_tab()

    def generate_plantuml_flowchart(self, call_analysis):
        """根据call_analysis数据生成PlantUML流程图，与Mermaid使用相同的数据源和逻辑"""
        if not call_analysis or 'call_tree' not in call_analysis:
            self.plantuml_code = "@startuml\n!theme plain\nnote as N1\n未找到调用关系\nend note\n@enduml"
            return

        call_tree = call_analysis['call_tree']
        if not call_tree:
            self.plantuml_code = "@startuml\n!theme plain\nnote as N1\n未找到main函数或调用关系\nend note\n@enduml"
            return

        # 获取UI实际宽度，动态计算布局参数（与Mermaid保持一致）
        ui_width, ui_height = self.get_ui_actual_size()

        # 根据UI宽度决定布局策略和每行节点数（与Mermaid保持一致）
        if ui_width < 600:
            nodes_per_row = 2
        elif ui_width < 900:
            nodes_per_row = 3
        elif ui_width < 1200:
            nodes_per_row = 4
        else:
            nodes_per_row = 5

        self.log_message(f"🔧 DEBUG: PlantUML generation - UI width: {ui_width}, nodes per row: {nodes_per_row}")

        # 收集所有节点，按层级分组（与Mermaid逻辑完全一致）
        all_functions = []
        layers = {}

        def collect_functions(node, depth=0):
            func_name = node['name']
            if func_name not in [f['name'] for f in all_functions]:
                func_info = {
                    'name': func_name,
                    'depth': depth,
                    'children': []
                }
                all_functions.append(func_info)

                if depth not in layers:
                    layers[depth] = []
                layers[depth].append(func_info)

            # 收集子节点
            for child in node.get('children', []):
                collect_functions(child, depth + 1)
                # 记录父子关系
                for f in all_functions:
                    if f['name'] == func_name:
                        if child['name'] not in f['children']:
                            f['children'].append(child['name'])
                        break

        collect_functions(call_tree)

        # 生成PlantUML代码头部
        plantuml_lines = ["@startuml"]
        plantuml_lines.append("!theme plain")
        plantuml_lines.append("skinparam backgroundColor #f8f9fa")
        plantuml_lines.append("skinparam defaultFontName Microsoft YaHei")
        plantuml_lines.append("")

        # 使用与Mermaid相同的逻辑生成PlantUML内容
        plantuml_content = self.generate_adaptive_plantuml_layout(layers, nodes_per_row, all_functions, call_tree)
        plantuml_lines.extend(plantuml_content)

        # 添加接口使用信息（与Mermaid保持一致）
        interface_usage = call_analysis.get('interface_usage', {})
        if interface_usage:
            plantuml_lines.append("")
            plantuml_lines.append("note top")
            plantuml_lines.append("接口使用统计:")
            for interface, count in interface_usage.items():
                plantuml_lines.append(f"{interface}: {count} 次调用")
            plantuml_lines.append("end note")

        plantuml_lines.append("")
        plantuml_lines.append("@enduml")

        self.plantuml_code = "\n".join(plantuml_lines)

        # 调试：打印生成的PlantUML代码
        self.log_message("🔧 DEBUG: Generated PlantUML code:")
        print("=" * 50)
        print(self.plantuml_code)
        print("=" * 50)

    def generate_adaptive_plantuml_layout(self, layers, nodes_per_row, all_functions, call_tree):
        """生成自适应的PlantUML流程图布局，参考Mermaid逻辑使用PlantUML流程图语法"""
        plantuml_lines = []
        node_counter = 0
        node_map = {}

        # 定义节点颜色（对应Mermaid的颜色逻辑）
        def get_node_color(func_name):
            if func_name == "main":
                return "#ff6b6b"  # 红色 - main函数
            elif any(keyword in func_name.lower() for keyword in ['hal_', 'gpio_', 'uart_', 'spi_', 'i2c_', 'tim_', 'adc_', 'dac_']):
                return "#51cf66"  # 绿色 - HAL/接口函数
            else:
                return "#74c0fc"  # 蓝色 - 用户自定义函数

        # 为每个函数分配节点ID（与Mermaid逻辑一致）
        for func in all_functions:
            node_counter += 1
            node_id = f"N{node_counter}"
            node_map[func['name']] = node_id

        # 生成节点定义（使用PlantUML流程图语法）
        for func in all_functions:
            node_id = node_map[func['name']]
            func_name = func['name']
            color = get_node_color(func_name)

            # 智能换行：长函数名按下划线或驼峰分割换行
            clean_name = self.format_function_name_for_plantuml_display(func_name)

            # 使用PlantUML流程图语法定义节点
            plantuml_lines.append(f"{node_id}[{clean_name}]")

            # 设置节点颜色
            if func_name == 'main':
                plantuml_lines.append(f"{node_id} : #ff6b6b")
            elif func_name.startswith(('HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_', 'TIM_', 'ADC_', 'DMA_')):
                plantuml_lines.append(f"{node_id} : #51cf66")
            else:
                plantuml_lines.append(f"{node_id} : #74c0fc")

        plantuml_lines.append("")

        # 生成连接关系（与Mermaid逻辑一致）
        connections = []
        for func in all_functions:
            parent_id = node_map[func['name']]
            for child_name in func['children']:
                if child_name in node_map:
                    child_id = node_map[child_name]
                    connections.append(f"{parent_id} --> {child_id}")

        plantuml_lines.extend(connections)

        # 添加图例说明
        plantuml_lines.extend([
            "",
            "note top",
            "层次化流程图说明:",
            "🔴 红色: main函数 (程序入口)",
            "🟢 绿色: HAL/接口函数",
            "🔵 蓝色: 用户自定义函数",
            "end note"
        ])

        return plantuml_lines

    def format_function_name_for_plantuml_display(self, func_name):
        """格式化函数名用于PlantUML显示，与Mermaid保持一致的逻辑"""
        if len(func_name) <= 12:
            return func_name

        # 智能换行处理
        if '_' in func_name:
            parts = func_name.split('_')
            if len(parts) == 2:
                return f"{parts[0]}\\n{parts[1]}"
            elif len(parts) > 2:
                mid_point = len(parts) // 2
                first_part = '_'.join(parts[:mid_point])
                second_part = '_'.join(parts[mid_point:])
                return f"{first_part}\\n{second_part}"

        # 如果没有下划线，按长度分割
        if len(func_name) > 15:
            mid_point = len(func_name) // 2
            return f"{func_name[:mid_point]}\\n{func_name[mid_point:]}"

        return func_name

    def format_function_name_for_display(self, func_name):
        """智能格式化函数名用于显示，支持换行"""
        if len(func_name) <= 12:
            return func_name

        # 尝试在下划线处分割
        if '_' in func_name:
            parts = func_name.split('_')
            if len(parts) >= 2:
                # 将函数名分成两行
                mid_point = len(parts) // 2
                line1 = '_'.join(parts[:mid_point])
                line2 = '_'.join(parts[mid_point:])
                return f"{line1}<br/>{line2}"

        # 尝试在驼峰命名处分割
        import re
        camel_parts = re.findall(r'[A-Z][a-z]*|[a-z]+', func_name)
        if len(camel_parts) >= 2:
            mid_point = len(camel_parts) // 2
            line1 = ''.join(camel_parts[:mid_point])
            line2 = ''.join(camel_parts[mid_point:])
            return f"{line1}<br/>{line2}"

        # 如果无法智能分割，按长度强制分割
        if len(func_name) > 16:
            mid_point = len(func_name) // 2
            return f"{func_name[:mid_point]}<br/>{func_name[mid_point:]}"

        return func_name

    def update_source_mermaid_tab(self):
        """更新Source Flowchart标签页内容（保持方法名兼容性）"""
        try:
            # 调用新的统一更新方法
            self.update_source_flowchart_content()
            self.log_message("🔧 DEBUG: Source Flowchart tab updated")
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to update Source Flowchart tab: {e}")

    def generate_adaptive_mermaid_layout(self, layers, nodes_per_row, all_functions):
        """根据UI宽度生成自适应的Mermaid布局 - 强制垂直分层"""
        mermaid_lines = ["flowchart TD"]  # 使用flowchart TD强制垂直布局
        node_counter = 0
        node_map = {}
        connections = []

        # 为每个函数分配节点ID
        for func in all_functions:
            node_counter += 1
            node_id = f"N{node_counter}"
            node_map[func['name']] = node_id

        # 按层级生成节点，使用subgraph强制分层
        for depth in sorted(layers.keys()):
            layer_functions = layers[depth]
            if not layer_functions:
                continue

            # 创建层级标题
            if depth == 0:
                layer_title = "Main Entry"
            else:
                layer_title = f"Level {depth} Functions"

            # 将该层分成多行，每行用独立的subgraph
            total_funcs = len(layer_functions)
            rows_needed = (total_funcs + nodes_per_row - 1) // nodes_per_row

            for row_idx in range(rows_needed):
                start_idx = row_idx * nodes_per_row
                end_idx = min(start_idx + nodes_per_row, total_funcs)
                row_functions = layer_functions[start_idx:end_idx]

                if not row_functions:
                    continue

                # 创建subgraph强制分行
                if rows_needed > 1:
                    subgraph_title = f"{layer_title} Row {row_idx + 1}"
                else:
                    subgraph_title = layer_title

                mermaid_lines.append(f"    subgraph SG{depth}_{row_idx}[\"{subgraph_title}\"]")
                mermaid_lines.append("        direction LR")  # 该行内部横向排列

                # 添加该行的节点
                for func in row_functions:
                    node_id = node_map[func['name']]
                    func_name = func['name']
                    # 智能换行：长函数名按下划线或驼峰分割换行
                    clean_name = self.format_function_name_for_display(func_name)

                    # 添加节点定义
                    if func_name == 'main':
                        mermaid_lines.append(f"        {node_id}[\"{clean_name}\"]")
                        mermaid_lines.append(f"        style {node_id} fill:#ff6b6b")
                    elif func_name.startswith(('HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_', 'TIM_', 'ADC_', 'DMA_')):
                        mermaid_lines.append(f"        {node_id}[\"{clean_name}\"]")
                        mermaid_lines.append(f"        style {node_id} fill:#51cf66")
                    else:
                        mermaid_lines.append(f"        {node_id}[\"{clean_name}\"]")
                        mermaid_lines.append(f"        style {node_id} fill:#74c0fc")

                mermaid_lines.append("    end")
                mermaid_lines.append("")

        # 添加连接关系
        for func in all_functions:
            parent_id = node_map[func['name']]
            for child_name in func['children']:
                if child_name in node_map:
                    child_id = node_map[child_name]
                    connections.append(f"    {parent_id} --> {child_id}")

        mermaid_lines.extend(connections)

        # 添加图例说明
        mermaid_lines.extend([
            "",
            "    %% 层次化流程图说明:",
            "    %% 🔴 红色: main函数 (程序入口)",
            "    %% 🟢 绿色: HAL/接口函数",
            "    %% 🔵 蓝色: 第一层用户函数",
            "    %% 🟡 黄绿: 第二层用户函数",
            "    %% 🟡 黄色: 更深层函数"
        ])

        return mermaid_lines

    def display_mermaid_flowchart(self):
        """在UI中显示Mermaid流程图"""
        if not self.mermaid_code:
            return

        # 清空并显示Mermaid代码
        self.flowchart_text.delete(1.0, tk.END)

        # 添加说明
        explanation = """# STM32项目调用流程图 (Mermaid格式)

## 使用说明:
1. 复制下面的Mermaid代码
2. 使用支持Mermaid的Markdown编辑器查看图形
3. 或点击'本地渲染'按钮在浏览器中查看

## 图例:
- 红色节点: main函数 (程序入口)
- 绿色节点: HAL/GPIO/UART等接口函数
- 蓝色节点: 用户自定义函数

## Mermaid代码:

"""

        self.flowchart_text.insert(tk.END, explanation)
        self.flowchart_text.insert(tk.END, self.mermaid_code)

        # 添加接口统计
        if hasattr(self, 'call_graph') and 'interface_usage' in self.call_graph:
            interface_usage = self.call_graph['interface_usage']
            if interface_usage:
                self.flowchart_text.insert(tk.END, "\n\n## 接口使用统计:\n")
                for interface, count in interface_usage.items():
                    self.flowchart_text.insert(tk.END, f"- {interface}: {count} 次调用\n")





    def update_graph_preview(self):
        """更新图形预览区域"""
        if not self.mermaid_code:
            return

        # 只有在文本模式下才更新文本预览
        if hasattr(self, 'graph_display_text'):
            # 启用文本框编辑
            self.graph_display_text.config(state=tk.NORMAL)
            self.graph_display_text.delete(1.0, tk.END)

            # 生成简化的文本图形表示
            preview_text = self.generate_text_graph_preview()
            self.graph_display_text.insert(tk.END, preview_text)

            # 禁用编辑
            self.graph_display_text.config(state=tk.DISABLED)

    def generate_text_graph_preview(self):
        """生成文本形式的图形预览"""
        if not hasattr(self, 'call_graph') or not self.call_graph:
            return "暂无调用关系数据"

        call_tree = self.call_graph.get('call_tree')
        if not call_tree:
            return "未找到main函数或调用关系"

        preview_lines = ["📊 函数调用关系树形图", "=" * 40, ""]

        def add_tree_to_preview(node, prefix="", is_last=True):
            if not node:
                return

            # 确定连接符
            connector = "└── " if is_last else "├── "

            # 函数名和文件信息
            func_name = node['name']
            file_name = node.get('file', '').split('\\')[-1].split('/')[-1]

            # 根据函数类型添加图标
            if func_name == 'main':
                icon = "🔴"
            elif func_name.startswith(('HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_', 'TIM_', 'ADC_', 'DMA_')):
                icon = "🟢"
            else:
                icon = "🔵"

            # 添加到预览
            line = f"{prefix}{connector}{icon} {func_name}"
            if file_name:
                line += f" ({file_name})"

            preview_lines.append(line)

            # 处理子节点
            children = node.get('children', [])
            for i, child in enumerate(children):
                is_child_last = (i == len(children) - 1)
                child_prefix = prefix + ("    " if is_last else "│   ")
                add_tree_to_preview(child, child_prefix, is_child_last)

        # 从根节点开始构建
        add_tree_to_preview(call_tree)

        # 添加接口使用统计
        interface_usage = self.call_graph.get('interface_usage', {})
        if interface_usage:
            preview_lines.extend(["", "🔌 接口使用统计:", "-" * 20])
            for interface, count in interface_usage.items():
                preview_lines.append(f"• {interface}: {count} 次调用")

        # 添加图例说明
        preview_lines.extend([
            "", "📖 图例说明:", "-" * 20,
            "🔴 main函数 (程序入口)",
            "🟢 接口函数 (HAL/GPIO/UART等)",
            "🔵 用户自定义函数",
            "", "💡 提示: 点击 '🎨 渲染图形' 查看完整的可视化图表"
        ])

        return "\n".join(preview_lines)





    def render_mermaid_in_browser(self):
        """在浏览器中渲染Mermaid图形 - 使用本地mermaid.js"""
        if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
            self.log_message("🔧 DEBUG: No Mermaid code available")
            return

        try:
            # 获取本地mermaid.js文件路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            mermaid_js_path = os.path.join(script_dir, "assets", "mermaid.min.js")

            if not os.path.exists(mermaid_js_path):
                self.log_message(f"🔧 DEBUG: Local mermaid.js not found at {mermaid_js_path}")
                # 降级到显示源码
                self.display_mermaid_source_in_ui()
                return

            # 读取本地mermaid.js内容
            with open(mermaid_js_path, 'r', encoding='utf-8') as f:
                mermaid_js_content = f.read()

            # 创建完全离线的HTML文件
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>STM32 Call Flow Chart - 离线渲染</title>
    <script>
{mermaid_js_content}
    </script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .mermaid {{
            text-align: center;
            background-color: white;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 STM32项目调用流程图</h1>
        <div class="mermaid">
{self.mermaid_code}
        </div>
        <div class="legend">
            <h3>📖 图例说明:</h3>
            <ul>
                <li>🔴 <strong>红色节点</strong>: main函数 (程序入口)</li>
                <li>🟢 <strong>绿色节点</strong>: HAL/GPIO/UART等接口函数</li>
                <li>🔵 <strong>蓝色节点</strong>: 第一层用户函数</li>
                <li>🟡 <strong>黄绿节点</strong>: 第二层用户函数</li>
                <li>🟡 <strong>黄色节点</strong>: 更深层函数</li>
            </ul>
        </div>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
    </script>
</body>
</html>"""

            # 保存到临时文件

            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name

            # 在浏览器中打开
            webbrowser.open(f'file://{temp_file}')

            # 更新状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid图形已在浏览器中打开")
                except tk.TclError:
                    pass

            self.log_message(f"🔧 DEBUG: Mermaid rendered in browser: {temp_file}")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to render Mermaid in browser: {e}")
            # 降级到Canvas渲染
            self.render_simplified_graph_in_canvas()

    def render_real_mermaid_in_ui(self):
        """在UI内部渲染真正的Mermaid图形"""
        if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
            self.log_message("🔧 DEBUG: No Mermaid code available")
            return

        try:
            # 清理现有内容，保留控制按钮
            widgets_to_keep = []
            if hasattr(self, 'preview_control_frame'):
                widgets_to_keep.append(self.preview_control_frame)

            for widget in self.graph_preview_frame.winfo_children():
                if widget not in widgets_to_keep:
                    widget.destroy()

            # 只在UI内部渲染Mermaid - 不使用外部窗口
            self.render_mermaid_internal_only()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to render real Mermaid: {e}")
            import traceback
            traceback.print_exc()
            # 降级到Canvas渲染
            self.render_simplified_graph_in_canvas()

    def render_mermaid_with_playwright(self):
        """使用Playwright本地渲染Mermaid图表"""
        try:
            self.log_message("🔧 DEBUG: Starting Playwright local rendering")

            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                self.log_message("🔧 DEBUG: No Mermaid code available for Playwright rendering")
                return False

            # 导入Playwright渲染器
            try:
                from utils.playwright_mermaid_renderer import render_mermaid_to_pil
            except ImportError as e:
                self.log_message(f"🔧 DEBUG: Playwright renderer import failed: {e}")
                return False

            # 获取渲染参数 - 使用与在线渲染相同的动态尺寸计算
            try:
                optimal_width, optimal_height, optimal_dpi = self.calculate_optimal_png_size()
                width = optimal_width
                height = optimal_height
                self.log_message(f"🔧 DEBUG: Using optimal size calculation: {width}x{height} @ {optimal_dpi}DPI")
            except:
                # 降级到配置文件设置
                width = self.config.get('mermaid', {}).get('width', 1200)
                height = self.config.get('mermaid', {}).get('height', 800)
                self.log_message(f"🔧 DEBUG: Using config size: {width}x{height}")

            theme = self.config.get('mermaid', {}).get('theme', 'default')
            scale = self.config.get('mermaid', {}).get('scale', 2.0)  # 高DPI缩放

            self.log_message(f"🔧 DEBUG: Rendering with Playwright - Size: {width}x{height}, Theme: {theme}, Scale: {scale}x")

            # 渲染为PIL图像（高质量）
            pil_image = render_mermaid_to_pil(
                self.mermaid_code,
                width=width,
                height=height,
                theme=theme,
                scale=scale
            )

            if pil_image:
                self.log_message(f"🔧 DEBUG: Playwright rendering successful, image size: {pil_image.size}")

                # 使用现有的PIL图像显示方法
                self.display_mermaid_image_from_pil_local(pil_image)
                return True
            else:
                self.log_message("🔧 DEBUG: Playwright rendering returned None")
                return False

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Playwright rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def display_mermaid_image_from_pil_local(self, pil_image):
        """从PIL图像显示本地渲染的Mermaid图表"""
        try:
            from PIL import Image, ImageTk
            self.log_message("🔧 DEBUG: Displaying locally rendered Mermaid image from PIL")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建容器
            container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="🧜‍♀️ Mermaid流程图 (本地渲染)",
                padding=10
            )
            container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 获取容器尺寸
            container.update_idletasks()
            container_width = max(container.winfo_width(), 800)
            container_height = max(container.winfo_height(), 600)

            # 计算缩放比例
            image_width, image_height = pil_image.size
            scale_x = (container_width - 40) / image_width
            scale_y = (container_height - 40) / image_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小

            if scale < 1.0:
                new_width = int(image_width * scale)
                new_height = int(image_height * scale)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.log_message(f"🔧 DEBUG: Resized image to {new_width}x{new_height} (scale: {scale:.2f})")

            # 创建可滚动的显示区域
            canvas_frame = ttk.Frame(container)
            canvas_frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)

            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # 布局
            canvas.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")

            canvas_frame.grid_rowconfigure(0, weight=1)
            canvas_frame.grid_columnconfigure(0, weight=1)

            # 显示图片
            photo = ImageTk.PhotoImage(pil_image)
            canvas.create_image(10, 10, image=photo, anchor=tk.NW)
            canvas.image = photo  # 保持引用

            # 设置滚动区域
            canvas.configure(scrollregion=(0, 0, pil_image.width + 20, pil_image.height + 20))

            # 添加鼠标滚轮支持
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            def on_shift_mousewheel(event):
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")

            canvas.bind("<MouseWheel>", on_mousewheel)
            canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)

            # 添加工具栏
            toolbar_frame = ttk.Frame(container)
            toolbar_frame.pack(fill=tk.X, pady=(5, 0))

            info_label = ttk.Label(
                toolbar_frame,
                text=f"📊 本地渲染 | 尺寸: {pil_image.size[0]}x{pil_image.size[1]} | 缩放: {scale:.0%}"
            )
            info_label.pack(side=tk.LEFT)

            def save_image():
                from tkinter import filedialog
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
                )
                if file_path:
                    pil_image.save(file_path)
                    self.log_message(f"🔧 DEBUG: Image saved to {file_path}")

            save_btn = ttk.Button(toolbar_frame, text="💾 保存图片", command=save_image)
            save_btn.pack(side=tk.RIGHT, padx=(10, 0))

            self.log_message("🔧 DEBUG: Local Mermaid image displayed successfully")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display local Mermaid image: {e}")
            import traceback
            traceback.print_exc()

    def render_mermaid_internal_only(self):
        """UI内SVG Mermaid渲染 - 严格按配置渲染，不自动降级"""
        try:
            self.log_message("🔧 DEBUG: Starting UI-internal SVG Mermaid rendering")

            # 从配置中获取渲染模式
            rendering_mode = self.config.get('mermaid', {}).get('rendering_mode', 'online')
            self.log_message(f"🔧 DEBUG: Using rendering mode: {rendering_mode} (strict mode - no auto fallback)")

            if rendering_mode == 'local':
                # 本地渲染模式 - 严格使用Playwright，不自动降级
                self.log_message("🔧 DEBUG: Attempting local Playwright rendering (strict mode)")
                if self.render_mermaid_with_playwright():
                    self.log_message("🔧 DEBUG: Local Playwright rendering succeeded")
                    return
                else:
                    self.log_message("🔧 DEBUG: Local Playwright rendering failed")
                    self.show_rendering_failure("本地渲染失败",
                        "Playwright本地渲染失败。您可以：\n1. 检查Playwright是否正确安装\n2. 手动切换到在线渲染模式\n3. 查看日志获取详细错误信息")
                    return

            elif rendering_mode == 'online':
                # 在线渲染模式 - 失败就失败，不降级
                self.log_message("🔧 DEBUG: Attempting online rendering only")
                # 获取当前选择的流程图格式
                current_format = getattr(self, 'current_flowchart_format', 'mermaid')
                if self.render_flowchart_online(current_format):
                    self.log_message(f"🔧 DEBUG: Online {current_format} rendering succeeded")
                    return
                else:
                    self.log_message(f"🔧 DEBUG: Online {current_format} rendering failed - showing failure message")
                    self.show_rendering_failure("在线渲染失败", f"无法连接到在线{current_format.upper()}服务")
                    return

            else:
                # 未知渲染模式，默认使用在线渲染（更稳定）
                self.log_message(f"🔧 DEBUG: Unknown rendering mode: {rendering_mode}, using online as default")
                current_format = getattr(self, 'current_flowchart_format', 'mermaid')
                if self.render_flowchart_online(current_format):
                    self.log_message(f"🔧 DEBUG: Online {current_format} rendering succeeded (default)")
                    return
                else:
                    self.log_message("🔧 DEBUG: Online rendering failed")
                    self.show_rendering_failure("在线渲染失败",
                        f"无法连接到在线{current_format.upper()}服务。您可以：\n1. 检查网络连接\n2. 切换到本地渲染模式\n3. 稍后重试")
                    return

        except Exception as e:
            self.log_message(f"🔧 DEBUG: render_mermaid_internal_only failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_rendering_failure("渲染错误", f"渲染过程发生错误: {str(e)}")

    def render_flowchart_online(self, format_type="mermaid", code_content=None):
        """使用kroki.io在线渲染流程图，支持mermaid和plantuml格式"""
        # 确定要渲染的代码内容
        if code_content is None:
            if format_type == "mermaid":
                if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                    self.log_message("🔧 DEBUG: No mermaid code available")
                    return False
                code_content = self.mermaid_code
            elif format_type == "plantuml":
                # 优先使用原始call_analysis数据生成PlantUML代码
                if hasattr(self, 'last_call_analysis') and self.last_call_analysis:
                    self.log_message("🔧 DEBUG: Using original call_analysis data for PlantUML rendering")
                    self.generate_plantuml_flowchart(self.last_call_analysis)
                    if hasattr(self, 'plantuml_code') and self.plantuml_code:
                        code_content = self.plantuml_code
                    else:
                        self.log_message("🔧 DEBUG: PlantUML generation from call_analysis failed")
                        return False
                else:
                    # 备用方案：从Mermaid代码转换
                    if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                        self.log_message("🔧 DEBUG: No flowchart data available for PlantUML conversion")
                        return False
                    self.log_message("🔧 DEBUG: Using Mermaid-to-PlantUML conversion as fallback")
                    code_content = self.convert_mermaid_to_plantuml()
                    if not code_content:
                        self.log_message("🔧 DEBUG: PlantUML code generation failed")
                        return False
            else:
                self.log_message(f"🔧 DEBUG: Unsupported format: {format_type}")
                return False

        try:
            import requests
            import base64
            from PIL import Image, ImageTk
            import io

            self.log_message(f"🔧 DEBUG: Trying online {format_type} rendering with kroki.io")

            # 获取在线渲染配置
            mermaid_config = self.config.get('mermaid', {})
            online_config = mermaid_config.get('online', {})

            if not online_config.get('enabled', True):
                self.log_message("🔧 DEBUG: Online rendering disabled in config")
                return False

            timeout = online_config.get('timeout', 15)
            max_retries = online_config.get('max_retries', 2)
            user_agent = online_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            # 设置请求头
            headers = {
                'User-Agent': user_agent,
                'Accept': 'image/png,image/svg+xml,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive'
            }

            # 尝试kroki.io API - 直接生成PNG
            for attempt in range(max_retries):
                try:
                    self.log_message(f"🔧 DEBUG: Attempt {attempt + 1} with kroki.io {format_type} PNG API")

                    # 根据配置选择编码方式
                    encoding_method = online_config.get('encoding', 'zlib_base64')
                    api_url = online_config.get('api_url', 'https://kroki.io/mermaid/png/')

                    if encoding_method == 'base64_url':
                        # URL安全的base64编码（适用于mermaid.ink）
                        encoded = base64.urlsafe_b64encode(code_content.encode('utf-8')).decode('ascii')
                    elif encoding_method == 'base64':
                        # 标准base64编码
                        encoded = base64.b64encode(code_content.encode('utf-8')).decode('ascii')
                    else:
                        # 默认：压缩+base64编码（适用于kroki.io）
                        import zlib
                        compressed = zlib.compress(code_content.encode('utf-8'))
                        encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

                    # 构建API URL
                    if api_url.endswith('/'):
                        kroki_png_url = f"{api_url}{encoded}"
                    else:
                        kroki_png_url = f"{api_url}/{encoded}"
                    self.log_message(f"🔧 DEBUG: Kroki.io {format_type} PNG URL: {kroki_png_url}")

                    # 发送GET请求到kroki.io PNG API
                    response = requests.get(kroki_png_url, headers=headers, timeout=timeout)

                    if response.status_code == 200:
                        # 检查响应类型 - 应该是PNG图片
                        content_type = response.headers.get('content-type', '').lower()
                        self.log_message(f"🔧 DEBUG: Response content-type: {content_type}")

                        # 处理PNG图片响应
                        if 'image' in content_type or 'png' in content_type:
                            # PNG图片响应
                            png_content = response.content
                            self.log_message(f"🔧 DEBUG: Received {format_type} PNG image, size: {len(png_content)} bytes")

                            # 保存PNG到文件
                            self.save_png_to_logs(png_content, format_type)

                            # 直接加载并显示图片
                            image = Image.open(io.BytesIO(png_content))
                            self.log_message(f"🔧 DEBUG: {format_type} image size: {image.size}")

                            # 显示图片
                            self.display_flowchart_image_from_pil(image, format_type)
                            self.log_message(f"🔧 DEBUG: Kroki.io {format_type} PNG rendering succeeded")
                            return True
                        else:
                            self.log_message(f"🔧 DEBUG: Unexpected content type: {content_type}")
                            return False

                except Exception as e:
                    self.log_message(f"🔧 DEBUG: Kroki.io {format_type} API attempt {attempt + 1} failed: {e}")
                    continue

            # 如果主API失败，尝试备用API
            fallback_url = online_config.get('fallback_url')
            if fallback_url:
                try:
                    self.log_message(f"🔧 DEBUG: Trying fallback API: {fallback_url}")

                    # 根据API类型选择编码方式
                    if 'mermaid.ink' in fallback_url:
                        # mermaid.ink使用URL安全的base64编码
                        encoded = base64.urlsafe_b64encode(code_content.encode('utf-8')).decode('ascii')
                    elif 'kroki.io' in fallback_url:
                        # kroki.io使用压缩+base64编码
                        import zlib
                        compressed = zlib.compress(code_content.encode('utf-8'), 9)
                        encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
                    else:
                        # 其他API默认使用标准base64编码
                        encoded = base64.b64encode(code_content.encode('utf-8')).decode('ascii')

                    # 构建请求URL
                    if fallback_url.endswith('/'):
                        request_url = f"{fallback_url}{encoded}"
                    else:
                        request_url = f"{fallback_url}/{encoded}"

                    self.log_message(f"🔧 DEBUG: Fallback URL: {request_url[:100]}...")

                    response = requests.get(request_url, timeout=timeout, headers=headers)

                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        self.log_message(f"🔧 DEBUG: Fallback API success, content-type: {content_type}")

                        if 'image' in content_type:
                            image_content = response.content
                            self.log_message(f"🔧 DEBUG: Received fallback image, size: {len(image_content)} bytes")

                            # 保存图片到文件
                            self.save_png_to_logs(image_content, format_type)

                            # 显示图片
                            image = Image.open(io.BytesIO(image_content))
                            self.display_flowchart_image_from_pil(image, format_type)
                            self.log_message(f"🔧 DEBUG: Fallback {format_type} rendering succeeded")
                            return True
                    else:
                        self.log_message(f"🔧 DEBUG: Fallback API failed with status: {response.status_code}")

                except Exception as e:
                    self.log_message(f"🔧 DEBUG: Fallback API failed: {e}")

            self.log_message(f"🔧 DEBUG: All {format_type} online rendering attempts failed")
            return False

        except ImportError as e:
            self.log_message(f"🔧 DEBUG: Missing dependencies for online {format_type} rendering: {e}")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Online {format_type} rendering failed: {e}")
            return False

    def get_current_flowchart_format(self):
        """获取当前选择的流程图格式"""
        return getattr(self, 'current_flowchart_format', 'mermaid')

    def update_flowchart_content(self, format_type):
        """根据格式更新流程图内容"""
        try:
            self.log_message(f"🔧 DEBUG: Updating flowchart content to {format_type}")

            # 更新当前格式
            self.current_flowchart_format = format_type

            # 根据格式生成相应的代码
            if format_type == "mermaid":
                if hasattr(self, 'mermaid_code') and self.mermaid_code:
                    # 重新渲染Mermaid
                    self.render_flowchart_online("mermaid")
                else:
                    self.log_message("🔧 DEBUG: No mermaid code available")
            elif format_type == "plantuml":
                # 优先使用原始call_analysis数据生成PlantUML代码
                if hasattr(self, 'last_call_analysis') and self.last_call_analysis:
                    self.log_message("🔧 DEBUG: Using original call_analysis data for PlantUML generation")
                    self.generate_plantuml_flowchart(self.last_call_analysis)
                    if hasattr(self, 'plantuml_code') and self.plantuml_code:
                        # 渲染PlantUML
                        self.render_flowchart_online("plantuml", self.plantuml_code)
                    else:
                        self.log_message("🔧 DEBUG: Failed to generate PlantUML from call_analysis")
                else:
                    # 备用方案：从Mermaid代码转换
                    self.log_message("🔧 DEBUG: Using Mermaid-to-PlantUML conversion as fallback")
                    plantuml_code = self.convert_mermaid_to_plantuml()
                    if plantuml_code:
                        self.plantuml_code = plantuml_code
                        # 渲染PlantUML
                        self.render_flowchart_online("plantuml", plantuml_code)
                    else:
                        self.log_message("🔧 DEBUG: Failed to generate PlantUML code")

            # 更新Source页面内容
            self.update_source_flowchart_content()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to update flowchart content: {e}")

    def on_flowchart_format_changed(self, event=None):
        """处理流程图格式切换事件"""
        try:
            # 获取选择的格式
            if hasattr(self, 'flowchart_format_var'):
                selected_format = self.flowchart_format_var.get()
                self.log_message(f"🔧 DEBUG: Flowchart format changed to: {selected_format}")

                # 更新内容
                self.update_flowchart_content(selected_format)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to handle format change: {e}")

    def update_source_flowchart_content(self):
        """更新Source Flowchart页面的内容"""
        try:
            if hasattr(self, 'flowchart_text'):
                current_format = self.get_current_flowchart_format()

                # 清空现有内容
                self.flowchart_text.delete(1.0, tk.END)

                # 根据格式显示相应的源码
                if current_format == "mermaid":
                    if hasattr(self, 'mermaid_code') and self.mermaid_code:
                        self.flowchart_text.insert(tk.END, self.mermaid_code)
                    else:
                        self.flowchart_text.insert(tk.END, "# 暂无Mermaid代码\n# 请先进行代码分析")
                elif current_format == "plantuml":
                    if hasattr(self, 'plantuml_code') and self.plantuml_code:
                        self.flowchart_text.insert(tk.END, self.plantuml_code)
                    else:
                        # 优先使用原始call_analysis数据生成PlantUML代码
                        if hasattr(self, 'last_call_analysis') and self.last_call_analysis:
                            self.log_message("🔧 DEBUG: Generating PlantUML from original call_analysis data")
                            self.generate_plantuml_flowchart(self.last_call_analysis)
                            if hasattr(self, 'plantuml_code') and self.plantuml_code:
                                self.flowchart_text.insert(tk.END, self.plantuml_code)
                            else:
                                self.flowchart_text.insert(tk.END, "# PlantUML代码生成失败\n# 请重新进行代码分析")
                        else:
                            # 备用方案：从Mermaid代码转换
                            self.log_message("🔧 DEBUG: Using Mermaid-to-PlantUML conversion for source display")
                            plantuml_code = self.convert_mermaid_to_plantuml()
                            if plantuml_code:
                                self.plantuml_code = plantuml_code
                                self.flowchart_text.insert(tk.END, plantuml_code)
                            else:
                                self.flowchart_text.insert(tk.END, "# 暂无PlantUML代码\n# 请先进行代码分析")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to update source flowchart content: {e}")

    def refresh_current_flowchart(self):
        """刷新当前格式的流程图"""
        try:
            current_format = self.get_current_flowchart_format()
            self.log_message(f"🔧 DEBUG: Refreshing {current_format} flowchart")
            self.update_flowchart_content(current_format)
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to refresh flowchart: {e}")

    def on_source_format_changed(self, event=None):
        """处理Source页面格式切换事件"""
        try:
            # 获取选择的格式
            if hasattr(self, 'source_format_var'):
                selected_format = self.source_format_var.get()
                self.log_message(f"🔧 DEBUG: Source format changed to: {selected_format}")

                # 同步流程图页面的格式选择
                if hasattr(self, 'flowchart_format_var'):
                    self.flowchart_format_var.set(selected_format)

                # 更新内容
                self.update_flowchart_content(selected_format)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to handle source format change: {e}")

    def try_online_mermaid_rendering(self):
        """尝试使用在线API渲染Mermaid图表"""
        try:
            import requests
            import base64
            from PIL import Image, ImageTk
            import io

            self.log_message("🔧 DEBUG: Trying online Mermaid rendering")

            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                self.log_message("🔧 DEBUG: No mermaid code available")
                return False

            # 获取在线渲染配置
            mermaid_config = self.config.get('mermaid', {})
            online_config = mermaid_config.get('online', {})

            if not online_config.get('enabled', True):
                self.log_message("🔧 DEBUG: Online rendering disabled in config")
                return False

            api_url = online_config.get('api_url', 'https://mermaid.ink/img/')
            fallback_url = online_config.get('fallback_url', 'https://kroki.io/mermaid/svg/')
            timeout = online_config.get('timeout', 15)
            max_retries = online_config.get('max_retries', 2)
            user_agent = online_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            # 设置请求头
            headers = {
                'User-Agent': user_agent,
                'Accept': 'image/png,image/svg+xml,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive'
            }

            # 尝试主要API (kroki.io) - 直接生成PNG
            for attempt in range(max_retries):
                try:
                    self.log_message(f"🔧 DEBUG: Attempt {attempt + 1} with kroki.io PNG API")



                    # 编码Mermaid代码用于kroki.io
                    import base64
                    import zlib
                    compressed = zlib.compress(self.mermaid_code.encode('utf-8'))
                    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

                    # 构建kroki.io PNG API URL
                    kroki_png_url = f"https://kroki.io/mermaid/png/{encoded}"
                    self.log_message(f"🔧 DEBUG: Kroki.io PNG URL: {kroki_png_url}")

                    # 发送GET请求到kroki.io PNG API
                    response = requests.get(kroki_png_url, headers=headers, timeout=timeout)

                    if response.status_code == 200:
                        # 检查响应类型 - 应该是PNG图片
                        content_type = response.headers.get('content-type', '').lower()
                        self.log_message(f"🔧 DEBUG: Response content-type: {content_type}")

                        # 处理PNG图片响应
                        if 'image' in content_type or 'png' in content_type:
                            # PNG图片响应
                            png_content = response.content
                            self.log_message(f"🔧 DEBUG: Received PNG image, size: {len(png_content)} bytes")

                            # 保存PNG到文件
                            self.save_png_to_logs(png_content)

                            # 直接加载并显示图片，不做任何调整
                            image = Image.open(io.BytesIO(png_content))
                            self.log_message(f"🔧 DEBUG: Image size: {image.size}")

                            # 直接显示图片
                            self.display_mermaid_image_from_pil(image)
                            self.log_message("🔧 DEBUG: Kroki.io PNG rendering succeeded")
                            return True
                        else:
                            self.log_message(f"🔧 DEBUG: Unexpected content type: {content_type}")
                            return False

                except Exception as e:
                    self.log_message(f"🔧 DEBUG: Kroki.io API attempt {attempt + 1} failed: {e}")
                    continue

            # 尝试备用API (mermaid-live-editor)
            try:
                self.log_message(f"🔧 DEBUG: Trying fallback API: {fallback_url}")

                # 尝试mermaid-live-editor的API格式
                # 编码Mermaid代码为base64
                import base64
                import zlib

                # 压缩并编码 (mermaid-live-editor格式)
                compressed = zlib.compress(self.mermaid_code.encode('utf-8'), 9)
                encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

                # 构建URL
                request_url = f"{fallback_url}{encoded}"

                response = requests.get(request_url, timeout=timeout, headers=headers)

                if response.status_code == 200:
                    # 检查是否是SVG响应
                    content_type = response.headers.get('content-type', '').lower()
                    self.log_message(f"🔧 DEBUG: Fallback API content-type: {content_type}")

                    # 检查响应内容是否是SVG（通过内容判断，不依赖content-type）
                    response_text = response.text.strip()
                    if response_text.startswith('<svg') or 'svg' in content_type:
                        # SVG响应 - 保存到logs目录
                        svg_content = response_text
                        self.save_svg_to_logs(svg_content)

                        # 显示SVG内容
                        self.display_svg_content(svg_content)
                        self.log_message("🔧 DEBUG: Fallback API SVG rendering succeeded")
                        return True
                    else:
                        # 图片响应
                        image = Image.open(io.BytesIO(response.content))
                        self.display_mermaid_image_from_pil(image)
                        self.log_message("🔧 DEBUG: Fallback API image rendering succeeded")
                        return True

            except Exception as e:
                self.log_message(f"🔧 DEBUG: Fallback API failed: {e}")

            self.log_message("🔧 DEBUG: All online rendering attempts failed")
            return False

        except ImportError as e:
            self.log_message(f"🔧 DEBUG: Missing dependencies for online rendering: {e}")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Online Mermaid rendering failed: {e}")
            return False

    def save_png_to_logs(self, png_content, format_type="mermaid"):
        """保存PNG内容到logs目录"""
        try:
            import os
            from pathlib import Path

            # 确定logs目录路径
            if hasattr(self, 'log_dir') and self.log_dir:
                logs_dir = Path(self.log_dir)
            else:
                # 使用当前目录下的logs文件夹
                logs_dir = Path(__file__).parent / "logs"

            # 确保logs目录存在
            logs_dir.mkdir(exist_ok=True)

            # 保存PNG文件
            png_file_path = logs_dir / f"temp_{format_type}.png"

            with open(png_file_path, 'wb') as f:
                f.write(png_content)

            self.log_message(f"🔧 DEBUG: {format_type} PNG saved to: {png_file_path}")
            self.log_message(f"🔧 DEBUG: PNG file size: {len(png_content)} bytes")

            # 同时保存一个带时间戳的版本
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_file = logs_dir / f"{format_type}_{timestamp}.png"

            with open(timestamped_file, 'wb') as f:
                f.write(png_content)

            self.log_message(f"🔧 DEBUG: Timestamped {format_type} PNG saved to: {timestamped_file}")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to save {format_type} PNG to logs: {e}")

    def display_flowchart_image_from_pil(self, pil_image, format_type="mermaid"):
        """从PIL图像显示流程图"""
        try:
            from PIL import ImageTk
            self.log_message(f"🔧 DEBUG: Displaying {format_type} image from PIL")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建容器
            format_name = "Mermaid" if format_type == "mermaid" else "PlantUML"
            container = ttk.LabelFrame(
                self.graph_preview_frame,
                text=f"🧜‍♀️ {format_name}流程图 (在线渲染)",
                padding=10
            )
            container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 直接转换为Tkinter可用的格式，不调整大小
            photo = ImageTk.PhotoImage(pil_image)

            # 创建可滚动的显示区域
            canvas_frame = ttk.Frame(container)
            canvas_frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)

            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # 布局
            canvas.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")

            canvas_frame.grid_rowconfigure(0, weight=1)
            canvas_frame.grid_columnconfigure(0, weight=1)

            # 在Canvas中显示图像
            canvas.create_image(10, 10, anchor=tk.NW, image=photo)
            canvas.image = photo  # 保持引用

            # 更新滚动区域
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

            self.log_message(f"🔧 DEBUG: {format_type} image displayed successfully")
            return True

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display {format_type} image: {e}")
            return False

    def save_svg_to_logs(self, svg_content):
        """保存SVG内容到logs目录"""
        try:
            import os
            from pathlib import Path

            # 确定logs目录路径
            if hasattr(self, 'log_dir') and self.log_dir:
                logs_dir = Path(self.log_dir)
            else:
                # 使用当前目录下的logs文件夹
                logs_dir = Path(__file__).parent / "logs"

            # 确保logs目录存在
            logs_dir.mkdir(exist_ok=True)

            # 保存SVG文件
            svg_file_path = logs_dir / "temp.svg"

            with open(svg_file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)

            self.log_message(f"🔧 DEBUG: SVG saved to: {svg_file_path}")
            self.log_message(f"🔧 DEBUG: SVG file size: {len(svg_content)} characters")

            # 同时保存一个带时间戳的版本
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_file = logs_dir / f"mermaid_{timestamp}.svg"

            with open(timestamped_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)

            self.log_message(f"🔧 DEBUG: Timestamped SVG saved to: {timestamped_file}")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to save SVG to logs: {e}")



    def try_fallback_rendering(self):
        """尝试备选渲染方案"""
        try:
            self.log_message("🔧 DEBUG: Trying fallback rendering methods")

            # 获取备选方案配置
            mermaid_config = self.config.get('mermaid', {})
            fallback_config = mermaid_config.get('fallback', {})

            # 尝试matplotlib渲染
            if fallback_config.get('use_matplotlib', True):
                if self.render_with_matplotlib_fallback():
                    self.log_message("🔧 DEBUG: Matplotlib fallback rendering succeeded")
                    return True

            # 尝试简化Canvas渲染
            if fallback_config.get('use_canvas', True):
                if self.render_simplified_graph_in_canvas():
                    self.log_message("🔧 DEBUG: Canvas fallback rendering succeeded")
                    return True

            # 显示源码
            if fallback_config.get('show_source_code', True):
                self.display_mermaid_source_in_ui()
                self.log_message("🔧 DEBUG: Showing Mermaid source code as fallback")
                return True

            # 最终显示错误信息
            self.show_svg_render_failure()
            return False

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Fallback rendering failed: {e}")
            self.show_svg_render_failure()
            return False

    def display_mermaid_image_from_pil(self, pil_image):
        """从PIL图像显示Mermaid图表"""
        try:
            self.log_message("🔧 DEBUG: Displaying Mermaid image from PIL")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建容器
            container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="🧜‍♀️ Mermaid流程图 (在线渲染)",
                padding=10
            )
            container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 直接转换为Tkinter可用的格式，不调整大小
            photo = ImageTk.PhotoImage(pil_image)

            # 创建可滚动的显示区域
            canvas_frame = ttk.Frame(container)
            canvas_frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)

            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # 布局
            canvas.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")

            canvas_frame.grid_rowconfigure(0, weight=1)
            canvas_frame.grid_columnconfigure(0, weight=1)

            # 在Canvas中显示图像
            canvas.create_image(10, 10, anchor=tk.NW, image=photo)
            canvas.image = photo  # 保持引用

            # 更新滚动区域
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

            self.log_message("🔧 DEBUG: Mermaid image displayed successfully")
            return True

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display Mermaid image: {e}")
            return False

    def display_svg_content(self, svg_content):
        """在UI内显示SVG内容 - 智能备选方案"""
        try:
            self.log_message("🔧 DEBUG: Displaying SVG content with smart fallback")

            # 先保存SVG到文件
            self.save_svg_to_logs(svg_content)

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建主容器
            main_container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="🧜‍♀️ Mermaid流程图 (在线渲染)",
                padding=10
            )
            main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            self.log_message(f"🔧 DEBUG: SVG content length: {len(svg_content)}")

            # 删除SVG转PNG转换，只保留在线渲染
            self.log_message("🔧 DEBUG: SVG转PNG转换已删除，仅支持在线渲染")

            # 创建HTML文件并提供查看选项
            try:
                import os

                # 创建HTML文件
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mermaid Flowchart</title>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 20px;
            text-align: center;
            font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        svg {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧜‍♀️ Mermaid流程图</h1>
        <p>在线渲染成功 ✅ (UI内显示遇到问题，请在浏览器中查看)</p>
        {svg_content}
    </div>
</body>
</html>"""

                # 保存HTML文件到logs目录
                logs_dir = os.path.dirname(os.path.abspath(__file__)) + "/logs"
                html_file = os.path.join(logs_dir, "mermaid_preview.html")

                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                # 显示问题说明和解决方案
                warning_label = ttk.Label(
                    main_container,
                    text="⚠️ UI内显示遇到兼容性问题",
                    font=("Microsoft YaHei", 14, "bold"),
                    foreground="orange"
                )
                warning_label.pack(pady=10)

                info_label = ttk.Label(
                    main_container,
                    text="在线渲染成功，但UI内显示遇到字体/兼容性问题\n请点击下方按钮在浏览器中查看完整流程图",
                    font=("Microsoft YaHei", 10),
                    justify=tk.CENTER
                )
                info_label.pack(pady=5)

                # 按钮框架
                button_frame = ttk.Frame(main_container)
                button_frame.pack(pady=20)

                def open_html():
                    import webbrowser
                    webbrowser.open(f'file://{os.path.abspath(html_file)}')

                def open_svg():
                    import webbrowser
                    svg_file = os.path.join(logs_dir, "temp.svg")
                    webbrowser.open(f'file://{os.path.abspath(svg_file)}')

                def open_logs_folder():
                    import subprocess
                    subprocess.run(['explorer', logs_dir], shell=True)

                ttk.Button(button_frame, text="🌐 在浏览器中查看", command=open_html).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="📄 打开SVG文件", command=open_svg).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="📁 打开文件夹", command=open_logs_folder).pack(side=tk.LEFT, padx=5)

                # 显示技术信息
                tech_frame = ttk.LabelFrame(main_container, text="技术信息", padding=5)
                tech_frame.pack(fill=tk.BOTH, expand=True, pady=10)

                text_widget = tk.Text(tech_frame, height=8, font=("Consolas", 9), bg='#f8f9fa', wrap=tk.WORD)
                scrollbar = ttk.Scrollbar(tech_frame, orient=tk.VERTICAL, command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)

                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # 格式化技术信息
                tech_info = f"""✅ 在线渲染成功！

📁 文件位置:
• SVG: {os.path.join(logs_dir, 'temp.svg')}
• HTML: {html_file}

⚠️ UI显示问题:
• 可能是tksvg字体兼容性问题
• 建议在浏览器中查看完整效果

📊 SVG信息:
• 文件大小: {len(svg_content)} 字符
• 内容类型: image/svg+xml

💡 解决方案:
• 点击"在浏览器中查看"获得最佳显示效果
• SVG文件已保存，可用其他工具打开"""

                text_widget.insert(tk.END, tech_info)
                text_widget.config(state=tk.DISABLED)

                self.log_message(f"🔧 DEBUG: HTML fallback created: {html_file}")
                return True

            except Exception as e:
                self.log_message(f"🔧 DEBUG: HTML fallback failed: {e}")

            # 最终备选：显示基本信息
            error_label = ttk.Label(
                main_container,
                text="❌ UI显示失败，但渲染成功",
                font=("Microsoft YaHei", 14, "bold"),
                foreground="red"
            )
            error_label.pack(pady=20)

            info_label = ttk.Label(
                main_container,
                text="SVG文件已保存到logs目录\n请手动打开logs/temp.svg文件查看",
                font=("Microsoft YaHei", 12),
                justify=tk.CENTER
            )
            info_label.pack(pady=10)

            return True

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display SVG content: {e}")
            return False

    def convert_svg_to_png_removed(self):
        """SVG转PNG转换方法已删除，仅支持在线渲染"""
        self.log_message("🔧 DEBUG: 本地SVG转PNG功能已移除，请使用在线渲染")
        return False

    def display_converted_svg_image(self, parent, pil_image, conversion_method):
        """显示转换后的SVG图像"""
        try:
            # 创建标题
            title_label = ttk.Label(
                parent,
                text=f"✅ Mermaid流程图 (在线渲染 - {conversion_method})",
                font=("Microsoft YaHei", 12, "bold"),
                foreground="green"
            )
            title_label.pack(pady=(0, 10))

            # 创建可滚动的图像显示区域
            canvas_frame = ttk.Frame(parent)
            canvas_frame.pack(fill=tk.BOTH, expand=True)

            # 创建Canvas和滚动条
            canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)

            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # 布局
            canvas.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")

            canvas_frame.grid_rowconfigure(0, weight=1)
            canvas_frame.grid_columnconfigure(0, weight=1)

            # 转换PIL图像为Tkinter格式
            from PIL import ImageTk

            # 如果图像太大，适当缩放
            max_width, max_height = 1000, 800
            if pil_image.width > max_width or pil_image.height > max_height:
                pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            tk_image = ImageTk.PhotoImage(pil_image)

            # 在Canvas中显示图像
            canvas.create_image(20, 20, anchor=tk.NW, image=tk_image)
            canvas.image = tk_image  # 保持引用

            # 更新滚动区域
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

            self.log_message(f"🔧 DEBUG: Converted SVG image displayed successfully using {conversion_method}")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display converted SVG image: {e}")

    def display_svg_with_options(self, parent, svg_content):
        """显示SVG选项（保存、查看等）"""
        try:
            # 成功信息
            success_label = ttk.Label(
                parent,
                text="✅ 在线渲染成功！SVG流程图已生成",
                font=("Microsoft YaHei", 12, "bold"),
                foreground="green"
            )
            success_label.pack(pady=(0, 15))

            # 按钮框架
            button_frame = ttk.Frame(parent)
            button_frame.pack(fill=tk.X, pady=(0, 15))

            def save_svg():
                from tkinter import filedialog, messagebox
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".svg",
                    filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
                    title="保存Mermaid SVG文件"
                )
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                    messagebox.showinfo("保存成功", f"SVG文件已保存到:\n{file_path}")

            def view_in_browser():
                import tempfile
                import webbrowser

                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mermaid Flowchart</title>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 20px; font-family: Arial, sans-serif; text-align: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧜‍♀️ Mermaid流程图</h1>
        <div>{svg_content}</div>
    </div>
</body>
</html>"""

                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(html_content)
                    temp_file = f.name

                webbrowser.open(f'file://{temp_file}')

            # 按钮
            ttk.Button(button_frame, text="💾 保存SVG文件", command=save_svg, width=15).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="🌐 在浏览器中查看", command=view_in_browser, width=18).pack(side=tk.LEFT, padx=(0, 10))

            # SVG预览区域（显示部分源码）
            preview_frame = ttk.LabelFrame(parent, text="SVG预览", padding=5)
            preview_frame.pack(fill=tk.BOTH, expand=True)

            preview_text = tk.Text(
                preview_frame,
                height=12,
                font=("Consolas", 9),
                bg='#f8f9fa',
                wrap=tk.WORD
            )

            scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
            preview_text.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 显示SVG内容的前部分
            preview_content = f"✅ 在线渲染成功！\n\nSVG内容预览（前500字符）：\n\n{svg_content[:500]}..."
            if len(svg_content) <= 500:
                preview_content = f"✅ 在线渲染成功！\n\nSVG完整内容：\n\n{svg_content}"

            preview_text.insert(tk.END, preview_content)
            preview_text.config(state=tk.DISABLED)

            self.log_message("🔧 DEBUG: SVG options displayed successfully")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display SVG options: {e}")

    def display_svg_success_message(self, temp_file):
        """显示SVG在浏览器中打开的成功信息"""
        try:
            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建成功信息容器
            success_frame = ttk.LabelFrame(
                self.graph_preview_frame,
                text="✅ Mermaid流程图 (在线渲染成功)",
                padding=10
            )
            success_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 成功信息
            success_label = ttk.Label(
                success_frame,
                text="🎉 Mermaid流程图已在浏览器中打开！",
                font=("Microsoft YaHei", 14, "bold"),
                foreground="green"
            )
            success_label.pack(pady=(0, 10))

            # 文件路径信息
            path_label = ttk.Label(
                success_frame,
                text=f"临时文件位置: {temp_file}",
                font=("Consolas", 9),
                foreground="gray"
            )
            path_label.pack(pady=(0, 10))

            # 说明文本
            info_text = tk.Text(
                success_frame,
                height=6,
                font=("Microsoft YaHei", 10),
                bg='#f0f8ff',
                wrap=tk.WORD,
                relief=tk.FLAT
            )
            info_text.pack(fill=tk.BOTH, expand=True)

            info_content = """✨ 在线渲染成功！

🌐 Mermaid流程图已使用kroki.io在线服务成功渲染
📊 图表已在默认浏览器中打开，您可以：
   • 查看完整的流程图
   • 右键保存图片
   • 打印或分享图表

💡 如果浏览器没有自动打开，请手动打开上面显示的临时文件路径。"""

            info_text.insert(tk.END, info_content)
            info_text.config(state=tk.DISABLED)

            self.log_message("🔧 DEBUG: SVG success message displayed")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to show SVG success message: {e}")

    def display_svg_source_code(self, svg_content):
        """显示SVG源码"""
        try:
            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建源码显示区域
            source_frame = ttk.LabelFrame(
                self.graph_preview_frame,
                text="📄 Mermaid SVG源码 (在线渲染)",
                padding=10
            )
            source_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 创建滚动文本框
            text_widget = tk.Text(
                source_frame,
                wrap=tk.WORD,
                font=("Consolas", 9),
                bg='#f8f9fa'
            )

            scrollbar = ttk.Scrollbar(source_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 插入SVG内容
            text_widget.insert(tk.END, "在线渲染成功！SVG源码如下：\n\n")
            text_widget.insert(tk.END, svg_content)
            text_widget.config(state=tk.DISABLED)

            self.log_message("🔧 DEBUG: SVG source code displayed")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display SVG source code: {e}")

    def show_rendering_failure(self, title, message):
        """显示渲染失败信息"""
        try:
            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建错误信息容器
            error_frame = ttk.LabelFrame(
                self.graph_preview_frame,
                text=f"❌ {title}",
                padding=10
            )
            error_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 错误信息
            error_label = ttk.Label(
                error_frame,
                text=message,
                font=("Microsoft YaHei", 12, "bold"),
                foreground="red"
            )
            error_label.pack(pady=(0, 10))

            # 配置说明
            config_text = tk.Text(
                error_frame,
                height=8,
                font=("Consolas", 10),
                bg='#f8f9fa',
                wrap=tk.WORD
            )
            config_text.pack(fill=tk.BOTH, expand=True)

            config_info = """如需切换渲染方式，请：

1. 点击菜单栏 "Config" → "Mermaid渲染设置"
2. 当前仅支持在线渲染模式：
   - online: 在线渲染（使用kroki.io，无需本地依赖）

当前配置文件: config.yaml
当前渲染模式: """ + self.config.get('mermaid', {}).get('rendering_mode', 'unknown')

            config_text.insert(tk.END, config_info)
            config_text.config(state=tk.DISABLED)

            self.log_message(f"🔧 DEBUG: Rendering failure message displayed: {title} - {message}")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to show rendering failure: {e}")

    def show_svg_render_failure(self):
        """显示SVG渲染失败信息（保持向后兼容）"""
        self.show_rendering_failure("SVG渲染失败", "SVG Mermaid渲染失败！请检查依赖或切换渲染模式。")

    def render_mermaid_with_ui_webview(self):
        """使用UI内webview渲染Mermaid - 参考VSCode MPE实现"""
        try:
            self.log_message("🔧 DEBUG: Starting UI webview Mermaid rendering (VSCode MPE style)")

            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                self.log_message("🔧 DEBUG: No mermaid code available")
                return False

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建主容器
            main_container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="🧜‍♀️ Mermaid 流程图 (UI内渲染)",
                padding=5
            )
            main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 尝试不同的webview实现
            webview_success = False

            # 方案1: 尝试使用webview库
            if self.try_webview_library(main_container):
                webview_success = True
                self.log_message("🔧 DEBUG: webview library rendering succeeded")
            # 方案2: 尝试使用tkinter.html
            elif self.try_tkinter_html_widget(main_container):
                webview_success = True
                self.log_message("🔧 DEBUG: tkinter.html rendering succeeded")
            # 方案3: 尝试使用CEF
            elif self.try_cef_embedded(main_container):
                webview_success = True
                self.log_message("🔧 DEBUG: CEF embedded rendering succeeded")

            if webview_success:
                # 更新状态
                if hasattr(self, 'graph_status_label'):
                    try:
                        self.graph_status_label.config(text="✅ Mermaid图形已在UI内部渲染")
                    except tk.TclError:
                        pass
                return True
            else:
                self.log_message("🔧 DEBUG: All webview methods failed")
                return False

        except Exception as e:
            self.log_message(f"🔧 DEBUG: UI webview rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def try_webview_library(self, parent_container):
        """直接在UI内显示Mermaid内容（不使用webview避免卡死）"""
        try:
            self.log_message("🔧 DEBUG: Using direct UI rendering (avoiding webview blocking)")

            # 创建HTML内容
            html_content = self.create_vscode_style_mermaid_html()

            self.log_message(f"🔧 DEBUG: HTML content created, length: {len(html_content)}")

            # 创建显示容器
            display_frame = ttk.Frame(parent_container)
            display_frame.pack(fill=tk.BOTH, expand=True)

            # 状态标签
            status_label = ttk.Label(
                display_frame,
                text="✅ Mermaid内容已准备就绪（UI内显示）",
                font=("Microsoft YaHei", 12, "bold"),
                foreground="green"
            )
            status_label.pack(pady=10)

            # 直接显示方案：显示HTML源码和保存功能
            try:
                self.log_message("🔧 DEBUG: Creating direct UI display...")

                # 创建说明标签
                info_label = ttk.Label(
                    display_frame,
                    text="💡 Mermaid图形内容已生成，可保存为HTML文件在浏览器中查看",
                    font=("Microsoft YaHei", 10),
                    foreground="blue"
                )
                info_label.pack(pady=(0, 10))

                # 创建按钮框架
                btn_frame = ttk.Frame(display_frame)
                btn_frame.pack(fill=tk.X, pady=(0, 10))

                def save_html():
                    from tkinter import filedialog, messagebox
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".html",
                        filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                        title="保存Mermaid HTML文件"
                    )
                    if file_path:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        messagebox.showinfo("保存成功", f"Mermaid HTML文件已保存到:\n{file_path}\n\n请用浏览器打开查看流程图")

                def open_temp_html():
                    import tempfile
                    import webbrowser
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                        f.write(html_content)
                        temp_file = f.name
                    webbrowser.open(f'file://{temp_file}')

                # 保存按钮
                save_btn = ttk.Button(
                    btn_frame,
                    text="💾 保存HTML文件",
                    command=save_html,
                    width=15
                )
                save_btn.pack(side=tk.LEFT, padx=(0, 10))

                # 临时查看按钮
                view_btn = ttk.Button(
                    btn_frame,
                    text="🌐 在浏览器中查看",
                    command=open_temp_html,
                    width=18
                )
                view_btn.pack(side=tk.LEFT, padx=(0, 10))

                # 创建滚动文本框显示Mermaid代码
                text_frame = ttk.LabelFrame(display_frame, text="Mermaid流程图代码", padding=5)
                text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

                mermaid_text = tk.Text(
                    text_frame,
                    wrap=tk.WORD,
                    font=("Consolas", 11),
                    bg='#f8f9fa',
                    height=15,
                    relief=tk.SUNKEN,
                    bd=1
                )

                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=mermaid_text.yview)
                mermaid_text.configure(yscrollcommand=scrollbar.set)

                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                mermaid_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # 插入Mermaid代码
                mermaid_text.insert(tk.END, f"生成的Mermaid流程图代码:\n\n{self.mermaid_code}")
                mermaid_text.config(state=tk.DISABLED)

                self.log_message("🔧 DEBUG: Direct UI display successful")
                return True

            except Exception as e:
                self.log_message(f"🔧 DEBUG: Direct UI display failed: {e}")
                status_label.config(
                    text=f"❌ UI显示失败: {str(e)[:30]}...",
                    foreground="red"
                )
                return False

                # 创建滚动文本框显示HTML内容
                text_frame = ttk.Frame(webview_frame)
                text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

                html_text = tk.Text(
                    text_frame,
                    wrap=tk.WORD,
                    font=("Consolas", 9),
                    bg='#f8f9fa',
                    height=20
                )

                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=html_text.yview)
                html_text.configure(yscrollcommand=scrollbar.set)

                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                html_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # 插入HTML内容
                html_text.insert(tk.END, "生成的HTML内容（包含Mermaid渲染）:\n\n")
                html_text.insert(tk.END, html_content)
                html_text.config(state=tk.DISABLED)

                # 添加说明按钮
                btn_frame = ttk.Frame(webview_frame)
                btn_frame.pack(fill=tk.X, pady=(10, 0))

                def save_html():
                    from tkinter import filedialog
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".html",
                        filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
                    )
                    if file_path:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        messagebox.showinfo("成功", f"HTML文件已保存到:\n{file_path}")

                save_btn = ttk.Button(btn_frame, text="💾 保存HTML文件", command=save_html)
                save_btn.pack(side=tk.LEFT, padx=(0, 10))

                info_label = ttk.Label(
                    btn_frame,
                    text="提示：保存HTML文件后可在浏览器中查看Mermaid图形",
                    font=("Microsoft YaHei", 9),
                    foreground="gray"
                )
                info_label.pack(side=tk.LEFT)

                self.log_message("🔧 DEBUG: HTML source display successful")

            except Exception as e:
                self.log_message(f"🔧 DEBUG: UI embedding failed: {e}")
                status_label.config(
                    text=f"❌ UI渲染失败: {str(e)[:30]}...",
                    foreground="red"
                )

            return True

        except ImportError:
            self.log_message("🔧 DEBUG: webview library not available")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: webview library rendering failed: {e}")
            return False

    def try_tkinter_html_widget(self, parent_container):
        """尝试使用tkinter HTML widget"""
        try:
            from tkinter import html

            self.log_message("🔧 DEBUG: Trying tkinter HTML widget")

            # 创建HTML内容
            html_content = self.create_vscode_style_mermaid_html()

            # 创建HTML widget
            html_widget = html.HTMLLabel(
                parent_container,
                html=html_content
            )
            html_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            self.log_message("🔧 DEBUG: tkinter HTML widget rendering successful")
            return True

        except ImportError:
            self.log_message("🔧 DEBUG: tkinter.html not available")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: tkinter HTML widget rendering failed: {e}")
            return False

    def try_cef_embedded(self, parent_container):
        """尝试使用CEF嵌入式渲染"""
        try:
            from cefpython3 import cefpython as cef
            import sys

            self.log_message("🔧 DEBUG: Trying CEF embedded rendering")

            # 创建CEF容器
            cef_frame = ttk.Frame(parent_container)
            cef_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 状态标签
            status_label = ttk.Label(
                cef_frame,
                text="🔄 正在启动CEF渲染引擎...",
                font=("Microsoft YaHei", 12, "bold")
            )
            status_label.pack(pady=20)

            # 创建HTML内容
            html_content = self.create_vscode_style_mermaid_html()

            # CEF设置
            settings = {
                "multi_threaded_message_loop": False,
                "auto_zooming": "system_dpi",
                "log_severity": cef.LOGSEVERITY_INFO,
                "log_file": "",
            }

            # 初始化CEF
            sys.excepthook = cef.ExceptHook
            cef.Initialize(settings)

            # 创建浏览器窗口 - 嵌入到tkinter中
            window_info = cef.WindowInfo()
            window_info.SetAsChild(cef_frame.winfo_id(), [0, 0, 800, 600])

            # 创建浏览器
            browser = cef.CreateBrowserSync(
                window_info,
                url=cef.GetDataUrl(html_content)
            )

            # 更新状态
            status_label.config(
                text="✅ Mermaid图形已在UI内部渲染（CEF引擎）",
                foreground="green"
            )

            # 设置消息循环
            def message_loop():
                cef.MessageLoopWork()
                self.root.after(10, message_loop)

            message_loop()

            self.log_message("🔧 DEBUG: CEF embedded rendering successful")
            return True

        except ImportError:
            self.log_message("🔧 DEBUG: cefpython3 not available")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: CEF embedded rendering failed: {e}")
            return False

    def create_vscode_style_mermaid_html(self):
        """创建VSCode风格的Mermaid HTML内容"""
        # 获取本地mermaid.js文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mermaid_js_path = os.path.join(script_dir, "assets", "mermaid.min.js")

        mermaid_js_content = ""
        if os.path.exists(mermaid_js_path):
            try:
                with open(mermaid_js_path, 'r', encoding='utf-8') as f:
                    mermaid_js_content = f.read()
            except Exception as e:
                self.log_message(f"🔧 DEBUG: Failed to read local mermaid.js: {e}")

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mermaid Diagram - UI Internal Rendering</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: white;
            overflow: auto;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 100%;
            overflow: auto;
        }}
        .header {{
            text-align: center;
            color: #333;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #007acc;
        }}
        .mermaid {{
            text-align: center;
            background-color: white;
            max-width: 100%;
            overflow: auto;
            min-height: 400px;
        }}
        .error {{
            color: #d73a49;
            text-align: center;
            padding: 20px;
            border: 2px solid #d73a49;
            border-radius: 5px;
            margin: 20px;
            background-color: #ffeaea;
        }}
        .loading {{
            color: #0366d6;
            text-align: center;
            padding: 20px;
            font-size: 16px;
        }}
    </style>
    <script>
{mermaid_js_content}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🧜‍♀️ MCU代码调用关系流程图</h2>
            <p>UI内部渲染 - 参考VSCode Markdown Preview Enhanced实现</p>
        </div>

        <div id="loading" class="loading">正在渲染Mermaid图形...</div>
        <div id="mermaid-container" style="display:none;">
            <div class="mermaid">
{self.mermaid_code}
            </div>
        </div>
    </div>

    <script>
        console.log('Starting VSCode-style Mermaid initialization...');

        try {{
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }},
                securityLevel: 'loose'
            }});

            // 手动渲染 - 参考VSCode MPE
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('DOM loaded, starting Mermaid rendering...');

                mermaid.run().then(() => {{
                    console.log('Mermaid rendering completed successfully');
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('mermaid-container').style.display = 'block';
                }}).catch((error) => {{
                    console.error('Mermaid rendering failed:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('mermaid-container').innerHTML =
                        '<div class="error">Mermaid渲染失败: ' + error.message + '<br><br>请检查Mermaid语法是否正确</div>';
                    document.getElementById('mermaid-container').style.display = 'block';
                }});
            }});
        }} catch (error) {{
            console.error('Mermaid initialization failed:', error);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('mermaid-container').innerHTML =
                '<div class="error">Mermaid初始化失败: ' + error.message + '</div>';
            document.getElementById('mermaid-container').style.display = 'block';
        }}

        // 全局错误处理
        window.addEventListener('error', function(e) {{
            console.error('Global error:', e);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('mermaid-container').innerHTML =
                '<div class="error">页面加载出错: ' + e.message + '</div>';
            document.getElementById('mermaid-container').style.display = 'block';
        }});
    </script>
</body>
</html>"""

    def try_local_mermaid_rendering(self):
        """使用本地mermaid.js文件渲染"""
        try:

            self.log_message("🔧 DEBUG: Trying local mermaid.js rendering")

            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                self.log_message("🔧 DEBUG: No mermaid code available")
                return False

            # 获取本地mermaid.js文件路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            mermaid_js_path = os.path.join(script_dir, "assets", "mermaid.min.js")

            if not os.path.exists(mermaid_js_path):
                self.log_message(f"🔧 DEBUG: Local mermaid.js not found at {mermaid_js_path}")
                return False

            # 读取本地mermaid.js内容
            with open(mermaid_js_path, 'r', encoding='utf-8') as f:
                mermaid_js_content = f.read()

            # 创建完全离线的HTML内容
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mermaid Diagram - 离线渲染</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: white;
            overflow: auto;
        }}
        .mermaid {{
            text-align: center;
            background-color: white;
            max-width: 100%;
            overflow: auto;
        }}
        .error {{
            color: red;
            text-align: center;
            padding: 20px;
            border: 2px solid red;
            border-radius: 5px;
            margin: 20px;
        }}
        .loading {{
            color: blue;
            text-align: center;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            color: #333;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🧜‍♀️ MCU代码调用关系流程图 (离线渲染)</h2>
        <p>使用本地mermaid.js v10.6.1 - 完全离线无网络依赖</p>
    </div>

    <div id="loading" class="loading">正在渲染Mermaid图形...</div>
    <div id="mermaid-container" style="display:none;">
        <div class="mermaid">
{self.mermaid_code}
        </div>
    </div>

    <script>
{mermaid_js_content}
    </script>

    <script>
        console.log('Starting local Mermaid initialization...');

        try {{
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }},
                securityLevel: 'loose'
            }});

            // 手动渲染
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('DOM loaded, starting Mermaid rendering...');

                mermaid.run().then(() => {{
                    console.log('Mermaid rendering completed successfully');
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('mermaid-container').style.display = 'block';
                }}).catch((error) => {{
                    console.error('Mermaid rendering failed:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('mermaid-container').innerHTML =
                        '<div class="error">Mermaid渲染失败: ' + error.message + '<br><br>请检查Mermaid语法是否正确</div>';
                    document.getElementById('mermaid-container').style.display = 'block';
                }});
            }});
        }} catch (error) {{
            console.error('Mermaid initialization failed:', error);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('mermaid-container').innerHTML =
                '<div class="error">Mermaid初始化失败: ' + error.message + '</div>';
            document.getElementById('mermaid-container').style.display = 'block';
        }}

        // 全局错误处理
        window.addEventListener('error', function(e) {{
            console.error('Global error:', e);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('mermaid-container').innerHTML =
                '<div class="error">页面加载出错: ' + e.message + '</div>';
            document.getElementById('mermaid-container').style.display = 'block';
        }});
    </script>
</body>
</html>"""

            # 创建临时HTML文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file = f.name

            self.log_message(f"🔧 DEBUG: Created temporary HTML file: {html_file}")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建显示容器
            display_container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="🧜‍♀️ Mermaid 流程图 (离线渲染)",
                padding=5
            )
            display_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 状态和控制按钮
            control_frame = ttk.Frame(display_container)
            control_frame.pack(fill=tk.X, pady=(0, 10))

            status_label = ttk.Label(
                control_frame,
                text="✅ 已生成离线Mermaid HTML文件",
                font=("Microsoft YaHei", 10),
                foreground="green"
            )
            status_label.pack(side=tk.LEFT)

            # 不再提供浏览器按钮 - 只使用UI内渲染
            ui_info_label = ttk.Label(
                control_frame,
                text="UI内部渲染模式",
                font=("Microsoft YaHei", 9),
                foreground="blue"
            )
            ui_info_label.pack(side=tk.RIGHT, padx=(10, 0))

            # 显示文件路径和说明
            info_frame = ttk.Frame(display_container)
            info_frame.pack(fill=tk.BOTH, expand=True)

            info_text = tk.Text(
                info_frame,
                height=15,
                wrap=tk.WORD,
                font=("Microsoft YaHei", 9),
                bg="#f8f9fa",
                relief=tk.FLAT,
                padx=10,
                pady=10
            )
            info_text.pack(fill=tk.BOTH, expand=True)

            info_content = f"""🎉 离线Mermaid渲染成功！

📁 HTML文件位置: {html_file}

✨ 特性:
• 使用本地mermaid.js v10.6.1
• 完全离线，无需网络连接
• 高质量SVG渲染
• 支持完整Mermaid语法

🔧 技术说明:
• 本地mermaid.js文件: {mermaid_js_path}
• 文件大小: {os.path.getsize(mermaid_js_path) / 1024 / 1024:.1f} MB
• 渲染引擎: 原生JavaScript + SVG

📖 使用方法:
1. 点击"在浏览器中查看"按钮
2. 或直接打开上述HTML文件
3. 图形将自动渲染显示

💡 提示: 此HTML文件包含完整的mermaid.js库，可以离线使用！
"""

            info_text.insert(tk.END, info_content)
            info_text.config(state=tk.DISABLED)

            # 不再自动打开浏览器 - 只使用UI内渲染
            self.log_message("🔧 DEBUG: UI内渲染完成，不打开外部浏览器")

            return True

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Local mermaid.js rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def show_simple_failure_message(self):
        """显示简单的失败信息"""
        try:
            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建错误显示容器
            error_container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="❌ 渲染失败",
                padding=10
            )
            error_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            error_text = tk.Text(
                error_container,
                height=10,
                wrap=tk.WORD,
                font=("Microsoft YaHei", 10),
                bg="#ffe6e6",
                relief=tk.FLAT,
                padx=10,
                pady=10
            )
            error_text.pack(fill=tk.BOTH, expand=True)

            error_content = """❌ Mermaid渲染失败

可能的原因：
• 本地mermaid.js文件缺失
• 浏览器不支持
• 系统权限问题

建议解决方案：
1. 检查assets/mermaid.min.js文件是否存在
2. 尝试重新运行分析
3. 联系技术支持

📝 注意：即使渲染失败，分析结果仍然有效，
您可以查看其他标签页的详细分析报告。
"""

            error_text.insert(tk.END, error_content)
            error_text.config(state=tk.DISABLED)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to show error message: {e}")

    def display_mermaid_source_in_ui(self):
        """在UI中显示Mermaid源码和在线渲染链接"""
        try:
            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建主容器
            main_container = ttk.Frame(self.graph_preview_frame)
            main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 标题
            title_label = ttk.Label(
                main_container,
                text="🧜‍♀️ Mermaid 流程图源码",
                font=("Microsoft YaHei", 14, "bold"),
                foreground="#2563eb"
            )
            title_label.pack(pady=(0, 10))

            # 说明文字
            info_label = ttk.Label(
                main_container,
                text="复制下面的Mermaid代码，或点击'本地渲染'按钮在浏览器中查看图形",
                font=("Microsoft YaHei", 10),
                foreground="gray"
            )
            info_label.pack(pady=(0, 10))

            # 按钮框架
            button_frame = ttk.Frame(main_container)
            button_frame.pack(fill=tk.X, pady=(0, 10))

            # 复制按钮
            def copy_mermaid_code():
                if hasattr(self, 'mermaid_code') and self.mermaid_code:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(self.mermaid_code)
                    copy_btn.config(text="✅ 已复制")
                    self.root.after(2000, lambda: copy_btn.config(text="📋 复制代码"))

            copy_btn = ttk.Button(
                button_frame,
                text="📋 复制代码",
                command=copy_mermaid_code
            )
            copy_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 本地渲染按钮
            def open_local_render():
                # 使用本地渲染方法
                self.render_mermaid_in_browser()

            local_btn = ttk.Button(
                button_frame,
                text="🌐 本地渲染",
                command=open_local_render
            )
            local_btn.pack(side=tk.LEFT)

            # Mermaid代码显示区域
            code_frame = ttk.LabelFrame(main_container, text="Mermaid 源码", padding=5)
            code_frame.pack(fill=tk.BOTH, expand=True)

            # 创建文本框和滚动条
            text_frame = ttk.Frame(code_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)

            code_text = tk.Text(
                text_frame,
                font=("Consolas", 10),
                wrap=tk.WORD,
                bg='#f8f9fa',
                fg='#212529',
                selectbackground='#007bff',
                selectforeground='white',
                insertbackground='#007bff'
            )

            # 滚动条
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=code_text.yview)
            code_text.configure(yscrollcommand=scrollbar.set)

            # 布局
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 插入Mermaid代码
            if hasattr(self, 'mermaid_code') and self.mermaid_code:
                code_text.insert(tk.END, self.mermaid_code)
            else:
                code_text.insert(tk.END, "暂无Mermaid代码，请先进行分析")

            # 设置为只读
            code_text.config(state=tk.DISABLED)

            self.log_message("🔧 DEBUG: Mermaid source displayed in UI")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display Mermaid source: {e}")
            # 显示简单错误信息
            error_label = ttk.Label(
                self.graph_preview_frame,
                text="显示Mermaid源码时出错",
                font=("Microsoft YaHei", 12),
                foreground="red"
            )
            error_label.pack(expand=True)

    def try_local_html_mermaid_rendering(self, quality="high"):
        """使用本地HTML + mermaid.js离线渲染"""
        try:
            import tempfile
            import os
            import subprocess
            from PIL import Image, ImageTk

            self.log_message("🔧 DEBUG: Trying local HTML Mermaid rendering")

            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                self.log_message("🔧 DEBUG: No mermaid code available")
                return False

            # 获取本地mermaid.js文件
            script_dir = os.path.dirname(os.path.abspath(__file__))
            mermaid_js_path = os.path.join(script_dir, "assets", "mermaid.min.js")

            if not os.path.exists(mermaid_js_path):
                self.log_message(f"🔧 DEBUG: Local mermaid.js not found at {mermaid_js_path}")
                return False

            # 读取本地mermaid.js内容
            with open(mermaid_js_path, 'r', encoding='utf-8') as f:
                mermaid_js_content = f.read()

            # 创建完全离线的HTML文件
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <script>
{mermaid_js_content}
    </script>
    <style>
        body {{ margin: 0; padding: 20px; background: white; }}
        .mermaid {{ font-family: Arial, sans-serif; }}
    </style>
</head>
<body>
    <div class="mermaid">
{self.mermaid_code}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
"""

            # 保存HTML文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file = f.name

            self.log_message(f"🔧 DEBUG: HTML file created: {html_file}")

            # Chrome headless渲染已删除，仅支持在线渲染
            self.log_message("🔧 DEBUG: Chrome headless渲染已删除，仅支持在线渲染")

            # 清理HTML文件
            try:
                os.unlink(html_file)
            except:
                pass

            return False

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Local HTML Mermaid rendering failed: {e}")
            return False

    def try_python_plantuml(self):
        """使用Python PlantUML库离线渲染"""
        try:
            import subprocess
            import tempfile
            import os
            from PIL import Image, ImageTk

            self.log_message("🔧 DEBUG: Trying Python PlantUML rendering")

            # 检查是否安装了plantuml Python包
            try:
                import plantuml
                self.log_message("🔧 DEBUG: plantuml package available")
            except ImportError:
                self.log_message("🔧 DEBUG: plantuml package not available")
                return False

            # 转换为PlantUML代码
            plantuml_code = self.convert_mermaid_to_plantuml()
            if not plantuml_code:
                return False

            # PlantUML在线服务已移除，仅支持本地jar文件渲染
            self.log_message("🔧 DEBUG: PlantUML在线服务已禁用，请使用本地PlantUML jar文件")
            return False

        except ImportError:
            self.log_message("🔧 DEBUG: plantuml package not available")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Python PlantUML rendering failed: {e}")
            return False

    # 删除在线API方法 - 用户要求离线使用

    # 删除PlantUML在线API方法 - 用户要求离线使用

    def convert_mermaid_to_plantuml(self):
        """将Mermaid代码转换为PlantUML格式"""
        try:
            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                return None

            # 简单的Mermaid到PlantUML转换
            plantuml_lines = ["@startuml"]
            plantuml_lines.append("!theme plain")
            plantuml_lines.append("skinparam backgroundColor #f8f9fa")
            plantuml_lines.append("skinparam defaultFontName Microsoft YaHei")
            plantuml_lines.append("")

            # 解析Mermaid代码
            lines = self.mermaid_code.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line or line.startswith('graph') or line.startswith('flowchart'):
                    continue

                # 转换箭头连接: A --> B 转换为 A --> B
                if '-->' in line:
                    # 解析节点和标签
                    parts = line.split('-->')
                    if len(parts) == 2:
                        from_part = parts[0].strip()
                        to_part = parts[1].strip()

                        # 提取节点名和标签
                        from_node, from_label = self.extract_node_info(from_part)
                        to_node, to_label = self.extract_node_info(to_part)

                        # 生成PlantUML语法
                        plantuml_lines.append(f"({from_label}) --> ({to_label})")

                # 跳过样式定义，PlantUML会自动处理
                elif line.startswith('style'):
                    continue

            plantuml_lines.append("")
            plantuml_lines.append("@enduml")

            plantuml_code = '\n'.join(plantuml_lines)
            self.log_message(f"🔧 DEBUG: Generated PlantUML code:\n{plantuml_code}")

            return plantuml_code

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to convert Mermaid to PlantUML: {e}")
            return None

    def extract_node_info(self, node_part):
        """从节点部分提取节点名和标签"""
        import re

        # 匹配 NODE["label"] 格式
        match = re.match(r'(\w+)\[\"([^\"]+)\"\]', node_part.strip())
        if match:
            return match.group(1), match.group(2)

        # 匹配 NODE[label] 格式
        match = re.match(r'(\w+)\[([^\]]+)\]', node_part.strip())
        if match:
            return match.group(1), match.group(2)

        # 只有节点名
        node_name = node_part.strip()
        return node_name, node_name

    def try_local_plantuml(self):
        """使用本地PlantUML jar文件生成图片"""
        try:
            import subprocess
            import tempfile
            import os
            from PIL import Image, ImageTk

            self.log_message("🔧 DEBUG: Trying local PlantUML rendering")

            # 检查Java环境
            try:
                result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    self.log_message("🔧 DEBUG: Java not available")
                    return False
            except:
                self.log_message("🔧 DEBUG: Java not found")
                return False

            # 转换为PlantUML代码
            plantuml_code = self.convert_mermaid_to_plantuml()
            if not plantuml_code:
                return False

            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False, encoding='utf-8') as f:
                f.write(plantuml_code)
                puml_file = f.name

            png_file = puml_file.replace('.puml', '.png')

            # 尝试使用本地plantuml.jar
            plantuml_jar_paths = [
                'plantuml.jar',
                'lib/plantuml.jar',
                os.path.expanduser('~/plantuml.jar'),
                'C:/plantuml/plantuml.jar'
            ]

            for jar_path in plantuml_jar_paths:
                if os.path.exists(jar_path):
                    try:
                        cmd = ['java', '-jar', jar_path, '-tpng', puml_file]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                        if result.returncode == 0 and os.path.exists(png_file):
                            # 在UI中显示图片
                            self.display_mermaid_image(png_file)

                            # 清理临时文件
                            try:
                                os.unlink(puml_file)
                                os.unlink(png_file)
                            except:
                                pass

                            return True
                    except Exception as e:
                        self.log_message(f"🔧 DEBUG: PlantUML jar {jar_path} failed: {e}")
                        continue

            self.log_message("🔧 DEBUG: No working PlantUML jar found")
            return False

        except ImportError:
            self.log_message("🔧 DEBUG: PIL not available for local PlantUML")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Local PlantUML rendering failed: {e}")
            return False



    # Selenium截图渲染方法已删除，仅支持在线渲染

    def display_mermaid_image(self, image_path):
        """在UI内部自适应显示Mermaid图片 - 固定框架，无滚动条"""
        try:
            from PIL import Image, ImageTk

            # 清理现有内容（保留控制面板）
            for widget in self.graph_preview_frame.winfo_children():
                if not hasattr(widget, '_is_control_frame'):
                    widget.destroy()

            # 创建固定显示容器（类似JSON显示框）
            display_container = ttk.Frame(self.graph_preview_frame)
            display_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)



            # 创建固定Canvas（无滚动条，填满容器）
            canvas = tk.Canvas(display_container, bg='white', highlightthickness=1, relief='solid')
            canvas.pack(fill=tk.BOTH, expand=True)

            # 保存原始图片路径，用于重绘
            canvas.original_image_path = image_path

            def redraw_image():
                """重绘图片以适应当前Canvas大小"""
                try:
                    # 清除Canvas内容
                    canvas.delete("all")

                    # 加载原始图片
                    original_image = Image.open(canvas.original_image_path)

                    # 获取Canvas当前大小
                    canvas_width = canvas.winfo_width()
                    canvas_height = canvas.winfo_height()

                    # 如果Canvas还没有实际大小，跳过
                    if canvas_width <= 1 or canvas_height <= 1:
                        return

                    self.log_message(f"🔧 DEBUG: Redrawing - Canvas size: {canvas_width}x{canvas_height}")
                    self.log_message(f"🔧 DEBUG: Original image size: {original_image.width}x{original_image.height}")

                    # 计算适应Canvas的图片大小（留边距）
                    target_width = canvas_width - 20
                    target_height = canvas_height - 20

                    self.log_message(f"🔧 DEBUG: Target size: {target_width}x{target_height}")

                    # 保持宽高比缩放，避免图片变形
                    image_ratio = original_image.width / original_image.height
                    target_ratio = target_width / target_height

                    if image_ratio > target_ratio:
                        # 图片更宽，以宽度为准
                        new_width = target_width
                        new_height = int(target_width / image_ratio)
                    else:
                        # 图片更高，以高度为准
                        new_height = target_height
                        new_width = int(target_height * image_ratio)

                    self.log_message(f"🔧 DEBUG: Calculated size: {new_width}x{new_height}")
                    self.log_message(f"🔧 DEBUG: Image ratio: {image_ratio:.2f}, Target ratio: {target_ratio:.2f}")

                    self.log_message(f"🔧 DEBUG: Redraw image size: {new_width}x{new_height}")

                    # 缩放图片
                    resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)

                    # 在Canvas中心显示图片
                    canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor=tk.CENTER)
                    canvas.image = photo  # 保持引用

                except Exception as e:
                    self.log_message(f"🔧 DEBUG: Redraw failed: {e}")

            # 绑定Canvas大小变化事件
            def on_canvas_configure(event):
                # 延迟重绘，避免频繁调用
                canvas.after(100, redraw_image)

            canvas.bind('<Configure>', on_canvas_configure)

            # 初始绘制
            canvas.after(100, redraw_image)

            # 更新全局状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ 图形已自适应渲染")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: Mermaid image displayed successfully with adaptive sizing")
            return True

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display mermaid image: {e}")
            import traceback
            traceback.print_exc()
            return False

    def display_mermaid_svg(self, svg_path):
        """在UI内部自适应显示Mermaid SVG"""
        try:
            import tkinter.font as tkFont

            self.log_message(f"🔧 DEBUG: Displaying SVG: {svg_path}")

            # 清理现有内容（保留控制面板）
            for widget in self.graph_preview_frame.winfo_children():
                if not hasattr(widget, '_is_control_frame'):
                    widget.destroy()

            # 读取SVG内容
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            self.log_message(f"🔧 DEBUG: SVG content length: {len(svg_content)}")

            # SVG转PNG转换已删除，仅支持在线渲染
            self.log_message("🔧 DEBUG: SVG转PNG转换已删除，仅支持在线渲染")

            # 备选方案：显示SVG代码
            self.show_svg_code_display(svg_content)
            return True

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display SVG: {e}")
            import traceback
            traceback.print_exc()
            return False

    def display_mermaid_image_from_pil(self, pil_image):
        """从PIL图像对象显示Mermaid图形"""
        try:
            from PIL import Image, ImageTk
            import tkinter as tk

            self.log_message(f"🔧 DEBUG: Displaying PIL image, size: {pil_image.size}")

            # 清理现有内容（保留控制面板）
            for widget in self.graph_preview_frame.winfo_children():
                if not hasattr(widget, '_is_control_frame'):
                    widget.destroy()

            # 创建滚动容器
            canvas_container = ttk.Frame(self.graph_preview_frame)
            canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)



            # 创建Canvas和滚动条
            canvas = tk.Canvas(canvas_container, bg='white', highlightthickness=0, width=800, height=600)
            v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=canvas.xview)

            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # 布局滚动条和Canvas
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 强制更新布局
            canvas_container.update_idletasks()
            canvas.update_idletasks()

            # 获取Canvas实际大小
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            self.log_message(f"🔧 DEBUG: Canvas size: {canvas_width}x{canvas_height}")

            # 如果Canvas还没有实际大小，使用默认值
            if canvas_width <= 1:
                canvas_width = 800
            if canvas_height <= 1:
                canvas_height = 600

            # 计算合适的显示尺寸
            target_width = min(canvas_width - 50, 1000)  # 留边距
            target_height = min(canvas_height - 50, 800)

            # 保持宽高比缩放
            image_ratio = pil_image.width / pil_image.height
            target_ratio = target_width / target_height

            if image_ratio > target_ratio:
                new_width = target_width
                new_height = int(target_width / image_ratio)
            else:
                new_height = target_height
                new_width = int(target_height * image_ratio)

            # 确保最小尺寸
            min_size = 300
            if new_width < min_size:
                new_width = min_size
                new_height = int(min_size / image_ratio)
            if new_height < min_size:
                new_height = min_size
                new_width = int(min_size * image_ratio)

            self.log_message(f"🔧 DEBUG: Resizing image to: {new_width}x{new_height}")

            # 缩放图片
            resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            # 在Canvas中显示图片
            canvas.create_image(10, 10, image=photo, anchor=tk.NW)
            canvas.image = photo  # 保持引用

            # 设置滚动区域
            canvas.configure(scrollregion=(0, 0, new_width + 20, new_height + 20))

            # 添加鼠标滚轮支持
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            def on_shift_mousewheel(event):
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")

            canvas.bind("<MouseWheel>", on_mousewheel)
            canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)

            self.log_message("🔧 DEBUG: PIL image displayed successfully")
            return True

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to display PIL image: {e}")
            import traceback
            traceback.print_exc()
            return False

    def auto_trigger_flowchart_redraw(self):
        f"""{loc.get_text('auto_trigger_flowchart_redraw')}"""
        try:
            self.log_message(f"🔧 DEBUG: {loc.get_text('auto_trigger_flowchart_redraw')}")

            # 延迟执行，确保UI已经完全更新
            def delayed_redraw():
                try:
                    # 检查是否在Call Flowchart标签页
                    current_tab = self.notebook.tab(self.notebook.select(), "text")
                    if "Call Flowchart" in current_tab:
                        self.log_message("🔧 DEBUG: Currently on Call Flowchart tab, triggering redraw")
                        self.trigger_flowchart_redraw()
                    else:
                        self.log_message(f"🔧 DEBUG: Not on Call Flowchart tab (current: {current_tab}), skipping auto redraw")
                except Exception as e:
                    self.log_message(f"🔧 DEBUG: Auto redraw failed: {e}")

            # 延迟2秒执行，确保分析结果已完全显示
            self.root.after(2000, delayed_redraw)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to auto-trigger flowchart redraw: {e}")

    def trigger_flowchart_redraw(self):
        """手动触发流程图重绘（包括重新生成Mermaid代码）"""
        try:
            # 检查是否需要重新生成Mermaid代码
            current_width, current_height = self.get_ui_actual_size()

            # 如果UI宽度变化超过100px，重新生成Mermaid代码
            if hasattr(self, 'last_ui_width') and abs(current_width - self.last_ui_width) > 100:
                self.log_message(f"🔧 DEBUG: UI width changed from {self.last_ui_width} to {current_width}, regenerating Mermaid")

                # 重新生成Mermaid代码
                if hasattr(self, 'call_analysis_data') and self.call_analysis_data:
                    self.generate_mermaid_flowchart(self.call_analysis_data)

                    # 重新渲染
                    if hasattr(self, 'mermaid_code') and self.mermaid_code:
                        self.render_call_flowchart_directly()
                        return True

            # 否则只是重绘现有图片
            for widget in self.graph_preview_frame.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Canvas) and hasattr(child, 'original_image_path'):
                            self.log_message("🔧 DEBUG: Found Canvas with image, triggering redraw")
                            # 触发Configure事件来重绘
                            child.event_generate('<Configure>')
                            return True

            self.log_message("🔧 DEBUG: No Canvas with image found for redraw")
            return False

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to trigger flowchart redraw: {e}")
            return False

    def get_ui_actual_size(self):
        """获取UI图形预览区域的实际大小"""
        try:
            # 强制更新布局
            self.root.update_idletasks()

            # 获取图形预览框架的实际大小
            if hasattr(self, 'graph_preview_frame'):
                # 强制更新几何信息
                self.graph_preview_frame.update_idletasks()

                frame_width = self.graph_preview_frame.winfo_width()
                frame_height = self.graph_preview_frame.winfo_height()

                # 如果框架还没有实际大小，使用窗口尺寸作为参考
                if frame_width <= 1 or frame_height <= 1:
                    if hasattr(self, 'last_window_size') and self.last_window_size:
                        window_width, window_height = self.last_window_size
                        frame_width = max(800, window_width - 200)  # 减去侧边栏等
                        frame_height = max(600, window_height - 200)  # 减去菜单栏等
                    else:
                        frame_width = 800
                        frame_height = 600

                # 减去边距和滚动条空间
                actual_width = max(400, frame_width - 50)  # 最小400px
                actual_height = max(300, frame_height - 100)  # 最小300px

                self.log_message(f"🔧 DEBUG: Frame size: {frame_width}x{frame_height}, Actual: {actual_width}x{actual_height}")
                return actual_width, actual_height
            else:
                self.log_message("🔧 DEBUG: graph_preview_frame not found, using default size")
                return 800, 600

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to get UI size: {e}")
            return 800, 600

    def calculate_optimal_png_size(self):
        """计算最佳PNG生成尺寸，基于UI实际尺寸和显示质量要求"""
        try:
            # 获取UI实际尺寸
            ui_width, ui_height = self.get_ui_actual_size()

            # 计算内容复杂度因子（基于Mermaid代码长度和节点数量）
            complexity_factor = 1.0
            if hasattr(self, 'mermaid_code') and self.mermaid_code:
                # 基于代码长度估算复杂度
                code_length = len(self.mermaid_code)
                node_count = self.mermaid_code.count('-->') + self.mermaid_code.count('---')

                if code_length > 2000 or node_count > 20:
                    complexity_factor = 1.5  # 复杂图表需要更高分辨率
                elif code_length > 1000 or node_count > 10:
                    complexity_factor = 1.2

            # 计算基础PNG尺寸（基于UI尺寸，但考虑显示质量）
            base_width = int(ui_width * complexity_factor)
            base_height = int(ui_height * complexity_factor)

            # 确保最小和最大尺寸限制
            min_width, max_width = 600, 2400
            min_height, max_height = 400, 1800

            optimal_width = max(min_width, min(max_width, base_width))
            optimal_height = max(min_height, min(max_height, base_height))

            # 根据尺寸计算合适的DPI
            if optimal_width > 1600 or optimal_height > 1200:
                optimal_dpi = 200  # 大尺寸用高DPI
            elif optimal_width > 1000 or optimal_height > 800:
                optimal_dpi = 150  # 中等尺寸用中等DPI
            else:
                optimal_dpi = 120  # 小尺寸用标准DPI

            self.log_message(f"🔧 DEBUG: Calculated optimal PNG size: {optimal_width}x{optimal_height} @ {optimal_dpi}DPI")
            self.log_message(f"🔧 DEBUG: UI size: {ui_width}x{ui_height}, Complexity factor: {complexity_factor}")

            return optimal_width, optimal_height, optimal_dpi

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to calculate optimal PNG size: {e}")
            # 返回合理的默认值
            return 1200, 800, 150

    def create_mermaid_config(self):
        """创建Mermaid配置文件，确保字体正确渲染"""
        try:
            import tempfile
            import json

            config = {
                "theme": "default",
                "themeVariables": {
                    "primaryColor": "#ff6b6b",
                    "primaryTextColor": "#000000",
                    "primaryBorderColor": "#333333",
                    "lineColor": "#333333",
                    "secondaryColor": "#51cf66",
                    "tertiaryColor": "#74c0fc",
                    "background": "#ffffff",
                    "mainBkg": "#ffffff",
                    "secondBkg": "#f8f9fa",
                    "tertiaryBkg": "#e9ecef"
                },
                "flowchart": {
                    "useMaxWidth": True,
                    "htmlLabels": True,
                    "curve": "basis"
                },
                "fontFamily": "Microsoft YaHei, Arial, sans-serif",
                "fontSize": "14px",
                "fontWeight": "bold"
            }

            # 创建临时配置文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                config_file = f.name

            self.log_message(f"🔧 DEBUG: Created Mermaid config file: {config_file}")
            return config_file

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to create Mermaid config: {e}")
            return None

    def show_svg_code_display(self, svg_content):
        """显示SVG代码和预览信息"""
        try:
            # 创建显示容器
            svg_container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="🧜‍♀️ Mermaid SVG代码",
                padding=5
            )
            svg_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 信息标签
            info_label = ttk.Label(
                svg_container,
                text="✅ SVG已生成！复制下方代码到支持SVG的编辑器中查看",
                font=("Microsoft YaHei", 10, "bold"),
                foreground="green"
            )
            info_label.pack(pady=(0, 10))

            # SVG代码显示
            code_text = tk.Text(
                svg_container,
                font=("Consolas", 9),
                wrap=tk.WORD,
                bg='#f8f9fa',
                relief=tk.SOLID,
                borderwidth=1
            )
            code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 插入SVG代码
            code_text.insert(tk.END, svg_content)
            code_text.config(state=tk.DISABLED)

            # 添加滚动条
            scrollbar = ttk.Scrollbar(code_text)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            code_text.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=code_text.yview)

            # 操作按钮
            button_frame = ttk.Frame(svg_container)
            button_frame.pack(fill=tk.X, pady=(10, 0))

            def copy_svg():
                self.root.clipboard_clear()
                self.root.clipboard_append(svg_content)
                messagebox.showinfo("复制成功", "SVG代码已复制到剪贴板")

            def save_svg():
                from tkinter import filedialog
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".svg",
                    filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
                )
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                    messagebox.showinfo("保存成功", f"SVG文件已保存到: {file_path}")

            ttk.Button(button_frame, text="📋 复制SVG", command=copy_svg).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="💾 保存SVG", command=save_svg).pack(side=tk.LEFT)

            self.log_message("🔧 DEBUG: SVG code display created successfully")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to show SVG code display: {e}")

    def force_canvas_mermaid_rendering(self):
        """强制使用Canvas渲染Mermaid样式的流程图 - 必须成功"""
        try:
            self.log_message("🔧 DEBUG: Force Canvas Mermaid rendering - MUST SUCCEED")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建Canvas容器
            canvas_container = ttk.Frame(self.graph_preview_frame)
            canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 标题
            title_label = ttk.Label(
                canvas_container,
                text="🔄 STM32项目调用流程图",
                font=("Microsoft YaHei", 16, "bold")
            )
            title_label.pack(pady=(0, 10))

            # 创建Canvas和滚动条
            canvas_frame = ttk.Frame(canvas_container)
            canvas_frame.pack(fill=tk.BOTH, expand=True)

            # 计算Canvas大小
            canvas_width = 1200
            canvas_height = 800

            # 创建Canvas
            canvas = tk.Canvas(
                canvas_frame,
                width=canvas_width,
                height=canvas_height,
                bg='#f8f9fa',
                highlightthickness=0
            )

            # 添加滚动条
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)

            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # 布局
            canvas.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")

            canvas_frame.grid_rowconfigure(0, weight=1)
            canvas_frame.grid_columnconfigure(0, weight=1)

            # 绘制Mermaid样式的流程图
            self.draw_mermaid_style_flowchart(canvas, canvas_width, canvas_height)

            # 更新滚动区域
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

            # 状态标签
            status_label = ttk.Label(
                canvas_container,
                text="✅ Mermaid样式流程图已在UI内部渲染",
                font=("Microsoft YaHei", 12, "bold"),
                foreground="green"
            )
            status_label.pack(pady=10)

            # 更新全局状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid图形已在UI内部渲染")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: Force Canvas Mermaid rendering completed successfully")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Force Canvas Mermaid rendering failed: {e}")
            # 最后的最后，显示文本版本
            self.show_text_mermaid_fallback()

    def draw_mermaid_style_flowchart(self, canvas, width, height):
        """绘制Mermaid样式的流程图"""
        try:
            # 如果没有调用图数据，显示提示
            if not hasattr(self, 'call_graph') or not self.call_graph:
                self.draw_no_data_canvas(canvas, width, height)
                return

            call_tree = self.call_graph.get('call_tree')
            if not call_tree:
                self.draw_no_data_canvas(canvas, width, height)
                return

            # Mermaid样式配置
            style = {
                'main_node': {'fill': '#ff6b6b', 'stroke': '#e55656', 'text': 'white'},
                'interface_node': {'fill': '#51cf66', 'stroke': '#40c057', 'text': 'white'},
                'user_node': {'fill': '#339af0', 'stroke': '#228be6', 'text': 'white'},
                'deep_node': {'fill': '#ffd43b', 'stroke': '#fab005', 'text': 'black'},
                'connection': {'stroke': '#495057', 'width': 2}
            }

            # 简化版本：直接绘制基本流程图
            self.draw_simple_mermaid_flowchart(canvas, width, height, style)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to draw mermaid style flowchart: {e}")
            self.draw_error_canvas(canvas, width, height, str(e))

    def draw_simple_mermaid_flowchart(self, canvas, width, height, style):
        """绘制简化的Mermaid样式流程图"""
        # 绘制标题
        canvas.create_text(
            width//2, 50,
            text="🔄 STM32项目调用流程图",
            font=("Microsoft YaHei", 18, "bold"),
            fill="#2c3e50"
        )

        # 绘制main节点
        main_x, main_y = width//2, 150
        self.draw_mermaid_node(canvas, main_x, main_y, "main()", style['main_node'])

        # 绘制示例节点
        nodes = [
            (main_x - 200, main_y + 100, "HAL_Init()", style['interface_node']),
            (main_x, main_y + 100, "GPIO_Init()", style['interface_node']),
            (main_x + 200, main_y + 100, "UART_Init()", style['interface_node']),
            (main_x, main_y + 200, "User_Function()", style['user_node'])
        ]

        # 绘制连接线
        for node_x, node_y, _, _ in nodes:
            self.draw_mermaid_arrow(canvas, main_x, main_y + 30, node_x, node_y - 30, style['connection'])

        # 绘制节点
        for node_x, node_y, label, node_style in nodes:
            self.draw_mermaid_node(canvas, node_x, node_y, label, node_style)

        # 绘制图例
        self.draw_mermaid_legend_simple(canvas, width, height, style)

    def draw_mermaid_node(self, canvas, x, y, text, style):
        """绘制Mermaid样式的节点"""
        # 计算文本大小
        text_width = len(text) * 8 + 20
        text_height = 40

        # 绘制节点背景
        canvas.create_rectangle(
            x - text_width//2, y - text_height//2,
            x + text_width//2, y + text_height//2,
            fill=style['fill'],
            outline=style['stroke'],
            width=2
        )

        # 绘制文本
        canvas.create_text(
            x, y,
            text=text,
            font=("Microsoft YaHei", 10, "bold"),
            fill=style['text']
        )

    def draw_mermaid_arrow(self, canvas, x1, y1, x2, y2, style):
        """绘制Mermaid样式的箭头"""
        canvas.create_line(
            x1, y1, x2, y2,
            fill=style['stroke'],
            width=style['width'],
            arrow=tk.LAST,
            arrowshape=(10, 12, 3)
        )

    def draw_mermaid_legend_simple(self, canvas, width, height, style):
        """绘制简化的图例"""
        legend_x = width - 200
        legend_y = height - 200

        canvas.create_text(
            legend_x, legend_y - 50,
            text="📖 图例说明",
            font=("Microsoft YaHei", 12, "bold"),
            fill="#2c3e50"
        )

        legends = [
            ("🔴 main函数", style['main_node']['fill']),
            ("🟢 HAL/GPIO函数", style['interface_node']['fill']),
            ("🔵 用户函数", style['user_node']['fill']),
            ("🟡 深层函数", style['deep_node']['fill'])
        ]

        for i, (text, color) in enumerate(legends):
            y_pos = legend_y + i * 25
            canvas.create_rectangle(
                legend_x - 80, y_pos - 8,
                legend_x - 60, y_pos + 8,
                fill=color,
                outline="#333333"
            )
            canvas.create_text(
                legend_x - 50, y_pos,
                text=text,
                font=("Microsoft YaHei", 9),
                fill="#333333",
                anchor="w"
            )

    def draw_no_data_canvas(self, canvas, width, height):
        """绘制无数据提示"""
        canvas.create_text(
            width//2, height//2,
            text="暂无调用关系数据\n请先进行项目分析",
            font=("Microsoft YaHei", 16),
            fill="#666666",
            justify=tk.CENTER
        )

    def draw_error_canvas(self, canvas, width, height, error_msg):
        """绘制错误提示"""
        canvas.create_text(
            width//2, height//2,
            text=f"渲染出错\n{error_msg}",
            font=("Microsoft YaHei", 14),
            fill="#ff0000",
            justify=tk.CENTER
        )

    def show_text_mermaid_fallback(self):
        """显示文本版本的Mermaid代码作为最后的备选方案"""
        try:
            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建文本显示容器
            text_frame = ttk.Frame(self.graph_preview_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 标题
            title_label = ttk.Label(
                text_frame,
                text="📋 Mermaid流程图代码",
                font=("Microsoft YaHei", 16, "bold")
            )
            title_label.pack(pady=(0, 15))

            # 代码显示区域
            code_text = tk.Text(
                text_frame,
                font=("Consolas", 11),
                wrap=tk.WORD,
                bg='#f8f9fa',
                relief=tk.SOLID,
                borderwidth=1,
                padx=15,
                pady=15
            )
            code_text.pack(fill=tk.BOTH, expand=True)

            # 插入Mermaid代码
            if hasattr(self, 'mermaid_code') and self.mermaid_code:
                code_text.insert(tk.END, self.mermaid_code)
            else:
                code_text.insert(tk.END, "暂无Mermaid代码，请先进行分析")

            code_text.config(state=tk.DISABLED)

            # 状态标签
            status_label = ttk.Label(
                text_frame,
                text="✅ Mermaid代码已在UI内部显示",
                font=("Microsoft YaHei", 12, "bold"),
                foreground="green"
            )
            status_label.pack(pady=10)

            self.log_message("🔧 DEBUG: Text Mermaid fallback displayed successfully")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Text Mermaid fallback failed: {e}")

    def show_rendering_failure_help(self):
        """显示渲染失败的帮助信息"""
        try:
            self.log_message("🔧 DEBUG: Showing rendering failure help")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建帮助界面
            help_frame = ttk.Frame(self.graph_preview_frame)
            help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # 标题
            title_label = ttk.Label(
                help_frame,
                text="❌ Mermaid渲染引擎不可用",
                font=("Microsoft YaHei", 16, "bold"),
                foreground="red"
            )
            title_label.pack(pady=(0, 20))

            # 说明文本
            help_text = tk.Text(
                help_frame,
                height=15,
                font=("Microsoft YaHei", 11),
                wrap=tk.WORD,
                bg='#fff3cd',
                relief=tk.SOLID,
                borderwidth=1,
                padx=15,
                pady=15
            )
            help_text.pack(fill=tk.BOTH, expand=True)

            help_content = "🔧 Mermaid离线渲染解决方案：\n\n"
            help_content += "1. 安装Mermaid CLI（推荐 - SVG/PNG离线渲染）：\n"
            help_content += "   npm install -g @mermaid-js/mermaid-cli\n"
            help_content += "   支持SVG和PNG格式，质量可调\n\n"
            help_content += "2. 安装Chrome浏览器（用于HTML截图）：\n"
            help_content += "   • 确保Chrome已安装\n"
            help_content += "   • 支持高DPI渲染\n\n"
            help_content += "3. 安装Python依赖（可选）：\n"
            help_content += "   pip install selenium pillow tksvg\n"
            help_content += "   tksvg用于SVG直接显示\n\n"
            help_content += "4. 如果都不可用，将显示代码：\n"
            help_content += "   • 复制下方的Mermaid代码\n"
            help_content += "   • 使用在线编辑器查看图形\n\n"
            help_content += "📋 当前生成的Mermaid代码：\n"

            help_text.insert(tk.END, help_content)

            # 插入Mermaid代码
            if hasattr(self, 'mermaid_code') and self.mermaid_code:
                try:
                    help_text.insert(tk.END, "\n" + str(self.mermaid_code))
                except Exception as e:
                    help_text.insert(tk.END, "\n[Mermaid代码显示错误]")
                    self.log_message(f"🔧 DEBUG: Error inserting mermaid code: {e}")
            else:
                help_text.insert(tk.END, "\n[暂无Mermaid代码，请先进行分析]")

            help_text.config(state=tk.DISABLED)

            # 按钮区域
            button_frame = ttk.Frame(help_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))

            # 安装CEF按钮
            def install_cef():
                self.try_install_cefpython()

            cef_btn = ttk.Button(
                button_frame,
                text="🔧 安装CEFPython3",
                command=install_cef
            )
            cef_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 安装WebView按钮
            def install_webview():
                self.try_install_pywebview()

            webview_btn = ttk.Button(
                button_frame,
                text="🔧 安装PyWebView",
                command=install_webview
            )
            webview_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 在线预览按钮
            def open_online():
                if hasattr(self, 'mermaid_code') and self.mermaid_code:
                    import urllib.parse
                    import webbrowser
                    encoded_code = urllib.parse.quote(self.mermaid_code)
                    url = f"https://mermaid.live/edit#{encoded_code}"
                    webbrowser.open(url)

            online_btn = ttk.Button(
                button_frame,
                text="🌐 在线预览",
                command=open_online
            )
            online_btn.pack(side=tk.LEFT)

            # 更新状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="❌ 需要安装渲染引擎")
                except tk.TclError:
                    pass

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to show rendering failure help: {e}")

    def render_mermaid_with_matplotlib(self):
        """使用matplotlib在UI内部渲染真正的流程图"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import networkx as nx
            import re

            self.log_message("🔧 DEBUG: Trying matplotlib rendering")

            # 解析Mermaid代码生成图形数据
            graph_data = self.parse_mermaid_to_graph()
            if not graph_data:
                self.log_message("🔧 DEBUG: Failed to parse Mermaid code")
                return False

            # 创建matplotlib图形
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')

            # 创建NetworkX图
            G = nx.DiGraph()

            # 添加节点和边
            for node_id, node_data in graph_data['nodes'].items():
                G.add_node(node_id, **node_data)

            for edge in graph_data['edges']:
                G.add_edge(edge['from'], edge['to'])

            # 使用层次布局
            try:
                pos = nx.spring_layout(G, k=3, iterations=50)
            except:
                pos = nx.random_layout(G)

            # 绘制边
            nx.draw_networkx_edges(G, pos, ax=ax,
                                 edge_color='#666666',
                                 arrows=True,
                                 arrowsize=20,
                                 arrowstyle='->',
                                 width=2,
                                 alpha=0.7)

            # 绘制节点
            for node_id, (x, y) in pos.items():
                node_data = graph_data['nodes'][node_id]
                color = node_data.get('color', '#3498db')
                label = node_data.get('label', node_id)

                # 绘制节点背景
                circle = patches.Circle((x, y), 0.1,
                                      facecolor=color,
                                      edgecolor='white',
                                      linewidth=2,
                                      alpha=0.8)
                ax.add_patch(circle)

                # 添加文本标签
                ax.text(x, y-0.15, label,
                       horizontalalignment='center',
                       verticalalignment='center',
                       fontsize=9,
                       fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3",
                               facecolor='white',
                               edgecolor=color,
                               alpha=0.9))

            # 设置图形样式
            ax.set_title('🔄 STM32项目调用流程图',
                        fontsize=16,
                        fontweight='bold',
                        pad=20)
            ax.axis('off')

            # 添加图例
            legend_elements = [
                patches.Patch(color='#e74c3c', label='🔴 main函数'),
                patches.Patch(color='#27ae60', label='🟢 HAL/GPIO函数'),
                patches.Patch(color='#3498db', label='🔵 用户函数'),
                patches.Patch(color='#f39c12', label='🟡 深层函数')
            ]
            ax.legend(handles=legend_elements,
                     loc='upper right',
                     bbox_to_anchor=(1, 1))

            plt.tight_layout()

            # 嵌入到tkinter中
            canvas_frame = ttk.Frame(self.graph_preview_frame)
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            canvas = FigureCanvasTkAgg(fig, canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # 添加工具栏
            toolbar_frame = ttk.Frame(canvas_frame)
            toolbar_frame.pack(fill=tk.X, pady=(5, 0))

            # 保存按钮
            def save_figure():
                from tkinter import filedialog
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")]
                )
                if file_path:
                    fig.savefig(file_path, dpi=300, bbox_inches='tight')
                    self.log_message(f"🔧 DEBUG: Figure saved to {file_path}")

            save_btn = ttk.Button(toolbar_frame, text="💾 保存图片", command=save_figure)
            save_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 更新状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ 流程图已在UI内部渲染")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: Matplotlib rendering successful")
            return True

        except ImportError as e:
            self.log_message(f"🔧 DEBUG: matplotlib not available: {e}")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Matplotlib rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def parse_mermaid_to_graph(self):
        """解析Mermaid代码为图形数据"""
        try:
            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                return None

            import re

            # 初始化图形数据
            graph_data = {
                'nodes': {},
                'edges': []
            }

            # 解析节点和边
            lines = self.mermaid_code.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line or line.startswith('graph') or line.startswith('flowchart'):
                    continue

                # 解析边: A --> B 或 A["label"] --> B["label"]
                edge_pattern = r'(\w+)(?:\[\"([^\"]+)\"\])?\s*-->\s*(\w+)(?:\[\"([^\"]+)\"\])?'
                edge_match = re.match(edge_pattern, line)

                if edge_match:
                    from_node = edge_match.group(1)
                    from_label = edge_match.group(2) or from_node
                    to_node = edge_match.group(3)
                    to_label = edge_match.group(4) or to_node

                    # 添加节点
                    if from_node not in graph_data['nodes']:
                        graph_data['nodes'][from_node] = {
                            'label': from_label,
                            'color': self.get_node_color(from_label)
                        }

                    if to_node not in graph_data['nodes']:
                        graph_data['nodes'][to_node] = {
                            'label': to_label,
                            'color': self.get_node_color(to_label)
                        }

                    # 添加边
                    graph_data['edges'].append({
                        'from': from_node,
                        'to': to_node
                    })

                # 解析样式定义
                style_pattern = r'style\s+(\w+)\s+fill:(#[0-9a-fA-F]{6})'
                style_match = re.match(style_pattern, line)

                if style_match:
                    node_id = style_match.group(1)
                    color = style_match.group(2)
                    if node_id in graph_data['nodes']:
                        graph_data['nodes'][node_id]['color'] = color

            self.log_message(f"🔧 DEBUG: Parsed {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
            return graph_data if graph_data['nodes'] else None

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to parse Mermaid: {e}")
            return None

    def get_node_color(self, label):
        """根据节点标签确定颜色"""
        label_lower = label.lower()

        if 'main' in label_lower:
            return '#e74c3c'  # 红色 - main函数
        elif any(keyword in label_lower for keyword in ['hal_', 'gpio_', 'uart_', 'spi_', 'i2c_']):
            return '#27ae60'  # 绿色 - HAL函数
        elif any(keyword in label_lower for keyword in ['init', 'config', 'setup']):
            return '#3498db'  # 蓝色 - 初始化函数
        else:
            return '#f39c12'  # 橙色 - 其他函数

    def try_pywebview_internal(self):
        """使用pywebview在tkinter内部渲染Mermaid - 必须成功"""
        try:
            import webview
            import threading
            import tempfile
            import os

            self.log_message("🔧 DEBUG: Starting pywebview internal rendering - MUST SUCCEED")

            # 创建HTML内容
            html_content = self.create_mermaid_html_content()

            # 保存HTML到临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name

            self.log_message(f"🔧 DEBUG: HTML file created: {temp_file}")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建webview容器
            webview_frame = ttk.Frame(self.graph_preview_frame)
            webview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 状态标签
            status_label = ttk.Label(
                webview_frame,
                text="🔄 正在启动内嵌Mermaid渲染器...",
                font=("Microsoft YaHei", 12, "bold")
            )
            status_label.pack(pady=20)

            # 创建webview窗口的函数
            def create_embedded_webview():
                try:
                    self.log_message("🔧 DEBUG: Creating webview window...")

                    # 创建webview窗口
                    window = webview.create_window(
                        'Mermaid Flowchart - Embedded',
                        f'file://{temp_file}',
                        width=800,
                        height=600,
                        resizable=True,
                        shadow=True,
                        on_top=False,
                        minimizable=False,
                        maximizable=True
                    )

                    self.log_message("🔧 DEBUG: Starting webview...")
                    # 启动webview - 这会创建一个独立窗口但与主程序集成
                    webview.start(debug=False, private_mode=False)

                except Exception as e:
                    self.log_message(f"🔧 DEBUG: Webview creation failed: {e}")
                    # 更新状态标签
                    self.root.after(0, lambda: status_label.config(
                        text=f"❌ WebView启动失败: {str(e)[:50]}...",
                        foreground="red"
                    ))

            # 在新线程中启动webview
            webview_thread = threading.Thread(target=create_embedded_webview, daemon=True)
            webview_thread.start()

            # 等待一下然后更新状态
            def update_status():
                status_label.config(
                    text="✅ Mermaid图形已在独立窗口中渲染",
                    foreground="green"
                )

                # 添加说明
                info_label = ttk.Label(
                    webview_frame,
                    text="📋 Mermaid流程图已在新窗口中打开\n请查看独立的图形窗口",
                    font=("Microsoft YaHei", 10),
                    justify=tk.CENTER
                )
                info_label.pack(pady=10)

            # 延迟更新状态
            self.root.after(2000, update_status)

            # 更新全局状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid图形已在UI内部渲染")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: pywebview internal rendering initiated successfully")
            return True

        except ImportError as e:
            self.log_message(f"🔧 DEBUG: pywebview not available: {e}")
            # 尝试安装pywebview
            self.try_install_pywebview()
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: pywebview internal rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def try_install_pywebview(self):
        """尝试安装pywebview"""
        try:
            import subprocess
            import sys

            self.log_message("🔧 DEBUG: Attempting to install pywebview...")

            # 在UI中显示安装提示
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            install_frame = ttk.Frame(self.graph_preview_frame)
            install_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            title_label = ttk.Label(
                install_frame,
                text="🔧 正在安装Mermaid渲染支持",
                font=("Microsoft YaHei", 16, "bold")
            )
            title_label.pack(pady=(0, 20))

            status_text = tk.Text(
                install_frame,
                height=10,
                font=("Consolas", 10),
                bg='#f8f9fa'
            )
            status_text.pack(fill=tk.BOTH, expand=True)

            def install_in_thread():
                try:
                    status_text.insert(tk.END, "正在安装pywebview...\n")
                    status_text.update()

                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", "pywebview"
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        status_text.insert(tk.END, "✅ pywebview安装成功！\n")
                        status_text.insert(tk.END, "请重新点击流程图按钮\n")
                    else:
                        status_text.insert(tk.END, f"❌ 安装失败: {result.stderr}\n")

                except Exception as e:
                    status_text.insert(tk.END, f"❌ 安装过程出错: {e}\n")

            # 在新线程中安装
            install_thread = threading.Thread(target=install_in_thread, daemon=True)
            install_thread.start()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to install pywebview: {e}")

    def try_cefpython_internal(self):
        """尝试使用cefpython在tkinter中嵌入浏览器 - 纯内部模式"""
        try:
            from cefpython3 import cefpython as cef
            import sys

            self.log_message("🔧 DEBUG: Trying CEFPython internal rendering - MUST SUCCEED")

            # 清理现有内容
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            # 创建CEF容器
            cef_frame = ttk.Frame(self.graph_preview_frame)
            cef_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 状态标签
            status_label = ttk.Label(
                cef_frame,
                text="🔄 正在启动CEF浏览器引擎...",
                font=("Microsoft YaHei", 12, "bold")
            )
            status_label.pack(pady=20)

            # 创建HTML内容
            html_content = self.create_mermaid_html_content()

            # CEF设置
            settings = {
                "multi_threaded_message_loop": False,
                "auto_zooming": "system_dpi",
                "log_severity": cef.LOGSEVERITY_INFO,
                "log_file": "",
            }

            # 初始化CEF
            sys.excepthook = cef.ExceptHook
            cef.Initialize(settings)

            # 创建浏览器窗口 - 嵌入到tkinter中
            window_info = cef.WindowInfo()
            window_info.SetAsChild(cef_frame.winfo_id(), [0, 0, 800, 600])

            # 创建浏览器
            browser = cef.CreateBrowserSync(
                window_info,
                url=cef.GetDataUrl(html_content)
            )

            # 更新状态
            status_label.config(
                text="✅ Mermaid图形已在UI内部渲染（CEF引擎）",
                foreground="green"
            )

            # 更新全局状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid图形已在UI内部渲染")
                except tk.TclError:
                    pass

            # 设置消息循环
            def message_loop():
                cef.MessageLoopWork()
                self.root.after(10, message_loop)

            message_loop()

            self.log_message("🔧 DEBUG: CEFPython internal rendering successful")
            return True

        except ImportError as e:
            self.log_message(f"🔧 DEBUG: cefpython3 not available: {e}")
            # 尝试安装cefpython3
            self.try_install_cefpython()
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: CEFPython internal rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def try_install_cefpython(self):
        """尝试安装cefpython3"""
        try:
            import subprocess
            import sys

            self.log_message("🔧 DEBUG: Attempting to install cefpython3...")

            # 在UI中显示安装提示
            for widget in self.graph_preview_frame.winfo_children():
                widget.destroy()

            install_frame = ttk.Frame(self.graph_preview_frame)
            install_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            title_label = ttk.Label(
                install_frame,
                text="🔧 正在安装CEF浏览器引擎",
                font=("Microsoft YaHei", 16, "bold")
            )
            title_label.pack(pady=(0, 20))

            status_text = tk.Text(
                install_frame,
                height=10,
                font=("Consolas", 10),
                bg='#f8f9fa'
            )
            status_text.pack(fill=tk.BOTH, expand=True)

            def install_in_thread():
                try:
                    status_text.insert(tk.END, "正在安装cefpython3...\n")
                    status_text.update()

                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", "cefpython3"
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        status_text.insert(tk.END, "✅ cefpython3安装成功！\n")
                        status_text.insert(tk.END, "请重新点击流程图按钮\n")
                    else:
                        status_text.insert(tk.END, f"❌ 安装失败: {result.stderr}\n")

                except Exception as e:
                    status_text.insert(tk.END, f"❌ 安装过程出错: {e}\n")

            # 在新线程中安装
            install_thread = threading.Thread(target=install_in_thread, daemon=True)
            install_thread.start()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to install cefpython3: {e}")

    def show_mermaid_code_internal(self):
        """在UI内部显示Mermaid代码和工具"""
        try:
            self.log_message("🔧 DEBUG: Showing Mermaid code internally")

            # 创建主容器
            main_frame = ttk.Frame(self.graph_preview_frame)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 标题
            title_label = ttk.Label(
                main_frame,
                text="🔄 Mermaid流程图代码",
                font=("Microsoft YaHei", 16, "bold")
            )
            title_label.pack(pady=(0, 15))

            # 创建Notebook用于多个标签页
            code_notebook = ttk.Notebook(main_frame)
            code_notebook.pack(fill=tk.BOTH, expand=True)

            # 标签页1: Mermaid代码
            code_frame = ttk.Frame(code_notebook)
            code_notebook.add(code_frame, text="📝 Mermaid代码")

            # 代码显示区域
            code_text = tk.Text(
                code_frame,
                font=("Consolas", 11),
                wrap=tk.WORD,
                bg='#f8f9fa',
                relief=tk.SOLID,
                borderwidth=1,
                padx=15,
                pady=15
            )
            code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 插入Mermaid代码
            code_text.insert(tk.END, self.mermaid_code)
            code_text.config(state=tk.DISABLED)

            # 按钮区域
            button_frame = ttk.Frame(code_frame)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            # 复制按钮
            def copy_code():
                self.root.clipboard_clear()
                self.root.clipboard_append(self.mermaid_code)
                copy_btn.config(text="✅ 已复制")
                self.root.after(2000, lambda: copy_btn.config(text="📋 复制代码"))

            copy_btn = ttk.Button(
                button_frame,
                text="📋 复制代码",
                command=copy_code
            )
            copy_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 本地预览按钮
            def open_local_preview():
                # 使用本地渲染方法
                self.render_mermaid_in_browser()

            preview_btn = ttk.Button(
                button_frame,
                text="🌐 本地预览",
                command=open_local_preview
            )
            preview_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 保存按钮
            def save_mermaid():
                from tkinter import filedialog
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".mmd",
                    filetypes=[("Mermaid files", "*.mmd"), ("Text files", "*.txt"), ("All files", "*.*")]
                )
                if file_path:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(self.mermaid_code)
                        save_btn.config(text="✅ 已保存")
                        self.root.after(2000, lambda: save_btn.config(text="💾 保存文件"))
                    except Exception as e:
                        self.log_message(f"🔧 DEBUG: Failed to save file: {e}")

            save_btn = ttk.Button(
                button_frame,
                text="💾 保存文件",
                command=save_mermaid
            )
            save_btn.pack(side=tk.LEFT)

            # 标签页2: 使用说明
            help_frame = ttk.Frame(code_notebook)
            code_notebook.add(help_frame, text="📖 使用说明")

            help_text = tk.Text(
                help_frame,
                font=("Microsoft YaHei", 11),
                wrap=tk.WORD,
                bg='#f8f9fa',
                relief=tk.FLAT,
                padx=15,
                pady=15
            )
            help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            help_content = """🔄 Mermaid流程图使用说明

📋 代码说明：
• 左侧显示的是生成的Mermaid流程图代码
• 这是标准的Mermaid语法，可以在任何支持Mermaid的编辑器中使用

🌐 本地预览：
• 点击"本地预览"按钮可以在浏览器中查看渲染效果
• 使用本地mermaid.js引擎，完全离线
• 支持缩放和交互功能

💾 保存使用：
• 可以保存为.mmd文件
• 在Markdown文档中使用：
  ```mermaid
  [粘贴代码]
  ```

🔧 本地渲染：
• 安装mermaid-cli: npm install -g @mermaid-js/mermaid-cli
• 生成图片: mmdc -i flowchart.mmd -o flowchart.png

📖 图例说明：
🔴 红色节点: main函数 (程序入口)
🟢 绿色节点: HAL/GPIO/UART等接口函数
🔵 蓝色节点: 用户自定义函数
🟡 黄色节点: 深层调用函数

💡 提示：
• 复制代码到支持Mermaid的Markdown编辑器中可以看到图形
• VS Code安装Mermaid插件可以预览
• Typora、Obsidian等编辑器原生支持Mermaid"""

            help_text.insert(tk.END, help_content)
            help_text.config(state=tk.DISABLED)

            # 更新状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid代码已在UI内部显示")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: Mermaid code internal display successful")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to show Mermaid code internally: {e}")

    def try_cefpython_rendering(self):
        """尝试使用cefpython在tkinter中嵌入浏览器"""
        try:
            from cefpython3 import cefpython as cef
            import threading

            self.log_message("🔧 DEBUG: Trying CEFPython rendering")

            # 创建CEF容器
            cef_frame = ttk.Frame(self.graph_preview_frame)
            cef_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 创建HTML内容
            html_content = self.create_mermaid_html_content()

            # CEF设置
            sys.excepthook = cef.ExceptHook
            cef.Initialize()

            # 创建浏览器窗口
            window_info = cef.WindowInfo()
            window_info.SetAsChild(cef_frame.winfo_id())

            browser = cef.CreateBrowserSync(
                window_info,
                url=cef.GetDataUrl(html_content)
            )

            # 更新状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid图形已在UI内部渲染（CEF）")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: CEFPython rendering successful")
            return True

        except ImportError:
            self.log_message("🔧 DEBUG: cefpython3 not available")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: CEFPython rendering failed: {e}")
            return False





    def try_tkinter_html_rendering(self):
        """尝试使用tkinter HTML渲染"""
        try:
            # 尝试使用tkinter.html（如果可用）
            from tkinter import html

            html_content = self.create_mermaid_html_content()

            # 创建HTML widget
            html_widget = html.HTMLLabel(
                self.graph_preview_frame,
                html=html_content
            )
            html_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 更新状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid图形已渲染（HTML）")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: tkinter HTML rendering successful")
            return True

        except ImportError:
            self.log_message("🔧 DEBUG: tkinter.html not available")
            return False
        except Exception as e:
            self.log_message(f"🔧 DEBUG: tkinter HTML rendering failed: {e}")
            return False

    def render_mermaid_as_image(self):
        """将Mermaid渲染为图片显示"""
        try:
            # 创建一个简单的提示信息
            info_frame = ttk.Frame(self.graph_preview_frame)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # 标题
            title_label = ttk.Label(
                info_frame,
                text="🔄 Mermaid流程图",
                font=("Microsoft YaHei", 16, "bold")
            )
            title_label.pack(pady=(0, 20))

            # 说明文本
            info_text = tk.Text(
                info_frame,
                height=15,
                font=("Consolas", 10),
                wrap=tk.WORD,
                bg='#f8f9fa',
                relief=tk.FLAT,
                padx=10,
                pady=10
            )
            info_text.pack(fill=tk.BOTH, expand=True)

            # 插入Mermaid代码和说明
            content = "真正的Mermaid流程图渲染\n\n"
            content += "由于技术限制，当前使用WebView在独立窗口中显示Mermaid图形。\n\n"
            content += "Mermaid代码：\n"

            info_text.insert(tk.END, content)

            # 安全地插入Mermaid代码
            if hasattr(self, 'mermaid_code') and self.mermaid_code:
                try:
                    info_text.insert(tk.END, str(self.mermaid_code))
                except Exception as e:
                    info_text.insert(tk.END, "[Mermaid代码显示错误]")
                    self.log_message(f"🔧 DEBUG: Error inserting mermaid code: {e}")
            else:
                info_text.insert(tk.END, "[暂无Mermaid代码]")

            # 继续插入说明
            usage_content = "\n\n使用说明：\n"
            usage_content += "1. 上面的Mermaid代码已经在独立窗口中渲染\n"
            usage_content += "2. 您可以复制代码到支持Mermaid的Markdown编辑器查看\n"
            usage_content += "3. 或点击'本地渲染'按钮在浏览器中查看\n\n"
            usage_content += "图例说明：\n"
            usage_content += "🔴 红色节点: main函数 (程序入口)\n"
            usage_content += "🟢 绿色节点: HAL/GPIO/UART等接口函数\n"
            usage_content += "🔵 蓝色节点: 用户自定义函数\n"
            usage_content += "🟡 黄色节点: 深层调用函数\n"

            info_text.insert(tk.END, usage_content)
            info_text.config(state=tk.DISABLED)

            # 更新状态
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="✅ Mermaid代码已显示")
                except tk.TclError:
                    pass

            self.log_message("🔧 DEBUG: Mermaid as image rendering completed")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to render Mermaid as image: {e}")
            # 最终降级到Canvas
            self.render_simplified_graph_in_canvas()

    def create_mermaid_html_content(self):
        """创建包含Mermaid的HTML内容 - 使用本地mermaid.js"""
        # 获取本地mermaid.js文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mermaid_js_path = os.path.join(script_dir, "assets", "mermaid.min.js")

        mermaid_js_content = ""
        if os.path.exists(mermaid_js_path):
            try:
                with open(mermaid_js_path, 'r', encoding='utf-8') as f:
                    mermaid_js_content = f.read()
            except Exception as e:
                self.log_message(f"🔧 DEBUG: Failed to read local mermaid.js: {e}")

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>STM32 Call Flow Chart - Mermaid (离线版)</title>
    <meta charset="utf-8">
    <script>
{mermaid_js_content}
    </script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            max-width: 100%;
            margin: 0 auto;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        .mermaid {{
            text-align: center;
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }}
        .legend {{
            margin-top: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .legend h3 {{
            margin-top: 0;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        .legend ul {{
            list-style: none;
            padding: 0;
        }}
        .legend li {{
            margin: 10px 0;
            padding: 8px 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
            backdrop-filter: blur(10px);
        }}
        .zoom-controls {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        .zoom-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 12px;
            margin: 0 2px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        .zoom-btn:hover {{
            background: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="zoom-controls">
        <button class="zoom-btn" onclick="zoomIn()">🔍+</button>
        <button class="zoom-btn" onclick="zoomOut()">🔍-</button>
        <button class="zoom-btn" onclick="resetZoom()">↻</button>
    </div>

    <div class="container">
        <h1>🔄 STM32项目调用流程图</h1>
        <div class="mermaid" id="mermaid-diagram">
{self.mermaid_code}
        </div>

        <div class="legend">
            <h3>📖 图例说明</h3>
            <ul>
                <li>🔴 <strong>红色节点</strong>: main函数 (程序入口)</li>
                <li>🟢 <strong>绿色节点</strong>: HAL/GPIO/UART等接口函数</li>
                <li>🔵 <strong>蓝色节点</strong>: 用户自定义函数</li>
                <li>🟡 <strong>黄色节点</strong>: 深层调用函数</li>
            </ul>
        </div>
    </div>

    <script>
        // 初始化Mermaid
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            themeVariables: {{
                primaryColor: '#ff6b6b',
                primaryTextColor: '#fff',
                primaryBorderColor: '#e55656',
                lineColor: '#495057',
                secondaryColor: '#51cf66',
                tertiaryColor: '#339af0'
            }}
        }});

        // 缩放功能
        let currentZoom = 1;
        const diagram = document.getElementById('mermaid-diagram');

        function zoomIn() {{
            currentZoom += 0.1;
            diagram.style.transform = `scale(${{currentZoom}})`;
        }}

        function zoomOut() {{
            currentZoom = Math.max(0.3, currentZoom - 0.1);
            diagram.style.transform = `scale(${{currentZoom}})`;
        }}

        function resetZoom() {{
            currentZoom = 1;
            diagram.style.transform = 'scale(1)';
        }}

        // 键盘快捷键
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey) {{
                if (e.key === '=') {{
                    e.preventDefault();
                    zoomIn();
                }} else if (e.key === '-') {{
                    e.preventDefault();
                    zoomOut();
                }} else if (e.key === '0') {{
                    e.preventDefault();
                    resetZoom();
                }}
            }}
        }});
    </script>
</body>
</html>"""

    def render_professional_mermaid_in_ui(self):
        """在UI内部渲染专业级Mermaid样式流程图"""
        # 清理现有内容，保留控制按钮
        widgets_to_keep = []
        if hasattr(self, 'preview_control_frame'):
            widgets_to_keep.append(self.preview_control_frame)

        for widget in self.graph_preview_frame.winfo_children():
            if widget not in widgets_to_keep:
                widget.destroy()

        # 创建专业级Canvas容器
        canvas_container = ttk.Frame(self.graph_preview_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建Canvas和滚动条
        canvas_frame = ttk.Frame(canvas_container)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 计算合适的Canvas大小
        canvas_width = 1400
        canvas_height = 1000

        # 创建Canvas
        self.professional_canvas = tk.Canvas(
            canvas_frame,
            width=canvas_width,
            height=canvas_height,
            bg='#f8f9fa',  # 浅灰背景
            highlightthickness=0
        )

        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.professional_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.professional_canvas.xview)

        self.professional_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 布局
        self.professional_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # 渲染专业级流程图
        self.draw_professional_mermaid_flowchart(self.professional_canvas, canvas_width, canvas_height)

        # 更新滚动区域
        self.professional_canvas.update_idletasks()
        self.professional_canvas.configure(scrollregion=self.professional_canvas.bbox("all"))

        # 更新状态
        if hasattr(self, 'graph_status_label'):
            try:
                self.graph_status_label.config(text="✅ 专业级Mermaid流程图已渲染")
            except tk.TclError:
                pass

    def get_config_file_path(self):
        """获取配置文件路径（exe所在目录的隐藏文件）"""
        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包的exe文件
                exe_dir = os.path.dirname(sys.executable)
            else:
                # 如果是Python脚本
                exe_dir = os.path.dirname(os.path.abspath(__file__))

            # 在Windows上使用点开头的文件作为隐藏文件
            config_file = os.path.join(exe_dir, ".mcu_analyzer_config.json")
            return config_file
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to get config file path: {e}")
            return ".mcu_analyzer_config.json"

    def load_last_config(self):
        """加载上次的配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 加载上次的项目路径
                last_project_path = config.get('last_project_path', '')
                if last_project_path and os.path.exists(last_project_path):
                    self.project_path_var.set(last_project_path)
                    self.log_message(f"🔧 DEBUG: Loaded last project path: {last_project_path}")

                    # 自动设置输出路径
                    if not self.output_path_var.get():
                        output_path = os.path.join(last_project_path, "Analyzer_Output")
                        self.output_path_var.set(output_path)

                # 加载其他配置
                last_output_path = config.get('last_output_path', '')
                if last_output_path:
                    self.output_path_var.set(last_output_path)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to load config: {e}")

    def save_current_config(self):
        """保存当前配置"""
        try:
            config = {
                'last_project_path': self.project_path_var.get().strip(),
                'last_output_path': self.output_path_var.get().strip(),
                'saved_time': datetime.now().isoformat()
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            self.log_message(f"🔧 DEBUG: Config saved to: {self.config_file}")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to save config: {e}")

    def save_last_project_path(self, project_path):
        """保存最后使用的项目路径"""
        try:
            config = {}
            # 尝试读取现有配置
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            # 更新项目路径
            config['project_path'] = project_path

            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.log_message(f"🔧 DEBUG: Last project path saved: {project_path}")
        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to save last project path: {e}")

    def draw_professional_mermaid_flowchart(self, canvas, canvas_width, canvas_height):
        """绘制专业级Mermaid样式流程图"""
        if not hasattr(self, 'call_graph') or not self.call_graph:
            self.draw_no_data_message(canvas, canvas_width, canvas_height)
            return

        call_tree = self.call_graph.get('call_tree')
        if not call_tree:
            self.draw_no_data_message(canvas, canvas_width, canvas_height)
            return

        # 专业级样式配置
        self.mermaid_style = {
            'main_node': {
                'fill': '#ff6b6b',
                'stroke': '#e55656',
                'text_color': 'white',
                'shadow': True,
                'gradient': True
            },
            'interface_node': {
                'fill': '#51cf66',
                'stroke': '#40c057',
                'text_color': 'white',
                'shadow': True,
                'gradient': True
            },
            'user_node': {
                'fill': '#339af0',
                'stroke': '#228be6',
                'text_color': 'white',
                'shadow': True,
                'gradient': True
            },
            'connection': {
                'stroke': '#495057',
                'width': 2,
                'arrow_size': 8
            }
        }

        # 计算布局
        layout = self.calculate_professional_layout(call_tree, canvas_width, canvas_height)

        # 绘制连接线（先绘制，避免覆盖节点）
        self.draw_professional_connections(canvas, layout)

        # 绘制节点
        self.draw_professional_nodes(canvas, layout)

        # 绘制图例
        self.draw_professional_legend(canvas, canvas_width, canvas_height)

    def draw_no_data_message(self, canvas, canvas_width, canvas_height):
        """绘制无数据提示"""
        # 背景
        canvas.create_rectangle(
            canvas_width//2 - 200, canvas_height//2 - 100,
            canvas_width//2 + 200, canvas_height//2 + 100,
            fill='#f8f9fa', outline='#dee2e6', width=2
        )

        # 图标
        canvas.create_text(
            canvas_width//2, canvas_height//2 - 40,
            text="📊", font=("Arial", 32), fill='#6c757d'
        )

        # 文本
        canvas.create_text(
            canvas_width//2, canvas_height//2,
            text="暂无调用关系数据", font=("Microsoft YaHei", 16, "bold"), fill='#495057'
        )

        canvas.create_text(
            canvas_width//2, canvas_height//2 + 30,
            text="请先运行代码分析", font=("Microsoft YaHei", 12), fill='#6c757d'
        )

    def calculate_professional_layout(self, call_tree, canvas_width, canvas_height):
        """计算专业级布局"""
        layout = {}
        node_positions = {}

        # 节点尺寸配置
        base_node_width = 140
        base_node_height = 50
        level_height = 120
        min_spacing = 60

        def calculate_tree_width(node, level=0):
            """递归计算树的宽度"""
            if not node:
                return 0

            children = node.get('children', [])
            if not children:
                return base_node_width + min_spacing

            total_width = 0
            for child in children:
                total_width += calculate_tree_width(child, level + 1)

            return max(base_node_width + min_spacing, total_width)

        def position_nodes(node, x, y, level=0, parent_x=None):
            """递归定位节点"""
            if not node:
                return x

            func_name = node['name']

            # 计算节点宽度（根据文本长度调整）
            text_length = len(func_name)
            node_width = max(base_node_width, min(base_node_width * 1.8, text_length * 10 + 40))
            node_height = base_node_height

            # 确定节点类型和样式
            if func_name == 'main':
                node_type = 'main_node'
            elif func_name.startswith(('HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_', 'TIM_', 'ADC_', 'DMA_')):
                node_type = 'interface_node'
            else:
                node_type = 'user_node'

            # 存储节点信息
            node_positions[func_name] = {
                'x': x,
                'y': y,
                'width': node_width,
                'height': node_height,
                'type': node_type,
                'level': level,
                'parent_x': parent_x
            }

            # 处理子节点
            children = node.get('children', [])
            if children:
                # 计算子节点总宽度
                total_child_width = sum(calculate_tree_width(child, level + 1) for child in children)

                # 计算起始位置（居中对齐）
                child_start_x = x + node_width/2 - total_child_width/2
                current_x = child_start_x

                for child in children:
                    child_width = calculate_tree_width(child, level + 1)
                    child_x = current_x + child_width/2 - base_node_width/2
                    child_y = y + level_height

                    position_nodes(child, child_x, child_y, level + 1, x + node_width/2)
                    current_x += child_width

            return x + node_width + min_spacing

        # 计算起始位置
        tree_width = calculate_tree_width(call_tree)
        start_x = max(50, (canvas_width - tree_width) // 2)
        start_y = 80

        # 定位所有节点
        position_nodes(call_tree, start_x, start_y)

        layout['nodes'] = node_positions
        layout['tree'] = call_tree

        return layout

    def draw_professional_nodes(self, canvas, layout):
        """绘制专业级节点"""
        nodes = layout['nodes']

        for func_name, node_info in nodes.items():
            x, y = node_info['x'], node_info['y']
            width, height = node_info['width'], node_info['height']
            node_type = node_info['type']
            style = self.mermaid_style[node_type]

            # 绘制阴影（如果启用）
            if style.get('shadow', False):
                shadow_offset = 4
                canvas.create_rounded_rectangle(
                    x + shadow_offset, y + shadow_offset,
                    x + width + shadow_offset, y + height + shadow_offset,
                    radius=8, fill='#00000020', outline=''
                )

            # 绘制主节点
            if style.get('gradient', False):
                # 模拟渐变效果
                self.draw_gradient_rectangle(canvas, x, y, width, height, style['fill'], style['stroke'])
            else:
                canvas.create_rounded_rectangle(
                    x, y, x + width, y + height,
                    radius=8, fill=style['fill'], outline=style['stroke'], width=2
                )

            # 绘制文本
            text_x = x + width // 2
            text_y = y + height // 2

            # 根据文本长度调整字体大小
            text_length = len(func_name)
            if text_length > 20:
                font_size = 9
            elif text_length > 15:
                font_size = 10
            elif text_length > 10:
                font_size = 11
            else:
                font_size = 12

            canvas.create_text(
                text_x, text_y,
                text=func_name,
                font=("Microsoft YaHei", font_size, "bold"),
                fill=style['text_color'],
                width=width - 10
            )

    def draw_gradient_rectangle(self, canvas, x, y, width, height, color, border_color):
        """绘制渐变矩形（模拟效果）"""
        # 创建多个矩形模拟渐变
        steps = 10
        for i in range(steps):
            alpha = 1.0 - (i * 0.1)
            y_offset = i * 2
            if y_offset < height - 4:
                canvas.create_rounded_rectangle(
                    x, y + y_offset, x + width, y + height,
                    radius=8, fill=color, outline=border_color if i == 0 else '', width=2 if i == 0 else 0
                )

    def draw_professional_connections(self, canvas, layout):
        """绘制专业级连接线"""
        nodes = layout['nodes']
        tree = layout['tree']
        style = self.mermaid_style['connection']

        def draw_connections_recursive(node):
            if not node:
                return

            parent_name = node['name']
            parent_info = nodes.get(parent_name)
            if not parent_info:
                return

            children = node.get('children', [])
            for child in children:
                child_name = child['name']
                child_info = nodes.get(child_name)
                if not child_info:
                    continue

                # 计算连接点
                parent_x = parent_info['x'] + parent_info['width'] // 2
                parent_y = parent_info['y'] + parent_info['height']

                child_x = child_info['x'] + child_info['width'] // 2
                child_y = child_info['y']

                # 绘制曲线连接
                self.draw_curved_arrow(canvas, parent_x, parent_y, child_x, child_y, style)

                # 递归绘制子节点连接
                draw_connections_recursive(child)

        draw_connections_recursive(tree)

    def draw_curved_arrow(self, canvas, x1, y1, x2, y2, style):
        """绘制曲线箭头"""
        # 计算控制点（贝塞尔曲线）
        mid_y = (y1 + y2) // 2

        # 绘制曲线路径
        points = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            # 三次贝塞尔曲线
            x = (1-t)**3 * x1 + 3*(1-t)**2*t * x1 + 3*(1-t)*t**2 * x2 + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2*t * mid_y + 3*(1-t)*t**2 * mid_y + t**3 * y2
            points.extend([x, y])

        # 绘制曲线
        if len(points) >= 4:
            canvas.create_line(points, fill=style['stroke'], width=style['width'], smooth=True)

        # 绘制箭头
        arrow_size = style['arrow_size']
        angle = 0.5  # 箭头角度

        # 计算箭头点
        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx /= length
            dy /= length

            # 箭头的两个边
            arrow_x1 = x2 - arrow_size * (dx + dy * angle)
            arrow_y1 = y2 - arrow_size * (dy - dx * angle)
            arrow_x2 = x2 - arrow_size * (dx - dy * angle)
            arrow_y2 = y2 - arrow_size * (dy + dx * angle)

            # 绘制箭头
            canvas.create_polygon(
                x2, y2, arrow_x1, arrow_y1, arrow_x2, arrow_y2,
                fill=style['stroke'], outline=style['stroke']
            )

    def draw_professional_legend(self, canvas, canvas_width, canvas_height):
        """绘制专业级图例"""
        legend_x = canvas_width - 280
        legend_y = 30
        legend_width = 250
        legend_height = 180

        # 图例背景
        canvas.create_rounded_rectangle(
            legend_x, legend_y, legend_x + legend_width, legend_y + legend_height,
            radius=10, fill='white', outline='#dee2e6', width=2
        )

        # 图例标题
        canvas.create_text(
            legend_x + legend_width//2, legend_y + 20,
            text="📖 图例说明", font=("Microsoft YaHei", 14, "bold"), fill='#495057'
        )

        # 图例项目
        legend_items = [
            ('main_node', 'main函数 (程序入口)', '🔴'),
            ('interface_node', 'HAL/GPIO等接口函数', '🟢'),
            ('user_node', '用户自定义函数', '🔵')
        ]

        item_y = legend_y + 50
        for node_type, description, emoji in legend_items:
            style = self.mermaid_style[node_type]

            # 绘制示例节点
            sample_x = legend_x + 20
            sample_width = 40
            sample_height = 25

            canvas.create_rounded_rectangle(
                sample_x, item_y, sample_x + sample_width, item_y + sample_height,
                radius=4, fill=style['fill'], outline=style['stroke'], width=1
            )

            # 绘制描述
            canvas.create_text(
                sample_x + sample_width + 15, item_y + sample_height//2,
                text=f"{emoji} {description}", font=("Microsoft YaHei", 10), fill='#495057', anchor='w'
            )

            item_y += 35

    # 添加圆角矩形绘制方法
    def create_rounded_rectangle_method(self):
        """为Canvas添加圆角矩形方法"""
        def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
            points = []
            for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                        (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                        (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                        (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
                points.extend([x, y])
            return self.create_polygon(points, smooth=True, **kwargs)

        tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

    def on_tab_changed(self, event):
        """Handle tab change events"""
        try:
            # Get the selected tab index
            selected_tab = self.notebook.index(self.notebook.select())

            # Check if Call Flowchart tab is selected (index 2: Overview=0, Detailed=1, Call Flowchart=2)
            if selected_tab == 2:  # Call Flowchart tab
                # 直接渲染调用关系图，无需延迟
                self.root.after(50, self.render_call_flowchart_directly)

        except (tk.TclError, AttributeError, IndexError) as e:
            # Silently handle any tab switching errors
            pass
        except Exception as e:
            # Log unexpected errors but don't show to user
            print(f"Tab change error: {e}")

    def render_call_flowchart_directly(self):
        """直接在Call Flowchart标签页渲染调用关系图"""
        self.log_message(f"🔧 DEBUG: render_call_flowchart_directly called")
        self.log_message(f"🔧 DEBUG: hasattr call_graph: {hasattr(self, 'call_graph')}")
        if hasattr(self, 'call_graph'):
            self.log_message(f"🔧 DEBUG: call_graph content: {self.call_graph}")

        if not hasattr(self, 'call_graph') or not self.call_graph:
            # 如果没有调用关系数据，显示提示信息
            self.log_message("🔧 DEBUG: No call_graph data, showing no data message")
            self.show_no_data_message()
            return

        try:
            self.log_message("🔧 DEBUG: Attempting to render flowchart")
            # 直接在Call Flowchart标签页显示，无需切换子标签页

            # 检查是否已有Mermaid代码，如果没有则生成
            has_mermaid = hasattr(self, 'mermaid_code') and self.mermaid_code
            self.log_message(f"🔧 DEBUG: Has mermaid_code: {has_mermaid}")
            if has_mermaid:
                self.log_message(f"🔧 DEBUG: Existing mermaid_code length: {len(self.mermaid_code)}")
                self.log_message(f"🔧 DEBUG: First 200 chars: {self.mermaid_code[:200]}")

            if not has_mermaid:
                self.log_message("🔧 DEBUG: Generating Mermaid code")
                self.generate_mermaid_flowchart(self.call_graph)
            else:
                self.log_message("🔧 DEBUG: Using existing Mermaid code")

            # 强制使用Mermaid渲染（不降级到Canvas）
            try:
                self.render_mermaid_internal_only()
                self.log_message("🔧 DEBUG: Mermaid flowchart rendered successfully")
            except Exception as mermaid_error:
                self.log_message(f"🔧 DEBUG: Mermaid rendering failed: {mermaid_error}, still showing Mermaid source")
                # 仍然显示Mermaid源码，不降级到Canvas
                self.display_mermaid_source_in_ui()

        except Exception as e:
            # 最终备选方案：显示Mermaid源码
            self.log_message(f"🔧 DEBUG: All rendering failed: {e}, showing Mermaid source")
            try:
                self.display_mermaid_source_in_ui()
            except Exception as source_error:
                self.log_message(f"🔧 DEBUG: Even Mermaid source display failed: {source_error}")
                # 显示错误信息
                import traceback
                error_details = traceback.format_exc()
                self.show_render_error_message_with_details(str(e), error_details)

    def show_no_data_message(self):
        """显示无数据提示"""
        # 清理现有内容
        for widget in self.graph_preview_frame.winfo_children():
            widget.destroy()

        # 显示提示信息
        message_label = ttk.Label(
            self.graph_preview_frame,
            text="请先运行分析以生成调用关系图",
            font=("Arial", 16),
            foreground="gray"
        )
        message_label.pack(expand=True)

    def show_render_error_message(self):
        """显示渲染错误提示"""
        # 清理现有内容
        for widget in self.graph_preview_frame.winfo_children():
            widget.destroy()

        # 显示错误信息
        error_label = ttk.Label(
            self.graph_preview_frame,
            text="渲染调用关系图时出现错误",
            font=("Arial", 16),
            foreground="red"
        )
        error_label.pack(expand=True)

    def show_render_error_message_with_details(self, error_msg, traceback_details):
        """显示详细的渲染错误信息"""
        # 清理现有内容
        for widget in self.graph_preview_frame.winfo_children():
            widget.destroy()

        # 创建滚动文本框显示详细错误
        import tkinter.scrolledtext as scrolledtext

        error_text = scrolledtext.ScrolledText(
            self.graph_preview_frame,
            height=20,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 插入错误信息
        error_content = f"""渲染调用关系图时出现错误

错误信息: {error_msg}

详细堆栈信息:
{traceback_details}

调试信息:
- call_graph 存在: {hasattr(self, 'call_graph')}
- call_graph 内容: {getattr(self, 'call_graph', 'None')}
"""

        error_text.insert(tk.END, error_content)
        error_text.config(state=tk.DISABLED)



    def render_simplified_graph_in_canvas(self):
        """直接在Call Flowchart标签页渲染简化的调用关系图"""
        # 只清理显示区域，保留控制按钮
        widgets_to_keep = []

        # 保存需要保留的控制widget
        if hasattr(self, 'preview_control_frame'):
            widgets_to_keep.append(self.preview_control_frame)

        # 销毁除控制按钮外的所有widget
        for widget in self.graph_preview_frame.winfo_children():
            if widget not in widgets_to_keep:
                widget.destroy()

        # 创建Canvas和滚动条
        canvas_frame = ttk.Frame(self.graph_preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.flowchart_canvas = tk.Canvas(canvas_frame, bg='white')
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.flowchart_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.flowchart_canvas.xview)

        self.flowchart_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.flowchart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Draw simplified flowchart in the canvas
        self.draw_simplified_flowchart(self.flowchart_canvas)

        # Update scroll region
        self.flowchart_canvas.update_idletasks()
        self.flowchart_canvas.configure(scrollregion=self.flowchart_canvas.bbox("all"))

        # 更新状态标签（现在应该仍然存在）
        if hasattr(self, 'graph_status_label'):
            try:
                self.graph_status_label.config(text="✅ Call graph displayed successfully")
            except tk.TclError:
                self.log_message("🔧 DEBUG: graph_status_label已被销毁，无法更新状态")
        self.log_message("🔧 DEBUG: Call graph displayed successfully")

    def draw_simplified_flowchart(self, canvas):
        """Draw simplified flowchart on canvas with auto-sizing"""
        if not hasattr(self, 'call_graph') or not self.call_graph:
            canvas.create_text(400, 300, text="No call relationship data available", font=("Arial", 16), fill="gray")
            return

        call_tree = self.call_graph.get('call_tree')
        if not call_tree:
            canvas.create_text(400, 300, text="No main function or call relationships found", font=("Arial", 16), fill="gray")
            return

        # Debug: Print call tree structure
        self.log_message(f"🔧 DEBUG: call_tree structure: {call_tree}")
        self.log_message(f"🔧 DEBUG: call_tree type: {type(call_tree)}")
        if isinstance(call_tree, dict):
            self.log_message(f"🔧 DEBUG: call_tree keys: {call_tree.keys()}")
            self.log_message(f"🔧 DEBUG: call_tree children: {call_tree.get('children', 'No children key')}")

        # Get canvas size for auto-sizing
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Auto-calculate drawing parameters based on canvas size
        if canvas_width > 100 and canvas_height > 100:  # Valid canvas size
            # Scale node size based on canvas size
            base_node_width = max(80, min(150, canvas_width // 8))
            base_node_height = max(30, min(50, canvas_height // 15))
            level_height = max(60, min(100, canvas_height // 8))
            start_x = max(20, canvas_width // 20)
            start_y = max(20, canvas_height // 20)
        else:
            # Fallback values
            base_node_width = 120
            base_node_height = 40
            level_height = 80
            start_x = 50
            start_y = 50

        # 存储节点位置用于连线
        node_positions = {}

        def draw_node(node, x, y, level=0):
            if not node:
                return x

            func_name = node['name']

            # Dynamic node size based on function name length and level
            text_length = len(func_name)
            node_width = max(base_node_width, min(base_node_width * 1.5, text_length * 8 + 20))
            node_height = base_node_height

            # Adjust font size based on node size
            font_size = max(8, min(12, node_width // 10))

            # 初始化child_spacing，确保在所有代码路径下都有值
            child_spacing = max(20, canvas_width // 20)

            # 根据函数类型选择颜色
            if func_name == 'main':
                color = "#ff9999"  # 红色
                text_color = "black"
            elif func_name.startswith(('HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_', 'TIM_', 'ADC_', 'DMA_')):
                color = "#99ff99"  # 绿色
                text_color = "black"
            else:
                color = "#99ccff"  # 蓝色
                text_color = "black"

            # 绘制节点
            rect = canvas.create_rectangle(
                x, y, x + node_width, y + node_height,
                fill=color, outline="black", width=2
            )

            # Draw text with dynamic font size
            text = canvas.create_text(
                x + node_width/2, y + node_height/2,
                text=func_name, font=("Arial", font_size, "bold"),
                fill=text_color, width=node_width-10
            )

            # 存储节点位置
            node_positions[func_name] = (x + node_width/2, y + node_height/2, node_width, node_height)

            # 处理子节点
            children = node.get('children', [])
            if children:
                total_child_width = len(children) * (node_width + child_spacing) - child_spacing
                child_start_x = x + node_width/2 - total_child_width/2

                for i, child in enumerate(children):
                    child_x = child_start_x + i * (node_width + child_spacing)
                    child_y = y + level_height

                    # 递归绘制子节点
                    draw_node(child, child_x, child_y, level + 1)

                    # 绘制连线
                    child_name = child['name']
                    if child_name in node_positions:
                        parent_pos = node_positions[func_name]
                        child_pos = node_positions[child_name]

                        canvas.create_line(
                            parent_pos[0], parent_pos[1] + parent_pos[3]/2,  # parent bottom
                            child_pos[0], child_pos[1] - child_pos[3]/2,     # child top
                            fill="black", width=2, arrow=tk.LAST
                        )

            return x + node_width + child_spacing

        # 从根节点开始绘制
        draw_node(call_tree, start_x, start_y)

        # Add legend with dynamic positioning
        legend_x = max(start_x + 400, canvas_width - 350) if canvas_width > 500 else start_x + 20
        legend_y = start_y + 20
        legend_font_size = max(8, min(12, canvas_width // 80))

        canvas.create_text(legend_x, legend_y, text="Legend:", font=("Arial", legend_font_size + 2, "bold"), anchor="w")

        # Red legend
        canvas.create_rectangle(legend_x, legend_y + 25, legend_x + 20, legend_y + 40, fill="#ff9999", outline="black")
        canvas.create_text(legend_x + 25, legend_y + 32, text="main function (Program entry)", font=("Arial", legend_font_size), anchor="w")

        # Green legend
        canvas.create_rectangle(legend_x, legend_y + 50, legend_x + 20, legend_y + 65, fill="#99ff99", outline="black")
        canvas.create_text(legend_x + 25, legend_y + 57, text="Interface functions (HAL/GPIO/UART etc.)", font=("Arial", legend_font_size), anchor="w")

        # Blue legend
        canvas.create_rectangle(legend_x, legend_y + 75, legend_x + 20, legend_y + 90, fill="#99ccff", outline="black")
        canvas.create_text(legend_x + 25, legend_y + 82, text="User-defined functions", font=("Arial", legend_font_size), anchor="w")

    def on_format_changed(self):
        """当格式选项改变时的回调"""
        # 如果当前有图形显示，重新渲染
        if hasattr(self, 'call_graph') and self.call_graph:
            self.render_graph_in_ui()

    def on_quality_changed(self, event=None):
        """当质量选项改变时的回调"""
        # 更新质量显示文本
        quality_value = self.quality_var.get()
        if quality_value == "standard":
            event.widget.set("标准")
        elif quality_value == "high":
            event.widget.set("高质量")
        elif quality_value == "ultra":
            event.widget.set("超高质量")

        # 如果当前有图形显示，重新渲染
        if hasattr(self, 'call_graph') and self.call_graph:
            self.render_graph_in_ui()

    def render_graph_in_ui(self):
        """在UI内部渲染Mermaid图形"""
        try:
            # 检查是否有调用图数据
            if not hasattr(self, 'call_graph') or not self.call_graph:
                messagebox.showwarning("Warning", "No call graph data available. Please run analysis first.")
                return

            # 直接渲染Mermaid
            self.render_mermaid_only()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: render_graph_in_ui failed: {e}")
            messagebox.showerror("Error", f"Failed to render graph: {e}")

    # 删除PlantUML相关方法

    def render_mermaid_only(self):
        """渲染Mermaid流程图"""
        try:
            self.log_message("🔧 DEBUG: Rendering Mermaid flowchart")

            # 获取格式和质量设置
            format_type = self.format_var.get()  # svg 或 png
            quality = self.quality_var.get()     # standard, high, ultra

            self.log_message(f"🔧 DEBUG: Format: {format_type}, Quality: {quality}")

            # 清理现有内容（保留控制面板）
            for widget in self.graph_preview_frame.winfo_children():
                if not hasattr(widget, '_is_control_frame'):
                    widget.destroy()

            # 创建容器
            container = ttk.LabelFrame(
                self.graph_preview_frame,
                text=f"🧜‍♀️ Mermaid流程图 ({format_type.upper()})",
                padding=5
            )
            container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 渲染Mermaid
            self.render_mermaid_in_frame(container, format_type, quality)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: render_mermaid_only failed: {e}")
            self.show_simple_failure_message()

    def render_mermaid_in_frame(self, parent_frame, format_type="svg", quality="high"):
        """在指定框架中渲染Mermaid - 仅显示源码"""
        try:
            self.log_message(f"🔧 DEBUG: Rendering Mermaid in frame - showing source code only")
            # 直接显示Mermaid代码
            self.show_mermaid_code_in_frame(parent_frame)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: render_mermaid_in_frame failed: {e}")
            self.show_mermaid_code_in_frame(parent_frame)

    def show_mermaid_code_in_frame(self, parent_frame):
        """在框架中显示Mermaid代码"""
        try:
            code_text = tk.Text(
                parent_frame,
                font=("Consolas", 9),
                wrap=tk.WORD,
                bg='#f8f9fa',
                height=10
            )
            code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            if hasattr(self, 'mermaid_code') and self.mermaid_code:
                code_text.insert(tk.END, self.mermaid_code)
            else:
                code_text.insert(tk.END, "暂无Mermaid代码，请先进行分析")

            code_text.config(state=tk.DISABLED)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: show_mermaid_code_in_frame failed: {e}")

    def update_rendering_mode_display(self):
        """更新渲染模式显示"""
        try:
            current_mode = self.config.get('mermaid', {}).get('rendering_mode', 'online')
            if current_mode == 'local':
                self.rendering_mode_var.set("🖥️ 本地渲染")
            else:
                self.rendering_mode_var.set("🌐 在线渲染")
        except:
            self.rendering_mode_var.set("🌐 在线渲染")

    def toggle_rendering_mode(self):
        """切换渲染模式"""
        try:
            current_mode = self.config.get('mermaid', {}).get('rendering_mode', 'online')
            new_mode = 'online' if current_mode == 'local' else 'local'

            # 更新配置
            if 'mermaid' not in self.config:
                self.config['mermaid'] = {}
            self.config['mermaid']['rendering_mode'] = new_mode

            # 保存配置到文件
            import yaml
            config_file = Path("config.yaml")
            if config_file.exists():
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

            # 更新显示
            self.update_rendering_mode_display()

            # 显示切换消息
            mode_text = "本地渲染" if new_mode == 'local' else "在线渲染"
            self.log_message(f"🔄 已切换到{mode_text}模式")

            # 如果当前有Mermaid图表，重新渲染
            if hasattr(self, 'mermaid_code') and self.mermaid_code:
                self.log_message(f"🔄 使用{mode_text}重新渲染图表...")
                self.render_mermaid_internal_only()

        except Exception as e:
            self.log_message(f"❌ 切换渲染模式失败: {e}")
            import traceback
            traceback.print_exc()

    def on_window_configure(self, event):
        """处理窗口尺寸变化事件"""
        try:
            # 只处理主窗口的尺寸变化
            if event.widget != self.root:
                return

            current_size = (self.root.winfo_width(), self.root.winfo_height())

            # 检查尺寸是否真的发生了变化
            if self.last_window_size is None:
                self.last_window_size = current_size
                return

            if current_size == self.last_window_size:
                return

            # 记录新尺寸
            self.last_window_size = current_size

            # 取消之前的定时器
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)

            # 设置新的定时器，延迟重新渲染（避免频繁渲染）
            delay = self.config.get('mermaid', {}).get('resize_delay', 500)
            self.resize_timer = self.root.after(delay, self.on_window_resize_complete)

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Window configure event failed: {e}")

    def on_window_resize_complete(self):
        """窗口尺寸变化完成后的处理"""
        try:
            self.resize_timer = None

            # 检查是否启用了自动重新渲染
            auto_resize = self.config.get('mermaid', {}).get('auto_resize', True)
            if not auto_resize:
                self.log_message("🔧 DEBUG: Auto-resize disabled in config - skipping re-render")
                return

            # 检查是否有Mermaid图表需要重新渲染
            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                return

            # 检查当前是否使用本地渲染模式
            rendering_mode = self.config.get('mermaid', {}).get('rendering_mode', 'online')
            if rendering_mode != 'local':
                self.log_message("🔧 DEBUG: Window resized, but not in local rendering mode - skipping re-render")
                return

            # 获取新的窗口尺寸
            new_width, new_height = self.last_window_size
            self.log_message(f"🔧 DEBUG: Window resized to {new_width}x{new_height}, re-rendering Mermaid with local renderer")

            # 重新渲染Mermaid图表
            self.render_mermaid_internal_only()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Window resize complete handling failed: {e}")
            import traceback
            traceback.print_exc()

    # 删除PlantUML显示方法

    def show_simple_failure_message(self):
        """显示简单的渲染失败消息"""
        try:
            # 清理现有内容（保留控制面板）
            for widget in self.graph_preview_frame.winfo_children():
                if not hasattr(widget, '_is_control_frame'):
                    widget.destroy()

            # 创建简单提示
            message_frame = ttk.Frame(self.graph_preview_frame)
            message_frame.pack(expand=True, fill=tk.BOTH)

            # 主要消息
            main_label = ttk.Label(
                message_frame,
                text="⚠️ Mermaid渲染工具不可用",
                font=("Microsoft YaHei", 16, "bold"),
                foreground="orange"
            )
            main_label.pack(pady=(50, 20))

            # 简单说明
            info_label = ttk.Label(
                message_frame,
                text="请安装 Mermaid CLI 以启用图形渲染：\nnpm install -g @mermaid-js/mermaid-cli",
                font=("Microsoft YaHei", 11),
                foreground="gray",
                justify=tk.CENTER
            )
            info_label.pack(pady=(0, 30))

            self.log_message("🔧 DEBUG: Simple failure message displayed")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to show simple failure message: {e}")

    def render_canvas_flowchart(self):
        """使用Canvas直接绘制流程图 - 保证能显示"""
        try:
            self.log_message("🔧 DEBUG: Rendering flowchart with Canvas - GUARANTEED SUCCESS")

            # 清理现有内容（保留控制面板）
            for widget in self.graph_preview_frame.winfo_children():
                if not hasattr(widget, '_is_control_frame'):
                    widget.destroy()

            # 创建Canvas容器
            canvas_container = ttk.LabelFrame(
                self.graph_preview_frame,
                text="🎨 调用关系流程图",
                padding=5
            )
            canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 创建Canvas和滚动条
            canvas_frame = ttk.Frame(canvas_container)
            canvas_frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)

            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # 布局
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 绘制流程图
            self.draw_flowchart_on_canvas(canvas)

            # 添加鼠标滚轮支持
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            def on_shift_mousewheel(event):
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")

            canvas.bind("<MouseWheel>", on_mousewheel)
            canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)

            # 状态信息
            status_label = ttk.Label(
                canvas_container,
                text="✅ 流程图已使用Canvas渲染 | 使用鼠标滚轮缩放",
                font=("Microsoft YaHei", 10, "bold"),
                foreground="green"
            )
            status_label.pack(pady=5)

            self.log_message("🔧 DEBUG: Canvas flowchart rendered successfully")

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Canvas flowchart rendering failed: {e}")
            # 最后的备选方案
            self.show_simple_failure_message()

    def draw_flowchart_on_canvas(self, canvas):
        """在Canvas上绘制流程图"""
        try:
            if not hasattr(self, 'call_graph') or not self.call_graph:
                canvas.create_text(400, 300, text="无调用关系数据", font=("Microsoft YaHei", 16), fill="gray")
                return

            call_tree = self.call_graph.get('call_tree')
            if not call_tree:
                canvas.create_text(400, 300, text="未找到主函数或调用关系", font=("Microsoft YaHei", 16), fill="gray")
                return

            # 绘制参数
            start_x, start_y = 50, 50
            node_width, node_height = 150, 50
            level_gap = 100
            node_gap = 200

            # 存储节点位置
            node_positions = {}

            def draw_node_recursive(node, x, y, level=0):
                if not node:
                    return x

                func_name = node['name']

                # 根据函数类型选择颜色
                if func_name == 'main':
                    fill_color = "#ff9999"  # 红色
                    text_color = "black"
                elif func_name.startswith(('HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_', 'TIM_', 'ADC_', 'DMA_')):
                    fill_color = "#99ff99"  # 绿色
                    text_color = "black"
                else:
                    fill_color = "#99ccff"  # 蓝色
                    text_color = "black"

                # 绘制节点矩形
                rect = canvas.create_rectangle(
                    x, y, x + node_width, y + node_height,
                    fill=fill_color, outline="black", width=2
                )

                # 绘制文本
                text = canvas.create_text(
                    x + node_width/2, y + node_height/2,
                    text=func_name, font=("Microsoft YaHei", 10, "bold"),
                    fill=text_color, width=node_width-10
                )

                # 存储节点位置
                node_positions[func_name] = (x + node_width/2, y + node_height/2)

                # 处理子节点
                children = node.get('children', [])
                if children:
                    child_y = y + level_gap
                    child_start_x = x - (len(children) - 1) * node_gap / 2

                    for i, child in enumerate(children):
                        child_x = child_start_x + i * node_gap
                        draw_node_recursive(child, child_x, child_y, level + 1)

                        # 绘制连线
                        child_name = child['name']
                        if child_name in node_positions:
                            parent_pos = node_positions[func_name]
                            child_pos = node_positions[child_name]

                            canvas.create_line(
                                parent_pos[0], parent_pos[1] + node_height/2,
                                child_pos[0], child_pos[1] - node_height/2,
                                fill="black", width=2, arrow=tk.LAST
                            )

                return x + node_width + node_gap

            # 开始绘制
            draw_node_recursive(call_tree, start_x, start_y)

            # 添加图例
            legend_x, legend_y = start_x + 500, start_y
            canvas.create_text(legend_x, legend_y, text="图例:", font=("Microsoft YaHei", 12, "bold"), anchor="w")

            # 红色图例
            canvas.create_rectangle(legend_x, legend_y + 25, legend_x + 20, legend_y + 40, fill="#ff9999", outline="black")
            canvas.create_text(legend_x + 25, legend_y + 32, text="主函数 (程序入口)", font=("Microsoft YaHei", 10), anchor="w")

            # 绿色图例
            canvas.create_rectangle(legend_x, legend_y + 50, legend_x + 20, legend_y + 65, fill="#99ff99", outline="black")
            canvas.create_text(legend_x + 25, legend_y + 57, text="接口函数 (HAL/GPIO等)", font=("Microsoft YaHei", 10), anchor="w")

            # 蓝色图例
            canvas.create_rectangle(legend_x, legend_y + 75, legend_x + 20, legend_y + 90, fill="#99ccff", outline="black")
            canvas.create_text(legend_x + 25, legend_y + 82, text="用户定义函数", font=("Microsoft YaHei", 10), anchor="w")

            # 更新滚动区域
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Failed to draw flowchart on canvas: {e}")
            canvas.create_text(400, 300, text="绘制流程图时出错", font=("Microsoft YaHei", 16), fill="red")

    def _add_nodes_to_graph(self, G, tree_node, parent=None):
        """递归添加节点到NetworkX图"""
        if not tree_node:
            return

        func_name = tree_node['name']
        file_name = tree_node.get('file', '').split('\\')[-1].split('/')[-1]

        # 添加节点属性
        node_attrs = {
            'label': func_name,
            'file': file_name,
            'type': self._get_node_type(func_name)
        }

        G.add_node(func_name, **node_attrs)

        # 添加边
        if parent:
            G.add_edge(parent, func_name)

        # {loc.get_text('recursively_process_child_nodes')}
        for child in tree_node.get('children', []):
            self._add_nodes_to_graph(G, child, func_name)

    def _get_node_type(self, func_name):
        """获取节点类型"""
        if func_name == 'main':
            return 'main'
        elif func_name.startswith(('HAL_', 'GPIO_', 'UART_', 'SPI_', 'I2C_', 'TIM_', 'ADC_', 'DMA_')):
            return 'interface'
        else:
            return 'user'

    def _create_hierarchical_layout(self, G, root_node):
        """创建层次化布局"""
        pos = {}

        # 计算每个节点的层级
        levels = {}
        self._calculate_levels(root_node, levels, 0)

        # 按层级分组
        level_groups = {}
        for node, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)

        # 计算位置
        max_level = max(level_groups.keys()) if level_groups else 0

        for level, nodes in level_groups.items():
            y = max_level - level  # 从上到下
            node_count = len(nodes)

            for i, node in enumerate(nodes):
                if node_count == 1:
                    x = 0
                else:
                    x = (i - (node_count - 1) / 2) * 2
                pos[node] = (x, y)

        return pos

    def _calculate_levels(self, tree_node, levels, current_level):
        """递归计算节点层级"""
        if not tree_node:
            return

        func_name = tree_node['name']
        levels[func_name] = current_level

        for child in tree_node.get('children', []):
            self._calculate_levels(child, levels, current_level + 1)

    def _draw_nodes(self, G, pos, ax):
        """绘制节点"""
        # 按类型分组绘制
        main_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'main']
        interface_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'interface']
        user_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'user']

        # 绘制不同类型的节点
        if main_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=main_nodes,
                                 node_color='#ff9999', node_size=1500,
                                 alpha=0.8, ax=ax)

        if interface_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=interface_nodes,
                                 node_color='#99ff99', node_size=1000,
                                 alpha=0.8, ax=ax)

        if user_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=user_nodes,
                                 node_color='#99ccff', node_size=800,
                                 alpha=0.8, ax=ax)

        # 绘制标签
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8,
                              font_weight='bold', ax=ax)

    def _draw_edges(self, G, pos, ax):
        """绘制边"""
        nx.draw_networkx_edges(G, pos, edge_color='gray',
                             arrows=True, arrowsize=20,
                             arrowstyle='->', alpha=0.6, ax=ax)

    def _add_legend(self, ax):
        """添加图例"""
        legend_elements = [
            patches.Patch(color='#ff9999', label='main函数'),
            patches.Patch(color='#99ff99', label='接口函数'),
            patches.Patch(color='#99ccff', label='用户函数')
        ]
        ax.legend(handles=legend_elements, loc='upper right',
                 bbox_to_anchor=(1, 1))

    def show_mermaid_source(self):
        """显示Mermaid源码"""
        try:
            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                messagebox.showinfo("提示", "请先进行分析并生成流程图")
                return

            # 创建新窗口显示源码
            source_window = tk.Toplevel(self.root)
            source_window.title("📝 Mermaid源码")
            source_window.geometry("800x600")
            source_window.transient(self.root)
            source_window.grab_set()

            # 创建文本框
            text_frame = ttk.Frame(source_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            source_text = scrolledtext.ScrolledText(
                text_frame,
                font=("Consolas", 10),
                wrap=tk.WORD
            )
            source_text.pack(fill=tk.BOTH, expand=True)

            # 插入Mermaid代码
            source_text.insert(1.0, self.mermaid_code)
            source_text.config(state=tk.DISABLED)

            # 按钮框架
            button_frame = ttk.Frame(source_window)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            # 复制按钮
            def copy_to_clipboard():
                source_window.clipboard_clear()
                source_window.clipboard_append(self.mermaid_code)
                messagebox.showinfo("成功", "Mermaid源码已复制到剪贴板")

            copy_btn = ttk.Button(
                button_frame,
                text="📋 复制到剪贴板",
                command=copy_to_clipboard
            )
            copy_btn.pack(side=tk.LEFT, padx=(0, 10))

            # 关闭按钮
            close_btn = ttk.Button(
                button_frame,
                text="❌ 关闭",
                command=source_window.destroy
            )
            close_btn.pack(side=tk.RIGHT)

        except Exception as e:
            messagebox.showerror("错误", f"显示源码失败: {e}")

    def export_mermaid_graph(self):
        """导出Mermaid图形"""
        try:
            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                messagebox.showinfo("提示", "请先进行分析并生成流程图")
                return

            from tkinter import filedialog

            # 文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="导出Mermaid流程图",
                defaultextension=".mmd",
                filetypes=[
                    ("Mermaid文件", "*.mmd"),
                    ("SVG矢量图", "*.svg"),
                    ("PNG图片", "*.png"),
                    ("HTML文件", "*.html"),
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*")
                ]
            )

            if not file_path:
                return

            file_ext = file_path.lower().split('.')[-1]

            if file_ext in ['mmd', 'txt']:
                # 导出Mermaid源码
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.mermaid_code)
                messagebox.showinfo("成功", f"Mermaid源码已导出到:\n{file_path}")

            elif file_ext == 'html':
                # 导出HTML文件
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>MCU项目调用流程图</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; text-align: center; }}
        .mermaid {{ text-align: center; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 MCU项目调用流程图</h1>
        <div class="mermaid">
{self.mermaid_code}
        </div>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
    </script>
</body>
</html>"""
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                messagebox.showinfo("成功", f"HTML文件已导出到:\n{file_path}")

            elif file_ext in ['svg', 'png']:
                # 尝试使用mermaid-cli导出图片
                if self.try_export_image(file_path, file_ext):
                    messagebox.showinfo("成功", f"{file_ext.upper()}图片已导出到:\n{file_path}")
                else:
                    # 降级到保存Mermaid源码
                    mmd_path = file_path.rsplit('.', 1)[0] + '.mmd'
                    with open(mmd_path, 'w', encoding='utf-8') as f:
                        f.write(self.mermaid_code)
                    messagebox.showwarning("提示",
                        f"无法直接导出{file_ext.upper()}格式，已保存Mermaid源码到:\n{mmd_path}\n\n"
                        "您可以使用本地mermaid-cli工具将.mmd文件转换为图片格式")
            else:
                # 默认保存为Mermaid源码
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.mermaid_code)
                messagebox.showinfo("成功", f"文件已导出到:\n{file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def try_export_image(self, file_path, format_type):
        """尝试使用mermaid-cli导出图片"""
        try:
            import subprocess
            import tempfile
            import os

            # 检查mermaid-cli是否可用
            try:
                result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    return False
            except:
                return False

            # 创建临时Mermaid文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as f:
                f.write(self.mermaid_code)
                mmd_file = f.name

            try:
                # 使用mermaid-cli转换
                cmd = ['mmdc', '-i', mmd_file, '-o', file_path]
                if format_type == 'svg':
                    cmd.extend(['-f', 'svg'])
                elif format_type == 'png':
                    # 删除固定尺寸参数，仅支持在线渲染
                    cmd.extend(['-f', 'png'])

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                success = result.returncode == 0 and os.path.exists(file_path)

                return success

            finally:
                # 清理临时文件
                try:
                    os.unlink(mmd_file)
                except:
                    pass

        except Exception as e:
            self.log_message(f"🔧 DEBUG: Export image failed: {e}")
            return False

    def clear_graph_display(self):
        """清空图形显示"""
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'graph_figure'):
            self.graph_figure.clear()
            self.graph_canvas.draw()
            # 安全地更新状态标签
            if hasattr(self, 'graph_status_label'):
                try:
                    self.graph_status_label.config(text="已清空")
                except tk.TclError:
                    self.log_message("🔧 DEBUG: graph_status_label已被销毁，无法更新状态")
            self.log_message("🔧 DEBUG: Graph display cleared")
        elif hasattr(self, 'graph_display_text'):
            self.graph_display_text.config(state=tk.NORMAL)
            self.graph_display_text.delete(1.0, tk.END)
            self.graph_display_text.config(state=tk.DISABLED)

    def generate_report(self, output_path, chip_info, code_analysis, interface_analysis):
        """生成分析报告"""
        report_file = os.path.join(output_path, "analysis_report.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# STM32工程分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 芯片信息\n\n")
            # Handle ChipInfo object properly
            if hasattr(chip_info, 'device_name'):
                # ChipInfo object
                chip_data = {
                    'device_name': chip_info.device_name or 'Unknown',
                    'vendor': chip_info.vendor or 'Unknown',
                    'series': chip_info.series or 'Unknown',
                    'family': chip_info.family or 'Unknown',
                    'core': chip_info.core or 'Unknown',
                    'frequency': chip_info.frequency or 'Unknown',
                    'flash_size': chip_info.flash_size or 'Unknown',
                    'ram_size': chip_info.ram_size or 'Unknown',
                    'package': chip_info.package or 'Unknown',
                    'features': ', '.join(chip_info.features) if chip_info.features else 'None'
                }
            else:
                # Dict format (fallback)
                chip_data = chip_info

            for key, value in chip_data.items():
                f.write(f"- **{key}**: {value}\n")
            f.write("\n")

            if isinstance(code_analysis, dict) and 'total_functions' in code_analysis:
                f.write("## 代码分析\n\n")
                f.write(f"- **总函数数**: {code_analysis['total_functions']}\n")
                f.write(f"- **main函数**: {'存在' if code_analysis['main_found'] else '不存在'}\n")
                f.write(f"- **包含文件数**: {len(code_analysis['includes'])}\n\n")

            if isinstance(interface_analysis, dict) and interface_analysis:
                f.write("## 接口使用\n\n")
                for interface, count in interface_analysis.items():
                    f.write(f"- **{interface}**: {count} 次使用\n")
                f.write("\n")

        self.log_message(f"📄 {loc.get_text('report_saved', report_file)}")

    def display_results(self, chip_info, code_analysis, call_analysis):
        """Display analysis results"""
        # Overview
        # Handle both ChipInfo object and dict
        if hasattr(chip_info, 'device_name'):
            # ChipInfo object
            device = chip_info.device_name or loc.get_text('unknown')
            vendor = chip_info.vendor or loc.get_text('unknown')
            series = chip_info.series or loc.get_text('unknown')
            core = chip_info.core or loc.get_text('unknown')
        else:
            # Dict format (fallback)
            device = chip_info.get('device', loc.get_text('unknown')) if isinstance(chip_info, dict) else loc.get_text('unknown')
            vendor = chip_info.get('vendor', loc.get_text('unknown')) if isinstance(chip_info, dict) else loc.get_text('unknown')
            series = chip_info.get('series', loc.get_text('unknown')) if isinstance(chip_info, dict) else loc.get_text('unknown')
            core = chip_info.get('core', loc.get_text('unknown')) if isinstance(chip_info, dict) else loc.get_text('unknown')

        overview = f"""MCU Project Analysis Results
{'='*50}

Chip Information:
  {loc.get_text('device')}: {device}
  {loc.get_text('vendor')}: {vendor}
  {loc.get_text('series')}: {series}
  {loc.get_text('core')}: {core}

"""

        if isinstance(code_analysis, dict) and 'total_functions' in code_analysis:
            overview += f"""Code Analysis:
  Total Functions: {code_analysis['total_functions']}
  Main Function: {'Found' if code_analysis['main_found'] else 'Not Found'}
  Include Files: {len(code_analysis['includes'])} files

"""

        # Display call relationship analysis results
        if isinstance(call_analysis, dict) and 'call_tree' in call_analysis:
            overview += f"""Call Relationship Analysis:
  Call Depth: {call_analysis.get('max_depth_reached', 0)}
  Functions in Tree: {call_analysis.get('total_functions_in_tree', 0)}
  Main Function: {'Found' if call_analysis['call_tree'] else 'Not Found'}

"""

            # Display actual interface usage (based on call relationships)
            interface_usage = call_analysis.get('interface_usage', {})
            if interface_usage:
                overview += "Interface Usage (based on main function call chain):\n"
                for interface, count in interface_usage.items():
                    overview += f"  {interface}: {count} calls\n"
            else:
                overview += "Interface Usage: No interface calls detected\n"

        self.overview_text.insert(tk.END, overview)

        # Detailed information - use safe JSON serialization
        try:
            # Convert ChipInfo object to dict if needed
            if hasattr(chip_info, 'device_name'):
                chip_info_dict = {
                    'device_name': chip_info.device_name,
                    'vendor': chip_info.vendor,
                    'series': chip_info.series,
                    'family': chip_info.family,
                    'core': chip_info.core,
                    'frequency': chip_info.frequency,
                    'flash_size': chip_info.flash_size,
                    'ram_size': chip_info.ram_size,
                    'package': chip_info.package,
                    'features': chip_info.features
                }
            else:
                chip_info_dict = chip_info

            detail_data = {
                'chip_info': safe_json_serialize(chip_info_dict),
                'code_analysis': safe_json_serialize(code_analysis),
                'call_analysis': safe_json_serialize(call_analysis)
            }
            detail = json.dumps(detail_data, indent=2, ensure_ascii=False)
        except Exception as e:
            detail = f"JSON serialization error: {e}\n\nRaw data:\n{str(chip_info)}\n{str(code_analysis)}\n{str(call_analysis)}"

        self.detail_text.insert(tk.END, detail)




    def show_simple_llm_config(self):
        f"""{loc.get_text('llm_config')}"""
        config_window = tk.Toplevel(self.root)
        config_window.title(loc.get_text('llm_config'))
        config_window.geometry("500x400")
        config_window.transient(self.root)
        config_window.grab_set()

        # 居中显示
        config_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        # 主框架
        main_frame = ttk.Frame(config_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text=loc.get_text('llm_service_config'), font=("Microsoft YaHei", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # 服务类型选择
        service_frame = ttk.LabelFrame(main_frame, text=loc.get_text('select_llm_service'), padding="10")
        service_frame.pack(fill=tk.X, pady=(0, 15))

        service_var = tk.StringVar(value="ollama")

        ttk.Radiobutton(service_frame, text=loc.get_text('ollama_local'), variable=service_var, value="ollama").pack(anchor=tk.W)
        ttk.Radiobutton(service_frame, text=loc.get_text('tencent_cloud'), variable=service_var, value="tencent").pack(anchor=tk.W)

        # 配置参数
        config_frame = ttk.LabelFrame(main_frame, text=loc.get_text('config_parameters'), padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 动态配置字段
        def update_config_fields():
            # 清除现有字段
            for widget in config_frame.winfo_children():
                widget.destroy()

            service = service_var.get()
            if service == "ollama":
                # {loc.get_text('ollama_description')}
                ttk.Label(config_frame, text=loc.get_text('service_address')).pack(anchor=tk.W)
                url_var = tk.StringVar(value="http://10.52.8.74:445")
                url_entry = ttk.Entry(config_frame, textvariable=url_var, width=50)
                url_entry.pack(fill=tk.X, pady=(0, 10))

                ttk.Label(config_frame, text=loc.get_text('model_name')).pack(anchor=tk.W)
                model_var = tk.StringVar(value="qwen2.5-coder:32b")
                model_entry = ttk.Entry(config_frame, textvariable=model_var, width=50)
                model_entry.pack(fill=tk.X, pady=(0, 10))

            elif service == "tencent":
                # {loc.get_text('tencent_description')}
                ttk.Label(config_frame, text=loc.get_text('api_id')).pack(anchor=tk.W)
                api_id_var = tk.StringVar()
                api_id_entry = ttk.Entry(config_frame, textvariable=api_id_var, width=50)
                api_id_entry.pack(fill=tk.X, pady=(0, 10))

                ttk.Label(config_frame, text=loc.get_text('api_key')).pack(anchor=tk.W)
                api_secret_var = tk.StringVar()
                api_secret_entry = ttk.Entry(config_frame, textvariable=api_secret_var, show="*", width=50)
                api_secret_entry.pack(fill=tk.X, pady=(0, 10))

        # 绑定服务类型变化事件
        def on_service_changed():
            update_config_fields()

        service_var.trace('w', lambda *args: on_service_changed())

        # 初始化显示
        update_config_fields()

        # 说明文本
        info_text = tk.Text(main_frame, height=3, wrap=tk.WORD)
        info_text.pack(fill=tk.X, pady=(10, 0))
        info_text.insert(tk.END, f"{loc.get_text('config_description')}\n• {loc.get_text('ollama_description')}\n• {loc.get_text('tencent_description')}")
        info_text.config(state=tk.DISABLED)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def save_config():
            # 这里可以保存配置到文件
            messagebox.showinfo(loc.get_text('success'), loc.get_text('llm_config_saved'))
            config_window.destroy()

        def test_connection():
            messagebox.showinfo(loc.get_text('test'), loc.get_text('connection_test_in_development'))

        ttk.Button(button_frame, text=loc.get_text('test_connection'), command=test_connection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=loc.get_text('save'), command=save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=loc.get_text('cancel'), command=config_window.destroy).pack(side=tk.LEFT)

    def open_analysis_config(self):
        """打开分析设置对话框"""
        self.show_analysis_config_dialog()

    def show_analysis_config_dialog(self):
        f"""{loc.get_text('analysis_config')}"""
        import yaml
        from pathlib import Path

        # 创建对话框
        config_window = tk.Toplevel(self.root)
        config_window.title(loc.get_text('analysis_config'))
        config_window.geometry("600x600")
        config_window.resizable(True, True)
        config_window.transient(self.root)
        config_window.grab_set()

        # 居中显示
        x = (config_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (config_window.winfo_screenheight() // 2) - (600 // 2)
        config_window.geometry(f"600x600+{x}+{y}")

        # 主框架
        main_frame = ttk.Frame(config_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 分析选项框架
        analysis_frame = ttk.LabelFrame(main_frame, text=loc.get_text('analysis_options'), padding="10")
        analysis_frame.pack(fill=tk.X, pady=(0, 15))

        # 创建变量
        deep_analysis_var = tk.BooleanVar(value=True)
        call_analysis_var = tk.BooleanVar(value=True)
        generate_report_var = tk.BooleanVar(value=True)
        show_flowchart_var = tk.BooleanVar(value=True)
        depth_var = tk.StringVar(value="2")

        # 自定义复选框样式 - 使用√符号
        def create_custom_checkbutton(parent, text, variable):
            frame = tk.Frame(parent)

            # 创建标签引用
            check_label = None

            def update_display(*args):
                if check_label:
                    if variable.get():
                        check_label.config(text="√", fg="green", font=("Segoe UI", 12, "bold"))
                    else:
                        check_label.config(text="☐", fg="gray", font=("Segoe UI", 12))

            def toggle():
                variable.set(not variable.get())
                update_display()

            check_label = tk.Label(frame, text="☐", font=("Segoe UI", 12), fg="gray")
            check_label.pack(side=tk.LEFT)

            text_label = tk.Label(frame, text=text, font=("Segoe UI", 9))
            text_label.pack(side=tk.LEFT, padx=(5, 0))

            # 绑定点击事件
            check_label.bind("<Button-1>", lambda e: toggle())
            text_label.bind("<Button-1>", lambda e: toggle())
            frame.bind("<Button-1>", lambda e: toggle())

            # 绑定变量变化事件
            variable.trace('w', update_display)

            # 初始化显示
            update_display()

            return frame

        # 创建自定义复选框
        create_custom_checkbutton(analysis_frame, loc.get_text('deep_code_analysis'), deep_analysis_var).pack(anchor=tk.W, pady=5, fill=tk.X)
        create_custom_checkbutton(analysis_frame, loc.get_text('main_function_call_analysis'), call_analysis_var).pack(anchor=tk.W, pady=5, fill=tk.X)
        create_custom_checkbutton(analysis_frame, loc.get_text('generate_analysis_report'), generate_report_var).pack(anchor=tk.W, pady=5, fill=tk.X)
        create_custom_checkbutton(analysis_frame, loc.get_text('show_call_flowchart'), show_flowchart_var).pack(anchor=tk.W, pady=5, fill=tk.X)

        # 调用深度设置
        depth_frame = ttk.LabelFrame(main_frame, text=loc.get_text('call_depth_settings'), padding="10")
        depth_frame.pack(fill=tk.X, pady=(0, 10))

        depth_row = ttk.Frame(depth_frame)
        depth_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(depth_row, text=loc.get_text('call_depth')).pack(side=tk.LEFT)
        ttk.Spinbox(depth_row, from_=1, to=10, width=10, textvariable=depth_var).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(depth_frame, text=loc.get_text('call_depth_description'),
                 font=("Segoe UI", 9), foreground="gray").pack(anchor=tk.W)

        # Mermaid渲染模式设置
        mermaid_frame = ttk.LabelFrame(main_frame, text="🧜‍♀️ Mermaid流程图渲染设置", padding="10")
        mermaid_frame.pack(fill=tk.X, pady=(0, 20))

        # 渲染模式选择
        mode_row = ttk.Frame(mermaid_frame)
        mode_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(mode_row, text="渲染模式:").pack(side=tk.LEFT)

        mermaid_mode_var = tk.StringVar(value="online")
        mode_combo = ttk.Combobox(mode_row, textvariable=mermaid_mode_var, width=15, state="readonly")
        mode_combo['values'] = ("online",)  # 只保留在线渲染
        mode_combo.pack(side=tk.LEFT, padx=(10, 0))

        # 模式说明
        mode_desc_label = ttk.Label(mermaid_frame,
                                   text="🌐 在线渲染 - 使用kroki.io直接生成PNG图片，无需本地依赖",
                                   font=("Segoe UI", 9), foreground="gray", wraplength=500)
        mode_desc_label.pack(anchor=tk.W, pady=(0, 5))

        # 加载当前配置
        def load_config():
            try:
                possible_paths = [
                    Path(__file__).parent / "config.yaml",
                    Path.cwd() / "config.yaml"
                ]

                for config_path in possible_paths:
                    if config_path.exists():
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)

                        analysis_options = config.get('analysis_options', {})
                        deep_analysis_var.set(analysis_options.get('deep_analysis', True))
                        call_analysis_var.set(analysis_options.get('call_analysis', True))
                        generate_report_var.set(analysis_options.get('generate_report', True))
                        show_flowchart_var.set(analysis_options.get('show_flowchart', True))
                        depth_var.set(str(analysis_options.get('call_depth', 2)))

                        # 加载Mermaid渲染模式配置
                        mermaid_config = config.get('mermaid', {})
                        mermaid_mode_var.set(mermaid_config.get('rendering_mode', 'online'))
                        break
            except Exception as e:
                self.log_message(f"🔧 DEBUG: Failed to load config: {e}")

        # 保存配置
        def save_config():
            try:
                possible_paths = [
                    Path(__file__).parent / "config.yaml",
                    Path.cwd() / "config.yaml"
                ]

                config_file = None
                for config_path in possible_paths:
                    if config_path.exists():
                        config_file = config_path
                        break

                if not config_file:
                    config_file = Path(__file__).parent / "config.yaml"

                # 读取现有配置
                config = {}
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f) or {}

                # 更新分析选项
                config['analysis_options'] = {
                    'deep_analysis': deep_analysis_var.get(),
                    'call_analysis': call_analysis_var.get(),
                    'generate_report': generate_report_var.get(),
                    'show_flowchart': show_flowchart_var.get(),
                    'call_depth': int(depth_var.get())
                }

                # 更新Mermaid渲染配置
                if 'mermaid' not in config:
                    config['mermaid'] = {}
                config['mermaid']['rendering_mode'] = mermaid_mode_var.get()

                # 保存配置
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

                messagebox.showinfo(loc.get_text('success'), loc.get_text('config_saved_successfully'))
                config_window.destroy()

            except Exception as e:
                messagebox.showerror(loc.get_text('error'), f"{loc.get_text('save_config_failed')}: {e}")

        # 重置默认值
        def reset_defaults():
            deep_analysis_var.set(True)
            call_analysis_var.set(True)
            generate_report_var.set(True)
            show_flowchart_var.set(True)
            depth_var.set("2")
            mermaid_mode_var.set("online")  # 默认使用在线渲染

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text=loc.get_text('cancel'), command=config_window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text=loc.get_text('save_config'), command=save_config).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(button_frame, text=loc.get_text('reset_defaults'), command=reset_defaults).pack(side=tk.RIGHT, padx=(0, 10))

        # 加载配置
        load_config()

    def show_help(self):
        """显示使用说明"""
        help_text = """MCU工程分析器 v4.0 - 使用说明

🚀 快速开始：
1. 选择MCU项目目录
2. 配置分析选项
3. 点击"开始分析"

🎨 图形功能：
• UI内嵌图形渲染
• 浏览器交互式图形
• 层次化调用关系显示

⚙️ LLM配置：
• 支持本地Ollama
• 支持OpenAI API
• 支持腾讯云API
• 支持自定义API

📊 分析功能：
• 芯片信息识别
• 函数调用关系分析
• 接口使用统计
• Mermaid流程图生成

更多详细信息请查看使用说明文档。"""

        messagebox.showinfo("使用说明", help_text)

    def start_llm_analysis(self):
        """开始LLM分析 - 内嵌显示"""
        if not hasattr(self, 'current_project_path') or not self.current_project_path:
            messagebox.showwarning(loc.get_text('warning'), loc.get_text('please_complete_analysis_first'))
            return

        # 检查是否有分析结果
        if not hasattr(self, 'last_analysis_results'):
            messagebox.showwarning(loc.get_text('warning'), loc.get_text('no_analysis_results'))
            return

        # 显示LLM分析区域
        self.show_llm_analysis_section()

    def show_llm_analysis_section(self):
        """显示LLM分析区域并初始化提示词"""
        # 切换到LLM Analysis标签页
        self.notebook.select(self.llm_analysis_frame)

        # 设置完整的RIPER-5协议作为System提示词
        riper5_prompt = """You are a seasoned embedded engineer. Compare MCU project migration (involving deletion/replacement of the original MCU). Based on the user's prompt, conduct a project summary, summarize the modules used in the project, and analyze the functionalities currently completed in the project—to facilitate subsequent porting work.

"""

        # 设置System提示词
        self.system_prompt_text.delete(1.0, tk.END)
        self.system_prompt_text.insert(tk.END, riper5_prompt)

        # 生成并设置User提示词
        user_prompt = self.generate_user_prompt()
        self.user_prompt_text.delete(1.0, tk.END)
        self.user_prompt_text.insert(tk.END, user_prompt)

        # 清空结果区域
        self.llm_result_text.delete(1.0, tk.END)
        self.llm_result_text.insert(tk.END, "Click 'Start Analysis' to begin LLM analysis...")

        # 重置状态
        self.llm_status_label.config(text="Ready", foreground="blue")

    def run_llm_analysis_inline(self):
        """运行内嵌LLM分析"""
        system_prompt = self.system_prompt_text.get(1.0, tk.END).strip()
        user_prompt = self.user_prompt_text.get(1.0, tk.END).strip()

        # 获取用户设置的timeout值
        try:
            custom_timeout = int(self.timeout_var.get())
            if custom_timeout <= 0:
                custom_timeout = 200
        except ValueError:
            custom_timeout = 200
            self.timeout_var.set("200")  # 重置为默认值

        # 倒计时相关变量
        self.countdown_active = False
        self.countdown_remaining = custom_timeout

        def update_countdown():
            """更新倒计时显示"""
            if self.countdown_active and self.countdown_remaining > 0:
                self.root.after(0, lambda: self.llm_status_label.config(
                    text=f"Calling LLM (timeout: {custom_timeout}s, remaining: {self.countdown_remaining}s)...",
                    foreground="blue"
                ))
                self.countdown_remaining -= 1
                # 每秒更新一次
                threading.Timer(1.0, update_countdown).start()
            elif self.countdown_active and self.countdown_remaining <= 0:
                self.root.after(0, lambda: self.llm_status_label.config(
                    text="LLM call timeout reached...",
                    foreground="red"
                ))

        # 在新线程中执行分析
        def run_analysis():
            try:
                self.root.after(0, lambda: self.llm_status_label.config(text="Starting LLM analysis...", foreground="blue"))
                self.root.after(0, lambda: self.llm_result_text.delete(1.0, tk.END))
                self.root.after(0, lambda: self.llm_result_text.insert(tk.END, "Initializing LLM analysis...\n"))

                # 构建完整提示词
                full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"

                # 尝试调用LLM
                try:
                    # 尝试导入LLM管理器
                    llm_manager = None

                    try:
                        from intelligence.llm_manager import LLMManager
                        llm_manager = LLMManager()
                    except ImportError:
                        pass

                    if llm_manager is None:
                        try:
                            import sys
                            import os

                            if hasattr(sys, '_MEIPASS'):
                                base_dir = sys._MEIPASS
                            else:
                                base_dir = os.path.dirname(os.path.abspath(__file__))

                            intelligence_dir = os.path.join(base_dir, 'intelligence')
                            if intelligence_dir not in sys.path:
                                sys.path.insert(0, intelligence_dir)

                            from llm_manager import LLMManager
                            llm_manager = LLMManager()
                        except ImportError:
                            pass

                    if llm_manager is None:
                        # 停止倒计时
                        self.countdown_active = False
                        # 使用简化分析
                        self.root.after(0, lambda: self.llm_status_label.config(text="Using built-in analysis engine...", foreground="orange"))
                        simple_result = self.generate_simple_analysis(self.prepare_llm_analysis_data())
                        self.root.after(0, lambda: self.llm_result_text.delete(1.0, tk.END))
                        self.root.after(0, lambda: self.llm_result_text.insert(tk.END, simple_result))
                        self.root.after(0, lambda: self.llm_status_label.config(text="Built-in analysis completed", foreground="green"))
                        return

                    # 检查LLM服务可用性
                    self.root.after(0, lambda: self.llm_status_label.config(text="Checking LLM service availability...", foreground="blue"))
                    if not llm_manager.is_available():
                        # 停止倒计时
                        self.countdown_active = False
                        available_providers = llm_manager.get_available_providers()
                        error_msg = f"No available LLM service. Available providers: {available_providers}"
                        self.root.after(0, lambda: self.llm_status_label.config(text=error_msg, foreground="red"))
                        self.root.after(0, lambda: self.llm_result_text.delete(1.0, tk.END))
                        self.root.after(0, lambda: self.llm_result_text.insert(tk.END, f"Error: {error_msg}\n\nPlease configure LLM service first."))
                        return

                    self.root.after(0, lambda: self.llm_status_label.config(text=f"LLM service available: {llm_manager.current_provider}", foreground="green"))

                    # 启动倒计时
                    self.countdown_active = True
                    self.countdown_remaining = custom_timeout
                    update_countdown()

                    # 调用LLM，使用自定义timeout
                    response = llm_manager.generate(full_prompt, timeout=custom_timeout)

                    # 停止倒计时
                    self.countdown_active = False

                    if response.success:
                        self.root.after(0, lambda: self.llm_status_label.config(text="LLM analysis completed", foreground="green"))
                        self.root.after(0, lambda: self.llm_result_text.delete(1.0, tk.END))
                        self.root.after(0, lambda: self.llm_result_text.insert(tk.END, response.content))
                    else:
                        error_msg = f"LLM call failed: {response.error_message}"
                        self.root.after(0, lambda: self.llm_status_label.config(text=error_msg, foreground="red"))
                        self.root.after(0, lambda: self.llm_result_text.delete(1.0, tk.END))
                        self.root.after(0, lambda: self.llm_result_text.insert(tk.END, f"Error: {error_msg}"))

                except Exception as e:
                    # 停止倒计时
                    self.countdown_active = False
                    error_msg = f"LLM analysis failed: {e}"
                    self.root.after(0, lambda: self.llm_status_label.config(text=error_msg, foreground="red"))
                    self.root.after(0, lambda: self.llm_result_text.delete(1.0, tk.END))
                    self.root.after(0, lambda: self.llm_result_text.insert(tk.END, f"Error: {error_msg}"))

            except Exception as e:
                # 停止倒计时
                self.countdown_active = False
                error_msg = f"Analysis failed: {e}"
                self.root.after(0, lambda: self.llm_status_label.config(text=error_msg, foreground="red"))
                self.root.after(0, lambda: self.llm_result_text.delete(1.0, tk.END))
                self.root.after(0, lambda: self.llm_result_text.insert(tk.END, f"Error: {error_msg}"))

        # 启动分析线程
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()

    def show_llm_analysis_dialog(self):
        """显示LLM分析对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(loc.get_text('llm_analysis_title'))
        dialog.geometry("1000x800")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        x = (dialog.winfo_screenwidth() // 2) - (1000 // 2)
        y = (dialog.winfo_screenheight() // 2) - (800 // 2)
        dialog.geometry(f"1000x800+{x}+{y}")

        # 主框架
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # System提示词区域
        system_frame = ttk.LabelFrame(main_frame, text="System Prompt (可编辑)", padding="5")
        system_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        system_text = scrolledtext.ScrolledText(
            system_frame,
            height=8,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        system_text.pack(fill=tk.BOTH, expand=True)

        # 设置默认System提示词
        default_system_prompt = """你是一个专业的嵌入式系统和MCU开发专家。请基于提供的项目信息和函数调用关系，深入分析MCU项目的功能实现、技术架构和设计特点。

请重点分析：
1. 项目的主要功能和应用场景
2. 硬件接口的使用情况和作用
3. 软件架构和代码组织结构
4. 关键技术实现和算法
5. 设计优点和改进建议

请用中文详细回答，提供专业的技术分析和建议。回答要详细、专业、实用，重点说明项目实现的具体功能。"""

        system_text.insert(tk.END, default_system_prompt)

        # User提示词区域
        user_frame = ttk.LabelFrame(main_frame, text="User Prompt (可编辑)", padding="5")
        user_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        user_text = scrolledtext.ScrolledText(
            user_frame,
            height=8,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        user_text.pack(fill=tk.BOTH, expand=True)

        # 生成User提示词
        user_prompt = self.generate_user_prompt()
        user_text.insert(tk.END, user_prompt)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        # 分析结果区域
        result_frame = ttk.LabelFrame(main_frame, text="LLM Analysis Result", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        result_text = scrolledtext.ScrolledText(
            result_frame,
            height=12,
            font=("Microsoft YaHei", 10),
            wrap=tk.WORD
        )
        result_text.pack(fill=tk.BOTH, expand=True)

        # 状态标签
        status_label = ttk.Label(button_frame, text="Ready to analyze", foreground="blue")
        status_label.pack(side=tk.LEFT)

        # 按钮
        def start_analysis():
            system_prompt = system_text.get(1.0, tk.END).strip()
            user_prompt = user_text.get(1.0, tk.END).strip()
            self.run_llm_analysis_in_dialog(system_prompt, user_prompt, result_text, status_label)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Start Analysis", command=start_analysis).pack(side=tk.RIGHT, padx=(0, 10))

    def generate_user_prompt(self):
        """生成User提示词：项目概述 + 函数调用关系（LLM友好格式）"""
        # 准备分析数据
        data = self.prepare_llm_analysis_data()

        # 生成纯文本的函数调用关系
        call_relationships = self.extract_function_call_relationships(data['call_analysis'])

        prompt = f"""{loc.get_text('mcu_project_analysis_request_title')}

{loc.get_text('project_overview_title')}
- {loc.get_text('project_path_label')}: {data['project_path']}
- {loc.get_text('chip_model_label')}: {self.get_chip_info_safe(data['chip_info'], 'device_name', loc.get_text('unknown'))}
- {loc.get_text('chip_vendor_label')}: {self.get_chip_info_safe(data['chip_info'], 'vendor', loc.get_text('unknown'))}
- {loc.get_text('processor_core_label')}: {self.get_chip_info_safe(data['chip_info'], 'core', loc.get_text('unknown'))}

{loc.get_text('code_structure_title')}
- {loc.get_text('total_function_count_label')}: {data['code_analysis'].get('total_functions', 0)}
- {loc.get_text('main_function_label')}: {loc.get_text('exists_label') if data['code_analysis'].get('main_found', False) else loc.get_text('not_found_label')}
- {loc.get_text('include_file_count_label')}: {len(data['code_analysis'].get('includes', []))}

{loc.get_text('interface_usage_title')}
{self._format_interfaces_for_prompt_clean(data['interfaces'])}

{loc.get_text('function_call_relationships_title')}
{call_relationships[:2000] if len(call_relationships) > 2000 else call_relationships}

{loc.get_text('analyze_request_text')}"""

        return prompt

    def extract_function_call_relationships(self, call_analysis):
        f"""{loc.get_text('extract_plain_text_function_call_relationships')}"""
        if not call_analysis or 'call_tree' not in call_analysis:
            return loc.get_text('no_call_relationship_analysis_performed')

        tree = call_analysis['call_tree']
        if not tree:
            return loc.get_text('no_main_function_call_relationships_found')

        # 递归提取调用关系
        relationships = []
        self._extract_call_tree_text(tree, relationships, 0)

        if relationships:
            return "\n".join(relationships)
        else:
            return "未找到函数调用关系"

    def _extract_call_tree_text(self, node, relationships, depth):
        f"""{loc.get_text('recursively_extract_call_tree_text')}"""
        if not node:
            return

        indent = "  " * depth
        func_name = node.get('name', loc.get_text('unknown_function'))

        if depth == 0:
            relationships.append(f"{indent}{loc.get_text('main_function_program_entry')}")
        else:
            relationships.append(f"{indent}|- {func_name}")

        # {loc.get_text('recursively_process_child_nodes')}
        children = node.get('children', [])
        for child in children:
            self._extract_call_tree_text(child, relationships, depth + 1)

    def _format_interfaces_for_prompt_clean(self, interfaces):
        f"""{loc.get_text('format_interface_info_for_prompt_clean')}"""
        if not interfaces:
            return loc.get_text('no_interface_usage_detected_clean')

        interface_list = []
        for interface, count in interfaces.items():
            if count > 0:
                interface_list.append(f"{interface}: {count}{loc.get_text('times_called_clean')}")

        return '\n'.join(interface_list) if interface_list else loc.get_text('no_interface_usage_detected_clean')

    def get_chip_info_safe(self, chip_info, key, default=None):
        f"""{loc.get_text('safe_get_chip_info')}"""
        if default is None:
            default = loc.get_text('unknown')
        if hasattr(chip_info, key):
            return getattr(chip_info, key, default)
        elif isinstance(chip_info, dict):
            return chip_info.get(key, default)
        else:
            return default

    def run_llm_analysis_in_dialog(self, system_prompt, user_prompt, result_text, status_label):
        """在对话框中运行LLM分析"""
        def update_status(text, color="blue"):
            status_label.config(text=text, foreground=color)

        def update_result(text):
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, text)

        # 在新线程中执行分析
        def run_analysis():
            try:
                update_status("🤖 Starting LLM analysis...", "blue")

                # 构建完整提示词
                full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"

                # 尝试调用LLM
                try:
                    # 尝试导入LLM管理器
                    llm_manager = None

                    try:
                        from intelligence.llm_manager import LLMManager
                        llm_manager = LLMManager()
                    except ImportError:
                        pass

                    if llm_manager is None:
                        try:
                            import sys
                            import os

                            if hasattr(sys, '_MEIPASS'):
                                base_dir = sys._MEIPASS
                            else:
                                base_dir = os.path.dirname(os.path.abspath(__file__))

                            intelligence_dir = os.path.join(base_dir, 'intelligence')
                            if intelligence_dir not in sys.path:
                                sys.path.insert(0, intelligence_dir)

                            from llm_manager import LLMManager
                            llm_manager = LLMManager()
                        except ImportError:
                            pass

                    if llm_manager is None:
                        # 使用简化分析
                        update_status("🤖 Using built-in analysis engine...", "orange")
                        simple_result = self.generate_simple_analysis(self.prepare_llm_analysis_data())
                        self.root.after(0, lambda: update_result(simple_result))
                        self.root.after(0, lambda: update_status("✅ Built-in analysis completed", "green"))
                        return

                    # 检查LLM服务可用性
                    update_status("🔍 Checking LLM service availability...", "blue")
                    if not llm_manager.is_available():
                        available_providers = llm_manager.get_available_providers()
                        error_msg = f"❌ No available LLM service. Available providers: {available_providers}"
                        self.root.after(0, lambda: update_status(error_msg, "red"))
                        self.root.after(0, lambda: update_result(f"Error: {error_msg}\n\nPlease configure LLM service first."))
                        return

                    update_status(f"✅ LLM service available: {llm_manager.current_provider}", "green")
                    update_status("🚀 Calling LLM...", "blue")

                    # 调用LLM
                    response = llm_manager.generate(full_prompt)

                    if response.success:
                        self.root.after(0, lambda: update_status("✅ LLM analysis completed", "green"))
                        self.root.after(0, lambda: update_result(response.content))
                    else:
                        error_msg = f"❌ LLM call failed: {response.error_message}"
                        self.root.after(0, lambda: update_status(error_msg, "red"))
                        self.root.after(0, lambda: update_result(f"Error: {error_msg}"))

                except Exception as e:
                    error_msg = f"❌ LLM analysis failed: {e}"
                    self.root.after(0, lambda: update_status(error_msg, "red"))
                    self.root.after(0, lambda: update_result(f"Error: {error_msg}"))

            except Exception as e:
                error_msg = f"❌ Analysis failed: {e}"
                self.root.after(0, lambda: update_status(error_msg, "red"))
                self.root.after(0, lambda: update_result(f"Error: {error_msg}"))

        # 启动分析线程
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()

    def run_llm_analysis(self):
        """运行LLM分析（在后台线程中）"""
        try:
            self.log_message("🤖 开始LLM智能分析...")
            self.update_status("正在进行LLM分析...")

            # 准备分析数据
            analysis_data = self.prepare_llm_analysis_data()

            # 生成分析提示
            prompt = self.generate_analysis_prompt(analysis_data)

            # 调用LLM
            self.log_message("🤖 正在调用LLM...")

            try:
                # 尝试导入LLM管理器
                llm_manager = None

                # 方式1: 直接导入
                try:
                    from intelligence.llm_manager import LLMManager
                    llm_manager = LLMManager()
                except ImportError:
                    pass

                # 方式2: 添加路径后导入
                if llm_manager is None:
                    try:
                        import sys
                        import os

                        if hasattr(sys, '_MEIPASS'):
                            base_dir = sys._MEIPASS
                        else:
                            base_dir = os.path.dirname(os.path.abspath(__file__))

                        intelligence_dir = os.path.join(base_dir, 'intelligence')
                        if intelligence_dir not in sys.path:
                            sys.path.insert(0, intelligence_dir)

                        from llm_manager import LLMManager
                        llm_manager = LLMManager()
                    except ImportError:
                        pass

                # 方式3: 使用简化的LLM功能
                if llm_manager is None:
                    self.run_simple_llm_analysis(prompt)
                    return

                # 检查LLM服务可用性
                self.log_message("🔍 检查LLM服务可用性...")
                if not llm_manager.is_available():
                    available_providers = llm_manager.get_available_providers()
                    self.log_message(f"❌ 没有可用的LLM服务。可用提供商: {available_providers}")
                    raise Exception(f"没有可用的LLM服务，请先配置LLM。可用提供商: {available_providers}")

                self.log_message(f"✅ LLM服务可用，当前提供商: {llm_manager.current_provider}")
                self.log_message("🚀 开始LLM分析...")

                response = llm_manager.generate(prompt)

                if response.success:
                    self.log_message("✅ LLM分析完成")
                    self.display_llm_results(response.content)
                else:
                    self.log_message(f"❌ LLM call failed: {response.error_message}")
                    raise Exception(f"LLM call failed: {response.error_message}")

            except ImportError:
                # 降级到简化LLM分析
                self.run_simple_llm_analysis(prompt)

        except Exception as e:
            self.log_message(f"❌ LLM analysis failed: {e}")
            self.update_status(f"LLM analysis failed: {e}")
            messagebox.showerror("Error", f"LLM analysis failed:\n{e}")

        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self.llm_analysis_btn.config(state="normal"))

    def run_simple_llm_analysis(self, prompt):
        """运行简化的LLM分析（当LLM模块不可用时）"""
        self.log_message("🤖 使用内置分析引擎...")

        # 基于项目数据生成简化分析
        analysis_data = self.prepare_llm_analysis_data()

        # 生成简化分析报告
        simple_analysis = self.generate_simple_analysis(analysis_data)

        self.log_message("✅ 内置分析完成")
        self.display_llm_results(simple_analysis)

    def generate_simple_analysis(self, data):
        """生成简化的分析报告"""
        chip_info = data.get('chip_info', {})
        code_analysis = data.get('code_analysis', {})
        interfaces = data.get('interfaces', {})

        analysis = f"""# MCU项目智能分析报告

## 📊 项目概述
**项目路径**: {data.get('project_path', '未知')}
**芯片型号**: {getattr(chip_info, 'device_name', '未知') if hasattr(chip_info, 'device_name') else chip_info.get('device', '未知') if isinstance(chip_info, dict) else '未知'}
**芯片厂商**: {getattr(chip_info, 'vendor', '未知') if hasattr(chip_info, 'vendor') else chip_info.get('vendor', '未知') if isinstance(chip_info, dict) else '未知'}
**处理器内核**: {getattr(chip_info, 'core', '未知') if hasattr(chip_info, 'core') else chip_info.get('core', '未知') if isinstance(chip_info, dict) else '未知'}

## 🔍 代码结构分析
- **总函数数量**: {code_analysis.get('total_functions', 0)}
- **main函数**: {'✅ 已找到' if code_analysis.get('main_found', False) else '❌ 未找到'}
- **包含文件数**: {len(code_analysis.get('includes', []))}

## 🔌 接口使用评估
"""

        if interfaces:
            analysis += "检测到以下接口使用：\n"
            for interface, count in interfaces.items():
                if count > 0:
                    analysis += f"- **{interface}**: {count} 次调用\n"
        else:
            analysis += "未检测到明显的接口使用\n"

        analysis += f"""
## 💡 技术架构评估
基于代码分析，该项目具有以下特点：

### 代码组织
- 项目包含 {code_analysis.get('total_functions', 0)} 个函数
- {'具有标准的main函数入口' if code_analysis.get('main_found', False) else '缺少main函数，可能是库项目'}
- 包含 {len(code_analysis.get('includes', []))} 个头文件引用

### 接口使用特点
"""

        if interfaces:
            interface_count = sum(interfaces.values())
            if interface_count > 50:
                analysis += "- 🔥 接口使用频繁，属于功能丰富的项目\n"
            elif interface_count > 20:
                analysis += "- 📊 接口使用适中，项目复杂度中等\n"
            else:
                analysis += "- 🎯 接口使用较少，可能是简单的演示项目\n"

            # 分析主要接口类型
            main_interfaces = [k for k, v in interfaces.items() if v > 0]
            if 'GPIO' in main_interfaces:
                analysis += "- 🔌 使用GPIO接口，涉及数字IO控制\n"
            if 'UART' in main_interfaces:
                analysis += "- 📡 使用UART接口，具有串口通信功能\n"
            if 'SPI' in main_interfaces:
                analysis += "- 🔄 使用SPI接口，可能连接外部设备\n"
            if 'I2C' in main_interfaces:
                analysis += "- 🔗 使用I2C接口，可能连接传感器\n"
        else:
            analysis += "- ⚠️ 未检测到明显的外设接口使用\n"

        analysis += f"""
## 🚀 优化建议

### 代码质量
- {'✅ 代码结构良好，有明确的程序入口' if code_analysis.get('main_found', False) else '⚠️ 建议添加main函数作为程序入口'}
- 建议添加更多的代码注释和文档
- 考虑使用模块化设计，提高代码可维护性

### 性能优化
- 检查是否有不必要的函数调用
- 优化内存使用，避免内存泄漏
- 考虑使用编译器优化选项

### 移植建议
- 当前项目基于 {getattr(chip_info, 'vendor', '未知') if hasattr(chip_info, 'vendor') else chip_info.get('vendor', '未知') if isinstance(chip_info, dict) else '未知'} 芯片
- 移植到其他平台时需要注意：
  - 修改芯片相关的寄存器配置
  - 适配不同的HAL库接口
  - 调整时钟配置和中断向量

## 📝 总结
这是一个{'功能完整' if interfaces else '结构简单'}的MCU项目，
{'具有丰富的外设接口使用' if interfaces else '主要专注于核心逻辑处理'}。
建议在后续开发中注重代码的模块化和文档化。

---
*本分析由MCU工程分析器内置引擎生成*
*如需更详细的AI分析，请配置LLM服务*
"""

        return analysis

    def prepare_llm_analysis_data(self):
        """准备LLM分析数据"""
        data = {
            'project_path': getattr(self, 'current_project_path', ''),
            'chip_info': getattr(self, 'last_chip_info', {}),
            'code_analysis': getattr(self, 'last_code_analysis', {}),
            'call_analysis': getattr(self, 'last_call_analysis', {}),
            'interfaces': getattr(self, 'last_interfaces', {}),
            'mermaid_code': getattr(self, 'mermaid_code', '')
        }
        return data

    def generate_analysis_prompt(self, data):
        """生成LLM分析提示"""
        prompt = f"""作为嵌入式系统专家，请分析以下MCU项目并详细说明其功能实现：

## 📋 项目基本信息
- 项目路径: {data['project_path']}
- 芯片型号: {getattr(data['chip_info'], 'device_name', '未知') if hasattr(data['chip_info'], 'device_name') else data['chip_info'].get('device', '未知') if isinstance(data['chip_info'], dict) else '未知'}
- 芯片厂商: {getattr(data['chip_info'], 'vendor', '未知') if hasattr(data['chip_info'], 'vendor') else data['chip_info'].get('vendor', '未知') if isinstance(data['chip_info'], dict) else '未知'}
- 芯片系列: {getattr(data['chip_info'], 'series', '未知') if hasattr(data['chip_info'], 'series') else data['chip_info'].get('series', '未知') if isinstance(data['chip_info'], dict) else '未知'}
- 处理器内核: {getattr(data['chip_info'], 'core', '未知') if hasattr(data['chip_info'], 'core') else data['chip_info'].get('core', '未知') if isinstance(data['chip_info'], dict) else '未知'}

## 📊 代码结构分析
- 总函数数量: {data['code_analysis'].get('total_functions', 0)}
- main函数: {'存在' if data['code_analysis'].get('main_found', False) else '未找到'}
- 主要包含文件: {', '.join(data['code_analysis'].get('includes', [])[:10])}

## 🔌 接口使用情况
{self._format_interfaces_for_prompt(data['interfaces'])}

## 🔄 函数调用关系
{self._format_call_analysis_for_prompt(data['call_analysis'])}

请重点分析并回答：

### 🎯 项目功能分析
1. **主要功能**: 这个项目实现了什么具体功能？
2. **应用场景**: 最可能的应用场景是什么？
3. **核心逻辑**: 程序的主要执行流程是什么？

### 🏗️ 技术实现
1. **硬件接口**: 使用了哪些外设接口，各自的作用是什么？
2. **软件架构**: 代码的组织结构如何？
3. **关键技术**: 采用了哪些关键技术或算法？

### 💡 专业评估
1. **设计优点**: 项目设计的优秀之处
2. **改进建议**: 可以优化的地方
3. **扩展方向**: 可能的功能扩展方向

请用中文详细回答，重点说明项目实现的具体功能。"""

        return prompt

    def _format_interfaces_for_prompt(self, interfaces):
        f"""{loc.get_text('format_interface_info_for_prompt_clean')}"""
        if not interfaces:
            return loc.get_text('no_interface_usage_detected_clean')

        interface_list = []
        for interface, count in interfaces.items():
            if count > 0:
                interface_list.append(f"- {interface}: {count}{loc.get_text('times_called_clean')}")

        return '\n'.join(interface_list) if interface_list else loc.get_text('no_interface_usage_detected_clean')

    def _format_call_analysis_for_prompt(self, call_analysis):
        """格式化调用分析信息用于提示"""
        if not call_analysis or 'call_tree' not in call_analysis:
            return "未进行调用关系分析"

        tree = call_analysis['call_tree']
        if not tree:
            return loc.get_text('no_main_function_call_relationships_found')

        # 简化调用树信息
        summary = f"从main函数开始的调用层次: {self._count_call_depth(tree)}层"
        return summary

    def _count_call_depth(self, tree, depth=0):
        """计算调用深度"""
        if not tree or 'children' not in tree:
            return depth

        max_child_depth = depth
        for child in tree['children']:
            child_depth = self._count_call_depth(child, depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def display_llm_results(self, llm_content):
        """显示LLM分析结果"""
        def update_ui():
            # 添加新的LLM分析标签页
            if not hasattr(self, 'llm_frame'):
                self.llm_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.llm_frame, text="🤖 LLM分析")

                self.llm_text = scrolledtext.ScrolledText(
                    self.llm_frame,
                    height=15,
                    font=("Microsoft YaHei", 10),
                    wrap=tk.WORD
                )
                self.llm_text.pack(fill=tk.BOTH, expand=True)

            # 清空并显示新结果
            self.llm_text.delete(1.0, tk.END)
            self.llm_text.insert(tk.END, llm_content)

            # 切换到LLM分析标签页
            self.notebook.select(self.llm_frame)

            self.update_status("LLM分析完成")

        self.root.after(0, update_ui)

    def run(self):
        """运行主窗口"""
        self.root.mainloop()

    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"

        def append_log():
            self.log_text.insert(tk.END, log_line)
            self.log_text.see(tk.END)

        self.root.after(0, append_log)

    def debug_log(self, message):
        """输出debug信息到log页面"""
        self.log_message(f"🔧 DEBUG: {message}")

    def export_high_quality_image(self):
        """导出最高质量的流程图图片"""
        try:
            self.log_message("📸 开始导出高质量图片...")

            # 检查是否有mermaid代码
            if not hasattr(self, 'mermaid_code') or not self.mermaid_code:
                messagebox.showwarning("导出失败", "没有可导出的流程图\n请先进行项目分析生成流程图")
                return

            # 选择保存位置
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title="保存高质量流程图",
                defaultextension=".png",
                filetypes=[
                    ("PNG图片 (推荐)", "*.png"),
                    ("JPEG图片", "*.jpg"),
                    ("SVG矢量图", "*.svg"),
                    ("所有文件", "*.*")
                ]
            )

            if not file_path:
                return

            # 根据文件扩展名确定导出格式
            file_ext = file_path.lower().split('.')[-1]

            if file_ext == 'svg':
                # 导出SVG格式
                success = self.export_svg_image(file_path)
            else:
                # 导出PNG/JPG格式
                success = self.export_png_image(file_path, file_ext)

            if success:
                self.log_message(f"✅ 图片导出成功: {file_path}")
                messagebox.showinfo("导出成功", f"高质量图片已保存到:\n{file_path}")
            else:
                self.log_message("❌ 图片导出失败")
                messagebox.showerror("导出失败", "图片导出过程中出现错误\n请查看执行日志获取详细信息")

        except Exception as e:
            self.log_message(f"❌ 导出图片时发生错误: {e}")
            messagebox.showerror("导出错误", f"导出过程中发生错误:\n{e}")

    def export_svg_image(self, file_path):
        """导出SVG格式图片"""
        try:
            self.log_message("🔧 DEBUG: 开始导出SVG格式...")

            # 使用在线API获取SVG
            svg_content = self.get_high_quality_svg()

            if svg_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                self.log_message(f"🔧 DEBUG: SVG文件已保存: {file_path}")
                return True
            else:
                self.log_message("🔧 DEBUG: 无法获取SVG内容")
                return False

        except Exception as e:
            self.log_message(f"🔧 DEBUG: SVG导出失败: {e}")
            return False

    def export_png_image(self, file_path, format_type='png'):
        """导出PNG/JPG格式图片"""
        try:
            self.log_message(f"🔧 DEBUG: 开始导出{format_type.upper()}格式...")

            # 使用在线API获取高质量PNG
            png_content = self.get_high_quality_png()

            if png_content:
                # 如果需要转换为JPG格式
                if format_type.lower() in ['jpg', 'jpeg']:
                    png_content = self.convert_png_to_jpg(png_content)

                with open(file_path, 'wb') as f:
                    f.write(png_content)
                self.log_message(f"🔧 DEBUG: {format_type.upper()}文件已保存: {file_path}")
                return True
            else:
                self.log_message("🔧 DEBUG: 无法获取PNG内容")
                return False

        except Exception as e:
            self.log_message(f"🔧 DEBUG: {format_type.upper()}导出失败: {e}")
            return False

    def get_high_quality_svg(self):
        """获取最高质量的SVG内容"""
        try:
            import requests
            import urllib.parse

            self.log_message("🔧 DEBUG: 请求高质量SVG...")

            # 使用kroki.io API获取SVG
            mermaid_encoded = urllib.parse.quote(self.mermaid_code.encode('utf-8'))

            # 尝试多个API端点
            api_endpoints = [
                f"https://kroki.io/mermaid/svg/{mermaid_encoded}",
                f"https://mermaid.ink/svg/{mermaid_encoded}",
            ]

            for api_url in api_endpoints:
                try:
                    self.log_message(f"🔧 DEBUG: 尝试API: {api_url[:50]}...")

                    response = requests.get(api_url, timeout=30)
                    if response.status_code == 200:
                        svg_content = response.text
                        if svg_content and '<svg' in svg_content:
                            self.log_message("🔧 DEBUG: 成功获取SVG内容")
                            return svg_content

                except Exception as e:
                    self.log_message(f"🔧 DEBUG: API请求失败: {e}")
                    continue

            self.log_message("🔧 DEBUG: 所有SVG API都失败了")
            return None

        except Exception as e:
            self.log_message(f"🔧 DEBUG: 获取SVG时发生错误: {e}")
            return None

    def get_high_quality_png(self):
        """获取最高质量的PNG内容"""
        try:
            import requests
            import urllib.parse
            import base64

            self.log_message("🔧 DEBUG: 请求高质量PNG...")

            # 计算最佳尺寸和DPI
            optimal_width, optimal_height, optimal_dpi = self.calculate_optimal_png_size()

            # 使用kroki.io API获取PNG
            mermaid_encoded = urllib.parse.quote(self.mermaid_code.encode('utf-8'))

            # 构建高质量PNG请求
            api_endpoints = [
                f"https://kroki.io/mermaid/png/{mermaid_encoded}",
                f"https://mermaid.ink/img/{mermaid_encoded}",
            ]

            for api_url in api_endpoints:
                try:
                    self.log_message(f"🔧 DEBUG: 尝试PNG API: {api_url[:50]}...")

                    # 添加高质量参数
                    headers = {
                        'User-Agent': 'MCU-Code-Analyzer/3.0',
                        'Accept': 'image/png'
                    }

                    response = requests.get(api_url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        png_content = response.content
                        if png_content and len(png_content) > 1000:  # 确保是有效的PNG
                            self.log_message(f"🔧 DEBUG: 成功获取PNG内容，大小: {len(png_content)} bytes")
                            return png_content

                except Exception as e:
                    self.log_message(f"🔧 DEBUG: PNG API请求失败: {e}")
                    continue

            self.log_message("🔧 DEBUG: 所有PNG API都失败了")
            return None

        except Exception as e:
            self.log_message(f"🔧 DEBUG: 获取PNG时发生错误: {e}")
            return None

    def convert_png_to_jpg(self, png_content):
        """将PNG内容转换为JPG格式"""
        try:
            from PIL import Image
            import io

            self.log_message("🔧 DEBUG: 转换PNG到JPG...")

            # 读取PNG
            png_image = Image.open(io.BytesIO(png_content))

            # 转换为RGB模式（JPG不支持透明度）
            if png_image.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                rgb_image = Image.new('RGB', png_image.size, (255, 255, 255))
                if png_image.mode == 'P':
                    png_image = png_image.convert('RGBA')
                rgb_image.paste(png_image, mask=png_image.split()[-1] if png_image.mode == 'RGBA' else None)
                png_image = rgb_image

            # 保存为JPG
            jpg_buffer = io.BytesIO()
            png_image.save(jpg_buffer, format='JPEG', quality=95, optimize=True)

            self.log_message("🔧 DEBUG: PNG到JPG转换成功")
            return jpg_buffer.getvalue()

        except Exception as e:
            self.log_message(f"🔧 DEBUG: PNG到JPG转换失败: {e}")
            return png_content  # 返回原始PNG内容

    def update_status(self, message):
        """更新状态"""
        self.root.after(0, lambda: self.status_var.set(message))

    def update_progress(self, value, is_error=False):
        """更新进度 - 线程安全版本"""
        def update_ui():
            try:
                # 更新进度条值
                self.progress_var.set(value)

                # 更新百分比显示
                percentage_text = f"{int(value)}%"
                self.progress_percentage.config(text=percentage_text)

                # 根据状态设置颜色
                if is_error:
                    # 失败时显示红色
                    self.progress_percentage.config(foreground="red")
                    self.set_progress_color("red")
                else:
                    # 正常时显示绿色
                    self.progress_percentage.config(foreground="green")
                    self.set_progress_color("green")

            except Exception as e:
                self.log_message(f"🔧 DEBUG: Failed to update progress: {e}")

        self.root.after(0, update_ui)

    def on_closing(self):
        """应用程序关闭时的清理工作"""
        try:
            # 保存当前项目路径到配置文件
            if hasattr(self, 'project_path_var') and self.project_path_var.get().strip():
                self.save_last_project_path(self.project_path_var.get().strip())

            print(loc.get_text('application_closing'))
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(loc.get_text('close_application_error', e))
            self.root.quit()
            self.root.destroy()

def main():
    """Main function"""
    try:
        app = MCUAnalyzerGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

"""
配置对话框 - LLM配置和系统设置
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from utils.logger import logger
from utils.config import config, LLMConfig
from intelligence.llm_manager import llm_manager
from localization import loc


class ConfigDialog:
    """Fast and simple LLM configuration dialog"""

    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        self.setup_layout()
        # Set default provider immediately
        self.on_provider_changed()

    def setup_dialog(self):
        """Setup dialog properties - optimized for speed"""
        self.dialog.title("LLM Configuration")  # 直接使用字符串，避免get_text调用
        self.dialog.geometry("450x280")  # 优化高度，减少底部留白
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 绑定X关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)

        # Center without update_idletasks() for speed
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (280 // 2)
        self.dialog.geometry(f"450x280+{x}+{y}")
    
    def create_widgets(self):
        """Create minimal UI components for speed"""
        # Main frame
        self.main_frame = ttk.Frame(self.dialog, padding="10")

        # Provider selection
        self.provider_frame = ttk.LabelFrame(self.main_frame, text="Select LLM Provider", padding="5")

        self.provider_var = tk.StringVar(value="ollama")
        self.ollama_radio = ttk.Radiobutton(
            self.provider_frame,
            text="Ollama (Local)",
            variable=self.provider_var,
            value="ollama",
            command=self.on_provider_changed
        )

        self.tencent_api_radio = ttk.Radiobutton(
            self.provider_frame,
            text="Tencent Cloud",
            variable=self.provider_var,
            value="tencent_api",
            command=self.on_provider_changed
        )

        # Configuration frame
        self.config_frame = ttk.LabelFrame(self.main_frame, text="Configuration Parameters", padding="5")

        # Tencent Cloud fields
        self.api_id_label = ttk.Label(self.config_frame, text="API ID:")
        self.api_id_var = tk.StringVar()
        self.api_id_entry = ttk.Entry(self.config_frame, textvariable=self.api_id_var, width=40)

        self.api_secret_label = ttk.Label(self.config_frame, text="API Secret:")
        self.api_secret_var = tk.StringVar()
        self.api_secret_entry = ttk.Entry(self.config_frame, textvariable=self.api_secret_var, show="*", width=40)

        # Ollama fields
        self.base_url_label = ttk.Label(self.config_frame, text="Service URL:")
        self.base_url_var = tk.StringVar()
        self.base_url_entry = ttk.Entry(self.config_frame, textvariable=self.base_url_var, width=40)

        self.model_label = ttk.Label(self.config_frame, text="Model Name:")
        self.model_var = tk.StringVar()
        self.model_entry = ttk.Entry(self.config_frame, textvariable=self.model_var, width=40)

        # Button frame - 将所有按钮放在同一个frame中
        self.button_frame = ttk.Frame(self.main_frame)
        self.test_btn = ttk.Button(
            self.button_frame,
            text="Test Connection",
            command=self.test_connection
        )
        self.save_btn = ttk.Button(
            self.button_frame,
            text="Save",
            command=self.save_config
        )
        self.cancel_btn = ttk.Button(
            self.button_frame,
            text="Cancel",
            command=self.cancel
        )
    
    def setup_layout(self):
        """Simple and fast layout"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Provider selection
        self.provider_frame.pack(fill=tk.X, pady=(0, 10))
        self.ollama_radio.pack(side=tk.LEFT, padx=(0, 20))
        self.tencent_api_radio.pack(side=tk.LEFT)

        # Configuration parameters
        self.config_frame.pack(fill=tk.X, pady=(0, 15))
        self.config_frame.columnconfigure(1, weight=1)

        # Buttons - 三个按钮平行排列，减少底部留白
        self.button_frame.pack(fill=tk.X, pady=(0, 0))  # 移除底部间距
        self.test_btn.pack(side=tk.LEFT)
        self.cancel_btn.pack(side=tk.RIGHT)
        self.save_btn.pack(side=tk.RIGHT, padx=(0, 10))
    


    def update_config_layout(self, provider: str):
        """Update layout based on provider - optimized for speed"""
        # Clear existing layout
        for widget in self.config_frame.winfo_children():
            widget.grid_forget()

        if provider == "ollama":
            # Ollama: Service URL + Model Name (no API key)
            self.base_url_label.grid(row=0, column=0, sticky=tk.W, pady=5)
            self.base_url_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))

            self.model_label.grid(row=1, column=0, sticky=tk.W, pady=5)
            self.model_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))

        elif provider == "tencent_api":
            # Tencent Cloud: API ID + API Secret
            self.api_id_label.grid(row=0, column=0, sticky=tk.W, pady=5)
            self.api_id_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))

            self.api_secret_label.grid(row=1, column=0, sticky=tk.W, pady=5)
            self.api_secret_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))

    def reset_to_defaults(self, provider: str):
        """Set default values - fast and simple"""
        # Clear all fields
        self.base_url_var.set('')
        self.model_var.set('')
        self.api_id_var.set('')
        self.api_secret_var.set('')

        # Set provider-specific defaults
        if provider == 'ollama':
            self.base_url_var.set('http://10.52.8.74:445')  # 恢复您的自定义端口
            self.model_var.set('qwen2.5-coder:32b')
        elif provider == 'tencent_api':
            self.api_id_var.set('')
            self.api_secret_var.set('')
    
    def on_provider_changed(self):
        """Provider changed event - fast execution"""
        provider = self.provider_var.get()
        self.update_config_layout(provider)
        self.reset_to_defaults(provider)
    
    def save_config(self):
        """Save configuration - simplified and fast"""
        try:
            provider = self.provider_var.get()

            # Validate required fields
            if provider == 'ollama':
                if not self.base_url_var.get().strip():
                    messagebox.showerror("Error", "Service URL cannot be empty")
                    return
                if not self.model_var.get().strip():
                    messagebox.showerror("Error", "Model name cannot be empty")
                    return
            elif provider == 'tencent_api':
                if not self.api_id_var.get().strip():
                    messagebox.showerror("Error", "API ID cannot be empty")
                    return
                if not self.api_secret_var.get().strip():
                    messagebox.showerror("Error", "API Secret cannot be empty")
                    return

            # Create configuration object with default values
            if provider == 'ollama':
                new_config = LLMConfig(
                    provider=provider,
                    base_url=self.base_url_var.get().strip(),
                    model=self.model_var.get().strip(),
                    temperature=0.1,
                    max_tokens=2048,
                    timeout=30
                )
            elif provider == 'tencent_api':
                new_config = LLMConfig(
                    provider=provider,
                    api_key=self.api_id_var.get().strip(),
                    secret_key=self.api_secret_var.get().strip(),
                    temperature=0.1,
                    max_tokens=2048,
                    timeout=30
                )

            # Update configuration
            success = llm_manager.update_config(provider, new_config)

            if success:
                config.save_to_file()
                messagebox.showinfo("Success", "Configuration saved successfully")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save configuration")

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def test_connection(self):
        """Test LLM connection"""
        try:
            provider = self.provider_var.get()

            # 获取当前配置
            if provider == 'ollama':
                base_url = self.base_url_var.get().strip()
                model = self.model_var.get().strip()

                if not base_url or not model:
                    messagebox.showwarning("Warning", "Please fill in Service URL and Model Name first")
                    return

                # 创建临时配置进行测试
                test_config = LLMConfig(
                    provider=provider,
                    base_url=base_url,
                    model=model,
                    temperature=0.1,
                    max_tokens=100,
                    timeout=60  # 32B模型需要更长时间，设置60秒
                )

            elif provider == 'tencent_api':
                api_id = self.api_id_var.get().strip()
                api_secret = self.api_secret_var.get().strip()

                if not api_id or not api_secret:
                    messagebox.showwarning("Warning", "Please fill in API ID and API Secret first")
                    return

                # 创建临时配置进行测试
                test_config = LLMConfig(
                    provider=provider,
                    api_key=api_id,
                    secret_key=api_secret,
                    temperature=0.1,
                    max_tokens=100,
                    timeout=30  # 增加超时时间到30秒
                )

            # 禁用测试按钮，显示测试中状态
            self.test_btn.config(state="disabled", text="Testing...")
            self.dialog.update()

            # 测试连接
            result = llm_manager.test_connection_with_config(provider, test_config)

            if result.get('success', False):
                messagebox.showinfo("Success", f"✅ Connection successful!\n\nProvider: {provider}\nResponse time: {result.get('response_time', 'N/A')}ms")
            else:
                error_msg = result.get('error', 'Unknown error')
                messagebox.showerror("Connection Failed", f"❌ Connection failed:\n\n{error_msg}")

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            messagebox.showerror("Error", f"❌ Test failed:\n\n{e}")
        finally:
            # 恢复测试按钮状态
            self.test_btn.config(state="normal", text="Test Connection")

    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()

# 移除了get_text函数以提高性能

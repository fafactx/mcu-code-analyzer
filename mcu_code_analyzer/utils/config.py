"""
配置管理系统 - 支持YAML配置文件、环境变量和运行时配置
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """LLM配置类"""
    provider: str = "ollama"
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 30

    # 腾讯云特有参数
    secret_id: str = ""
    secret_key: str = ""
    region: str = "ap-beijing"
    app_id: str = ""

    @classmethod
    def get_default_config(cls, provider: str) -> 'LLMConfig':
        """获取指定提供商的默认配置"""
        defaults = {
            'ollama': cls(
                provider='ollama',
                base_url='http://localhost:11434',
                model='llama2',
                api_key='',  # Ollama不需要API密钥
            ),
            'tencent_api': cls(
                provider='tencent_api',
                base_url='https://api.hunyuan.cloud.tencent.com/v1/',
                model='hunyuan-lite',
                api_key='',  # 混元API密钥
            ),
            'tencent_sdk': cls(
                provider='tencent_sdk',
                base_url='https://hunyuan.tencentcloudapi.com',
                model='hunyuan-lite',
                secret_id='',  # 腾讯云Secret ID
                secret_key='',  # 腾讯云Secret Key
                region='ap-beijing',
                api_key='',  # SDK方式不使用API Key
            )
        }
        return defaults.get(provider, cls())

    def get_required_fields(self) -> list:
        """获取当前提供商的必填字段"""
        required_fields = {
            'ollama': ['base_url', 'model'],
            'tencent_api': ['api_key', 'base_url', 'model'],
            'tencent_sdk': ['secret_id', 'secret_key', 'model']
        }
        return required_fields.get(self.provider, ['base_url', 'model'])

    def validate(self) -> tuple[bool, str]:
        """验证配置是否有效"""
        required = self.get_required_fields()

        for field in required:
            value = getattr(self, field, '')
            if not value or value.strip() == '':
                field_names = {
                    'api_key': 'API密钥',
                    'base_url': '基础URL',
                    'model': '模型名称',
                    'secret_id': 'SecretId',
                    'secret_key': 'SecretKey',
                    'region': '地区'
                }
                return False, f"{field_names.get(field, field)} 不能为空"

        # URL格式验证
        if self.base_url and not (self.base_url.startswith('http://') or self.base_url.startswith('https://')):
            return False, "基础URL必须以http://或https://开头"

        return True, "配置验证通过"


@dataclass
class AnalyzerConfig:
    """分析器配置类"""
    supported_extensions: list = field(default_factory=lambda: [".c", ".h", ".cpp", ".hpp"])
    exclude_dirs: list = field(default_factory=lambda: ["build", "debug", "release", ".git"])
    max_file_size: int = 10  # MB
    analysis_timeout: int = 300  # 秒


@dataclass
class UIConfig:
    """UI配置类"""
    window_width: int = 1200
    window_height: int = 800
    window_title: str = "STM32工程分析器 v2.0"
    theme_primary: str = "#2196F3"
    theme_secondary: str = "#FFC107"
    font_default: str = "Microsoft YaHei"
    font_code: str = "Consolas"
    font_size: int = 10


class Config:
    """配置管理器 - 单例模式"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._config_data = {}
            self._config_file = None
            self.analyzer = AnalyzerConfig()
            self.ui = UIConfig()
            self.llm_configs = {}
            self._load_default_config()
            Config._initialized = True
    
    def _load_default_config(self):
        """加载默认配置"""
        # 查找配置文件
        possible_paths = [
            Path(__file__).parent.parent / "config.yaml",
            Path.cwd() / "config.yaml",
            Path.cwd() / "stm32_analyzer" / "config.yaml"
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                self._config_file = config_path
                break
        
        if self._config_file:
            self.load_from_file(self._config_file)
        else:
            print("⚠️ 未找到配置文件，使用默认配置")
    
    def load_from_file(self, config_path: Path) -> bool:
        """从YAML文件加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f)
            
            self._parse_config()
            print(f"✅ 配置文件加载成功: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            return False
    
    def _parse_config(self):
        """解析配置数据"""
        # 解析分析器配置
        if 'analyzer' in self._config_data:
            analyzer_data = self._config_data['analyzer']
            self.analyzer = AnalyzerConfig(
                supported_extensions=analyzer_data.get('supported_extensions', [".c", ".h"]),
                exclude_dirs=analyzer_data.get('exclude_dirs', ["build", "debug"]),
                max_file_size=analyzer_data.get('max_file_size', 10),
                analysis_timeout=analyzer_data.get('analysis_timeout', 300)
            )
        
        # 解析UI配置
        if 'ui' in self._config_data:
            ui_data = self._config_data['ui']
            window_data = ui_data.get('window', {})
            theme_data = ui_data.get('theme', {})
            fonts_data = ui_data.get('fonts', {})
            
            self.ui = UIConfig(
                window_width=window_data.get('width', 1200),
                window_height=window_data.get('height', 800),
                window_title=window_data.get('title', "STM32工程分析器 v2.0"),
                theme_primary=theme_data.get('primary_color', "#2196F3"),
                theme_secondary=theme_data.get('secondary_color', "#FFC107"),
                font_default=fonts_data.get('default', "Microsoft YaHei"),
                font_code=fonts_data.get('code', "Consolas"),
                font_size=fonts_data.get('size', 10)
            )
        
        # 解析LLM配置
        if 'llm' in self._config_data:
            llm_data = self._config_data['llm']

            # Ollama配置
            if 'ollama' in llm_data:
                ollama_data = llm_data['ollama']
                self.llm_configs['ollama'] = LLMConfig(
                    provider="ollama",
                    base_url=ollama_data.get('base_url', 'http://localhost:11434'),
                    model=ollama_data.get('model', 'llama2'),
                    temperature=ollama_data.get('temperature', 0.1),
                    timeout=ollama_data.get('timeout', 200)
                )

            # 腾讯云混元API配置
            if 'tencent_api' in llm_data:
                tencent_api_data = llm_data['tencent_api']
                self.llm_configs['tencent_api'] = LLMConfig(
                    provider="tencent_api",
                    api_key=tencent_api_data.get('api_key', ''),
                    base_url=tencent_api_data.get('base_url', 'https://api.hunyuan.cloud.tencent.com/v1/'),
                    model=tencent_api_data.get('model', 'hunyuan-lite'),
                    temperature=tencent_api_data.get('temperature', 0.1),
                    max_tokens=tencent_api_data.get('max_tokens', 2048),
                    timeout=tencent_api_data.get('timeout', 30)
                )

            # 腾讯云混元SDK配置
            if 'tencent_sdk' in llm_data:
                tencent_sdk_data = llm_data['tencent_sdk']
                self.llm_configs['tencent_sdk'] = LLMConfig(
                    provider="tencent_sdk",
                    secret_id=tencent_sdk_data.get('secret_id', ''),
                    secret_key=tencent_sdk_data.get('secret_key', ''),
                    region=tencent_sdk_data.get('region', 'ap-beijing'),
                    base_url=tencent_sdk_data.get('base_url', 'https://hunyuan.tencentcloudapi.com'),
                    model=tencent_sdk_data.get('model', 'hunyuan-lite'),
                    temperature=tencent_sdk_data.get('temperature', 0.1),
                    max_tokens=tencent_sdk_data.get('max_tokens', 2048),
                    timeout=tencent_sdk_data.get('timeout', 30)
                )
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        config = self._config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_llm_config(self, provider: str) -> Optional[LLMConfig]:
        """获取指定LLM提供商的配置"""
        return self.llm_configs.get(provider)
    
    def update_llm_config(self, provider: str, config: LLMConfig):
        """更新LLM配置"""
        self.llm_configs[provider] = config
    
    def get_interface_patterns(self) -> Dict[str, list]:
        """获取接口模式配置"""
        return self.get('interface_analysis.patterns', {})
    
    def get_chip_series_mapping(self) -> Dict[str, str]:
        """获取芯片系列映射"""
        return self.get('chip_detection.stm32_series', {})
    
    def save_to_file(self, config_path: Optional[Path] = None) -> bool:
        """保存配置到文件"""
        if config_path is None:
            config_path = self._config_file
        
        if config_path is None:
            print("❌ 没有指定配置文件路径")
            return False
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config_data, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            print(f"✅ 配置已保存到: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def reload(self):
        """重新加载配置"""
        if self._config_file:
            self.load_from_file(self._config_file)
    
    def get_output_dir(self, base_path: Path) -> Path:
        """获取输出目录"""
        output_dir_name = self.get('output.default_dir', 'Analyzer_Output')
        return base_path / output_dir_name
    
    def is_debug_mode(self) -> bool:
        """是否为调试模式"""
        return self.get('app.debug', False)
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get('app.log_level', 'INFO')


# 全局配置实例
config = Config()

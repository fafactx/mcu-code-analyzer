"""
版本管理工具模块
提供版本号获取、更新和同步功能
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class VersionManager:
    """版本管理器"""
    
    def __init__(self, config_path: str = None):
        """初始化版本管理器
        
        Args:
            config_path: 配置文件路径，默认为当前目录的config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.project_root = self.config_path.parent
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"无法加载配置文件 {self.config_path}: {e}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise RuntimeError(f"无法保存配置文件 {self.config_path}: {e}")
    
    def get_version(self) -> str:
        """获取当前版本号"""
        return self._config.get('app', {}).get('version', '0.1.0')
    
    def get_version_info(self) -> Dict:
        """获取详细版本信息"""
        app_config = self._config.get('app', {})
        version_info = app_config.get('version_info', {})
        
        return {
            'version': app_config.get('version', '0.1.0'),
            'major': version_info.get('major', 0),
            'minor': version_info.get('minor', 1),
            'patch': version_info.get('patch', 0),
            'build': version_info.get('build', 1),
            'release_date': version_info.get('release_date', datetime.now().strftime('%Y-%m-%d')),
            'description': version_info.get('description', 'No description')
        }
    
    def update_version(self, major: int = None, minor: int = None, patch: int = None, 
                      build: int = None, description: str = None) -> str:
        """更新版本号
        
        Args:
            major: 主版本号
            minor: 次版本号  
            patch: 补丁版本号
            build: 构建号
            description: 版本描述
            
        Returns:
            新的版本号字符串
        """
        version_info = self.get_version_info()
        
        # 更新版本号组件
        if major is not None:
            version_info['major'] = major
        if minor is not None:
            version_info['minor'] = minor
        if patch is not None:
            version_info['patch'] = patch
        if build is not None:
            version_info['build'] = build
        if description is not None:
            version_info['description'] = description
        
        # 更新发布日期
        version_info['release_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # 生成新版本号
        new_version = f"{version_info['major']}.{version_info['minor']}.{version_info['patch']}"
        
        # 更新配置
        if 'app' not in self._config:
            self._config['app'] = {}
        
        self._config['app']['version'] = new_version
        self._config['app']['version_info'] = {
            'major': version_info['major'],
            'minor': version_info['minor'], 
            'patch': version_info['patch'],
            'build': version_info['build'],
            'release_date': version_info['release_date'],
            'description': version_info['description']
        }
        
        # 保存配置
        self._save_config()
        
        return new_version
    
    def increment_version(self, level: str = 'patch', description: str = None) -> str:
        """递增版本号
        
        Args:
            level: 递增级别 ('major', 'minor', 'patch', 'build')
            description: 版本描述
            
        Returns:
            新的版本号字符串
        """
        version_info = self.get_version_info()
        
        if level == 'major':
            return self.update_version(
                major=version_info['major'] + 1,
                minor=0,
                patch=0,
                build=1,
                description=description
            )
        elif level == 'minor':
            return self.update_version(
                minor=version_info['minor'] + 1,
                patch=0,
                build=1,
                description=description
            )
        elif level == 'patch':
            return self.update_version(
                patch=version_info['patch'] + 1,
                build=1,
                description=description
            )
        elif level == 'build':
            return self.update_version(
                build=version_info['build'] + 1,
                description=description
            )
        else:
            raise ValueError(f"无效的版本级别: {level}")
    
    def sync_version_to_files(self) -> List[str]:
        """同步版本号到所有相关文件

        Returns:
            已更新的文件列表
        """
        version = self.get_version()
        updated_files = []

        # 更新项目根目录的spec文件
        root_spec_files = list(self.project_root.parent.glob("*.spec"))
        for spec_file in root_spec_files:
            if self._update_spec_file(spec_file, version):
                updated_files.append(str(spec_file))

        # 更新mcu_code_analyzer目录的spec文件
        spec_files = list(self.project_root.glob("*.spec"))
        for spec_file in spec_files:
            if self._update_spec_file(spec_file, version):
                updated_files.append(str(spec_file))

        # 更新setup.py
        setup_file = self.project_root / "setup.py"
        if setup_file.exists():
            if self._update_setup_file(setup_file, version):
                updated_files.append(str(setup_file))

        # 更新__init__.py
        init_file = self.project_root / "__init__.py"
        if init_file.exists():
            if self._update_init_file(init_file, version):
                updated_files.append(str(init_file))

        return updated_files
    
    def _update_spec_file(self, spec_file: Path, version: str) -> bool:
        """更新spec文件中的版本号"""
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新version参数
            pattern = r"version\s*=\s*['\"][^'\"]*['\"]"
            replacement = f"version='{version}'"
            new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                with open(spec_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            
        except Exception as e:
            print(f"更新spec文件失败 {spec_file}: {e}")
        
        return False
    
    def _update_setup_file(self, setup_file: Path, version: str) -> bool:
        """更新setup.py文件中的版本号"""
        try:
            with open(setup_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新version参数
            pattern = r"version\s*=\s*['\"][^'\"]*['\"]"
            replacement = f"version='{version}'"
            new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                with open(setup_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            
        except Exception as e:
            print(f"更新setup.py文件失败: {e}")
        
        return False
    
    def _update_init_file(self, init_file: Path, version: str) -> bool:
        """更新__init__.py文件中的版本号"""
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找__version__定义
            pattern = r"__version__\s*=\s*['\"][^'\"]*['\"]"
            replacement = f"__version__ = '{version}'"
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
            else:
                # 如果没有__version__定义，添加一个
                new_content = f"__version__ = '{version}'\n" + content
            
            if new_content != content:
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            
        except Exception as e:
            print(f"更新__init__.py文件失败: {e}")
        
        return False
    
    def get_version_display_string(self) -> str:
        """获取用于显示的版本字符串"""
        version_info = self.get_version_info()
        return f"v{version_info['version']} (Build {version_info['build']}) - {version_info['release_date']}"


# 全局版本管理器实例
_version_manager = None

def get_version_manager() -> VersionManager:
    """获取全局版本管理器实例"""
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionManager()
    return _version_manager

def get_current_version() -> str:
    """获取当前版本号"""
    return get_version_manager().get_version()

def get_version_display() -> str:
    """获取版本显示字符串"""
    return get_version_manager().get_version_display_string()

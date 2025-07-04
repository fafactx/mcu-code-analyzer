#!/usr/bin/env python3
"""
MCU Code Analyzer v2.1.0 发布脚本
自动化版本发布流程
"""

import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime
from pathlib import Path

class ReleaseBuilder:
    def __init__(self):
        self.version = "2.1.0"
        self.project_name = "MCU_Code_Analyzer"
        self.release_dir = Path("releases")
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        
    def print_banner(self):
        """打印发布横幅"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                MCU Code Analyzer v{self.version} 发布工具                ║
║                                                              ║
║  🚀 自动化版本发布流程                                          ║
║  📦 创建分发包和安装程序                                        ║
║  📝 生成发布文档                                               ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def clean_build_dirs(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✅ 已清理: {dir_path}")
        
        # 创建发布目录
        self.release_dir.mkdir(exist_ok=True)
        print(f"  ✅ 发布目录: {self.release_dir}")
    
    def verify_version_consistency(self):
        """验证版本号一致性"""
        print("🔍 验证版本号一致性...")
        
        files_to_check = [
            ("mcu_code_analyzer/config.yaml", f"MCU Code Analyzer v{self.version}"),
            ("mcu_code_analyzer/setup.py", f'version="{self.version}"'),
            ("mcu_code_analyzer/__init__.py", f'__version__ = "{self.version}"')
        ]
        
        all_consistent = True
        for file_path, expected_content in files_to_check:
            if Path(file_path).exists():
                content = Path(file_path).read_text(encoding='utf-8')
                if expected_content in content:
                    print(f"  ✅ {file_path}: 版本号正确")
                else:
                    print(f"  ❌ {file_path}: 版本号不匹配")
                    all_consistent = False
            else:
                print(f"  ⚠️  {file_path}: 文件不存在")
                all_consistent = False
        
        if not all_consistent:
            print("❌ 版本号不一致，请检查并修复")
            return False
        
        print("✅ 所有文件版本号一致")
        return True
    
    def create_source_package(self):
        """创建源码包"""
        print("📦 创建源码包...")
        
        # 源码包文件名
        source_package = self.release_dir / f"{self.project_name}_v{self.version}_Source.zip"
        
        # 要包含的文件和目录
        include_patterns = [
            "mcu_code_analyzer/**/*.py",
            "mcu_code_analyzer/**/*.yaml",
            "mcu_code_analyzer/**/*.yml", 
            "mcu_code_analyzer/**/*.md",
            "mcu_code_analyzer/**/*.txt",
            "mcu_code_analyzer/**/*.json",
            "*.md",
            "*.txt",
            "requirements.txt",
            "RELEASE_NOTES_v2.1.0.md"
        ]
        
        # 排除的目录
        exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".git",
            ".pytest_cache",
            "build",
            "dist",
            "releases",
            "*.log"
        ]
        
        with zipfile.ZipFile(source_package, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pattern in include_patterns:
                for file_path in Path(".").glob(pattern):
                    if file_path.is_file():
                        # 检查是否应该排除
                        should_exclude = False
                        for exclude in exclude_patterns:
                            if exclude in str(file_path):
                                should_exclude = True
                                break
                        
                        if not should_exclude:
                            zipf.write(file_path, file_path)
                            print(f"  📄 添加: {file_path}")
        
        print(f"✅ 源码包已创建: {source_package}")
        return source_package
    
    def create_portable_package(self):
        """创建便携版包"""
        print("📦 创建便携版包...")
        
        portable_package = self.release_dir / f"{self.project_name}_v{self.version}_Portable.zip"
        
        # 便携版包含所有文件，包括portable_nodejs
        with zipfile.ZipFile(portable_package, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("mcu_code_analyzer"):
                # 排除一些不必要的文件
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if not file.endswith('.pyc') and not file.startswith('.'):
                        file_path = Path(root) / file
                        zipf.write(file_path, file_path)
            
            # 添加根目录的重要文件
            important_files = [
                "README.md",
                "requirements.txt", 
                "RELEASE_NOTES_v2.1.0.md"
            ]
            
            for file_name in important_files:
                if Path(file_name).exists():
                    zipf.write(file_name, file_name)
        
        print(f"✅ 便携版包已创建: {portable_package}")
        return portable_package
    
    def create_test_tools_package(self):
        """创建测试工具包"""
        print("📦 创建测试工具包...")
        
        test_package = self.release_dir / f"{self.project_name}_v{self.version}_TestTools.zip"
        
        # 测试工具文件
        test_files = [
            "mermaid_online_tester.py",
            "test_mermaid_ink.py", 
            "test_mermaid_live.py",
            "test_all_mermaid_apis.py",
            "test_more_apis.py",
            "simple_kroki_test.py",
            "test_kroki.py",
            "test_backup_apis.py"
        ]
        
        with zipfile.ZipFile(test_package, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_name in test_files:
                if Path(file_name).exists():
                    zipf.write(file_name, file_name)
                    print(f"  🔧 添加测试工具: {file_name}")
            
            # 添加说明文档
            readme_content = """# MCU Code Analyzer v2.1.0 测试工具包

## 🧪 测试工具说明

### 主要测试工具
- `mermaid_online_tester.py` - 全面测试各种在线mermaid渲染服务
- `test_mermaid_ink.py` - 专门测试Mermaid.ink服务
- `test_mermaid_live.py` - 测试Mermaid Live Editor
- `simple_kroki_test.py` - 简单的Kroki.io连接测试

### 使用方法
```bash
# 运行全面测试
python mermaid_online_tester.py

# 测试特定服务
python test_mermaid_ink.py
python test_mermaid_live.py
```

### 测试结果
测试工具会生成详细的报告，包括：
- 服务可用性
- 响应时间
- 成功率统计
- 配置建议

### 网络要求
- 需要互联网连接
- 某些服务可能需要VPN
- 建议在不同网络环境下测试
"""
            
            zipf.writestr("README_TestTools.md", readme_content)
        
        print(f"✅ 测试工具包已创建: {test_package}")
        return test_package
    
    def generate_release_summary(self, packages):
        """生成发布摘要"""
        print("📝 生成发布摘要...")
        
        summary_file = self.release_dir / f"Release_Summary_v{self.version}.md"
        
        summary_content = f"""# MCU Code Analyzer v{self.version} 发布摘要

## 📅 发布信息
- **版本**: v{self.version}
- **发布日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **发布类型**: 功能增强版本

## 📦 发布包

### 1. 源码包
- **文件**: {packages['source'].name}
- **大小**: {packages['source'].stat().st_size / 1024 / 1024:.1f} MB
- **内容**: 完整源代码，适合开发者

### 2. 便携版
- **文件**: {packages['portable'].name}
- **大小**: {packages['portable'].stat().st_size / 1024 / 1024:.1f} MB  
- **内容**: 包含所有依赖，开箱即用

### 3. 测试工具包
- **文件**: {packages['test_tools'].name}
- **大小**: {packages['test_tools'].stat().st_size / 1024:.1f} KB
- **内容**: 网络诊断和API测试工具

## 🚀 主要更新

### 新功能
- ✅ 多API在线mermaid渲染支持
- ✅ 智能编码方式选择
- ✅ 网络诊断工具集
- ✅ 备用API自动切换

### 问题修复
- ❌ 修复mermaid语法兼容性问题
- ❌ 改进网络错误处理
- ❌ 优化函数名显示

### 性能优化
- ⚡ 响应时间改进
- ⚡ 重试机制优化
- ⚡ 资源使用优化

## 📋 安装说明

### 源码版安装
```bash
# 解压源码包
unzip {packages['source'].name}

# 安装依赖
pip install -r requirements.txt

# 运行程序
python mcu_code_analyzer/main_gui.py
```

### 便携版使用
```bash
# 解压便携版
unzip {packages['portable'].name}

# 直接运行
python mcu_code_analyzer/main_gui.py
```

### 测试工具使用
```bash
# 解压测试工具包
unzip {packages['test_tools'].name}

# 运行网络诊断
python mermaid_online_tester.py
```

## 🔧 系统要求
- **Python**: 3.8+
- **操作系统**: Windows 10+, Linux, macOS
- **内存**: 建议512MB+
- **网络**: 在线功能需要互联网连接

## 📞 技术支持
如遇问题请：
1. 查看RELEASE_NOTES_v{self.version}.md
2. 运行测试工具诊断网络
3. 检查系统要求

---
**MCU Code Analyzer v{self.version}** - 让MCU代码分析更智能！
"""
        
        summary_file.write_text(summary_content, encoding='utf-8')
        print(f"✅ 发布摘要已生成: {summary_file}")
        
        return summary_file
    
    def run_release(self):
        """执行完整的发布流程"""
        self.print_banner()
        
        try:
            # 1. 清理构建目录
            self.clean_build_dirs()
            
            # 2. 验证版本一致性
            if not self.verify_version_consistency():
                return False
            
            # 3. 创建各种发布包
            packages = {}
            packages['source'] = self.create_source_package()
            packages['portable'] = self.create_portable_package()
            packages['test_tools'] = self.create_test_tools_package()
            
            # 4. 生成发布摘要
            summary = self.generate_release_summary(packages)
            
            # 5. 显示发布结果
            print("\n" + "="*60)
            print("🎉 MCU Code Analyzer v2.1.0 发布完成!")
            print("="*60)
            print(f"📁 发布目录: {self.release_dir.absolute()}")
            print(f"📦 源码包: {packages['source'].name}")
            print(f"📦 便携版: {packages['portable'].name}")
            print(f"🔧 测试工具: {packages['test_tools'].name}")
            print(f"📝 发布摘要: {summary.name}")
            print("\n✅ 所有发布包已准备就绪!")
            
            return True
            
        except Exception as e:
            print(f"❌ 发布过程中出现错误: {e}")
            return False

def main():
    """主函数"""
    builder = ReleaseBuilder()
    success = builder.run_release()
    
    if success:
        print("\n🎊 发布成功! 可以开始分发了!")
        sys.exit(0)
    else:
        print("\n💥 发布失败! 请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()

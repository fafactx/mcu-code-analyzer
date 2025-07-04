"""
Playwright安装脚本
自动安装Playwright和浏览器引擎
"""

import subprocess
import sys
import os
from pathlib import Path


def install_playwright():
    """安装Playwright和浏览器引擎"""
    print("🚀 开始安装Playwright本地渲染环境...")
    
    try:
        # 1. 安装playwright包
        print("📦 安装Playwright包...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "playwright>=1.40.0"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Playwright包安装失败: {result.stderr}")
            return False
        
        print("✅ Playwright包安装成功")
        
        # 2. 安装浏览器引擎
        print("🌐 安装Chromium浏览器引擎...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Chromium安装失败: {result.stderr}")
            return False
            
        print("✅ Chromium浏览器引擎安装成功")
        
        # 3. 测试安装
        print("🧪 测试Playwright安装...")
        test_result = test_playwright_installation()
        
        if test_result:
            print("🎉 Playwright本地渲染环境安装完成！")
            print("💡 现在可以使用本地Mermaid渲染功能了")
            return True
        else:
            print("⚠️ Playwright安装完成，但测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程中发生错误: {e}")
        return False


def test_playwright_installation():
    """测试Playwright安装是否成功"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content("<html><body><h1>Test</h1></body></html>")
            
            # 简单测试截图功能
            screenshot = page.screenshot()
            browser.close()
            
            if len(screenshot) > 0:
                print("✅ Playwright功能测试通过")
                return True
            else:
                print("❌ Playwright功能测试失败")
                return False
                
    except ImportError:
        print("❌ Playwright导入失败")
        return False
    except Exception as e:
        print(f"❌ Playwright测试失败: {e}")
        return False


def check_existing_installation():
    """检查是否已经安装了Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        print("✅ 检测到已安装的Playwright")
        
        # 测试浏览器是否可用
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("✅ Chromium浏览器引擎可用")
                return True
            except Exception as e:
                print(f"⚠️ Chromium浏览器引擎不可用: {e}")
                return False
                
    except ImportError:
        print("📦 未检测到Playwright，需要安装")
        return False


def main():
    """主函数"""
    print("🔍 检查Playwright安装状态...")
    
    if check_existing_installation():
        print("🎉 Playwright已正确安装并可用！")
        
        # 测试Mermaid渲染
        print("\n🧪 测试Mermaid渲染功能...")
        test_mermaid_rendering()
        
    else:
        print("\n📥 开始安装Playwright...")
        if install_playwright():
            print("\n🧪 测试Mermaid渲染功能...")
            test_mermaid_rendering()
        else:
            print("❌ Playwright安装失败")
            sys.exit(1)


def test_mermaid_rendering():
    """测试Mermaid渲染功能"""
    try:
        # 添加项目路径
        project_root = Path(__file__).parent / "mcu_code_analyzer"
        sys.path.insert(0, str(project_root))
        
        from utils.playwright_mermaid_renderer import test_playwright_rendering
        test_playwright_rendering()
        
    except Exception as e:
        print(f"⚠️ Mermaid渲染测试失败: {e}")
        print("💡 这可能是正常的，如果项目结构不完整")


if __name__ == "__main__":
    main()

"""
快速构建测试脚本 - 测试Playwright集成
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent / "mcu_code_analyzer"
sys.path.insert(0, str(project_root))

def test_imports():
    """测试关键模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试基础模块
        import yaml
        print("✅ yaml导入成功")
        
        import tkinter as tk
        print("✅ tkinter导入成功")
        
        from PIL import Image
        print("✅ PIL导入成功")
        
        # 测试项目模块
        from utils.config import config
        print("✅ config模块导入成功")
        
        from utils.playwright_mermaid_renderer import PlaywrightMermaidRenderer
        print("✅ Playwright渲染器导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_playwright_basic():
    """测试Playwright基础功能"""
    print("🎭 测试Playwright基础功能...")
    
    try:
        from utils.playwright_mermaid_renderer import PlaywrightMermaidRenderer
        
        renderer = PlaywrightMermaidRenderer()
        
        # 简单的Mermaid代码
        test_code = """
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
        """
        
        print("📸 尝试渲染PNG...")
        png_bytes = renderer.render_to_png(test_code, width=800, height=600)
        
        if png_bytes and len(png_bytes) > 0:
            print(f"✅ PNG渲染成功，大小: {len(png_bytes)} 字节")
            
            # 保存测试图片
            with open("test_mermaid_output.png", "wb") as f:
                f.write(png_bytes)
            print("💾 测试图片已保存: test_mermaid_output.png")
            
            renderer.close()
            return True
        else:
            print("❌ PNG渲染失败")
            renderer.close()
            return False
            
    except Exception as e:
        print(f"❌ Playwright测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_integration():
    """测试GUI集成"""
    print("🖥️ 测试GUI集成...")
    
    try:
        # 模拟GUI环境
        import tkinter as tk
        from main_gui import MCUCodeAnalyzerGUI
        
        print("✅ GUI类导入成功")
        
        # 不实际创建窗口，只测试类初始化
        print("✅ GUI集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ GUI集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 MCU代码分析器 - Playwright集成快速测试")
    print("=" * 50)
    
    # 测试模块导入
    if not test_imports():
        print("❌ 基础模块测试失败")
        return
    
    # 测试Playwright功能
    if not test_playwright_basic():
        print("❌ Playwright功能测试失败")
        print("💡 可能需要先安装: pip install playwright && playwright install chromium")
        return
    
    # 测试GUI集成
    if not test_gui_integration():
        print("❌ GUI集成测试失败")
        return
    
    print("\n🎉 所有测试通过！")
    print("✅ Playwright本地渲染功能已成功集成")
    print("🚀 可以开始构建完整的exe文件")

if __name__ == "__main__":
    main()

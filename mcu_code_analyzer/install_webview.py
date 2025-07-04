#!/usr/bin/env python3
"""
安装webview库以支持内嵌Mermaid图表渲染
"""

import subprocess
import sys
import os

def install_webview():
    """安装pywebview库"""
    print("🚀 正在安装pywebview库以支持内嵌图表渲染...")
    
    try:
        # 尝试安装pywebview
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
        print("✅ pywebview安装成功！")
        
        # 检查是否需要安装额外的依赖
        if os.name == 'nt':  # Windows
            print("🔧 检测到Windows系统，安装Edge WebView2支持...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview[cef]"])
                print("✅ Edge WebView2支持安装成功！")
            except:
                print("⚠️ Edge WebView2支持安装失败，将使用默认渲染器")
        
        print("\n🎉 安装完成！现在可以使用'🖼️ 内嵌渲染'功能了")
        print("\n特点：")
        print("• 在独立窗口中显示Mermaid图表")
        print("• 不依赖外部浏览器")
        print("• 支持完整的交互和缩放")
        print("• 更好的用户体验")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        print("\n💡 解决方案：")
        print("1. 检查网络连接")
        print("2. 尝试手动安装: pip install pywebview")
        print("3. 如果仍然失败，可以使用浏览器渲染功能")
        return False
    except Exception as e:
        print(f"❌ 安装过程中出现错误: {e}")
        return False

def check_webview_available():
    """检查webview是否可用"""
    try:
        import webview
        print("✅ pywebview已安装并可用")
        return True
    except ImportError:
        print("❌ pywebview未安装")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("MCU Code Analyzer - WebView安装工具")
    print("=" * 60)
    
    # 检查当前状态
    if check_webview_available():
        print("\n🎯 pywebview已经安装，无需重复安装")
        print("您可以直接使用'🖼️ 内嵌渲染'功能")
    else:
        print("\n📦 准备安装pywebview...")
        if install_webview():
            print("\n🔄 验证安装...")
            if check_webview_available():
                print("✅ 安装验证成功！")
            else:
                print("❌ 安装验证失败，请检查安装过程")
    
    print("\n" + "=" * 60)
    input("按回车键退出...")

if __name__ == "__main__":
    main()

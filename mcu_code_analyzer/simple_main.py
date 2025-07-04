#!/usr/bin/env python3
"""
MCU Code Analyzer - 简化入口文件
专门用于30MB构建，只启动GUI，不包含CLI功能
"""

def main():
    """简化的主函数 - 只启动GUI"""
    try:
        # 直接导入并启动GUI
        from main_gui import MCUAnalyzerGUI
        app = MCUAnalyzerGUI()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

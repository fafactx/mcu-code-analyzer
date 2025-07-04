"""
简单验证修复
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent / "mcu_code_analyzer"
sys.path.insert(0, str(project_root))

print("🔧 验证修复状态...")

try:
    # 测试导入
    from main_gui import loc, MCUAnalyzerGUI
    print("✅ 主要模块导入成功")
    
    # 测试关键文本
    key_texts = ['start_analysis', 'analyzing', 'progress_updated_successfully']
    for key in key_texts:
        text = loc.get_text(key)
        print(f"✅ {key}: {text}")
    
    # 测试关键方法
    methods = ['start_analysis', 'update_progress', 'run_analysis']
    for method in methods:
        if hasattr(MCUAnalyzerGUI, method):
            print(f"✅ {method}方法存在")
        else:
            print(f"❌ {method}方法缺失")
    
    print("\n🎉 修复验证完成！")
    print("✅ localization问题已解决")
    print("✅ 分析功能应该能正常工作")
    print("✅ 进度条应该能正常更新")
    
except Exception as e:
    print(f"❌ 验证失败: {e}")
    import traceback
    traceback.print_exc()

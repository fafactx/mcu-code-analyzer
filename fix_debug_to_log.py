#!/usr/bin/env python3
"""
修改main_gui.py，将所有debug print语句改为输出到Execution Log页面
"""

import re
from pathlib import Path

def fix_debug_output():
    """修改debug输出到log页面"""
    
    main_gui_file = Path("mcu_code_analyzer/main_gui.py")
    
    if not main_gui_file.exists():
        print("❌ main_gui.py文件不存在")
        return False
    
    # 读取文件内容
    with open(main_gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 修改debug输出...")
    
    # 统计修改数量
    changes_made = 0
    
    # 1. 修改所有包含"DEBUG:"的print语句
    debug_print_pattern = r'print\(f?"DEBUG: ([^"]+)"\)'
    def replace_debug_print(match):
        nonlocal changes_made
        changes_made += 1
        debug_msg = match.group(1)
        return f'self.log_message("🔧 DEBUG: {debug_msg}")'
    
    content = re.sub(debug_print_pattern, replace_debug_print, content)
    
    # 2. 修改其他包含DEBUG的print语句
    debug_print_pattern2 = r'print\(f"DEBUG: ([^"]+)"\)'
    def replace_debug_print2(match):
        nonlocal changes_made
        changes_made += 1
        debug_msg = match.group(1)
        return f'self.log_message("🔧 DEBUG: {debug_msg}")'
    
    content = re.sub(debug_print_pattern2, replace_debug_print2, content)
    
    # 3. 修改简单的DEBUG print语句
    debug_print_pattern3 = r'print\("DEBUG: ([^"]+)"\)'
    def replace_debug_print3(match):
        nonlocal changes_made
        changes_made += 1
        debug_msg = match.group(1)
        return f'self.log_message("🔧 DEBUG: {debug_msg}")'
    
    content = re.sub(debug_print_pattern3, replace_debug_print3, content)
    
    # 4. 修改特定的debug输出模式
    specific_patterns = [
        # 修改 print(f"DEBUG: xxx: {variable}")
        (r'print\(f"DEBUG: ([^:]+): \{([^}]+)\}"\)', r'self.log_message(f"🔧 DEBUG: \1: {\2}")'),
        
        # 修改 print("DEBUG: xxx")
        (r'print\("DEBUG: ([^"]+)"\)', r'self.log_message("🔧 DEBUG: \1")'),
        
        # 修改其他常见的debug模式
        (r'print\(f"DEBUG: ([^"]+) failed: \{([^}]+)\}"\)', r'self.log_message(f"🔧 DEBUG: \1 failed: {\2}")'),
        (r'print\(f"DEBUG: ([^"]+) succeeded"\)', r'self.log_message("🔧 DEBUG: \1 succeeded")'),
    ]
    
    for pattern, replacement in specific_patterns:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            changes_made += len(re.findall(pattern, old_content))
    
    # 5. 修改一些特殊的print语句
    special_replacements = [
        # 创建按钮的debug信息
        ('print(f"DEBUG: {loc.get_text(\'creating_analyze_button\')}")', 
         'self.log_message(f"🔧 DEBUG: {loc.get_text(\'creating_analyze_button\')}")'),
        
        ('print(f"DEBUG: {loc.get_text(\'analyze_button_created\')}")', 
         'self.log_message(f"🔧 DEBUG: {loc.get_text(\'analyze_button_created\')}")'),
        
        ('print(f"DEBUG: {loc.get_text(\'llm_analysis_button_created\')}")', 
         'self.log_message(f"🔧 DEBUG: {loc.get_text(\'llm_analysis_button_created\')}")'),
        
        # 进度条颜色设置
        ('print(f"DEBUG: Failed to set progress color: {e}")', 
         'self.log_message(f"🔧 DEBUG: Failed to set progress color: {e}")'),
    ]
    
    for old_text, new_text in special_replacements:
        if old_text in content:
            content = content.replace(old_text, new_text)
            changes_made += 1
    
    # 6. 处理一些复杂的debug输出
    complex_patterns = [
        # 处理多行debug输出
        (r'print\(f"DEBUG: ([^"]+)"\)\s*\n\s*print\(f"([^"]+)"\)', 
         r'self.log_message(f"🔧 DEBUG: \1")\n            self.log_message(f"🔧 DEBUG: \2")'),
    ]
    
    for pattern, replacement in complex_patterns:
        old_content = content
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if content != old_content:
            changes_made += 1
    
    # 写回文件
    with open(main_gui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Debug输出修改完成，共修改了 {changes_made} 处")
    return True

def add_debug_helper_method():
    """添加debug辅助方法"""
    
    main_gui_file = Path("mcu_code_analyzer/main_gui.py")
    
    with open(main_gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有debug_log方法
    if 'def debug_log(' in content:
        print("✅ debug_log方法已存在")
        return True
    
    # 在log_message方法后添加debug_log方法
    log_method_pos = content.find('    def log_message(self, message):')
    if log_method_pos == -1:
        print("❌ 找不到log_message方法")
        return False
    
    # 找到log_message方法的结束位置
    method_end_pos = content.find('\n    def ', log_method_pos + 1)
    if method_end_pos == -1:
        method_end_pos = len(content)
    
    # 插入debug_log方法
    debug_method = '''
    def debug_log(self, message):
        """输出debug信息到log页面"""
        self.log_message(f"🔧 DEBUG: {message}")
'''
    
    content = content[:method_end_pos] + debug_method + content[method_end_pos:]
    
    # 写回文件
    with open(main_gui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已添加debug_log辅助方法")
    return True

def verify_changes():
    """验证修改结果"""
    
    main_gui_file = Path("mcu_code_analyzer/main_gui.py")
    
    with open(main_gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计剩余的DEBUG print语句
    remaining_debug_prints = len(re.findall(r'print\([^)]*DEBUG[^)]*\)', content))
    
    # 统计新的log_message DEBUG语句
    new_debug_logs = len(re.findall(r'self\.log_message\([^)]*DEBUG[^)]*\)', content))
    
    print(f"\n📊 修改结果验证:")
    print(f"  剩余的DEBUG print语句: {remaining_debug_prints}")
    print(f"  新的DEBUG log语句: {new_debug_logs}")
    
    if remaining_debug_prints == 0:
        print("✅ 所有DEBUG print语句已成功转换")
    else:
        print("⚠️  仍有DEBUG print语句未转换")
        
        # 显示剩余的print语句
        debug_prints = re.findall(r'print\([^)]*DEBUG[^)]*\)', content)
        for i, print_stmt in enumerate(debug_prints[:5]):  # 只显示前5个
            print(f"    {i+1}. {print_stmt}")
        if len(debug_prints) > 5:
            print(f"    ... 还有 {len(debug_prints) - 5} 个")
    
    return remaining_debug_prints == 0

def main():
    """主函数"""
    print("🚀 修改debug输出到Execution Log页面")
    print("=" * 50)
    
    # 1. 修改debug输出
    if not fix_debug_output():
        print("❌ 修改debug输出失败")
        return False
    
    # 2. 添加debug辅助方法
    if not add_debug_helper_method():
        print("❌ 添加debug辅助方法失败")
        return False
    
    # 3. 验证修改结果
    success = verify_changes()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Debug输出修改完成！")
        print("✅ 所有DEBUG信息现在会显示在Execution Log页面")
        print("✅ 使用🔧图标标识DEBUG信息")
    else:
        print("⚠️  修改部分完成，但仍有一些DEBUG print语句")
        print("💡 可能需要手动检查和修改")
    
    print("\n💡 修改说明:")
    print("  • 所有 print(\"DEBUG: ...\") 改为 self.log_message(\"🔧 DEBUG: ...\")")
    print("  • DEBUG信息会显示在GUI的Execution Log标签页")
    print("  • 使用🔧图标便于识别DEBUG信息")
    print("  • 添加了debug_log()辅助方法")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ 修改被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 修改过程中发生错误: {e}")
        exit(1)

#!/usr/bin/env python3
"""
修复剩余的print语句
"""

import re
from pathlib import Path

def fix_remaining_prints():
    """修复剩余的print语句"""
    
    main_gui_file = Path("mcu_code_analyzer/main_gui.py")
    
    with open(main_gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 查找剩余的print语句...")
    
    # 查找所有剩余的print语句
    print_patterns = [
        r'print\(f"DEBUG: ([^"]+)"\)',
        r'print\("DEBUG: ([^"]+)"\)',
        r'print\(f"DEBUG: ([^"]+): \{([^}]+)\}"\)',
    ]
    
    changes_made = 0
    
    for pattern in print_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  找到 {len(matches)} 个匹配的print语句")
            
            # 替换这些print语句
            if 'f"DEBUG:' in pattern:
                # 处理f-string格式
                content = re.sub(pattern, lambda m: f'self.log_message(f"🔧 DEBUG: {m.group(1)}")', content)
            else:
                # 处理普通字符串格式
                content = re.sub(pattern, lambda m: f'self.log_message("🔧 DEBUG: {m.group(1)}")', content)
            
            changes_made += len(matches)
    
    # 手动处理一些特殊情况
    special_replacements = [
        ('print(f"DEBUG: Timestamped {format_type} PNG saved to: {timestamped_file}")', 
         'self.log_message(f"🔧 DEBUG: Timestamped {format_type} PNG saved to: {timestamped_file}")'),
        
        ('print(f"DEBUG: Failed to save {format_type} PNG to logs: {e}")', 
         'self.log_message(f"🔧 DEBUG: Failed to save {format_type} PNG to logs: {e}")'),
        
        ('print(f"DEBUG: Displaying {format_type} image from PIL")', 
         'self.log_message(f"🔧 DEBUG: Displaying {format_type} image from PIL")'),
        
        ('print(f"DEBUG: {format_type} image displayed successfully")', 
         'self.log_message(f"🔧 DEBUG: {format_type} image displayed successfully")'),
        
        ('print(f"DEBUG: Failed to display {format_type} image: {e}")', 
         'self.log_message(f"🔧 DEBUG: Failed to display {format_type} image: {e}")'),
        
        ('print(f"DEBUG: SVG saved to: {svg_file_path}")', 
         'self.log_message(f"🔧 DEBUG: SVG saved to: {svg_file_path}")'),
        
        ('print(f"DEBUG: SVG file size: {len(svg_content)} characters")', 
         'self.log_message(f"🔧 DEBUG: SVG file size: {len(svg_content)} characters")'),
        
        ('print(f"DEBUG: Timestamped SVG saved to: {timestamped_file}")', 
         'self.log_message(f"🔧 DEBUG: Timestamped SVG saved to: {timestamped_file}")'),
        
        ('print(f"DEBUG: Failed to save SVG to logs: {e}")', 
         'self.log_message(f"🔧 DEBUG: Failed to save SVG to logs: {e}")'),
        
        ('print("DEBUG: Trying fallback rendering methods")', 
         'self.log_message("🔧 DEBUG: Trying fallback rendering methods")'),
        
        ('print("DEBUG: Matplotlib fallback rendering succeeded")', 
         'self.log_message("🔧 DEBUG: Matplotlib fallback rendering succeeded")'),
        
        ('print("DEBUG: Canvas fallback rendering succeeded")', 
         'self.log_message("🔧 DEBUG: Canvas fallback rendering succeeded")'),
        
        ('print("DEBUG: Showing Mermaid source code as fallback")', 
         'self.log_message("🔧 DEBUG: Showing Mermaid source code as fallback")'),
        
        ('print(f"DEBUG: Fallback rendering failed: {e}")', 
         'self.log_message(f"🔧 DEBUG: Fallback rendering failed: {e}")'),
        
        ('print("DEBUG: Displaying Mermaid image from PIL")', 
         'self.log_message("🔧 DEBUG: Displaying Mermaid image from PIL")'),
        
        ('print("DEBUG: Mermaid image displayed successfully")', 
         'self.log_message("🔧 DEBUG: Mermaid image displayed successfully")'),
        
        ('print(f"DEBUG: Failed to display Mermaid image: {e}")', 
         'self.log_message(f"🔧 DEBUG: Failed to display Mermaid image: {e}")'),
        
        ('print("DEBUG: Displaying SVG content with smart fallback")', 
         'self.log_message("🔧 DEBUG: Displaying SVG content with smart fallback")'),
        
        ('print(f"DEBUG: SVG content length: {len(svg_content)}")', 
         'self.log_message(f"🔧 DEBUG: SVG content length: {len(svg_content)}")'),
        
        ('print("DEBUG: SVG转PNG转换已删除，仅支持在线渲染")', 
         'self.log_message("🔧 DEBUG: SVG转PNG转换已删除，仅支持在线渲染")'),
        
        ('print(f"DEBUG: HTML fallback created: {html_file}")', 
         'self.log_message(f"🔧 DEBUG: HTML fallback created: {html_file}")'),
        
        ('print(f"DEBUG: HTML fallback failed: {e}")', 
         'self.log_message(f"🔧 DEBUG: HTML fallback failed: {e}")'),
        
        ('print(f"DEBUG: Failed to display SVG content: {e}")', 
         'self.log_message(f"🔧 DEBUG: Failed to display SVG content: {e}")'),
        
        ('print("DEBUG: 本地SVG转PNG功能已移除，请使用在线渲染")', 
         'self.log_message("🔧 DEBUG: 本地SVG转PNG功能已移除，请使用在线渲染")'),
    ]
    
    for old_text, new_text in special_replacements:
        if old_text in content:
            content = content.replace(old_text, new_text)
            changes_made += 1
            print(f"  修复特殊print语句: {old_text[:50]}...")
    
    # 写回文件
    with open(main_gui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 剩余print语句修复完成，共修复了 {changes_made} 处")
    
    # 验证结果
    remaining_prints = len(re.findall(r'print\([^)]*DEBUG[^)]*\)', content))
    print(f"📊 剩余DEBUG print语句: {remaining_prints}")
    
    return remaining_prints == 0

def main():
    """主函数"""
    print("🚀 修复剩余的DEBUG print语句")
    print("=" * 40)
    
    success = fix_remaining_prints()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 所有DEBUG print语句修复完成！")
        print("✅ 现在所有DEBUG信息都会显示在Execution Log页面")
    else:
        print("⚠️  仍有一些DEBUG print语句未修复")
        print("💡 可能需要手动检查")
    
    return success

if __name__ == "__main__":
    main()

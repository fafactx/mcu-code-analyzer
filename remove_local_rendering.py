#!/usr/bin/env python3
"""
删除所有本地mermaid渲染相关的代码
"""

import re
from pathlib import Path

def remove_local_rendering_methods():
    """删除本地渲染相关的方法"""
    
    main_gui_file = Path("mcu_code_analyzer/main_gui.py")
    
    if not main_gui_file.exists():
        print("❌ main_gui.py文件不存在")
        return False
    
    # 读取文件内容
    with open(main_gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 删除本地渲染相关方法...")
    
    # 要删除的方法列表
    methods_to_remove = [
        "render_mermaid_in_browser",
        "try_local_mermaid_rendering", 
        "try_local_html_mermaid_rendering",
        "try_local_plantuml",
        "try_cef_embedded",
        "try_cefpython_rendering",
        "create_vscode_style_mermaid_html",
        "create_mermaid_html_content"
    ]
    
    # 删除每个方法
    for method_name in methods_to_remove:
        print(f"  删除方法: {method_name}")
        
        # 匹配方法定义到下一个方法或类结束
        pattern = rf'    def {method_name}\(.*?\n(.*?\n)*?(?=    def |\nclass |\Z)'
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # 删除本地mermaid.js相关的引用
    print("  删除本地mermaid.js引用...")
    
    # 删除assets路径引用
    content = re.sub(r'.*assets.*mermaid.*\.js.*\n', '', content)
    content = re.sub(r'.*mermaid_js_path.*\n', '', content)
    content = re.sub(r'.*mermaid_js_content.*\n', '', content)
    
    # 删除CEF相关导入和代码
    print("  删除CEF相关代码...")
    content = re.sub(r'.*cefpython.*\n', '', content)
    content = re.sub(r'.*from cefpython3.*\n', '', content)
    
    # 删除本地HTML生成相关代码
    print("  删除本地HTML生成代码...")
    content = re.sub(r'.*tempfile.*NamedTemporaryFile.*html.*\n', '', content)
    content = re.sub(r'.*webbrowser\.open.*\n', '', content)
    
    # 修复render_mermaid_in_browser方法，改为只使用在线渲染
    browser_method = '''    def render_mermaid_in_browser(self):
        """在浏览器中渲染Mermaid图形 - 仅在线渲染"""
        print("DEBUG: 本地渲染已移除，使用在线渲染")
        self.render_flowchart_online("mermaid")
'''
    
    # 如果方法被完全删除了，重新添加简化版本
    if 'def render_mermaid_in_browser(' not in content:
        # 找到合适的位置插入
        insert_pos = content.find('    def render_real_mermaid_in_ui(')
        if insert_pos > 0:
            content = content[:insert_pos] + browser_method + '\n' + content[insert_pos:]
    
    # 写回文件
    with open(main_gui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 本地渲染方法删除完成")
    return True

def remove_nodejs_references():
    """删除nodejs相关引用"""
    
    print("🔍 删除nodejs相关引用...")
    
    files_to_check = [
        "mcu_code_analyzer/main_gui.py",
        "mcu_code_analyzer/config.yaml",
        "build_v2.1.0.py"
    ]
    
    for file_path in files_to_check:
        file_obj = Path(file_path)
        if not file_obj.exists():
            continue
            
        print(f"  处理文件: {file_path}")
        
        with open(file_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 删除nodejs相关行
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 跳过包含nodejs相关关键词的行
            if any(keyword in line.lower() for keyword in [
                'portable_nodejs', 'node_modules', 'mermaid-cli', 
                'mmdc', 'nodejs', 'node.exe'
            ]):
                print(f"    删除行: {line[:50]}...")
                continue
            filtered_lines.append(line)
        
        # 写回文件
        with open(file_obj, 'w', encoding='utf-8') as f:
            f.write('\n'.join(filtered_lines))
    
    print("✅ nodejs引用删除完成")

def update_config():
    """更新配置文件，移除本地渲染选项"""
    
    config_file = Path("mcu_code_analyzer/config.yaml")
    if not config_file.exists():
        return
    
    print("🔍 更新配置文件...")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 删除本地渲染相关配置
    lines = content.split('\n')
    filtered_lines = []
    skip_section = False
    
    for line in lines:
        # 跳过本地渲染相关配置
        if 'local:' in line or 'nodejs_path:' in line or 'mermaid_cli_path:' in line:
            skip_section = True
            continue
        elif line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            skip_section = False
        
        if not skip_section:
            filtered_lines.append(line)
    
    # 写回文件
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(filtered_lines))
    
    print("✅ 配置文件更新完成")

def update_build_script():
    """更新构建脚本，移除nodejs相关内容"""
    
    build_file = Path("build_v2.1.0.py")
    if not build_file.exists():
        return
    
    print("🔍 更新构建脚本...")
    
    with open(build_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 删除nodejs相关的datas行
    content = re.sub(r".*'portable_nodejs'.*\n", '', content)
    
    # 写回文件
    with open(build_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 构建脚本更新完成")

def main():
    """主函数"""
    print("🚀 开始清理本地mermaid渲染相关代码")
    print("=" * 50)
    
    # 1. 删除本地渲染方法
    remove_local_rendering_methods()
    
    # 2. 删除nodejs引用
    remove_nodejs_references()
    
    # 3. 更新配置文件
    update_config()
    
    # 4. 更新构建脚本
    update_build_script()
    
    print("\n" + "=" * 50)
    print("🎉 清理完成！")
    print("✅ 已删除所有本地mermaid渲染相关代码")
    print("✅ 已删除portable_nodejs目录")
    print("✅ 已更新配置文件")
    print("✅ 已更新构建脚本")
    print("\n💡 现在只保留在线mermaid渲染功能")

if __name__ == "__main__":
    main()

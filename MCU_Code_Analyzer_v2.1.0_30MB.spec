# -*- mode: python ; coding: utf-8 -*-
# 基于老版本1.1的成功配置，目标30MB

block_cipher = None

a = Analysis(
    ['mcu_code_analyzer/simple_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('mcu_code_analyzer/config.yaml', '.'),
        ('mcu_code_analyzer/localization.py', '.'),
        ('mcu_code_analyzer/templates', 'templates'),
        ('mcu_code_analyzer/utils', 'utils'),
        ('mcu_code_analyzer/core', 'core'),
        ('mcu_code_analyzer/intelligence', 'intelligence'),
        ('mcu_code_analyzer/ui', 'ui'),
    ],
    hiddenimports=[
        # 完全复制老版本的4个库
        'tkinter',
        'yaml',
        'requests',
        'chardet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除所有大型库 (关键!)
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'Pillow',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.patches',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'networkx',
        'numpy',
        'pandas',
        'scipy',
        'cv2',
        'tensorflow',
        'torch',
        'sklearn',
        'cairosvg',
        'tksvg',
        'customtkinter',

        # 排除测试和开发工具
        'test',
        'tests',
        'testing',
        'unittest',
        'pytest',
        'jupyter',
        'IPython',
        'notebook',

        # 排除其他GUI框架
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        'kivy',
        'pygame',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MCU_Code_Analyzer_v2.1.0_30MB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # 保持与老版本一致
    upx=False,    # 保持与老版本一致
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)

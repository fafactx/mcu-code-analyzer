# -*- mode: python ; coding: utf-8 -*-
# MCU Code Analyzer v3.0 修复版构建配置

block_cipher = None

a = Analysis(
    ['mcu_code_analyzer/main_gui.py'],
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
        # v3.0修复版 - 包含在线渲染必需的库
        'tkinter',
        'yaml',
        'requests', 
        'chardet',
        # 添加PIL支持在线渲染
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        # 网络和编码支持
        'urllib3',
        'base64',
        'io',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的大型库，但保留PIL
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
        'jupyter',
        'IPython',
        'notebook',
        'test',
        'tests',
        'testing',
        'unittest',
        'pytest',
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
    name='MCU_Code_Analyzer_v3.0_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,   # 保持优化
    upx=False,    # 保持稳定性
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

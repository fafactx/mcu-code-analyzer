# -*- mode: python ; coding: utf-8 -*-
# MCU Code Analyzer v3.0 构建配置

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
        # v3.0精简依赖 - 仅包含必要库
        'tkinter',
        'yaml',
        'requests', 
        'chardet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # v3.0排除所有大型库
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
    name='MCU_Code_Analyzer_v3.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,   # v3.0启用strip优化
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

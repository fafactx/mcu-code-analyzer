# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('localization.py', '.'),
        ('templates', 'templates'),
        ('utils', 'utils'),
        ('core', 'core'),
        ('intelligence', 'intelligence'),
        ('ui', 'ui'),
        ('portable_nodejs', 'portable_nodejs'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.font',
        'customtkinter',
        'yaml',
        'pathlib',
        'threading',
        'json',
        'xml.etree.ElementTree',
        're',
        'collections',
        'dataclasses',
        'typing',
        'datetime',
        'tempfile',
        'webbrowser',
        'shutil',
        'subprocess',
        'os',
        'sys',
        'argparse',
        'requests',
        'urllib3',
        'encodings.utf_8',
        'encodings.cp1252',
        'encodings.ascii',
        'pkg_resources.py2_warn',
        'math',  # For loading spinner animation
        'time',  # For timing and delays
        'localization',  # Internationalization module
        'tksvg',  # SVG support for tkinter
        'PIL',  # Image processing
        'PIL.Image',
        'PIL.ImageTk',
        'cairosvg',  # SVG to PNG conversion
        'matplotlib',  # Graph plotting
        'matplotlib.pyplot',
        'matplotlib.patches',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'networkx',  # Graph analysis
        'numpy',  # Numerical computing
        'pandas',  # Data processing
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'scipy',
        'cv2',
        'tensorflow',
        'torch',
        'sklearn',
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
    name='MCUCodeAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩，避免DLL问题
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # 可以添加图标文件路径
)

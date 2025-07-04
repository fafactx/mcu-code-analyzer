"""
STM32工程分析器安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# 读取requirements文件
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding='utf-8').strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="stm32-analyzer",
    version='0.1.0',
    author="STM32 Analyzer Team",
    author_email="support@stm32analyzer.com",
    description="智能STM32工程分析器 - 深度代码分析与平台迁移助手",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stm32-analyzer/stm32-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "gui": [
            "tkinter",  # 通常内置，但某些Linux发行版需要单独安装
        ],
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "stm32-analyzer=stm32_analyzer.main:main",
            "stm32-analyzer-gui=stm32_analyzer.main:main",
            "stm32-analyzer-cli=stm32_analyzer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "stm32_analyzer": [
            "config.yaml",
            "templates/**/*.yaml",
            "templates/**/*.md",
            "templates/**/*.json",
        ],
    },
    keywords=[
        "stm32", "embedded", "code-analysis", "microcontroller",
        "nxp", "arm", "cortex-m", "hal", "cmsis", "keil",
        "code-migration", "llm", "ai", "static-analysis"
    ],
    project_urls={
        "Bug Reports": "https://github.com/stm32-analyzer/stm32-analyzer/issues",
        "Source": "https://github.com/stm32-analyzer/stm32-analyzer",
        "Documentation": "https://docs.stm32analyzer.com",
    },
)

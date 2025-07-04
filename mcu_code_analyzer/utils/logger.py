"""
日志系统 - 支持彩色输出、文件日志和多级别日志
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
import threading


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class Logger:
    """日志管理器 - 单例模式"""
    
    _instance = None
    _initialized = False
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._logger = None
            self._file_handler = None
            self._console_handler = None
            self._gui_callback = None
            self._setup_logger()
            Logger._initialized = True
    
    def _setup_logger(self):
        """设置日志器"""
        self._logger = logging.getLogger('STM32Analyzer')
        self._logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if self._logger.handlers:
            self._logger.handlers.clear()
        
        # 设置控制台处理器
        self._setup_console_handler()
        
        # 设置文件处理器
        self._setup_file_handler()
    
    def _setup_console_handler(self):
        """设置控制台处理器"""
        self._console_handler = logging.StreamHandler(sys.stdout)
        self._console_handler.setLevel(logging.INFO)
        
        # 彩色格式化器
        colored_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        self._console_handler.setFormatter(colored_formatter)
        self._logger.addHandler(self._console_handler)
    
    def _setup_file_handler(self):
        """设置文件处理器"""
        # 创建日志目录
        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 日志文件名包含时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"stm32_analyzer_{timestamp}.log"
        
        self._file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self._file_handler.setLevel(logging.DEBUG)
        
        # 文件格式化器（不包含颜色）
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._file_handler.setFormatter(file_formatter)
        self._logger.addHandler(self._file_handler)
        
        self.info(f"日志文件: {log_file}")
    
    def set_level(self, level: str):
        """设置日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self._logger.setLevel(level_map[level.upper()])
            if self._console_handler:
                self._console_handler.setLevel(level_map[level.upper()])
    
    def set_gui_callback(self, callback: Callable[[str, str], None]):
        """设置GUI回调函数，用于在界面中显示日志"""
        self._gui_callback = callback
    
    def _log_with_callback(self, level: str, message: str):
        """记录日志并调用GUI回调"""
        if self._gui_callback:
            try:
                self._gui_callback(message, level.lower())
            except Exception as e:
                # 避免回调函数错误影响日志记录
                self._logger.error(f"GUI回调函数错误: {e}")
    
    def debug(self, message: str):
        """调试日志"""
        self._logger.debug(message)
        self._log_with_callback('DEBUG', message)
    
    def info(self, message: str):
        """信息日志"""
        self._logger.info(message)
        self._log_with_callback('INFO', message)
    
    def warning(self, message: str):
        """警告日志"""
        self._logger.warning(message)
        self._log_with_callback('WARNING', message)
    
    def error(self, message: str):
        """错误日志"""
        self._logger.error(message)
        self._log_with_callback('ERROR', message)
    
    def critical(self, message: str):
        """严重错误日志"""
        self._logger.critical(message)
        self._log_with_callback('CRITICAL', message)
    
    def exception(self, message: str):
        """异常日志（包含堆栈跟踪）"""
        self._logger.exception(message)
        self._log_with_callback('ERROR', f"{message} (详细信息请查看日志文件)")
    
    def log_function_call(self, func_name: str, *args, **kwargs):
        """记录函数调用"""
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        params = ', '.join(filter(None, [args_str, kwargs_str]))
        self.debug(f"调用函数: {func_name}({params})")
    
    def log_performance(self, operation: str, duration: float):
        """记录性能信息"""
        self.info(f"性能统计: {operation} 耗时 {duration:.2f} 秒")
    
    def log_analysis_progress(self, current: int, total: int, item: str = ""):
        """记录分析进度"""
        percentage = (current / total) * 100 if total > 0 else 0
        progress_msg = f"分析进度: {current}/{total} ({percentage:.1f}%)"
        if item:
            progress_msg += f" - {item}"
        self.info(progress_msg)
    
    def log_file_operation(self, operation: str, file_path: Path, success: bool = True):
        """记录文件操作"""
        status = "成功" if success else "失败"
        self.info(f"文件{operation}: {file_path} - {status}")
    
    def close(self):
        """关闭日志器"""
        if self._file_handler:
            self._file_handler.close()
            self._logger.removeHandler(self._file_handler)
        
        if self._console_handler:
            self._logger.removeHandler(self._console_handler)


# 全局日志实例
logger = Logger()


def log_decorator(func):
    """日志装饰器 - 自动记录函数调用"""
    def wrapper(*args, **kwargs):
        logger.log_function_call(func.__name__, *args, **kwargs)
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.exception(f"函数 {func.__name__} 执行失败: {e}")
            raise
    return wrapper


def performance_monitor(func):
    """性能监控装饰器"""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.log_performance(func.__name__, duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.log_performance(f"{func.__name__} (失败)", duration)
            raise
    return wrapper

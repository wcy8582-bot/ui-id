import os
import sys
import logging
import time
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    """日志工具类"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化日志"""
        if not self._initialized:
            self.logger = None
            self.log_file = None
            self._initialized = True
    
    def init_logger(self, log_dir: str = "logs", enable_debug: bool = False, task_type: str = "", case_name: str = "") -> None:
        """初始化日志配置
        
        Args:
            log_dir: 日志目录
            enable_debug: 是否启用debug日志
            task_type: 任务类型，如"record"或"run"
            case_name: 用例名称
        """
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 生成日志文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if task_type and case_name:
            self.log_file = os.path.join(log_dir, f"{task_type}_{case_name}_{timestamp}.log")
        else:
            self.log_file = os.path.join(log_dir, f"{timestamp}.log")
        
        # 创建日志记录器
        self.logger = logging.getLogger("playwright_ui_automation")
        self.logger.setLevel(logging.DEBUG if enable_debug else logging.INFO)
        
        # 清空已有的处理器
        self.logger.handlers.clear()
        
        # 创建控制台处理器，输出到sys.stdout以便subprocess捕获
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # 自定义emit方法处理控制台句柄失效问题
        original_emit = console_handler.emit
        def safe_emit(record):
            try:
                original_emit(record)
            except Exception:
                pass  # 忽略所有控制台输出错误（如句柄失效）
        console_handler.emit = safe_emit

        # 创建文件处理器，支持按大小切割
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG if enable_debug else logging.INFO)
        
        # 定义日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
        )
        
        # 设置处理器格式
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """获取日志记录器
        
        Returns:
            日志记录器实例
        """
        if self.logger is None:
            self.init_logger()
        return self.logger
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """记录debug级别日志"""
        self.get_logger().debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """记录info级别日志"""
        self.get_logger().info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """记录warning级别日志"""
        self.get_logger().warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """记录error级别日志"""
        self.get_logger().error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """记录critical级别日志"""
        self.get_logger().critical(message, *args, **kwargs)


# 全局日志实例
logger = Logger()

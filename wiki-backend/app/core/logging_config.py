"""
日志配置
"""
import logging
import sys
from pathlib import Path

# 创建logs目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 配置根日志记录器
def setup_logging():
    """设置日志配置"""
    # 创建logger
    logger = logging.getLogger("api")
    logger.setLevel(logging.INFO)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器 - 所有日志
    file_handler = logging.FileHandler(
        log_dir / "api.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 错误日志文件处理器
    error_file_handler = logging.FileHandler(
        log_dir / "error.log",
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    
    return logger

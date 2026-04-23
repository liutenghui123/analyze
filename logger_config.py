"""
日志配置模块 - 提供统一的日志记录功能
"""
import logging
import os
from datetime import datetime


def setup_logger(name="fenxi8", log_dir=None, log_level=logging.INFO):
    """
    配置并返回logger实例

    参数:
        name: logger名称
        log_dir: 日志文件目录，默认为当前目录
        log_level: 日志级别

    返回:
        logging.Logger: 配置好的logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 创建日志目录
    if log_dir is None:
        log_dir = os.getcwd()
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名：fenxi8_YYYYMMDD_HHMMSS.log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"fenxi8_{timestamp}.log")

    # 创建formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 控制台只显示WARNING及以上
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger, log_file

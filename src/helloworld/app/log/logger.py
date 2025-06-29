import sys
from loguru import logger
import logging
from ..setting import logfile, log_level

logger.remove()

logger.add(
    logfile,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level=log_level.upper(),
    rotation="10 MB",
    retention=5, 
    compression="zip",
)

logger.add(sys.stdout, colorize=True, level="INFO")

# logger.remove()
# logger.add(logfile, level=log_level.upper(), rotation="10 MB", retention=5, compression="zip")


# class InterceptHandler(logging.Handler):
#     def emit(self, record):
#         try:
#             level = logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno  # 如果Loguru没有对应级别，使用原级别数值

#         # 追踪日志调用位置，跳过logging库自身的堆栈帧
#         frame, depth = logging.currentframe(), 2
#         while frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1

#         logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# # 替换root logger的处理器
# logging.basicConfig(handlers=[InterceptHandler()], level=log_level.upper())
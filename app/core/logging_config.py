"""日志配置 — 输出到控制台 + 文件"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")


def setup_logging():
    """配置日志：控制台 + 滚动文件"""
    os.makedirs(LOG_DIR, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除默认处理器，避免重复
    root_logger.handlers.clear()

    # ─── 格式 ─────────────────────────────────
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ─── 控制台输出 ────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ─── 文件输出（滚动，单个最大 5MB，保留 5 个）──
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 关闭 SQLAlchemy 的详细日志（只在 WARNING 以上输出）
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.info("=" * 50)
    logging.info("日志系统初始化完成")
    logging.info("日志目录: %s", LOG_DIR)

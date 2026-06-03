"""Mini 电商 API 入口"""

import logging
import time

from fastapi import FastAPI, Request
from app.config import settings
from app.core.logging_config import setup_logging
from app.database import Base, engine

# 初始化日志系统（必须在最前面）
setup_logging()
logger = logging.getLogger(__name__)

# 导入所有模型，确保表被创建
from app import models  # noqa: F401

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)


# ─── 请求日志中间件 ──────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    cost = (time.time() - start) * 1000
    logger.info("%s %s → %s (%.0fms)", request.method, request.url.path, response.status_code, cost)
    return response


# ─── 注册路由 ───────────────────────────────
from app.routers import admin, cart, orders, payment, products, users  # noqa: E402

app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payment.router)
app.include_router(admin.router)


# ─── 基础接口 ────────────────────────────────
@app.get("/")
def root():
    logger.debug("访问根路径")
    return {"message": f"Welcome to {settings.APP_NAME}", "version": settings.APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}

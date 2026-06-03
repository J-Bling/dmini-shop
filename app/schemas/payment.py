"""支付相关请求/响应模型"""

from datetime import datetime

from pydantic import BaseModel


class PayRequest(BaseModel):
    """发起支付请求"""
    channel: str = "mock"  # mock / alipay / wechat


class PayResponse(BaseModel):
    """发起支付响应"""
    pay_no: str
    amount: int
    channel: str
    pay_url: str | None = None
    expire_at: str | None = None


class CallbackRequest(BaseModel):
    """支付回调请求（模拟/真实都走这个格式）"""
    success: bool = True
    out_trade_no: str = ""  # 外部交易号（真实支付平台返回）
    raw: dict = {}  # 原始回调数据


class PaymentStatusResponse(BaseModel):
    """支付状态查询响应"""
    pay_no: str
    order_id: int
    channel: str
    amount: int
    status: str
    paid_at: datetime | None = None
    created_at: datetime

"""支付记录模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from app.database import Base


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    pay_no = Column(String(50), unique=True, nullable=False, index=True)
    channel = Column(String(20), nullable=False, default="mock")  # mock / alipay / wechat
    amount = Column(Integer, nullable=False)  # 单位：分
    status = Column(String(20), default="waiting")
    # waiting → success → failed
    # waiting → expired
    expire_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

"""统一支付服务 — 渠道路由 + 回调分发"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import PaymentRecord
from app.models.user import User
from app.schemas.payment import PayRequest, PayResponse, CallbackRequest, PaymentStatusResponse

logger = logging.getLogger(__name__)

# ─── 渠道注册表（扩展新支付方式只需在这里加一行）──
CHANNELS: dict[str, type] = {}


def register_channel(name: str, channel_class: type):
    """注册支付渠道"""
    CHANNELS[name] = channel_class
    logger.info("支付渠道已注册: %s -> %s", name, channel_class.__name__)


def get_channel(name: str):
    """获取支付渠道实例"""
    if name not in CHANNELS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的支付渠道: {name}")
    return CHANNELS[name]()


def _generate_pay_no() -> str:
    """生成支付单号"""
    import random
    now = datetime.now()
    ts = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"
    rand = random.randint(1000, 9999)
    return f"PAY{ts}{rand}"


def initiate_payment(db: Session, user: User, order_id: int, req: PayRequest) -> PayResponse:
    """发起支付"""
    # 校验订单
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"当前订单状态({order.status})不允许支付")

    # 查是否有未完成的支付记录（幂等）
    existing = db.query(PaymentRecord).filter(
        PaymentRecord.order_id == order_id,
        PaymentRecord.status == "waiting",
    ).first()
    if existing:
        # 如果还没过期，直接返回已有的
        if existing.expire_at and existing.expire_at > datetime.now(timezone.utc):
            channel = get_channel(existing.channel)
            return PayResponse(**channel.create_payment(db, order, existing))
        else:
            existing.status = "expired"

    # 创建支付记录
    pay_no = _generate_pay_no()
    record = PaymentRecord(
        order_id=order.id,
        pay_no=pay_no,
        channel=req.channel,
        amount=order.total_price,
        status="waiting",
        expire_at=datetime.now(timezone.utc) + timedelta(minutes=30),  # 30分钟过期
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 路由到对应渠道
    channel = get_channel(req.channel)
    pay_info = channel.create_payment(db, order, record)

    logger.info("发起支付 order_no=%s pay_no=%s channel=%s amount=%d",
                order.order_no, pay_no, req.channel, order.total_price)
    return PayResponse(**pay_info)


def handle_callback(db: Session, channel_name: str, callback_data: CallbackRequest) -> dict:
    """统一支付回调入口"""
    record = db.query(PaymentRecord).filter(
        PaymentRecord.pay_no == callback_data.out_trade_no,
        PaymentRecord.channel == channel_name,
    ).first()

    if not record:
        logger.warning("支付回调: 记录不存在 pay_no=%s channel=%s",
                       callback_data.out_trade_no, channel_name)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="支付记录不存在")

    if record.status != "waiting":
        logger.warning("支付回调: 重复回调 pay_no=%s status=%s", record.pay_no, record.status)
        return {"success": True, "message": "重复回调，已忽略", "pay_no": record.pay_no}

    channel = get_channel(channel_name)
    result = channel.handle_callback(db, record, callback_data.model_dump())

    logger.info("支付回调处理完成 pay_no=%s result=%s", record.pay_no, result)
    return {"success": result, "pay_no": record.pay_no, "order_id": record.order_id}


def query_payment_status(db: Session, user: User, pay_no: str) -> PaymentStatusResponse:
    """查询支付状态"""
    record = db.query(PaymentRecord).filter(PaymentRecord.pay_no == pay_no).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="支付记录不存在")

    # 校验权限：只能查自己的
    order = db.query(Order).filter(Order.id == record.order_id).first()
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问")

    return PaymentStatusResponse(
        pay_no=record.pay_no,
        order_id=record.order_id,
        channel=record.channel,
        amount=record.amount,
        status=record.status,
        paid_at=record.paid_at,
        created_at=record.created_at,
    )

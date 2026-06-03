"""支付 API 路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.payment import (
    CallbackRequest,
    PayRequest,
    PayResponse,
    PaymentStatusResponse,
)
from app.services import payment_service
from app.services.payment.channels.mock import MockPayChannel
from app.services.payment_service import register_channel

# ─── 注册支付渠道 ────────────────────────────
register_channel("mock", MockPayChannel)

router = APIRouter(prefix="/api/pay", tags=["支付"])


@router.post("/orders/{order_id}", response_model=PayResponse)
def initiate_payment(
    order_id: int,
    req: PayRequest = PayRequest(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发起支付"""
    return payment_service.initiate_payment(db, user, order_id, req)


@router.post("/callback/{channel}")
def pay_callback(
    channel: str,
    data: CallbackRequest,
    db: Session = Depends(get_db),
):
    """统一支付回调入口（模拟/支付宝/微信都走这）"""
    return payment_service.handle_callback(db, channel, data)


@router.get("/{pay_no}/status", response_model=PaymentStatusResponse)
def payment_status(
    pay_no: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询支付状态（前端轮询用）"""
    return payment_service.query_payment_status(db, user, pay_no)

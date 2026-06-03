"""订单 API 路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderListResponse, OrderResponse
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["订单"])


@router.post("", response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建订单（从购物车生成）"""
    return order_service.place_order(db, user, data)


@router.get("", response_model=OrderListResponse)
def list_orders(
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的订单列表"""
    return order_service.list_orders(db, user, status, skip, limit)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """订单详情"""
    return order_service.get_order(db, user, order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取消订单"""
    return order_service.cancel_order(db, user, order_id)


@router.post("/{order_id}/pay", response_model=OrderResponse)
def pay_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """模拟支付"""
    return order_service.pay_order(db, user, order_id)

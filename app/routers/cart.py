"""购物车 API 路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.cart import CartAdd, CartResponse, CartUpdate
from app.services import cart_service

router = APIRouter(prefix="/api/cart", tags=["购物车"])


@router.post("/items", response_model=CartResponse)
def add_item(
    data: CartAdd,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加商品到购物车"""
    return cart_service.add_to_cart(db, user, data)


@router.get("", response_model=CartResponse)
def get_cart(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取我的购物车"""
    return cart_service.get_cart(db, user)


@router.put("/items/{item_id}", response_model=CartResponse)
def update_item(
    item_id: int,
    data: CartUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改购物车商品数量"""
    return cart_service.update_cart_item(db, user, item_id, data)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """从购物车删除商品"""
    return cart_service.remove_from_cart(db, user, item_id)


@router.delete("", response_model=CartResponse)
def clear_cart(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """清空购物车"""
    return cart_service.clear_cart(db, user)

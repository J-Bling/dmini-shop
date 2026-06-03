"""订单业务逻辑"""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderItemResponse, OrderListResponse, OrderResponse

logger = logging.getLogger(__name__)


def _generate_order_no() -> str:
    """生成订单号：ORD + 日期 + 毫秒戳 + 随机数"""
    import random
    now = datetime.now()
    ts = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"
    rand = random.randint(1000, 9999)
    return f"ORD{ts}{rand}"


def place_order(db: Session, user: User, data: OrderCreate) -> OrderResponse:
    """下单：从购物车生成订单"""
    # 1. 获取用户购物车
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="购物车是空的")

    # 2. 验证库存 & 计算总价
    total_price = 0
    order_items_data = []
    for ci in cart_items:
        product = db.query(Product).filter(Product.id == ci.product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"商品(ID={ci.product_id})不存在")
        if product.stock < ci.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"商品「{product.name}」库存不足(需{ci.quantity}, 剩{product.stock})")
        if not product.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"商品「{product.name}」已下架")

        order_items_data.append({
            "product": product,
            "quantity": ci.quantity,
        })
        total_price += product.price * ci.quantity

    # 3. 创建订单
    order = Order(
        user_id=user.id,
        order_no=_generate_order_no(),
        status="pending",
        total_price=total_price,
        receiver_name=data.receiver_name,
        receiver_phone=data.receiver_phone,
        receiver_address=data.receiver_address,
        remark=data.remark,
    )
    db.add(order)
    db.flush()  # 获取 order.id

    # 4. 创建订单明细 & 扣减库存
    for oid in order_items_data:
        p = oid["product"]
        qty = oid["quantity"]
        item = OrderItem(
            order_id=order.id,
            product_id=p.id,
            product_name=p.name,
            product_price=p.price,
            quantity=qty,
        )
        db.add(item)
        p.stock -= qty

    # 5. 清空购物车
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()

    db.commit()
    db.refresh(order)

    logger.info("下单成功 order_no=%s total=%d分", order.order_no, total_price)
    return _to_response(order)


def list_orders(
    db: Session,
    user: User,
    status_filter: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> OrderListResponse:
    """获取用户订单列表"""
    query = db.query(Order).filter(Order.user_id == user.id)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    total = query.count()
    orders = query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
    return OrderListResponse(
        items=[_to_response(o) for o in orders],
        total=total,
    )


def get_order(db: Session, user: User, order_id: int) -> OrderResponse:
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return _to_response(order)


def cancel_order(db: Session, user: User, order_id: int) -> OrderResponse:
    """取消订单（仅待支付状态可取消）"""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"当前状态({order.status})不允许取消")

    # 归还库存
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    logger.info("订单取消 order_no=%s", order.order_no)
    return _to_response(order)


def pay_order(db: Session, user: User, order_id: int) -> OrderResponse:
    """模拟支付"""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"当前状态({order.status})不允许支付")

    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    logger.info("支付成功 order_no=%s", order.order_no)
    return _to_response(order)


def _to_response(order: Order) -> OrderResponse:
    """ORM → Pydantic"""
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        order_no=order.order_no,
        status=order.status,
        total_price=order.total_price,
        receiver_name=order.receiver_name,
        receiver_phone=order.receiver_phone,
        receiver_address=order.receiver_address,
        remark=order.remark,
        paid_at=order.paid_at,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_price=item.product_price,
                quantity=item.quantity,
            )
            for item in order.items
        ],
    )

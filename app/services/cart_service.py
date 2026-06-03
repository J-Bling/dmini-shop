"""购物车业务逻辑"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartAdd, CartResponse, CartItemResponse, CartUpdate


def add_to_cart(db: Session, user: User, data: CartAdd) -> CartResponse:
    """添加商品到购物车（如果已存在则增加数量）"""
    # 验证商品存在
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    # 查购物车是否已有该商品
    existing = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.product_id == data.product_id,
    ).first()

    if existing:
        existing.quantity += data.quantity
    else:
        existing = CartItem(user_id=user.id, product_id=data.product_id, quantity=data.quantity)
        db.add(existing)

    db.commit()
    return get_cart(db, user)


def get_cart(db: Session, user: User) -> CartResponse:
    """获取用户购物车"""
    items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    return _build_cart_response(items)


def update_cart_item(db: Session, user: User, item_id: int, data: CartUpdate) -> CartResponse:
    """修改购物车中某商品的数量"""
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车中未找到该商品")

    if data.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = data.quantity

    db.commit()
    return get_cart(db, user)


def remove_from_cart(db: Session, user: User, item_id: int) -> CartResponse:
    """从购物车删除某商品"""
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车中未找到该商品")

    db.delete(item)
    db.commit()
    return get_cart(db, user)


def clear_cart(db: Session, user: User) -> CartResponse:
    """清空购物车"""
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()
    return CartResponse(items=[], total_count=0, total_price=0)


def _build_cart_response(items: list[CartItem]) -> CartResponse:
    """组装购物车响应（附带商品信息）"""
    cart_items = []
    total_price = 0

    for item in items:
        p = item.product
        cart_items.append(CartItemResponse(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_name=p.name if p else "",
            product_price=p.price if p else 0,
            product_image=p.image_url if p else "",
            product_stock=p.stock if p else 0,
            created_at=item.created_at,
            updated_at=item.updated_at,
        ))
        if p:
            total_price += p.price * item.quantity

    return CartResponse(
        items=cart_items,
        total_count=sum(i.quantity for i in items),
        total_price=total_price,
    )

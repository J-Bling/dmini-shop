"""购物车请求/响应模型"""

from datetime import datetime

from pydantic import BaseModel


class CartAdd(BaseModel):
    """添加商品到购物车"""
    product_id: int
    quantity: int = 1


class CartUpdate(BaseModel):
    """修改购物车商品数量"""
    quantity: int


class CartItemResponse(BaseModel):
    """购物车单项"""
    id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: str = ""
    product_price: int = 0
    product_image: str = ""
    product_stock: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """购物车（含汇总）"""
    items: list[CartItemResponse]
    total_count: int = 0
    total_price: int = 0  # 单位：分

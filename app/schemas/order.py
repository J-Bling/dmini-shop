"""订单请求/响应模型"""

from datetime import datetime

from pydantic import BaseModel


class OrderCreate(BaseModel):
    """创建订单请求"""
    receiver_name: str = ""
    receiver_phone: str = ""
    receiver_address: str = ""
    remark: str = ""


class OrderItemResponse(BaseModel):
    """订单明细"""
    id: int
    product_id: int
    product_name: str
    product_price: int
    quantity: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    user_id: int
    order_no: str
    status: str
    total_price: int
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    remark: str
    paid_at: datetime | None
    created_at: datetime
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表"""
    items: list[OrderResponse]
    total: int

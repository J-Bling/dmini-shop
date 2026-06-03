"""商品和分类相关请求/响应模型"""

from datetime import datetime

from pydantic import BaseModel


# ─── 分类 ────────────────────────────────────


class CategoryCreate(BaseModel):
    name: str
    description: str = ""


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── 商品 ────────────────────────────────────


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: int  # 单位：分（1000 = 10.00元）
    stock: int = 0
    image_url: str = ""
    category_id: int | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    stock: int | None = None
    image_url: str | None = None
    category_id: int | None = None
    is_active: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    stock: int
    image_url: str
    category_id: int | None
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

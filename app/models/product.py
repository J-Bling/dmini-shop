"""商品 + 分类模型"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), default="")
    created_at = Column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    price = Column(Integer, nullable=False)  # 单位：分（避免浮点数精度问题）
    stock = Column(Integer, default=0)
    image_url = Column(String(500), default="")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Integer, default=1)  # 1=上架, 0=下架
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")

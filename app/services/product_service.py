"""商品和分类业务逻辑"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Category, Product
from app.schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


# ════════════════════════════════════════════
#  分类
# ════════════════════════════════════════════


def create_category(db: Session, data: CategoryCreate) -> Category:
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="分类名称已存在")
    obj = Category(name=data.name, description=data.description)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_categories(db: Session) -> list[Category]:
    return db.query(Category).all()


def get_category(db: Session, category_id: int) -> Category:
    obj = db.query(Category).filter(Category.id == category_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return obj


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    obj = get_category(db, category_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_category(db: Session, category_id: int) -> None:
    obj = get_category(db, category_id)
    # 检查分类下是否有商品
    if db.query(Product).filter(Product.category_id == category_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该分类下还有商品，无法删除")
    db.delete(obj)
    db.commit()


# ════════════════════════════════════════════
#  商品
# ════════════════════════════════════════════


def create_product(db: Session, data: ProductCreate) -> Product:
    obj = Product(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_products(
    db: Session,
    category_id: int | None = None,
    keyword: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Product]:
    query = db.query(Product)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if keyword:
        query = query.filter(Product.name.contains(keyword))

    return query.order_by(Product.id.desc()).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Product:
    obj = db.query(Product).filter(Product.id == product_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    return obj


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    obj = get_product(db, product_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_product(db: Session, product_id: int) -> None:
    obj = get_product(db, product_id)
    db.delete(obj)
    db.commit()

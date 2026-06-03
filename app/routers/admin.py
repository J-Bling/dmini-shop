"""后台管理路由（Jinja2 网页）"""

import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Query as FQuery
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.admin_dependencies import get_admin_user
from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Category, Product
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["后台管理"])
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(_BASE, "templates"))


def _ctx(title: str, active: str, **kw):
    """统一构建模板上下文（request 由 TemplateResponse 自动注入）"""
    return {"title": title, "active": active, **kw}


# ════════════════════════════════════════════
#  登录 / 登出
# ════════════════════════════════════════════


@router.get("/login")
def login_page(request: Request):
    """管理员登录页"""
    return templates.TemplateResponse(request, "admin/login.html", {"title": "管理员登录"})


@router.post("/login")
def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """管理员登录提交"""
    user = db.query(User).filter(User.username == username).first()
    if not user or user.role != "admin" or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request, "admin/login.html",
            {"title": "管理员登录", "error": "用户名或密码错误，或无管理员权限"},
        )

    token = create_access_token(data={"sub": str(user.id)})
    resp = RedirectResponse(url="/admin", status_code=303)
    resp.set_cookie(key="admin_token", value=token, max_age=86400, httponly=True, path="/")
    return resp


@router.get("/logout")
def logout():
    """退出登录"""
    resp = RedirectResponse(url="/admin/login", status_code=303)
    resp.delete_cookie("admin_token", path="/")
    return resp


# ════════════════════════════════════════════
#  控制台
# ════════════════════════════════════════════


@router.get("")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """后台控制台首页"""
    stats = {
        "products_count": db.query(Product).count(),
        "categories_count": db.query(Category).count(),
        "orders_count": db.query(Order).count(),
        "users_count": db.query(User).count(),
    }
    return templates.TemplateResponse(
        request, "admin/dashboard.html",
        _ctx("控制台", "dashboard", stats=stats, current_user=_admin),
    )


# ════════════════════════════════════════════
#  商品管理
# ════════════════════════════════════════════


@router.get("/products")
def product_list(
    request: Request,
    category_id: str = FQuery(""),
    keyword: str = FQuery(""),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """商品列表"""
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == int(category_id))
    if keyword:
        query = query.filter(Product.name.contains(keyword))
    products = query.order_by(Product.id.desc()).all()
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        request, "admin/products/list.html",
        _ctx("商品管理", "products", products=products, categories=categories,
             category_id=category_id, keyword=keyword, current_user=_admin),
    )


@router.get("/products/create")
def product_create_page(
    request: Request,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """新增商品页"""
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        request, "admin/products/form.html",
        _ctx("新增商品", "products", product=None, categories=categories, current_user=_admin),
    )


@router.post("/products/create")
def product_create_action(
    request: Request,
    name: str = Form(...),
    price: str = Form(...),
    stock: int = Form(...),
    category_id: str = Form(""),
    is_active: int = Form(1),
    image_url: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """新增商品提交"""
    product = Product(
        name=name,
        price=int(round(float(price) * 100)),
        stock=stock,
        category_id=int(category_id) if category_id else None,
        is_active=is_active,
        image_url=image_url,
        description=description,
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)


@router.get("/products/{product_id}/edit")
def product_edit_page(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """编辑商品页"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        request, "admin/products/form.html",
        _ctx("编辑商品", "products", product=product, categories=categories, current_user=_admin),
    )


@router.post("/products/{product_id}/edit")
def product_edit_action(
    product_id: int,
    request: Request,
    name: str = Form(...),
    price: str = Form(...),
    stock: int = Form(...),
    category_id: str = Form(""),
    is_active: int = Form(1),
    image_url: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """编辑商品提交"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    product.name = name
    product.price = int(round(float(price) * 100))
    product.stock = stock
    product.category_id = int(category_id) if category_id else None
    product.is_active = is_active
    product.image_url = image_url
    product.description = description
    db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/products/{product_id}/delete")
def product_delete_action(
    product_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """删除商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)


# ════════════════════════════════════════════
#  分类管理
# ════════════════════════════════════════════


@router.get("/categories")
def category_list(
    request: Request,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """分类列表"""
    return templates.TemplateResponse(
        request, "admin/categories/list.html",
        _ctx("分类管理", "categories", categories=db.query(Category).all(), current_user=_admin),
    )


@router.get("/categories/create")
def category_create_page(
    request: Request,
    _admin: User = Depends(get_admin_user),
):
    """新增分类页"""
    return templates.TemplateResponse(
        request, "admin/categories/form.html",
        _ctx("新增分类", "categories", category=None, current_user=_admin),
    )


@router.post("/categories/create")
def category_create_action(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """新增分类提交"""
    if db.query(Category).filter(Category.name == name).first():
        return templates.TemplateResponse(
            request, "admin/categories/form.html",
            _ctx("新增分类", "categories", category=None, current_user=_admin, error="分类名称已存在"),
        )
    db.add(Category(name=name, description=description))
    db.commit()
    return RedirectResponse(url="/admin/categories", status_code=303)


@router.get("/categories/{category_id}/edit")
def category_edit_page(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """编辑分类页"""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    return templates.TemplateResponse(
        request, "admin/categories/form.html",
        _ctx("编辑分类", "categories", category=cat, current_user=_admin),
    )


@router.post("/categories/{category_id}/edit")
def category_edit_action(
    category_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """编辑分类提交"""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    cat.name = name
    cat.description = description
    db.commit()
    return RedirectResponse(url="/admin/categories", status_code=303)


@router.post("/categories/{category_id}/delete")
def category_delete_action(
    category_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """删除分类"""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if cat:
        if db.query(Product).filter(Product.category_id == category_id).first():
            raise HTTPException(status_code=400, detail="该分类下还有商品，无法删除")
        db.delete(cat)
        db.commit()
    return RedirectResponse(url="/admin/categories", status_code=303)


# ════════════════════════════════════════════
#  订单管理
# ════════════════════════════════════════════


@router.get("/orders")
def order_list(
    request: Request,
    status: str = FQuery(""),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """订单列表"""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    return templates.TemplateResponse(
        request, "admin/orders/list.html",
        _ctx("订单管理", "orders", orders=query.order_by(Order.id.desc()).all(),
             status_filter=status, current_user=_admin),
    )


@router.get("/orders/{order_id}")
def order_detail(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return templates.TemplateResponse(
        request, "admin/orders/detail.html",
        _ctx("订单详情", "orders", order=order, current_user=_admin),
    )


@router.post("/orders/{order_id}/status")
def order_status_action(
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    ALLOWED = {
        "pending": ["paid", "cancelled"],
        "paid": ["shipped"],
        "shipped": ["delivered", "completed"],
        "delivered": ["completed"],
    }
    if order.status in ALLOWED and status in ALLOWED[order.status]:
        order.status = status
        if status == "paid":
            order.paid_at = datetime.now(timezone.utc)
        db.commit()

    return RedirectResponse(url=f"/admin/orders/{order_id}", status_code=303)


# ════════════════════════════════════════════
#  用户管理
# ════════════════════════════════════════════


@router.get("/users")
def user_list(
    request: Request,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """用户列表"""
    return templates.TemplateResponse(
        request, "admin/users/list.html",
        _ctx("用户管理", "users", users=db.query(User).order_by(User.id.desc()).all(), current_user=_admin),
    )

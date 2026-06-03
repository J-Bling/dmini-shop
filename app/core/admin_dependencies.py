"""管理员依赖注入（Cookie-based JWT 用于后台网页）"""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User


def get_admin_user(request: Request, db: Session = Depends(get_db)) -> User:
    """从 Cookie 中解析 JWT 并校验管理员身份"""
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.role != "admin":
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})

    return user

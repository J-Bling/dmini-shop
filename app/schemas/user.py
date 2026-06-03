"""用户相关的请求/响应模型"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: str
    nickname: str = ""


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """更新个人信息请求"""
    nickname: str | None = None
    email: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    nickname: str
    phone: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

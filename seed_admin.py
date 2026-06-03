"""创建默认管理员账号（运行一次即可）"""

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_EMAIL = "admin@mini-shop.com"

db = SessionLocal()
try:
    existing = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if existing:
        existing.role = "admin"
        print(f"管理员账号已存在，已升级角色: {ADMIN_USERNAME}")
    else:
        user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            nickname="管理员",
            role="admin",
        )
        db.add(user)
        print(f"管理员账号创建成功: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    db.commit()
finally:
    db.close()

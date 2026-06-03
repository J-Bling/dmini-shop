"""应用配置"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Mini Shop API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./mini_shop.db"

    # JWT
    SECRET_KEY: str = "change-this-to-a-secure-random-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时

    class Config:
        env_file = ".env"


settings = Settings()

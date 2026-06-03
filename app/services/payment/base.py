"""支付渠道抽象基类（策略模式）"""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import PaymentRecord


class PaymentChannel(ABC):
    """支付渠道基类，所有支付方式都继承这个"""

    @abstractmethod
    def create_payment(self, db: Session, order: Order, record: PaymentRecord) -> dict:
        """创建支付，返回前端需要的支付信息（如支付链接、二维码等）"""
        ...

    @abstractmethod
    def handle_callback(self, db: Session, record: PaymentRecord, callback_data: dict) -> bool:
        """处理支付回调，返回是否成功"""
        ...

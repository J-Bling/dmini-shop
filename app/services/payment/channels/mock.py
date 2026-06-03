"""模拟支付渠道"""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import PaymentRecord
from app.services.payment.base import PaymentChannel

logger = logging.getLogger(__name__)


class MockPayChannel(PaymentChannel):
    """模拟支付 — 不需要真实第三方"""

    def create_payment(self, db: Session, order: Order, record: PaymentRecord) -> dict:
        logger.info("模拟支付创建 pay_no=%s order_no=%s amount=%d", record.pay_no, order.order_no, record.amount)
        return {
            "pay_no": record.pay_no,
            "amount": record.amount,
            "channel": "mock",
            "pay_url": f"/api/pay/{record.pay_no}/confirm",
            "expire_at": record.expire_at.isoformat() if record.expire_at else None,
        }

    def handle_callback(self, db: Session, record: PaymentRecord, callback_data: dict) -> bool:
        """模拟回调 — 直接标记成功"""
        from app.models.order import Order

        success = callback_data.get("success", True)
        logger.info("模拟支付回调 pay_no=%s success=%s", record.pay_no, success)

        if success:
            now = datetime.now(timezone.utc)
            record.status = "success"
            record.paid_at = now

            # 更新订单
            order = db.query(Order).filter(Order.id == record.order_id).first()
            if order:
                order.status = "paid"
                order.paid_at = now

            db.commit()
            return True
        else:
            record.status = "failed"
            db.commit()
            return False

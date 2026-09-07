from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id", ondelete="RESTRICT")
    )
    quantity: Mapped[int] = mapped_column(Integer)
    price_at_order: Mapped[int] = mapped_column(Integer)  # сумма в копейках

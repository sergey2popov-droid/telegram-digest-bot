from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DigestItem(Base):
    __tablename__ = "digest_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    digest_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("digests.id"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

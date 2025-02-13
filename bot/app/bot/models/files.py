from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.models.base import Base


class Files(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    message_id = Column(BigInteger, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    category_id = Column(
        Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=False
    )
    category = relationship("Category", back_populates="files", lazy="joined")

    def __repr__(self):
        return f"<Files(id={self.id}, name={self.name})>"

    def get_category_name(self):
        return self.category.name

    def get_category_id(self):
        return self.category.id

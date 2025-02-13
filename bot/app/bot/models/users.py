from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean
from app.core.models.base import Base
from datetime import datetime


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(String(32), nullable=True)
    full_name = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    last_active_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    is_premium = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User {self.user_id}> {self.full_name}"

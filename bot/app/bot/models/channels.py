from sqlalchemy import Column, Integer, BigInteger, String

from app.core.models.base import Base


class Channels(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    link = Column(String, nullable=False)
    channel_id = Column(BigInteger, unique=True, index=True)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, link={self.link})>"

from sqlalchemy import Column, Integer, String
from db.models.base import Base

class Config(Base):
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Config(key={self.key}, value={self.value})>"
from sqlalchemy import Column, Integer, String
from .base import Base

class Language(Base):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Language(name='{self.name}', code='{self.code}')>"

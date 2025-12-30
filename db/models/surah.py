from sqlalchemy import Column, Integer, String
from .base import Base

class Surah(Base):
    __tablename__ = 'surahs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, unique=True, nullable=False, index=True)
    english_name = Column(String, nullable=False)
    bangla_name = Column(String, nullable=False)
    arabic_name = Column(String, nullable=True)
    english_meaning = Column(String, nullable=True)
    bangla_meaning = Column(String, nullable=True)
    total_ayah = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Surah(number={self.number}, name='{self.english_name}')>"

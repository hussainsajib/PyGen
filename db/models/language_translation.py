from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class LanguageTranslation(Base):
    __tablename__ = 'language_translations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    language_id = Column(Integer, ForeignKey('languages.id'), nullable=False)
    db_name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)

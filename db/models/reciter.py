from sqlalchemy import Column, Integer, String
from db.models.base import Base

class Reciter(Base):
    __tablename__ = "reciters"
    
    id = Column(Integer, primary_key=True, index=True)
    reciter_key = Column(String(50), unique=True, nullable=False, index=True)
    english_name = Column(String(100), nullable=False)
    bangla_name = Column(String(100), nullable=False)
    folder = Column(String(100), nullable=True)
    database = Column(String(100), nullable=True)
    style = Column(String(50), nullable=True)
    playlist_id = Column(String(100), nullable=True)
    wbw_database = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Reciter(key={self.reciter_key}, name={self.english_name})>"

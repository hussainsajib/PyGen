import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.surah import Surah

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_surah_model_creation(db_session):
    surah = Surah(
        number=1,
        english_name="Al-Fatiha",
        bangla_name="আল-ফাতিহা",
        arabic_name="سُوْرَۃُ الفَاتِحَة",
        english_meaning="The Opening",
        bangla_meaning="সূচনা",
        total_ayah=7
    )
    db_session.add(surah)
    db_session.commit()
    
    retrieved = db_session.query(Surah).filter_by(number=1).first()
    assert retrieved.english_name == "Al-Fatiha"
    assert retrieved.bangla_name == "আল-ফাতিহা"
    assert retrieved.arabic_name == "سُوْرَۃُ الفَاتِحَة"
    assert retrieved.english_meaning == "The Opening"
    assert retrieved.bangla_meaning == "সূচনা"
    assert retrieved.total_ayah == 7
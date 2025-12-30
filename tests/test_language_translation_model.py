import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
# This will fail initially
from db.models.language_translation import LanguageTranslation

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_language_translation_model_creation(db_session):
    lt = LanguageTranslation(
        language_id=1,
        db_name="rawai_al_bayan",
        display_name="Rawai Al Bayan"
    )
    db_session.add(lt)
    db_session.commit()
    
    retrieved = db_session.query(LanguageTranslation).filter_by(language_id=1).first()
    assert retrieved.db_name == "rawai_al_bayan"

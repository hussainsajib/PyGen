import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.language import Language

# Use an in-memory SQLite database for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_language_model_brand_name(db_session):
    # Test that we can create a Language instance with brand_name
    lang = Language(name="test_lang", code="tl", brand_name="Test Brand")
    db_session.add(lang)
    db_session.commit()
    
    retrieved = db_session.query(Language).filter_by(name="test_lang").first()
    assert retrieved is not None
    assert retrieved.brand_name == "Test Brand"

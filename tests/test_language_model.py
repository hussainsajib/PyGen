import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
# This import is expected to fail initially
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

def test_language_model_creation(db_session):
    # Test that we can create a Language instance
    lang = Language(name="test_lang", code="tl")
    db_session.add(lang)
    db_session.commit()
    
    retrieved = db_session.query(Language).filter_by(name="test_lang").first()
    assert retrieved is not None
    assert retrieved.code == "tl"

def test_language_constraints(db_session):
    # Test uniqueness constraint if applicable (assuming name is unique)
    lang1 = Language(name="unique_lang", code="ul")
    db_session.add(lang1)
    db_session.commit()
    
    lang2 = Language(name="unique_lang", code="ul2")
    db_session.add(lang2)
    with pytest.raises(Exception): # Specific exception depends on DB driver
        db_session.commit()

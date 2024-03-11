import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import TEST_DB_URL
from db.models import BaseModel


@pytest.fixture(scope="module")
def session():
    # required!
    # CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    # CREATE EXTENSION IF NOT EXISTS ltree;
    engine = create_engine(TEST_DB_URL)
    BaseModel.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    BaseModel.metadata.drop_all(bind=engine)

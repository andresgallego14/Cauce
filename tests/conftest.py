import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infraestructura.database import Base
import infraestructura.models  # noqa: F401  (al importarlo, Base conoce las tablas)


@pytest.fixture
def db():
    motor = create_engine("sqlite://")
    Base.metadata.create_all(motor)
    sesion = sessionmaker(bind=motor)()
    yield sesion
    sesion.close()
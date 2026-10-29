from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import URL_BASE_DE_DATOS

engine = create_engine(URL_BASE_DE_DATOS)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

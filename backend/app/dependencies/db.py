from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager, contextmanager
from app.config import config

DATABASE_URL = config.SQLALCHEMY_DATABASE_URI

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)

def get_db() -> Generator[Session, None]:
    with SessionLocal() as session:
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            raise
        finally:
            session.close()


@contextmanager
def get_db_session() -> Generator[Session, None]:
    with SessionLocal() as session:
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            raise
        finally:
            session.close()

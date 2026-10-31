import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "hangar_manager.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Crea las tablas en la base de datos si no existen."""
    from sim_hangar_manager.database.models import Base

    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Factory/Generator for DB session."""
    return SessionLocal()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
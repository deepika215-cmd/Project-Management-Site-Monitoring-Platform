import os
from pathlib import Path

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Resolve the bundled SQLite database relative to the backend directory,
# not relative to whichever terminal folder uvicorn was started from.
BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")
DEFAULT_SQLITE_PATH = BACKEND_DIR / "buildtrack.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL).strip()

# A relative SQLite URL from .env (sqlite:///./buildtrack.db) is converted
# to the same backend/buildtrack.db file so running uvicorn from a different
# working directory cannot silently create a second empty database.
if DATABASE_URL in {"sqlite:///./buildtrack.db", "sqlite:///buildtrack.db"}:
    DATABASE_URL = DEFAULT_DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

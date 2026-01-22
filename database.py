from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Database connection
# Format: mysql+pymysql://user:password@host:port/db_name
DB_USER = os.getenv("DB_USER", "u937550431_User1234")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Larick434")
DB_HOST = os.getenv("DB_HOST", "srv1752.hstgr.io")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "u937550431_paperchecker")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Fallback to SQLite if no env vars (optional, but good for local dev if they don't have mysql set up yet)
if not os.getenv("DB_HOST"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./automated_checking.db"

# Engine configuration
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

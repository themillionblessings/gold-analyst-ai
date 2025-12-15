import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to sqlite for local dev if DATABASE_URL not set, but production will force Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_dev.db")

# Handle Render's postgres:// vs postgresql:// quirk if present
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    # SQLite specific args, ignored effectively by Postgres engine usually but good to be careful
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

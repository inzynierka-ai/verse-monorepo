from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
from typing import Generator

# Database URL format: postgresql://username:password@localhost/dbname
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/verse"

# Create an engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a base class for our models
Base = declarative_base()

# SessionLocal to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
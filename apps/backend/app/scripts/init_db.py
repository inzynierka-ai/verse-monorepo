import os
import sys
import time
from sqlalchemy.exc import OperationalError

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models import User
from app.db.session import Base, engine, SessionLocal

def wait_for_db(max_retries=30, delay=1):
    """Wait for database to be available"""
    for attempt in range(max_retries):
        try:
            # Try to create a connection
            connection = engine.connect()
            connection.close()
            print("Database is ready!")
            return True
        except OperationalError:
            print(f"Database not ready, attempt {attempt + 1}/{max_retries}. Waiting {delay} seconds...")
            time.sleep(delay)
    
    raise Exception("Database did not become available in time")

def init_db():
    # Wait for database to be available
    wait_for_db()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if we already have data
        user_count = db.query(User).count()
        if user_count == 0:
            print("Initializing database with tables...")
        else:
            print(f"Database already has {user_count} users, skipping initialization")
    finally:
        db.close()
    
    print("Database initialization complete")

if __name__ == "__main__":
    init_db()
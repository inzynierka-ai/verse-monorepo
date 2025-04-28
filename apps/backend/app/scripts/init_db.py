import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models import User
from app.db.session import Base, engine, SessionLocal

def init_db():
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
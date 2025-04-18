from sqlalchemy.orm import Session
from app.models.user import User

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


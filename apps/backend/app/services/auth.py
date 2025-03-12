from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenData

SECRET_KEY = "your_secret_key"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # Changed from 30 to 1440 (24 hours)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate using username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

class ResourcePermission:
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
    
    async def __call__(
        self, 
        resource_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        # Get the appropriate model based on resource type
        if self.resource_type == "chapter":
            from app.models.chapter import Chapter
            resource = db.query(Chapter).filter(Chapter.id == resource_id).first()
            if not resource:
                raise HTTPException(status_code=404, detail=f"Chapter not found")
                
            # Get the associated story to check ownership
            story = resource.story
        
        elif self.resource_type == "scene":
            from app.models.scene import Scene
            resource = db.query(Scene).filter(Scene.id == resource_id).first()
            if not resource:
                raise HTTPException(status_code=404, detail=f"Scene not found")
                
            # Get the chapter, then the story
            story = resource.chapter.story
            
        elif self.resource_type == "story":
            from app.models.story import Story
            story = db.query(Story).filter(Story.id == resource_id).first()
            if not story:
                raise HTTPException(status_code=404, detail=f"Story not found")
            
        else:
            raise ValueError(f"Unknown resource type: {self.resource_type}")
        
        # Check if the current user owns the resource
        if story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to access this {self.resource_type}"
            )
            
        return resource
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, User as UserSchema
from app.services.auth import get_password_hash, authenticate_user, create_access_token, get_current_user

router = APIRouter(tags=["authentication"])

# Define request models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    user: UserSchema

class RegisterResponse(BaseModel):
    token: str
    user: UserSchema

# OAuth2 standard endpoint (for Swagger UI and token generation)
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Form data username field is used as username
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# JSON API endpoint for frontend
@router.post("/login", response_model=TokenResponse)
async def login_json(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    
    # Convert SQLAlchemy model to Pydantic model
    user_data = UserSchema.from_orm(user)
    
    return {
        "token": access_token,
        "user": user_data
    }

@router.post("/register", response_model=RegisterResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check email uniqueness
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check username uniqueness
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
        
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate token using username
    access_token = create_access_token(data={"sub": db_user.username})
    
    # Convert SQLAlchemy model to Pydantic model
    user_data = UserSchema.from_orm(db_user)
    
    return {
        "token": access_token,
        "user": user_data
    }

@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserSchema.from_orm(current_user)
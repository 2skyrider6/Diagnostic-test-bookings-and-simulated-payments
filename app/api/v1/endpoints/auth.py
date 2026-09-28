from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models, schemas
from app.core.config import settings
from app.services import auth_service
from app.db.session import get_db
from app.core.rate_limiter import RateLimiterDep

router = APIRouter()

@router.post("/signup", response_model=schemas.UserRead, dependencies=[Depends(RateLimiterDep(times=5, seconds=60))])
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth_service.create_user(db=db, user=user)

@router.post("/login", response_model=schemas.Token, dependencies=[Depends(RateLimiterDep(times=10, seconds=60))])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
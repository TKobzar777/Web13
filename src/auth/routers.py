from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status

from src.auth.email_utils import send_verification
from src.auth.schemas import UserCreate, UserResponse, Token
from src.auth.repo import UserRepository
from src.auth.utils import create_access_token, create_refresh_token, decode_access_token, create_verification_token, \
    decode_verification_token
from src.auth.password_utils import verify_password
from config.db import get_db

router = APIRouter()
env = Environment(loader=FileSystemLoader("src/templates"))


@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user(user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already registered"
        )
    user = await user_repo.create_user(user_create)
    verification_token = create_verification_token(user.email)
    verification_link = (
        f"http://localhost:8000/auth/verify-email?token={verification_token}"
    )

    # Render email template
    template = env.get_template('verification_email.html')
    email_body = template.render(verification_link=verification_link)

    # Send verification email
    background_tasks.add_task(send_verification, user.email, email_body)
    return user

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    print("Verifying email")
    email: str = decode_verification_token(token)
    print(f"Email: {email}")
    user_repo = UserRepository(db)
    user = await user_repo.get_user(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    print(f"user = {user.email}")
    await user_repo.activate_user(user)
    return {"msg": "Email verified successfully"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email})
    refresh_token = create_refresh_token(
        data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    token_data = decode_access_token(refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_repo = UserRepository(db)
    user = await user_repo.get_user(token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email})
    refresh_token = create_refresh_token(
        data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
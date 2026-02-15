from models.user import UserLogin
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_service import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
)
from repositories.user_repository import UserRepository, get_user_repository
from models.user import Token, UserCreate, User

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=User)
async def register(
    user: UserCreate,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    existing_user = await user_repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    password_hash = get_password_hash(user.password)
    user_id = await user_repo.insert_user(user, password_hash)
    return User(
        id=user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=password_hash,
    )


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    user_login: UserLogin,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    user = await user_repo.get_user_by_email(user_login.email)
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


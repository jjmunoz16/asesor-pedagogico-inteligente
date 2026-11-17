"""Rutas de autenticación y perfil del usuario."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.db.models import User, UserRole
from app.db.session import get_session


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(User).where(User.email == payload.email.lower().strip())).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )
    token = create_access_token(user)
    return TokenResponse(
        access_token=token,
        user=UserPublic(
            id=user.id, email=user.email, full_name=user.full_name, role=user.role
        ),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Annotated[Session, Depends(get_session)]):
    email = payload.email.lower().strip()
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario registrado con ese correo.",
        )
    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=UserRole.STUDENT,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token(user)
    return TokenResponse(
        access_token=token,
        user=UserPublic(
            id=user.id, email=user.email, full_name=user.full_name, role=user.role
        ),
    )


@router.get("/me", response_model=UserPublic)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
    )

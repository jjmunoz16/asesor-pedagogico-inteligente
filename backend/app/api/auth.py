"""Rutas de autenticación, revocación de sesión, gestión de contraseñas y roles admin."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from app.core.rate_limit import get_client_ip, login_rate_limiter, register_rate_limiter
from app.core.security import (
    bearer_scheme,
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    revoke_jwt_token,
    validate_password_strength,
    verify_password,
)
from app.db.models import AuditLog, User, UserRole
from app.db.session import get_session


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class RoleUpdateRequest(BaseModel):
    role: UserRole
    is_active: bool = True


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
def login(
    request: Request,
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
):
    ip = get_client_ip(request)
    normalized_email = payload.email.lower().strip()
    login_rate_limiter.check(
        f"login:ip:{ip}",
        detail="Demasiados intentos de inicio de sesión desde esta IP. Espera unos minutos.",
    )
    login_rate_limiter.check(
        f"login:acct:{ip}:{normalized_email}",
        detail="Cuenta temporalmente bloqueada por múltiples intentos fallidos.",
    )

    user = session.exec(select(User).where(User.email == normalized_email)).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        session.add(
            AuditLog(
                actor_user_id=user.id if user else None,
                action="login_failed",
                entity_type="user",
                entity_id=normalized_email[:120],
                metadata_json=json.dumps({"ip": ip}, ensure_ascii=False),
            )
        )
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    token = create_access_token(user)
    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="login_success",
            entity_type="user",
            entity_id=str(user.id),
            metadata_json=json.dumps({"ip": ip, "role": user.role.value}, ensure_ascii=False),
        )
    )
    session.commit()
    return TokenResponse(
        access_token=token,
        user=UserPublic(
            id=user.id, email=user.email, full_name=user.full_name, role=user.role
        ),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: Request,
    payload: RegisterRequest,
    session: Annotated[Session, Depends(get_session)],
):
    ip = get_client_ip(request)
    register_rate_limiter.check(
        f"register:ip:{ip}",
        detail="Límite de registros alcanzado desde esta IP. Intenta más tarde.",
    )
    validate_password_strength(payload.password)

    email = payload.email.lower().strip()
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario registrado con ese correo.",
        )
    # Principio de mínimo privilegio: auto-registro siempre crea rol STUDENT
    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=UserRole.STUDENT,
    )
    session.add(user)
    session.flush()
    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="user_registered",
            entity_type="user",
            entity_id=str(user.id),
            metadata_json=json.dumps({"ip": ip, "role": UserRole.STUDENT.value}, ensure_ascii=False),
        )
    )
    session.commit()
    session.refresh(user)
    token = create_access_token(user)
    return TokenResponse(
        access_token=token,
        user=UserPublic(
            id=user.id, email=user.email, full_name=user.full_name, role=user.role
        ),
    )


@router.post("/logout")
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    if credentials and credentials.credentials:
        revoke_jwt_token(session, credentials.credentials)
    session.add(
        AuditLog(
            actor_user_id=current_user.id,
            action="logout",
            entity_type="user",
            entity_id=str(current_user.id),
            metadata_json="{}",
        )
    )
    session.commit()
    return {"status": "logged_out"}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La contraseña actual no es correcta.",
        )
    validate_password_strength(payload.new_password)
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La nueva contraseña debe ser diferente a la actual.",
        )
    current_user.password_hash = hash_password(payload.new_password)
    session.add(current_user)
    session.add(
        AuditLog(
            actor_user_id=current_user.id,
            action="password_changed",
            entity_type="user",
            entity_id=str(current_user.id),
            metadata_json="{}",
        )
    )
    session.commit()
    return {"status": "password_updated"}


@router.get("/me", response_model=UserPublic)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
    )


@router.get("/users")
def list_users_admin(
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_session)],
):
    users = session.exec(select(User).order_by(User.id)).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.patch("/users/{user_id}/role")
def update_user_role_admin(
    user_id: int,
    payload: RoleUpdateRequest,
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_session)],
):
    target = session.exec(select(User).where(User.id == user_id)).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    if target.id == admin.id and (payload.role != UserRole.ADMIN or not payload.is_active):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes degradar ni desactivar tu propia cuenta administradora.",
        )
    target.role = payload.role
    target.is_active = payload.is_active
    session.add(target)
    session.add(
        AuditLog(
            actor_user_id=admin.id,
            action="user_role_updated",
            entity_type="user",
            entity_id=str(target.id),
            metadata_json=json.dumps(
                {"role": payload.role.value, "is_active": payload.is_active}, ensure_ascii=False
            ),
        )
    )
    session.commit()
    return {"id": target.id, "role": target.role.value, "is_active": target.is_active}

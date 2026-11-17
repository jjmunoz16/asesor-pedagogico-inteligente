"""Seguridad, hashing de contraseñas, tokens JWT y control de acceso RBAC."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.models import User, UserRole
from app.db.session import get_session


bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Genera un hash bcrypt seguro para la contraseña."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash almacenado."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user: User) -> str:
    """Emite un JWT firmado con el identificador y rol del usuario."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_session)],
    x_demo_role: Annotated[str | None, Header(alias="X-Demo-Role")] = None,
) -> User:
    """
    Obtiene el usuario autenticado a partir del Bearer JWT.
    Si PUBLIC_DEMO_MODE=True y no se envía token, permite acceso directo con el rol de revisión.
    """
    settings = get_settings()
    if not credentials or not credentials.credentials:
        if settings.public_demo_mode:
            target_role = UserRole.TEACHER
            if x_demo_role in {r.value for r in UserRole}:
                target_role = UserRole(x_demo_role)
            demo_user = session.exec(
                select(User).where(User.role == target_role, User.is_active == True)  # noqa: E712
            ).first()
            if demo_user:
                return demo_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación.",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
        ) from exc

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no válido o inactivo.",
        )
    return user


def require_roles(*allowed_roles: UserRole):
    """Dependencia RBAC que restringe el acceso a los roles permitidos."""

    def _checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción.",
            )
        return current_user

    return _checker

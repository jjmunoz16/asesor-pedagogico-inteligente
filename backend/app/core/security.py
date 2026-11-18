"""Seguridad, hashing de contraseñas, tokens JWT con revocación y control de acceso RBAC/BOLA."""

from datetime import datetime, timedelta, timezone
from typing import Annotated
import uuid

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.models import RevokedToken, Submission, User, UserRole
from app.db.session import get_session


bearer_scheme = HTTPBearer(auto_error=False)
JWT_ISSUER = "asesor-pedagogico-api"


def validate_password_strength(password: str) -> None:
    """Valida complejidad mínima de contraseña para prevenir claves triviales."""
    if len(password) < 8 or len(password) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La contraseña debe tener entre 8 y 128 caracteres.",
        )
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_upper and has_lower and has_digit):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La contraseña debe incluir al menos una mayúscula, una minúscula y un número.",
        )


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
    """Emite un JWT firmado con identificador único (jti), emisor y rol del usuario."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "jti": uuid.uuid4().hex,
        "iss": JWT_ISSUER,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(raw_token: str) -> dict:
    """Decodifica y valida firma, algoritmo fijo HS256, emisor y vigencia del JWT."""
    settings = get_settings()
    payload = jwt.decode(
        raw_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=JWT_ISSUER,
        options={"require": ["exp", "iat", "sub", "jti"]},
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Tipo de token inválido.")
    return payload


def revoke_jwt_token(session: Session, raw_token: str) -> None:
    """Registra el jti del token en la lista negra persistente hasta su expiración."""
    try:
        payload = decode_access_token(raw_token)
    except jwt.PyJWTError:
        return
    jti = str(payload.get("jti", ""))
    exp_ts = int(payload.get("exp", 0))
    if not jti:
        return
    exists = session.exec(select(RevokedToken).where(RevokedToken.jti == jti)).first()
    if not exists:
        session.add(
            RevokedToken(
                jti=jti,
                expires_at=datetime.fromtimestamp(exp_ts, tz=timezone.utc),
            )
        )
        session.commit()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_session)],
    x_demo_role: Annotated[str | None, Header(alias="X-Demo-Role")] = None,
) -> User:
    """
    Obtiene el usuario autenticado mediante Bearer JWT válido y no revocado.
    Solo permite acceso sin token si PUBLIC_DEMO_MODE está explícitamente activado.
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
            detail="Se requiere iniciar sesión para acceder a este recurso.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
        jti = str(payload["jti"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, manipulado o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    revoked = session.exec(select(RevokedToken).where(RevokedToken.jti == jti)).first()
    if revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión fue cerrada. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no válido o inactivo.",
            headers={"WWW-Authenticate": "Bearer"},
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


def assert_submission_access(submission: Submission, current_user: User) -> None:
    """Control BOLA/IDOR: protege entregas privadas de otros estudiantes."""
    if current_user.role in {UserRole.TEACHER, UserRole.ADMIN}:
        return
    if submission.is_preloaded_portfolio:
        return
    if submission.owner_user_id == current_user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes autorización para acceder a esta entrega académica privada.",
    )

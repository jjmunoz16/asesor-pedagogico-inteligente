"""Gestión de motor y sesiones de base de datos SQLModel."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


def normalize_database_url(url: str) -> str:
    """Asegura el uso del driver psycopg v3 cuando la URL viene como postgres:// o postgresql://."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def build_engine(database_url: str | None = None):
    url = normalize_database_url(database_url or get_settings().database_url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=False, pool_pre_ping=True, connect_args=connect_args)


engine = build_engine()


def init_db(custom_engine=None) -> None:
    """Crea todas las tablas registradas en SQLModel si no existen."""
    SQLModel.metadata.create_all(custom_engine or engine)


def get_session() -> Generator[Session, None, None]:
    """Provee una sesión transaccional por petición FastAPI."""
    with Session(engine) as session:
        yield session

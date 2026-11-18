"""Configuración compartida de pytest para pruebas aisladas con BD SQLite temporal."""

from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DEMO_STUDENT_PASSWORD", "PytestStudent2026!")
os.environ.setdefault("DEMO_TEACHER_PASSWORD", "PytestTeacher2026!")
os.environ.setdefault("DEMO_ADMIN_PASSWORD", "PytestAdmin2026!")

from app.core.config import get_settings  # noqa: E402
from app.core.rate_limit import reset_all_rate_limiters  # noqa: E402
from app.db.seed import run_seed  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(name="session")
def session_fixture():
    reset_all_rate_limiters()
    get_settings.cache_clear()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        run_seed(session)
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    app = create_app()

    def _override_session():
        yield session

    app.dependency_overrides[get_session] = _override_session
    app.router.lifespan_context = _noop_lifespan
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@asynccontextmanager
async def _noop_lifespan(_app):
    yield


def auth_header(client: TestClient, email: str, password: str) -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="demo_passwords")
def demo_passwords_fixture():
    s = get_settings()
    return {
        "student": s.demo_student_password,
        "teacher": s.demo_teacher_password,
        "admin": s.demo_admin_password,
    }

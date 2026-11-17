"""Rutas públicas, informe integral, mapa mental interactivo y configuración de IA."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.ai.router import ModelRouter
from app.core.config import get_settings
from app.core.security import get_current_user, require_roles
from app.db.models import AuditLog, RuntimeAIConfig, User, UserRole
from app.db.session import get_session
from app.services.mindmap_service import build_mindmap_graph
from app.services.report_service import build_integrated_learning_report


public_router = APIRouter(tags=["public"])
reports_router = APIRouter(prefix="/reports", tags=["reports"])
mindmap_router = APIRouter(prefix="/mindmap", tags=["mindmap"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


class UpdateAIConfigRequest(BaseModel):
    active_provider: str = Field(pattern="^(gemini|groq|ollama|lmstudio|deterministic)$")
    active_model: str = Field(min_length=1, max_length=120)


@public_router.get("/health")
def health(session: Annotated[Session, Depends(get_session)]):
    session.exec(select(RuntimeAIConfig)).first()
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "sandbox_mode": settings.sandbox_mode,
        "public_demo_mode": settings.public_demo_mode,
    }


@public_router.get("/public/overview")
def public_overview():
    """Funcionalidad Obligatoria #7: Abstract del proyecto y presentación del equipo desarrollador."""
    return {
        "project_title": "Asesor Pedagógico Inteligente",
        "course": "Profundización I – Inteligencia Artificial",
        "university": "Universidad de Manizales — Facultad de Ciencias e Ingeniería",
        "abstract": (
            "Plataforma web inteligente diseñada para analizar evidencias académicas reales de las "
            "Cohortes 1 y 2 (seis actividades prácticas), evaluar el cumplimiento de objetivos bajo "
            "tres dimensiones obligatorias (Verificación, Cuantificación determinista 0,0–5,0 y "
            "Recomendación), verificar código fuente en sandbox aislado, habilitar la supervisión y "
            "aprobación docente (Human-in-the-Loop) y consolidar los aprendizajes en un informe "
            "integral y un mapa mental interactivo de competencias."
        ),
        "technologies": [
            "Python 3.12 + FastAPI + Pydantic v2",
            "React + TypeScript + Vite + Tailwind CSS + @xyflow/react",
            "SQLModel + SQLite / PostgreSQL (Neon Free Tier)",
            "Model Router intercambiable (Gemini Free Tier, Groq Free Tier, Ollama/LM Studio, Auditor Determinista)",
            "Sandbox de verificación AST y ejecución aislada sin red",
        ],
        "team": [
            {
                "name": "Juan José Muñoz Naranjo",
                "role": "Arquitectura, Backend, Harness IA y Verificación",
                "initials": "JM",
                "photo_url": None,
            },
            {
                "name": "Christopher Villa Noreña",
                "role": "Frontend React, Experiencia de Usuario y Mapa Mental Interactivo",
                "initials": "CV",
                "photo_url": None,
            },
        ],
    }


@reports_router.get("/integrated")
def integrated_report(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    return build_integrated_learning_report(session)


@mindmap_router.get("")
def get_mindmap(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    cohort: str | None = None,
    level: str | None = None,
    activity: str | None = None,
):
    return build_mindmap_graph(
        session, cohort_filter=cohort, level_filter=level, activity_filter=activity
    )


@admin_router.get("/ai-config")
def get_ai_config(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    runtime = session.exec(select(RuntimeAIConfig)).first()
    router = ModelRouter()
    return {
        "active_provider": runtime.active_provider if runtime else get_settings().ai_provider,
        "active_model": runtime.active_model if runtime else get_settings().gemini_model,
        "providers": router.list_provider_statuses(),
    }


@admin_router.put("/ai-config")
def update_ai_config(
    payload: UpdateAIConfigRequest,
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
    session: Annotated[Session, Depends(get_session)],
):
    runtime = session.exec(select(RuntimeAIConfig)).first()
    if not runtime:
        runtime = RuntimeAIConfig()
    runtime.active_provider = payload.active_provider
    runtime.active_model = payload.active_model.strip()
    runtime.updated_by = admin.id
    runtime.updated_at = datetime.now(timezone.utc)
    session.add(runtime)
    session.add(
        AuditLog(
            actor_user_id=admin.id,
            action="ai_config_updated",
            entity_type="runtime_ai_config",
            entity_id=str(runtime.id or 1),
            metadata_json=f'{{"provider": "{runtime.active_provider}", "model": "{runtime.active_model}"}}',
        )
    )
    session.commit()
    session.refresh(runtime)
    return {
        "active_provider": runtime.active_provider,
        "active_model": runtime.active_model,
    }


@admin_router.get("/audit-logs")
def list_audit_logs(
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
    session: Annotated[Session, Depends(get_session)],
):
    return session.exec(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).all()

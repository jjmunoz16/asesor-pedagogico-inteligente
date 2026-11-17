"""Configuración central de la aplicación leída desde variables de entorno."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    """Parámetros de configuración cargados desde `.env` o variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Asesor Pedagógico Inteligente"
    app_version: str = "1.0.0"
    database_url: str = f"sqlite:///{(BASE_DIR / 'asesor_pedagogico.db').as_posix()}"

    jwt_secret_key: str = "dev-secret-key-change-before-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    ai_provider: Literal["gemini", "groq", "ollama", "lmstudio", "deterministic"] = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_model: str = "qwen2.5-coder-1.5b"

    sandbox_mode: Literal["static_only", "isolated_subprocess"] = "static_only"
    sandbox_timeout_seconds: int = 5

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_upload_size_mb: int = 20
    public_demo_mode: bool = True

    demo_student_password: str = "Estudiante2026!"
    demo_teacher_password: str = "Docente2026!"
    demo_admin_password: str = "Admin2026!"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def uploads_dir(self) -> Path:
        path = BASE_DIR / "storage" / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def source_material_dir(self) -> Path:
        return WORKSPACE_ROOT / "source-material"


@lru_cache
def get_settings() -> Settings:
    return Settings()

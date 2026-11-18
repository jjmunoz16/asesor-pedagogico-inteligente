"""Punto de entrada principal de la API FastAPI — Asesor Pedagógico Inteligente."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.auth import router as auth_router
from app.api.portfolio import router as portfolio_router
from app.api.reports_admin import (
    admin_router,
    mindmap_router,
    public_router,
    reports_router,
)
from app.api.rubrics_evals import evaluations_router, rubrics_router
from app.core.config import BASE_DIR, get_settings
from app.db.seed import run_seed
from app.db.session import engine, init_db


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inyecta cabeceras de endurecimiento HTTP (anti-XSS, anti-Clickjacking, HSTS)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self'"
        )
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with Session(engine) as session:
        run_seed(session)
    yield


def _resolve_static_dir() -> Path | None:
    """Busca archivos compilados del frontend para despliegue Todo-en-Uno."""
    for candidate in (BASE_DIR / "static", BASE_DIR.parent / "frontend" / "dist"):
        if (candidate / "index.html").is_file():
            return candidate
    return None


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.public_demo_mode else None,
        redoc_url="/redoc" if settings.public_demo_mode else None,
        openapi_url="/openapi.json" if settings.public_demo_mode else None,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, _exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno controlado del servidor."},
        )

    api_prefix = "/api/v1"
    app.include_router(public_router, prefix=api_prefix)
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(portfolio_router, prefix=api_prefix)
    app.include_router(rubrics_router, prefix=api_prefix)
    app.include_router(evaluations_router, prefix=api_prefix)
    app.include_router(reports_router, prefix=api_prefix)
    app.include_router(mindmap_router, prefix=api_prefix)
    app.include_router(admin_router, prefix=api_prefix)

    static_dir = _resolve_static_dir()
    if static_dir:
        assets_dir = static_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_spa(full_path: str):
            if full_path.startswith("api/") or "\x00" in full_path:
                raise HTTPException(status_code=404, detail="Recurso no encontrado")
            try:
                candidate = (static_dir / full_path).resolve()
            except (OSError, ValueError) as exc:
                raise HTTPException(status_code=404, detail="Recurso no encontrado") from exc
            if (
                full_path
                and candidate.is_file()
                and static_dir.resolve() in candidate.parents
            ):
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()

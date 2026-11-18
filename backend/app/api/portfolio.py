"""Rutas del portafolio académico (cohortes, actividades, entregas y carga segura)."""

from pathlib import Path
import re
from typing import Annotated
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.rate_limit import ai_action_rate_limiter, get_client_ip
from app.core.security import assert_submission_access, get_current_user, require_roles
from app.db.models import (
    Activity,
    ActivityType,
    AuditLog,
    Cohort,
    Evaluation,
    EvidenceFile,
    Submission,
    User,
    UserRole,
)
from app.db.session import get_session
from app.services.extractor_service import (
    classify_file,
    compute_sha256_bytes,
    extract_content_from_path,
)
from app.services.rubric_service import get_active_rubric_bundle


router = APIRouter(prefix="/portfolio", tags=["portfolio"])

ALLOWED_UPLOAD_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".md",
    ".txt",
    ".py",
    ".ipynb",
    ".json",
    ".csv",
    ".html",
    ".htm",
    ".png",
    ".jpg",
    ".jpeg",
    ".zip",
    ".mp4",
}
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
_GITHUB_REPO_RE = re.compile(r"^/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")


def _sanitize_upload_filename(raw_name: str | None) -> str:
    candidate = Path((raw_name or "archivo.bin").replace("\x00", "")).name.strip()
    if not candidate or candidate in {".", ".."} or candidate.startswith("."):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido o oculto no permitido.",
        )
    safe = _SAFE_FILENAME_RE.sub("_", candidate)[:120]
    ext = Path(safe).suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Extensión '{ext or 'sin extensión'}' no permitida por política de seguridad.",
        )
    return safe


def _validate_repo_url(repo_url: str | None) -> str | None:
    if not repo_url or not repo_url.strip():
        return None
    cleaned = repo_url.strip()
    parsed = urlparse(cleaned)
    if (
        parsed.scheme != "https"
        or parsed.netloc.lower() != "github.com"
        or not _GITHUB_REPO_RE.match(parsed.path)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La URL del repositorio debe seguir el formato https://github.com/usuario/repositorio.",
        )
    return cleaned


class ActivityCreateRequest(BaseModel):
    cohort_id: int
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=3, max_length=200)
    activity_type: ActivityType = ActivityType.LAB
    official_objective: str | None = Field(default=None, max_length=3000)
    description: str = Field(default="", max_length=3000)


@router.get("/cohorts")
def list_cohorts(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    return session.exec(select(Cohort).order_by(Cohort.order_index)).all()


@router.get("/activities")
def list_activities(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    cohort_id: int | None = None,
):
    stmt = select(Activity).order_by(Activity.id)
    if cohort_id is not None:
        stmt = stmt.where(Activity.cohort_id == cohort_id)
    activities = session.exec(stmt).all()
    cohorts = {c.id: c for c in session.exec(select(Cohort)).all()}
    is_privileged = current_user.role in {UserRole.TEACHER, UserRole.ADMIN}

    items = []
    for act in activities:
        subs = session.exec(
            select(Submission).where(Submission.activity_id == act.id).order_by(Submission.id.desc())
        ).all()
        visible_subs = [
            s
            for s in subs
            if is_privileged or s.is_preloaded_portfolio or s.owner_user_id == current_user.id
        ]
        latest_sub = visible_subs[0] if visible_subs else None
        evidences = (
            session.exec(select(EvidenceFile).where(EvidenceFile.submission_id == latest_sub.id)).all()
            if latest_sub
            else []
        )
        latest_eval = (
            session.exec(
                select(Evaluation)
                .where(Evaluation.submission_id == latest_sub.id)
                .order_by(Evaluation.id.desc())
            ).first()
            if latest_sub
            else None
        )
        bundle = get_active_rubric_bundle(session, act)
        cohort = cohorts.get(act.cohort_id)
        items.append(
            {
                "id": act.id,
                "slug": act.slug,
                "title": act.title,
                "activity_type": act.activity_type.value,
                "cohort_id": act.cohort_id,
                "cohort_code": cohort.code if cohort else "",
                "cohort_name": cohort.name if cohort else "",
                "official_objective": act.official_objective,
                "objective_source": act.objective_source,
                "description": act.description,
                "has_valid_rubric": bundle is not None,
                "rubric_is_template": bundle[0].is_template_proposal if bundle else False,
                "rubric_version": bundle[1].version_number if bundle else None,
                "latest_submission_id": latest_sub.id if latest_sub else None,
                "evidence_count": len(evidences),
                "evidences": [
                    {
                        "id": e.id,
                        "filename": e.filename,
                        "relative_path": e.relative_path,
                        "file_category": e.file_category.value,
                        "size_bytes": e.size_bytes,
                        "sha256_hash": e.sha256_hash,
                        "extraction_status": e.extraction_status.value,
                    }
                    for e in evidences
                ],
                "latest_evaluation": (
                    {
                        "id": latest_eval.id,
                        "status": latest_eval.status.value,
                        "calculated_score_ai": latest_eval.calculated_score_ai,
                        "final_score_approved": latest_eval.final_score_approved,
                        "ai_provider": latest_eval.ai_provider,
                        "ai_model": latest_eval.ai_model,
                    }
                    if latest_eval
                    else None
                ),
            }
        )
    return items


@router.post("/activities", status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreateRequest,
    teacher: Annotated[User, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_session)],
):
    if not session.exec(select(Cohort).where(Cohort.id == payload.cohort_id)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohorte no encontrada.")
    if session.exec(select(Activity).where(Activity.slug == payload.slug)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El slug ya existe.")
    act = Activity(
        cohort_id=payload.cohort_id,
        slug=payload.slug.strip(),
        title=payload.title.strip(),
        activity_type=payload.activity_type,
        official_objective=payload.official_objective.strip() if payload.official_objective else None,
        objective_source="Registrado por docente en plataforma",
        description=payload.description.strip(),
    )
    session.add(act)
    session.flush()
    session.add(
        AuditLog(
            actor_user_id=teacher.id,
            action="activity_created",
            entity_type="activity",
            entity_id=str(act.id),
            metadata_json="{}",
        )
    )
    session.commit()
    session.refresh(act)
    return act


@router.get("/submissions/{submission_id}")
def get_submission_detail(
    submission_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    sub = session.exec(select(Submission).where(Submission.id == submission_id)).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada.")
    assert_submission_access(sub, current_user)
    evidences = session.exec(select(EvidenceFile).where(EvidenceFile.submission_id == sub.id)).all()
    return {
        "id": sub.id,
        "activity_id": sub.activity_id,
        "student_group_name": sub.student_group_name,
        "repo_url": sub.repo_url,
        "notes": sub.notes,
        "submitted_at": sub.submitted_at.isoformat(),
        "evidences": evidences,
    }


@router.post("/activities/{activity_id}/submissions", status_code=status.HTTP_201_CREATED)
async def create_submission_with_files(
    request: Request,
    activity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    student_group_name: Annotated[str, Form(max_length=160)] = "Estudiante",
    repo_url: Annotated[str | None, Form(max_length=300)] = None,
    notes: Annotated[str, Form(max_length=2000)] = "",
    files: Annotated[list[UploadFile], File()] = [],
):
    ip = get_client_ip(request)
    ai_action_rate_limiter.check(f"upload:{ip}:{current_user.id}")

    activity = session.exec(select(Activity).where(Activity.id == activity_id)).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada.")
    if not files and not repo_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debe adjuntar al menos un archivo de evidencia o una URL de repositorio.",
        )
    if len(files) > 15:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Máximo 15 archivos por entrega.",
        )

    validated_repo = _validate_repo_url(repo_url)
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    sub = Submission(
        activity_id=activity.id,
        student_group_name=student_group_name.strip() or current_user.full_name,
        owner_user_id=current_user.id,
        repo_url=validated_repo,
        notes=notes.strip(),
        is_preloaded_portfolio=False,
    )
    session.add(sub)
    session.flush()

    upload_dir = (settings.uploads_dir / f"sub_{sub.id}").resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_evidences = []
    for up in files:
        safe_name = _sanitize_upload_filename(up.filename)
        # Lectura por bloques para frenar cargas gigantes antes de saturar memoria RAM
        chunks: list[bytes] = []
        total_len = 0
        while True:
            chunk = await up.read(65536)
            if not chunk:
                break
            total_len += len(chunk)
            if total_len > max_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"El archivo '{safe_name}' supera el límite de {settings.max_upload_size_mb} MB.",
                )
            chunks.append(chunk)
        raw_bytes = b"".join(chunks)

        dest = (upload_dir / safe_name).resolve()
        if upload_dir not in dest.parents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta de archivo inválida.")
        dest.write_bytes(raw_bytes)
        cat, mime = classify_file(dest)
        sha256 = compute_sha256_bytes(raw_bytes)
        summary, ext_status = extract_content_from_path(dest)
        ev = EvidenceFile(
            submission_id=sub.id,
            filename=safe_name,
            relative_path=safe_name,
            mime_type=up.content_type or mime,
            file_category=cat,
            size_bytes=len(raw_bytes),
            sha256_hash=sha256,
            storage_uri=str(dest),
            extracted_text_summary=summary,
            extraction_status=ext_status,
        )
        session.add(ev)
        saved_evidences.append(ev)

    session.add(
        AuditLog(
            actor_user_id=current_user.id,
            action="submission_uploaded",
            entity_type="submission",
            entity_id=str(sub.id),
            metadata_json=f'{{"files": {len(saved_evidences)}}}',
        )
    )
    session.commit()
    return {"submission_id": sub.id, "evidences_saved": len(saved_evidences)}

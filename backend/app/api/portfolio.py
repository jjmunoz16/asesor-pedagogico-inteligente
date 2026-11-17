"""Rutas del portafolio académico (cohortes, actividades, entregas y evidencias)."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import get_current_user, require_roles
from app.db.models import (
    Activity,
    ActivityType,
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


class ActivityCreateRequest(BaseModel):
    cohort_id: int
    slug: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=3, max_length=200)
    activity_type: ActivityType = ActivityType.LAB
    official_objective: str | None = None
    description: str = ""


@router.get("/cohorts")
def list_cohorts(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    return session.exec(select(Cohort).order_by(Cohort.order_index)).all()


@router.get("/activities")
def list_activities(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    cohort_id: int | None = None,
):
    stmt = select(Activity).order_by(Activity.id)
    if cohort_id is not None:
        stmt = stmt.where(Activity.cohort_id == cohort_id)
    activities = session.exec(stmt).all()
    cohorts = {c.id: c for c in session.exec(select(Cohort)).all()}

    items = []
    for act in activities:
        subs = session.exec(
            select(Submission).where(Submission.activity_id == act.id).order_by(Submission.id.desc())
        ).all()
        latest_sub = subs[0] if subs else None
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
    _: Annotated[User, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_session)],
):
    if session.exec(select(Activity).where(Activity.slug == payload.slug)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El slug ya existe.")
    act = Activity(
        cohort_id=payload.cohort_id,
        slug=payload.slug.strip(),
        title=payload.title.strip(),
        activity_type=payload.activity_type,
        official_objective=payload.official_objective,
        objective_source="Registrado en plataforma",
        description=payload.description,
    )
    session.add(act)
    session.commit()
    session.refresh(act)
    return act


@router.get("/submissions/{submission_id}")
def get_submission_detail(
    submission_id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    sub = session.exec(select(Submission).where(Submission.id == submission_id)).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada.")
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
    activity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    student_group_name: Annotated[str, Form()] = "Estudiante",
    repo_url: Annotated[str | None, Form()] = None,
    notes: Annotated[str, Form()] = "",
    files: Annotated[list[UploadFile], File()] = [],
):
    activity = session.exec(select(Activity).where(Activity.id == activity_id)).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada.")
    if not files and not repo_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debe adjuntar al menos un archivo de evidencia o una URL de repositorio.",
        )

    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    sub = Submission(
        activity_id=activity.id,
        student_group_name=student_group_name.strip(),
        owner_user_id=current_user.id,
        repo_url=repo_url.strip() if repo_url else None,
        notes=notes,
        is_preloaded_portfolio=False,
    )
    session.add(sub)
    session.flush()

    upload_dir = settings.uploads_dir / f"sub_{sub.id}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_evidences = []
    for up in files:
        raw_bytes = await up.read()
        if len(raw_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo '{up.filename}' supera el límite de {settings.max_upload_size_mb} MB.",
            )
        safe_name = Path(up.filename or "archivo.bin").name
        dest = upload_dir / safe_name
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

    session.commit()
    return {"submission_id": sub.id, "evidences_saved": len(saved_evidences)}

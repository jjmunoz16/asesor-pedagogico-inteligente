"""Rutas para gestión de rúbricas (100 %), evaluación en 3 dimensiones y revisión HITL."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.core.security import get_current_user, require_roles
from app.db.models import Activity, Rubric, RubricCriterion, RubricVersion, User, UserRole
from app.db.session import get_session
from app.schemas.evaluation import RunEvaluationRequest, TeacherReviewRequest
from app.schemas.rubric import RubricUpsertRequest
from app.services.evaluation_service import review_evaluation_hitl, run_submission_evaluation
from app.services.report_service import (
    build_individual_report,
    render_individual_report_markdown,
)
from app.services.rubric_service import create_or_version_rubric, get_active_rubric_bundle


rubrics_router = APIRouter(prefix="/rubrics", tags=["rubrics"])
evaluations_router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@rubrics_router.get("/activity/{activity_id}")
def get_activity_rubric(
    activity_id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    activity = session.exec(select(Activity).where(Activity.id == activity_id)).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada.")
    bundle = get_active_rubric_bundle(session, activity)
    if not bundle:
        return {"activity_id": activity_id, "rubric": None}
    rubric, version, criteria = bundle
    all_versions = session.exec(
        select(RubricVersion)
        .where(RubricVersion.rubric_id == rubric.id)
        .order_by(RubricVersion.version_number.desc())
    ).all()
    return {
        "activity_id": activity_id,
        "rubric": {
            "id": rubric.id,
            "name": rubric.name,
            "is_template_proposal": rubric.is_template_proposal,
            "active_version": {
                "id": version.id,
                "version_number": version.version_number,
                "is_valid": version.is_valid,
                "notes": version.notes,
                "created_at": version.created_at.isoformat(),
                "total_weight": round(sum(c.weight_percent for c in criteria), 2),
                "criteria": [
                    {
                        "id": c.id,
                        "code": c.code,
                        "competency_name": c.competency_name,
                        "criterion_name": c.criterion_name,
                        "description": c.description,
                        "weight_percent": c.weight_percent,
                        "performance_levels": json.loads(c.performance_levels_json),
                    }
                    for c in criteria
                ],
            },
            "versions_history": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "is_valid": v.is_valid,
                    "notes": v.notes,
                    "created_at": v.created_at.isoformat(),
                }
                for v in all_versions
            ],
        },
    }


@rubrics_router.post("", status_code=status.HTTP_201_CREATED)
def upsert_rubric(
    payload: RubricUpsertRequest,
    teacher: Annotated[User, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_session)],
):
    rubric, version, criteria = create_or_version_rubric(session, payload, user_id=teacher.id)
    return {
        "rubric_id": rubric.id,
        "version_id": version.id,
        "version_number": version.version_number,
        "total_weight": round(sum(c.weight_percent for c in criteria), 2),
    }


@evaluations_router.post("/submissions/{submission_id}/run", status_code=status.HTTP_201_CREATED)
async def run_evaluation(
    submission_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    payload: RunEvaluationRequest | None = None,
):
    req = payload or RunEvaluationRequest()
    evaluation = await run_submission_evaluation(
        session=session,
        submission_id=submission_id,
        actor_user=current_user,
        provider_override=req.provider_override,
        model_override=req.model_override,
    )
    return build_individual_report(session, evaluation.id)


@evaluations_router.get("/{evaluation_id}")
def get_evaluation_report(
    evaluation_id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    return build_individual_report(session, evaluation_id)


@evaluations_router.get("/{evaluation_id}/markdown")
def export_evaluation_markdown(
    evaluation_id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    report = build_individual_report(session, evaluation_id)
    md = render_individual_report_markdown(report)
    return Response(
        content=md,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="informe_evaluacion_{evaluation_id}.md"'
        },
    )


@evaluations_router.post("/{evaluation_id}/review")
def submit_teacher_review(
    evaluation_id: int,
    payload: TeacherReviewRequest,
    teacher: Annotated[User, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_session)],
):
    evaluation = review_evaluation_hitl(
        session=session,
        evaluation_id=evaluation_id,
        teacher=teacher,
        review_req=payload,
    )
    return build_individual_report(session, evaluation.id)

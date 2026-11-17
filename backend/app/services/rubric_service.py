"""Gestión de rúbricas versionadas con validación estricta del 100 %."""

import json

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.db.models import Activity, Rubric, RubricCriterion, RubricVersion
from app.schemas.rubric import RubricUpsertRequest
from app.services.scoring_service import validate_rubric_weights


def create_or_version_rubric(
    session: Session, payload: RubricUpsertRequest, user_id: int | None
) -> tuple[Rubric, RubricVersion, list[RubricCriterion]]:
    activity = session.exec(select(Activity).where(Activity.id == payload.activity_id)).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad {payload.activity_id} no encontrada.",
        )

    validate_rubric_weights(c.weight_percent for c in payload.criteria)

    rubric = session.exec(select(Rubric).where(Rubric.activity_id == activity.id)).first()
    if not rubric:
        rubric = Rubric(
            activity_id=activity.id,
            name=payload.name,
            is_template_proposal=payload.is_template_proposal,
            created_by=user_id,
        )
        session.add(rubric)
        session.flush()
    else:
        rubric.name = payload.name
        rubric.is_template_proposal = payload.is_template_proposal

    existing_versions = session.exec(
        select(RubricVersion).where(RubricVersion.rubric_id == rubric.id)
    ).all()
    next_version = max((v.version_number for v in existing_versions), default=0) + 1

    version = RubricVersion(
        rubric_id=rubric.id,
        version_number=next_version,
        is_valid=True,
        notes=payload.notes,
    )
    session.add(version)
    session.flush()

    created_criteria: list[RubricCriterion] = []
    for item in payload.criteria:
        criterion = RubricCriterion(
            rubric_version_id=version.id,
            code=item.code.strip(),
            competency_name=item.competency_name.strip(),
            criterion_name=item.criterion_name.strip(),
            description=item.description.strip(),
            weight_percent=round(float(item.weight_percent), 2),
            performance_levels_json=json.dumps(item.performance_levels, ensure_ascii=False),
        )
        session.add(criterion)
        created_criteria.append(criterion)

    session.flush()
    activity.active_rubric_version_id = version.id
    session.add(activity)
    session.commit()
    session.refresh(rubric)
    session.refresh(version)
    for c in created_criteria:
        session.refresh(c)

    return rubric, version, created_criteria


def get_active_rubric_bundle(
    session: Session, activity: Activity
) -> tuple[Rubric, RubricVersion, list[RubricCriterion]] | None:
    if not activity.active_rubric_version_id:
        return None
    version = session.exec(
        select(RubricVersion).where(RubricVersion.id == activity.active_rubric_version_id)
    ).first()
    if not version:
        return None
    rubric = session.exec(select(Rubric).where(Rubric.id == version.rubric_id)).first()
    criteria = session.exec(
        select(RubricCriterion)
        .where(RubricCriterion.rubric_version_id == version.id)
        .order_by(RubricCriterion.id)
    ).all()
    if not rubric or not criteria:
        return None
    return rubric, version, list(criteria)

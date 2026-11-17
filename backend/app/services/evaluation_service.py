"""Orquestación del Harness de Evaluación en 3 dimensiones y flujo docente HITL."""

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.ai.base import EvaluationContext
from app.ai.router import ModelRouter
from app.core.config import get_settings
from app.db.models import (
    Activity,
    AuditLog,
    CodeCheckResult,
    Cohort,
    CriterionEvaluation,
    Evaluation,
    EvaluationStatus,
    EvidenceFile,
    FileCategory,
    ObjectiveStatus,
    RubricCriterion,
    RuntimeAIConfig,
    Submission,
    TeacherReview,
    User,
)
from app.schemas.evaluation import AIEvaluationPayload, TeacherReviewRequest
from app.services.rubric_service import get_active_rubric_bundle
from app.services.sandbox_service import run_sandbox_checks
from app.services.scoring_service import calculate_weighted_score


def _resolve_active_ai_settings(
    session: Session, provider_override: str | None, model_override: str | None
) -> tuple[str, str | None]:
    if provider_override:
        return provider_override, model_override
    runtime = session.exec(select(RuntimeAIConfig)).first()
    if runtime:
        return runtime.active_provider, model_override or runtime.active_model
    settings = get_settings()
    return settings.ai_provider, model_override


def _load_code_files_for_sandbox(evidences: list[EvidenceFile]) -> list[tuple[str, str]]:
    """Lee únicamente archivos de código/datos pequeños desde su URI local o resumen extraído."""
    code_files: list[tuple[str, str]] = []
    for ev in evidences:
        ext = Path(ev.filename).suffix.lower()
        if ext in {".py", ".json", ".html", ".htm"} or ev.file_category == FileCategory.SOURCE_CODE:
            content = ""
            if ev.storage_uri:
                p = Path(ev.storage_uri)
                if p.exists() and p.is_file():
                    content = p.read_text(encoding="utf-8", errors="replace")
            if not content and ev.extracted_text_summary:
                content = ev.extracted_text_summary
            if content:
                code_files.append((ev.filename, content))
    return code_files


def _validate_payload_against_context(
    payload: AIEvaluationPayload,
    criteria: list[RubricCriterion],
    valid_filenames: set[str],
) -> None:
    """Comprueba que los criterion_id existan en la rúbrica y los archivos citados existan en la entrega."""
    expected_codes = {c.code for c in criteria}
    received_codes = {q.criterion_id for q in payload.cuantificacion_por_criterio}
    missing = expected_codes - received_codes
    extra = received_codes - expected_codes
    if missing or extra:
        raise ValueError(
            f"Criterios inválidos en salida IA. Faltantes={sorted(missing)}, desconocidos={sorted(extra)}."
        )

    for cited in payload.verificacion.evidencias_citadas:
        if cited.archivo not in valid_filenames:
            raise ValueError(
                f"El modelo citó un archivo inexistente en la entrega: '{cited.archivo}'."
            )


async def run_submission_evaluation(
    session: Session,
    submission_id: int,
    actor_user: User,
    provider_override: str | None = None,
    model_override: str | None = None,
) -> Evaluation:
    submission = session.exec(select(Submission).where(Submission.id == submission_id)).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada.")

    activity = session.exec(select(Activity).where(Activity.id == submission.activity_id)).first()
    cohort = session.exec(select(Cohort).where(Cohort.id == activity.cohort_id)).first()
    bundle = get_active_rubric_bundle(session, activity)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La actividad no tiene una rúbrica válida (suma 100 %) asignada.",
        )
    _, rubric_version, criteria = bundle

    evidences = session.exec(
        select(EvidenceFile).where(EvidenceFile.submission_id == submission.id)
    ).all()
    if not evidences:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La entrega no contiene archivos de evidencia para evaluar.",
        )

    settings = get_settings()
    code_files = _load_code_files_for_sandbox(list(evidences))
    sandbox_dict = run_sandbox_checks(
        code_files,
        mode=settings.sandbox_mode,
        timeout_seconds=settings.sandbox_timeout_seconds,
    )
    code_check = CodeCheckResult(
        submission_id=submission.id,
        sandbox_mode=sandbox_dict["sandbox_mode"],
        syntax_valid=sandbox_dict["syntax_valid"],
        files_checked_json=json.dumps(sandbox_dict["files_checked"], ensure_ascii=False),
        static_findings_json=json.dumps(sandbox_dict["static_findings"], ensure_ascii=False),
        unit_tests_passed=sandbox_dict["unit_tests_passed"],
        unit_tests_total=sandbox_dict["unit_tests_total"],
        execution_time_ms=sandbox_dict["execution_time_ms"],
    )
    session.add(code_check)

    ctx = EvaluationContext(
        activity_title=activity.title,
        cohort_name=cohort.name if cohort else "Sin cohorte",
        official_objective=activity.official_objective,
        criteria=[
            {
                "code": c.code,
                "competency_name": c.competency_name,
                "criterion_name": c.criterion_name,
                "description": c.description,
                "weight_percent": c.weight_percent,
                "performance_levels": json.loads(c.performance_levels_json),
            }
            for c in criteria
        ],
        evidences=[
            {
                "filename": e.filename,
                "file_category": e.file_category.value,
                "extraction_status": e.extraction_status.value,
                "sha256_hash": e.sha256_hash,
                "extracted_text_summary": e.extracted_text_summary,
            }
            for e in evidences
        ],
        sandbox_result=sandbox_dict,
    )

    provider_name, chosen_model = _resolve_active_ai_settings(
        session, provider_override, model_override
    )
    router = ModelRouter(settings=settings)
    try:
        used_provider, used_model, ai_payload = await router.evaluate_with_provider(
            ctx, provider_name=provider_name, model_override=chosen_model
        )
        valid_filenames = {e.filename for e in evidences}
        _validate_payload_against_context(ai_payload, criteria, valid_filenames)
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error ejecutando o validando la evaluación IA ({provider_name}): {exc}",
        ) from exc

    crit_by_code = {c.code: c for c in criteria}
    score_pairs: list[tuple[float, float]] = []
    for q in ai_payload.cuantificacion_por_criterio:
        crit = crit_by_code[q.criterion_id]
        score_pairs.append((q.puntaje_criterio, crit.weight_percent))

    # Cálculo determinista obligatorio en backend (nunca por el LLM)
    calculated_score = calculate_weighted_score(score_pairs)

    evaluation = Evaluation(
        submission_id=submission.id,
        rubric_version_id=rubric_version.id,
        status=EvaluationStatus.DRAFT_AI,
        ai_provider=used_provider,
        ai_model=used_model,
        prompt_version="v1.0",
        objective_met=ObjectiveStatus(ai_payload.verificacion.objetivo_cumplido),
        verification_summary=ai_payload.verificacion.resumen_verificacion,
        cited_evidences_json=json.dumps(
            [e.model_dump() for e in ai_payload.verificacion.evidencias_citadas],
            ensure_ascii=False,
        ),
        missing_items_json=json.dumps(
            ai_payload.verificacion.faltantes_detectados, ensure_ascii=False
        ),
        recommendations_json=json.dumps(
            ai_payload.recomendaciones.model_dump(), ensure_ascii=False
        ),
        calculated_score_ai=calculated_score,
        raw_validated_payload_json=ai_payload.model_dump_json(),
    )
    session.add(evaluation)
    session.flush()

    for q in ai_payload.cuantificacion_por_criterio:
        crit = crit_by_code[q.criterion_id]
        session.add(
            CriterionEvaluation(
                evaluation_id=evaluation.id,
                rubric_criterion_id=crit.id,
                ai_level_label=q.nivel_desempeno,
                ai_criterion_score=q.puntaje_criterio,
                cited_evidences_json=json.dumps(q.evidencias, ensure_ascii=False),
                justification=q.justificacion,
            )
        )

    session.add(
        AuditLog(
            actor_user_id=actor_user.id,
            action="evaluation_generated",
            entity_type="evaluation",
            entity_id=str(evaluation.id),
            metadata_json=json.dumps(
                {
                    "provider": used_provider,
                    "model": used_model,
                    "rubric_version_id": rubric_version.id,
                    "calculated_score_ai": calculated_score,
                },
                ensure_ascii=False,
            ),
        )
    )
    session.commit()
    session.refresh(evaluation)
    return evaluation


def review_evaluation_hitl(
    session: Session,
    evaluation_id: int,
    teacher: User,
    review_req: TeacherReviewRequest,
) -> Evaluation:
    evaluation = session.exec(select(Evaluation).where(Evaluation.id == evaluation_id)).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evaluación no encontrada."
        )

    crit_evals = session.exec(
        select(CriterionEvaluation).where(CriterionEvaluation.evaluation_id == evaluation.id)
    ).all()
    crit_eval_by_id = {ce.id: ce for ce in crit_evals}
    criteria_weights = {
        c.id: c.weight_percent
        for c in session.exec(
            select(RubricCriterion).where(
                RubricCriterion.rubric_version_id == evaluation.rubric_version_id
            )
        ).all()
    }

    diffs: dict[str, Any] = {}
    for adj in review_req.adjustments:
        ce = crit_eval_by_id.get(adj.criterion_evaluation_id)
        if not ce:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Criterio evaluado {adj.criterion_evaluation_id} no pertenece a esta evaluación.",
            )
        old_val = ce.teacher_criterion_score if ce.teacher_criterion_score is not None else ce.ai_criterion_score
        if abs(old_val - adj.teacher_criterion_score) > 0.001:
            diffs[str(ce.id)] = {
                "before": old_val,
                "after": adj.teacher_criterion_score,
                "note": adj.justification_note,
            }
        ce.teacher_criterion_score = round(adj.teacher_criterion_score, 2)
        if adj.justification_note:
            ce.justification = f"{ce.justification}\n[Nota docente]: {adj.justification_note}"
        session.add(ce)

    score_pairs = [
        (
            ce.teacher_criterion_score if ce.teacher_criterion_score is not None else ce.ai_criterion_score,
            criteria_weights[ce.rubric_criterion_id],
        )
        for ce in crit_evals
    ]
    recalculated = calculate_weighted_score(score_pairs)

    if review_req.decision == "rejected":
        evaluation.status = EvaluationStatus.REJECTED
    else:
        evaluation.status = EvaluationStatus.APPROVED
        evaluation.final_score_approved = recalculated

    session.add(evaluation)
    session.add(
        TeacherReview(
            evaluation_id=evaluation.id,
            teacher_id=teacher.id,
            decision=review_req.decision,
            comments=review_req.comments,
            score_diff_json=json.dumps(
                {
                    "ai_score": evaluation.calculated_score_ai,
                    "approved_score": evaluation.final_score_approved,
                    "criteria_changes": diffs,
                },
                ensure_ascii=False,
            ),
        )
    )
    session.add(
        AuditLog(
            actor_user_id=teacher.id,
            action=f"teacher_review_{review_req.decision}",
            entity_type="evaluation",
            entity_id=str(evaluation.id),
            metadata_json=json.dumps(
                {"approved_score": evaluation.final_score_approved}, ensure_ascii=False
            ),
        )
    )
    session.commit()
    session.refresh(evaluation)
    return evaluation

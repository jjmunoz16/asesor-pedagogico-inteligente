"""Generación de informes individuales (por actividad) e informe integral de aprendizaje."""

import json
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.db.models import (
    Activity,
    CodeCheckResult,
    Cohort,
    CriterionEvaluation,
    Evaluation,
    EvidenceFile,
    Rubric,
    RubricCriterion,
    RubricVersion,
    Submission,
    TeacherReview,
)


def build_individual_report(session: Session, evaluation_id: int) -> dict[str, Any]:
    evaluation = session.exec(select(Evaluation).where(Evaluation.id == evaluation_id)).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evaluación no encontrada."
        )

    submission = session.exec(select(Submission).where(Submission.id == evaluation.submission_id)).first()
    activity = session.exec(select(Activity).where(Activity.id == submission.activity_id)).first()
    cohort = session.exec(select(Cohort).where(Cohort.id == activity.cohort_id)).first()
    rubric_version = session.exec(
        select(RubricVersion).where(RubricVersion.id == evaluation.rubric_version_id)
    ).first()
    rubric = session.exec(select(Rubric).where(Rubric.id == rubric_version.rubric_id)).first()

    criteria = {
        c.id: c
        for c in session.exec(
            select(RubricCriterion).where(RubricCriterion.rubric_version_id == rubric_version.id)
        ).all()
    }
    crit_evals = session.exec(
        select(CriterionEvaluation).where(CriterionEvaluation.evaluation_id == evaluation.id)
    ).all()
    evidences = session.exec(
        select(EvidenceFile).where(EvidenceFile.submission_id == submission.id)
    ).all()
    latest_check = session.exec(
        select(CodeCheckResult)
        .where(CodeCheckResult.submission_id == submission.id)
        .order_by(CodeCheckResult.id.desc())
    ).first()
    reviews = session.exec(
        select(TeacherReview)
        .where(TeacherReview.evaluation_id == evaluation.id)
        .order_by(TeacherReview.id.desc())
    ).all()

    criteria_breakdown = []
    for ce in crit_evals:
        c = criteria.get(ce.rubric_criterion_id)
        if not c:
            continue
        effective_score = (
            ce.teacher_criterion_score if ce.teacher_criterion_score is not None else ce.ai_criterion_score
        )
        criteria_breakdown.append(
            {
                "criterion_evaluation_id": ce.id,
                "code": c.code,
                "competency_name": c.competency_name,
                "criterion_name": c.criterion_name,
                "weight_percent": c.weight_percent,
                "ai_level_label": ce.ai_level_label,
                "ai_criterion_score": ce.ai_criterion_score,
                "teacher_criterion_score": ce.teacher_criterion_score,
                "effective_score": effective_score,
                "weighted_contribution": round(effective_score * (c.weight_percent / 100.0), 3),
                "cited_evidences": json.loads(ce.cited_evidences_json),
                "justification": ce.justification,
            }
        )

    effective_final = (
        evaluation.final_score_approved
        if evaluation.final_score_approved is not None
        else evaluation.calculated_score_ai
    )

    return {
        "evaluation_id": evaluation.id,
        "status": evaluation.status.value,
        "activity": {
            "id": activity.id,
            "slug": activity.slug,
            "title": activity.title,
            "cohort": cohort.name if cohort else "",
            "cohort_code": cohort.code if cohort else "",
            "official_objective": activity.official_objective,
            "objective_source": activity.objective_source,
        },
        "submission": {
            "id": submission.id,
            "student_group_name": submission.student_group_name,
            "submitted_at": submission.submitted_at.isoformat(),
            "evidences": [
                {
                    "id": e.id,
                    "filename": e.filename,
                    "file_category": e.file_category.value,
                    "size_bytes": e.size_bytes,
                    "sha256_hash": e.sha256_hash,
                    "extraction_status": e.extraction_status.value,
                    "extracted_text_summary": e.extracted_text_summary,
                }
                for e in evidences
            ],
        },
        "traceability": {
            "rubric_name": rubric.name if rubric else "",
            "rubric_version": rubric_version.version_number,
            "is_template_proposal": rubric.is_template_proposal if rubric else True,
            "ai_provider": evaluation.ai_provider,
            "ai_model": evaluation.ai_model,
            "prompt_version": evaluation.prompt_version,
            "created_at": evaluation.created_at.isoformat(),
        },
        "dimension_verificacion": {
            "objetivo_cumplido": evaluation.objective_met.value,
            "resumen_verificacion": evaluation.verification_summary,
            "evidencias_citadas": json.loads(evaluation.cited_evidences_json),
            "faltantes_detectados": json.loads(evaluation.missing_items_json),
        },
        "verificacion_tecnica_sandbox": {
            "executed": latest_check is not None,
            "sandbox_mode": latest_check.sandbox_mode if latest_check else None,
            "syntax_valid": latest_check.syntax_valid if latest_check else None,
            "files_checked": json.loads(latest_check.files_checked_json) if latest_check else [],
            "static_findings": json.loads(latest_check.static_findings_json) if latest_check else [],
            "unit_tests_passed": latest_check.unit_tests_passed if latest_check else None,
            "unit_tests_total": latest_check.unit_tests_total if latest_check else None,
            "execution_time_ms": latest_check.execution_time_ms if latest_check else 0,
        },
        "dimension_cuantificacion": {
            "calculated_score_ai": evaluation.calculated_score_ai,
            "final_score_approved": evaluation.final_score_approved,
            "effective_final_score": effective_final,
            "criteria": criteria_breakdown,
        },
        "dimension_recomendacion": json.loads(evaluation.recommendations_json),
        "teacher_reviews": [
            {
                "id": r.id,
                "decision": r.decision,
                "comments": r.comments,
                "score_diff": json.loads(r.score_diff_json),
                "reviewed_at": r.reviewed_at.isoformat(),
            }
            for r in reviews
        ],
    }


def render_individual_report_markdown(report: dict[str, Any]) -> str:
    act = report["activity"]
    ver = report["dimension_verificacion"]
    quant = report["dimension_cuantificacion"]
    rec = report["dimension_recomendacion"]
    tr = report["traceability"]

    lines = [
        f"# Informe Individual — {act['title']} ({act['cohort']})",
        "",
        f"- **Grupo / Estudiante:** {report['submission']['student_group_name']}",
        f"- **Estado:** `{report['status']}`",
        f"- **Nota Final (Backend 0.0–5.0):** **{quant['effective_final_score']:.2f} / 5.00**",
        f"- **Rúbrica:** {tr['rubric_name']} (v{tr['rubric_version']})",
        f"- **Modelo / Motor:** `{tr['ai_provider']} / {tr['ai_model']}`",
        "",
        "## 1. VERIFICACIÓN (Cumplimiento de Objetivo)",
        f"- **Objetivo:** {act['official_objective'] or 'No consta objetivo oficial explícito.'}",
        f"- **Estado:** `{ver['objetivo_cumplido']}`",
        f"- **Resumen:** {ver['resumen_verificacion']}",
        "",
        "### Evidencias Citadas",
    ]
    for ev in ver["evidencias_citadas"]:
        lines.append(f"- `{ev['archivo']}` ({ev['ubicacion']}): {ev['fragmento']}")
    if ver["faltantes_detectados"]:
        lines.append("\n### Faltantes Detectados")
        for f in ver["faltantes_detectados"]:
            lines.append(f"- {f}")

    lines.extend(["", "## 2. CUANTIFICACIÓN (Rúbrica)"])
    for c in quant["criteria"]:
        lines.append(
            f"- **{c['criterion_name']} ({c['weight_percent']} %):** "
            f"{c['effective_score']:.2f}/5.00 ({c['ai_level_label']}) — {c['justification']}"
        )

    lines.extend(["", "## 3. RECOMENDACIÓN"])
    for key, label in [
        ("fortalezas", "Fortalezas"),
        ("debilidades", "Debilidades"),
        ("mejoras_tecnicas", "Mejoras Técnicas"),
        ("mejoras_conceptuales", "Mejoras Conceptuales"),
        ("mejoras_metodologicas", "Mejoras Metodológicas"),
    ]:
        lines.append(f"### {label}")
        for item in rec.get(key, []):
            lines.append(f"- {item}")

    return "\n".join(lines)


def build_integrated_learning_report(session: Session) -> dict[str, Any]:
    """Consolida resultados reales de Cohorte 1 y Cohorte 2 sin inventar calificaciones."""
    cohorts = session.exec(select(Cohort).order_by(Cohort.order_index)).all()
    activities = session.exec(select(Activity).order_by(Activity.id)).all()

    activity_summaries = []
    cohort_scores: dict[str, list[float]] = {c.code: [] for c in cohorts}
    competency_map: dict[str, list[float]] = {}
    all_gaps: list[str] = []
    all_actions: list[str] = []

    cohort_by_id = {c.id: c for c in cohorts}

    for act in activities:
        cohort = cohort_by_id.get(act.cohort_id)
        subs = session.exec(
            select(Submission).where(Submission.activity_id == act.id).order_by(Submission.id.desc())
        ).all()
        latest_eval: Evaluation | None = None
        if subs:
            latest_eval = session.exec(
                select(Evaluation)
                .where(Evaluation.submission_id == subs[0].id)
                .order_by(Evaluation.id.desc())
            ).first()

        score: float | None = None
        status_str = "sin_evaluar"
        if latest_eval:
            status_str = latest_eval.status.value
            score = (
                latest_eval.final_score_approved
                if latest_eval.final_score_approved is not None
                else latest_eval.calculated_score_ai
            )
            if cohort:
                cohort_scores[cohort.code].append(score)

            crit_evals = session.exec(
                select(CriterionEvaluation).where(CriterionEvaluation.evaluation_id == latest_eval.id)
            ).all()
            crit_defs = {
                c.id: c
                for c in session.exec(
                    select(RubricCriterion).where(
                        RubricCriterion.rubric_version_id == latest_eval.rubric_version_id
                    )
                ).all()
            }
            for ce in crit_evals:
                cdef = crit_defs.get(ce.rubric_criterion_id)
                if not cdef:
                    continue
                eff = (
                    ce.teacher_criterion_score
                    if ce.teacher_criterion_score is not None
                    else ce.ai_criterion_score
                )
                competency_map.setdefault(cdef.competency_name, []).append(eff)

            rec = json.loads(latest_eval.recommendations_json)
            all_gaps.extend(rec.get("debilidades", []))
            all_actions.extend(rec.get("mejoras_tecnicas", []))
            all_actions.extend(rec.get("mejoras_conceptuales", []))
            all_actions.extend(rec.get("mejoras_metodologicas", []))

        activity_summaries.append(
            {
                "activity_id": act.id,
                "slug": act.slug,
                "title": act.title,
                "cohort_code": cohort.code if cohort else "",
                "cohort_name": cohort.name if cohort else "",
                "evaluation_id": latest_eval.id if latest_eval else None,
                "status": status_str,
                "score": score,
                "objective_met": latest_eval.objective_met.value if latest_eval else None,
            }
        )

    evaluated_scores = [a["score"] for a in activity_summaries if a["score"] is not None]
    global_avg = round(sum(evaluated_scores) / len(evaluated_scores), 2) if evaluated_scores else None

    cohort_evolution = []
    for c in cohorts:
        vals = cohort_scores.get(c.code, [])
        cohort_evolution.append(
            {
                "cohort_code": c.code,
                "cohort_name": c.name,
                "activities_evaluated": len(vals),
                "average_score": round(sum(vals) / len(vals), 2) if vals else None,
            }
        )

    competencies = []
    for name, vals in competency_map.items():
        avg = round(sum(vals) / len(vals), 2)
        level = "Avanzado" if avg >= 4.2 else ("Intermedio" if avg >= 3.4 else "Por profundizar")
        competencies.append({"competency": name, "average_score": avg, "mastery_level": level})

    unique_gaps = list(dict.fromkeys(all_gaps))[:8]
    unique_plan = list(dict.fromkeys(all_actions))[:8]

    return {
        "total_activities": len(activities),
        "evaluated_activities": len(evaluated_scores),
        "global_average": global_avg,
        "cohort_evolution": cohort_evolution,
        "activities": activity_summaries,
        "competencies": competencies,
        "identified_gaps": unique_gaps,
        "strengthening_plan": unique_plan,
    }

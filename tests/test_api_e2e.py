"""Pruebas end-to-end de API: portafolio real, RBAC, evaluación 3D, HITL, informes y mapa mental."""

from fastapi.testclient import TestClient

from tests.conftest import auth_header


def test_public_overview_and_health(client: TestClient):
    h = client.get("/api/v1/health")
    assert h.status_code == 200
    assert h.json()["status"] == "ok"

    ov = client.get("/api/v1/public/overview")
    assert ov.status_code == 200
    body = ov.json()
    names = [m["name"] for m in body["team"]]
    assert "Juan José Muñoz Naranjo" in names
    assert "Christopher Villa Noreña" in names


def test_portfolio_seed_has_6_activities_and_rbac_enforced(client: TestClient, demo_passwords):
    student_hdr = auth_header(client, "estudiante@umanizales.edu.co", demo_passwords["student"])
    acts = client.get("/api/v1/portfolio/activities", headers=student_hdr)
    assert acts.status_code == 200
    data = acts.json()
    assert len(data) == 6
    assert sum(1 for a in data if a["cohort_code"] == "C1") == 4
    assert sum(1 for a in data if a["cohort_code"] == "C2") == 2

    # Estudiante NO puede crear/editar rúbricas ni cambiar configuración admin
    bad_rubric = client.post(
        "/api/v1/rubrics",
        headers=student_hdr,
        json={"activity_id": data[0]["id"], "name": "Test", "criteria": []},
    )
    assert bad_rubric.status_code == 403

    bad_admin = client.put(
        "/api/v1/admin/ai-config",
        headers=student_hdr,
        json={"active_provider": "deterministic", "active_model": "evidence-auditor-v1"},
    )
    assert bad_admin.status_code == 403


def test_full_evaluation_3d_hitl_reports_and_mindmap(client: TestClient, demo_passwords):
    student_hdr = auth_header(client, "estudiante@umanizales.edu.co", demo_passwords["student"])
    teacher_hdr = auth_header(client, "docente@umanizales.edu.co", demo_passwords["teacher"])

    acts = client.get("/api/v1/portfolio/activities", headers=student_hdr).json()
    lab6 = next(a for a in acts if a["slug"] == "lab6-harness-organizador")
    sub_id = lab6["latest_submission_id"]
    assert sub_id is not None

    # Ejecutar evaluación en modo deterministic (sin depender de red externa en tests)
    ev_resp = client.post(
        f"/api/v1/evaluations/submissions/{sub_id}/run",
        headers=student_hdr,
        json={"provider_override": "deterministic"},
    )
    assert ev_resp.status_code == 201, ev_resp.text
    report = ev_resp.json()
    assert report["status"] == "draft_ai"
    assert 0.0 <= report["dimension_cuantificacion"]["effective_final_score"] <= 5.0
    assert report["verificacion_tecnica_sandbox"]["executed"] is True
    assert report["verificacion_tecnica_sandbox"]["syntax_valid"] is True

    eval_id = report["evaluation_id"]

    # Estudiante no puede aprobar evaluación HITL
    forbidden = client.post(
        f"/api/v1/evaluations/{eval_id}/review",
        headers=student_hdr,
        json={"decision": "approved", "comments": "Autoaprobación ilegal"},
    )
    assert forbidden.status_code == 403

    # Docente ajusta un criterio y aprueba (recalculando nota en backend)
    first_crit_id = report["dimension_cuantificacion"]["criteria"][0]["criterion_evaluation_id"]
    review_resp = client.post(
        f"/api/v1/evaluations/{eval_id}/review",
        headers=teacher_hdr,
        json={
            "decision": "adjusted",
            "comments": "Excelente informe y pruebas unitarias.",
            "adjustments": [
                {
                    "criterion_evaluation_id": first_crit_id,
                    "teacher_criterion_score": 5.0,
                    "justification_note": "Objetivo cumplido al 100 %.",
                }
            ],
        },
    )
    assert review_resp.status_code == 200, review_resp.text
    approved = review_resp.json()
    assert approved["status"] == "approved"
    assert approved["dimension_cuantificacion"]["final_score_approved"] is not None

    # Exportar Markdown
    md_resp = client.get(f"/api/v1/evaluations/{eval_id}/markdown", headers=student_hdr)
    assert md_resp.status_code == 200
    assert "VERIFICACIÓN" in md_resp.text

    # Informe integral
    int_resp = client.get("/api/v1/reports/integrated", headers=student_hdr)
    assert int_resp.status_code == 200
    assert int_resp.json()["evaluated_activities"] == 1

    # Mapa mental interactivo extendido (29 nodos: núcleo, 4 macro-áreas, 8 ejes, 16 subtemas)
    mm_resp = client.get("/api/v1/mindmap", headers=student_hdr)
    assert mm_resp.status_code == 200
    mm = mm_resp.json()
    assert len(mm["nodes"]) >= 28
    assert len(mm["edges"]) >= 30


def test_open_demo_mode_vs_strict_auth(client: TestClient, monkeypatch):
    # En modo demo abierto (por defecto), se puede consultar sin token
    open_resp = client.get("/api/v1/portfolio/activities")
    assert open_resp.status_code == 200
    assert len(open_resp.json()) == 6

    # Con PUBLIC_DEMO_MODE=false, el endpoint exige token JWT (401)
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "public_demo_mode", False)
    strict_resp = client.get("/api/v1/portfolio/activities")
    assert strict_resp.status_code == 401


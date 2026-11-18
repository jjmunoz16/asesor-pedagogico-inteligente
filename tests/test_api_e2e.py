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

    # Exportar Markdown y PDF real individual
    md_resp = client.get(f"/api/v1/evaluations/{eval_id}/markdown", headers=student_hdr)
    assert md_resp.status_code == 200
    assert "VERIFICACIÓN" in md_resp.text

    pdf_resp = client.get(f"/api/v1/evaluations/{eval_id}/pdf", headers=student_hdr)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"].startswith("application/pdf")
    assert pdf_resp.content.startswith(b"%PDF-1.4")

    # Informe integral + exportaciones .md y .pdf reales
    int_resp = client.get("/api/v1/reports/integrated", headers=student_hdr)
    assert int_resp.status_code == 200
    assert int_resp.json()["evaluated_activities"] == 1

    int_md = client.get("/api/v1/reports/integrated/markdown", headers=student_hdr)
    assert int_md.status_code == 200
    assert "Informe Integral" in int_md.text

    int_pdf = client.get("/api/v1/reports/integrated/pdf", headers=student_hdr)
    assert int_pdf.status_code == 200
    assert int_pdf.content.startswith(b"%PDF-1.4")

    # Mapa mental interactivo extendido
    mm_resp = client.get("/api/v1/mindmap", headers=student_hdr)
    assert mm_resp.status_code == 200
    mm = mm_resp.json()
    assert len(mm["nodes"]) >= 28
    assert len(mm["edges"]) >= 30


def test_security_hardening_auth_bola_uploads_and_rate_limit(
    client: TestClient, demo_passwords, monkeypatch
):
    from app.core.config import get_settings

    # 1. Por defecto PUBLIC_DEMO_MODE=False: sin token exige 401 incluso enviando X-Demo-Role
    strict_resp = client.get(
        "/api/v1/portfolio/activities", headers={"X-Demo-Role": "admin"}
    )
    assert strict_resp.status_code == 401
    assert strict_resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert strict_resp.headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'self'" in (strict_resp.headers.get("Content-Security-Policy") or "")

    # 2. Registro con contraseña débil falla (422) y con contraseña fuerte crea rol STUDENT
    weak_reg = client.post(
        "/api/v1/auth/register",
        json={"email": "hacker@umanizales.edu.co", "full_name": "Hacker", "password": "password"},
    )
    assert weak_reg.status_code == 422

    reg1 = client.post(
        "/api/v1/auth/register",
        json={"email": "alumno1@umanizales.edu.co", "full_name": "Alumno Uno", "password": "ClaveSegura2026!"},
    )
    assert reg1.status_code == 201
    assert reg1.json()["user"]["role"] == "student"
    hdr1 = {"Authorization": f"Bearer {reg1.json()['access_token']}"}

    reg2 = client.post(
        "/api/v1/auth/register",
        json={"email": "alumno2@umanizales.edu.co", "full_name": "Alumno Dos", "password": "ClaveSegura2026!"},
    )
    assert reg2.status_code == 201
    hdr2 = {"Authorization": f"Bearer {reg2.json()['access_token']}"}

    # 3. Protección contra subida de ejecutables y SSRF en repo_url
    acts = client.get("/api/v1/portfolio/activities", headers=hdr1).json()
    act_id = acts[0]["id"]

    bad_ext = client.post(
        f"/api/v1/portfolio/activities/{act_id}/submissions",
        headers=hdr1,
        data={"student_group_name": "Alumno Uno"},
        files=[("files", ("payload.exe", b"MZ", "application/octet-stream"))],
    )
    assert bad_ext.status_code == 415

    bad_repo = client.post(
        f"/api/v1/portfolio/activities/{act_id}/submissions",
        headers=hdr1,
        data={"student_group_name": "Alumno Uno", "repo_url": "http://169.254.169.254/latest"},
    )
    assert bad_repo.status_code == 422

    # 4. Protección BOLA / IDOR: alumno2 no puede acceder ni evaluar la entrega privada de alumno1
    good_up = client.post(
        f"/api/v1/portfolio/activities/{act_id}/submissions",
        headers=hdr1,
        data={"student_group_name": "Alumno Uno", "repo_url": "https://github.com/umanizales/demo-lab"},
        files=[("files", ("notas.md", b"# Evidencia privada", "text/markdown"))],
    )
    assert good_up.status_code == 201
    private_sub_id = good_up.json()["submission_id"]

    idor_read = client.get(f"/api/v1/portfolio/submissions/{private_sub_id}", headers=hdr2)
    assert idor_read.status_code == 403

    idor_eval = client.post(
        f"/api/v1/evaluations/submissions/{private_sub_id}/run",
        headers=hdr2,
        json={"provider_override": "deterministic"},
    )
    assert idor_eval.status_code == 403

    # 5. Revocación de JWT al cerrar sesión (/logout)
    logout_resp = client.post("/api/v1/auth/logout", headers=hdr1)
    assert logout_resp.status_code == 200
    reused = client.get("/api/v1/auth/me", headers=hdr1)
    assert reused.status_code == 401

    # 6. Rate limiter contra fuerza bruta en /login
    for _ in range(8):
        client.post(
            "/api/v1/auth/login",
            json={"email": "alumno1@umanizales.edu.co", "password": "WrongPassword123"},
        )
    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "alumno1@umanizales.edu.co", "password": "WrongPassword123"},
    )
    assert blocked.status_code == 429

    # 7. Si PUBLIC_DEMO_MODE se activa explícitamente, permite lectura abierta
    monkeypatch.setattr(get_settings(), "public_demo_mode", True)
    open_resp = client.get("/api/v1/portfolio/activities")
    assert open_resp.status_code == 200



"""Pruebas de seguridad del sandbox de código y validación Pydantic de salidas IA."""

import pytest
from pydantic import ValidationError

from app.schemas.evaluation import AIEvaluationPayload
from app.services.sandbox_service import run_sandbox_checks


def test_sandbox_static_detects_risky_calls_and_syntax_errors():
    files = [
        ("bad_syntax.py", "def broken(:\n    pass\n"),
        ("unsafe.py", "import os\nos.system('whoami')\neval('1+1')\n"),
        ("valid.json", '{"ok": true}'),
    ]
    res = run_sandbox_checks(files, mode="static_only")
    assert res["syntax_valid"] is False
    assert any("Error de sintaxis" in f for f in res["static_findings"])
    assert any("Importación sensible" in f for f in res["static_findings"])
    assert any("eval()" in f for f in res["static_findings"])


def test_sandbox_isolated_subprocess_runs_unittest_without_secrets(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "super-secret-value-must-not-leak")
    test_code = (
        "import os, unittest\n"
        "class SampleTest(unittest.TestCase):\n"
        "    def test_no_secret_env(self):\n"
        "        self.assertIsNone(os.environ.get('GEMINI_API_KEY'))\n"
    )
    res = run_sandbox_checks(
        [("test_sample.py", test_code)],
        mode="isolated_subprocess",
        timeout_seconds=5,
    )
    assert res["syntax_valid"] is True
    assert res["unit_tests_passed"] == 1
    assert res["unit_tests_total"] == 1


def test_ai_payload_rejects_out_of_range_criterion_score():
    with pytest.raises(ValidationError):
        AIEvaluationPayload.model_validate(
            {
                "verificacion": {
                    "objetivo_cumplido": "cumplido",
                    "resumen_verificacion": "Todo bien",
                    "evidencias_citadas": [],
                    "faltantes_detectados": [],
                },
                "cuantificacion_por_criterio": [
                    {
                        "criterion_id": "CRIT-1",
                        "nivel_desempeno": "Sobresaliente",
                        "puntaje_criterio": 5.8,
                        "justificacion": "Excede rango",
                        "evidencias": ["a.pdf"],
                    }
                ],
                "recomendaciones": {
                    "fortalezas": [],
                    "debilidades": [],
                    "mejoras_tecnicas": [],
                    "mejoras_conceptuales": [],
                    "mejoras_metodologicas": [],
                },
            }
        )

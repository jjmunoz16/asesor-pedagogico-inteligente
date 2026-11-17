---
name: backend-fastapi
description: >-
  Convenciones y reglas para el desarrollo del backend en Python 3.12 + FastAPI + SQLModel + Pydantic v2 del proyecto Asesor Pedagógico Inteligente.
---

# Backend FastAPI — Asesor Pedagógico Inteligente

1. **Cálculo determinista:** El puntaje final (0.00 a 5.00) SIEMPRE se calcula en `app/services/scoring_service.py` usando las ponderaciones de la rúbrica (`sum == 100 %`). Nunca delegar el cálculo numérico final al LLM.
2. **Validación de rúbricas:** Toda nueva versión de rúbrica debe validar que la suma de `weight_percent` sea exactamente `100.00`. Conservar versiones históricas sin sobrescribir evaluaciones pasadas.
3. **Sandbox obligatorio:** Nunca ejecutar código de estudiantes en el proceso principal de FastAPI. Delegar siempre a `app/services/sandbox_service.py` (`static_only` o `isolated_subprocess` sin secretos ni red).
4. **Seguridad:** Secretos únicamente vía `os.environ` / `.env` (nunca en código ni logs). Contraseñas con hash seguro y JWT con RBAC (`student`, `teacher`, `admin`).
5. **Verificación:** Ejecutar `pytest` en `tests/` después de cada cambio relevante.

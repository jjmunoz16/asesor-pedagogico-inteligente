---
name: qa-security
description: >-
  Criterios de pruebas automatizadas, auditoría de seguridad y verificación de conformidad para Asesor Pedagógico Inteligente.
---

# Calidad, Pruebas y Seguridad — Asesor Pedagógico Inteligente

1. **Cobertura mínima obligatoria en `tests/`:**
   - Validación de rúbricas (rechaza suma ≠ 100 %, acepta suma == 100 %).
   - Cálculo determinista de notas (`0.00` a `5.00`) e inmutabilidad de versiones.
   - Validación Pydantic de salidas IA (rechaza criterios inventados o puntajes fuera de rango).
   - Seguridad del sandbox (bloqueo de `eval`/`exec`/`os.system` en modo estático, timeout y ausencia de secretos en subproceso aislado).
   - RBAC (estudiante no puede aprobar evaluaciones HITL ni acceder a config admin).
2. **Privacidad:** Confirmar que `.gitignore` excluye `source-material/`, `.env` y bases de datos locales antes de cualquier commit.

# Arquitectura del Sistema y Modelo de Datos — Asesor Pedagógico Inteligente

**Fase:** Fase 4 — Diseño de arquitectura y modelo de datos  
**Fecha:** 2026-11-16  
**Estado:** Propuesta técnica para aprobación antes de programar (`AGENTS.md` §5 y §10)

---

## 1. Principio Arquitectónico Central

Siguiendo los hallazgos del propio curso (`Lab_3 - VibeCode` y `AGENTS.md`), la arquitectura adopta el patrón **"Modelo intercambiable, harness permanente"**:
- El proveedor/modelo de IA (Gemini Free Tier, Groq Free Tier, Ollama local) es un **adaptador reemplazable** detrás de una interfaz común.
- La confiabilidad reside en el **Harness permanente del Backend**: extracción determinista de evidencias, verificación técnica en sandbox, validación estricta con **Pydantic / JSON Schema**, cálculo matemático determinista de la nota (0,0–5,0), persistencia trazable y flujo obligatorio de aprobación docente (*Human-in-the-Loop*).

---

## 2. Arquitectura Lógica por Capas

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         CAPA DE PRESENTACIÓN (SPA)                      │
│  React + TypeScript + Vite + Tailwind + @xyflow/react (Mapa Mental)     │
│  • Login / Roles  • Portafolio (Cohortes 1 y 2)  • Editor de Rúbricas   │
│  • Informe Individual (3 Dimensiones)  • Panel Docente (HITL)           │
│  • Informe Integral  • Mapa Mental Interactivo  • Equipo y Abstract     │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTPS / REST JSON (JWT Bearer)
┌───────────────────────────────────▼─────────────────────────────────────┐
│                        CAPA API & SEGURIDAD (FastAPI)                   │
│  • Auth RBAC (Estudiante / Docente / Admin)  • Rate Limit & CORS        │
│  • Validación Pydantic de entrada/salida     • Manejo de errores        │
└──────┬────────────────────┬───────────────────────┬─────────────────────┘
       │                    │                       │
┌──────▼──────────┐  ┌──────▼────────────────┐  ┌───▼─────────────────────┐
│ SERVICIOS CORE  │  │  HARNESS DE EVALUACIÓN │  │ SANDBOX VERIFICACIÓN    │
│ • Portafolio    │  │ 1. Extractores reales │  │ • AST Python / Sintaxis │
│ • Rúbricas      │  │    (PDF, DOCX, XLSX,  │  │ • Análisis estático     │
│   (Valida 100%) │  │     MD, HTML, PY, IMG)│  │ • Runner aislado sin   │
│ • ScoringService│  │ 2. Prompt + Context   │  │   red y con timeout     │
│   (Nota 0.0-5.0 │  │    Builder (citas)    │  │   (según entorno)       │
│   determinista) │  │ 3. Model Router       │  └─────────────────────────┘
│ • Informe Global│  │    (Cloud Free/Local) │
│ • Mapa Mental   │  │ 4. Validador Pydantic │
└──────┬──────────┘  └──────┬────────────────┘
       │                    │
┌──────▼────────────────────▼─────────────────────────────────────────────┐
│                   CAPA DE PERSISTENCIA Y TRAZABILIDAD                   │
│  • PostgreSQL (Neon/Supabase Free Tier en prod; SQLite en dev/tests)    │
│  • Almacenamiento de archivos (Supabase Storage / Volumen + SHA-256)    │
│  • Tablas de auditoría: versión rúbrica, modelo usado, diffs HITL       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Modelo de Datos Relacional

### Entidades principales y relaciones

1. **`users`**
   - `id` (UUID/PK), `email` (unique), `password_hash`, `full_name`, `role` (`student` | `teacher` | `admin`), `is_active`, `created_at`.
2. **`cohorts`** (Cortes académicos)
   - `id` (PK), `code` (`C1`, `C2`), `name` (`Cohorte 1 — Primer Corte`, `Cohorte 2 — Segundo Corte`), `order_index`.
3. **`activities`** (Las 6 actividades y futuras)
   - `id` (PK), `cohort_id` (FK → `cohorts`), `slug`, `title`, `activity_type` (`lab` | `exam` | `colloquium`), `official_objective` (text, nullable si no consta), `description`, `active_rubric_version_id` (FK nullable).
4. **`rubrics`** y **`rubric_versions`**
   - `rubrics`: `id` (PK), `activity_id` (FK), `name`, `created_by` (FK → `users`).
   - `rubric_versions`: `id` (PK), `rubric_id` (FK), `version_number` (int), `is_valid` (bool, true solo si suma de pesos == 100.00), `created_at`.
5. **`rubric_criteria`**
   - `id` (PK), `rubric_version_id` (FK), `competency_name`, `criterion_name`, `description`, `weight_percent` (Decimal 0–100), `performance_levels_json` (ej. Escala `0.0–5.0` o niveles `Insuficiente / Básico / Satisfactorio / Sobresaliente` con puntaje asociado).
6. **`submissions`** (Entregas del portafolio)
   - `id` (PK), `activity_id` (FK), `student_group_name`, `owner_user_id` (FK → `users`), `repo_url` (nullable), `notes`, `submitted_at`.
7. **`evidence_files`**
   - `id` (PK), `submission_id` (FK), `filename`, `relative_path`, `mime_type`, `file_category` (`report_pdf` | `report_docx` | `source_code` | `data_table` | `image_diagram` | `video` | `archive`), `sha256_hash`, `storage_uri`, `extracted_text_summary` (text), `extraction_status` (`extracted` | `partial_metadata_only` | `unsupported`).
8. **`code_check_results`**
   - `id` (PK), `submission_id` (FK), `sandbox_mode` (`static_only` | `isolated_subprocess`), `syntax_valid` (bool), `files_checked_json`, `static_findings_json`, `unit_tests_passed` (int nullable), `unit_tests_total` (int nullable), `execution_time_ms`, `executed_at`.
9. **`evaluations`** (Evaluaciones trazables)
   - `id` (PK), `submission_id` (FK), `rubric_version_id` (FK), `status` (`draft_ai` | `under_review` | `approved` | `rejected`), `ai_provider`, `ai_model`, `prompt_version`, `objective_met` (`cumplido` | `parcial` | `no_cumplido` | `no_verificable`), `verification_summary` (text), `recommendations_json` (técnicas, conceptuales, metodológicas), `strengths_json`, `weaknesses_json`, `calculated_score_ai` (Decimal 0.00–5.00, **calculada por backend**), `final_score_approved` (Decimal 0.00–5.00 nullable), `raw_validated_payload_json`, `created_at`.
10. **`criterion_evaluations`**
    - `id` (PK), `evaluation_id` (FK), `rubric_criterion_id` (FK), `ai_level_label`, `ai_criterion_score` (0.0–5.0), `teacher_criterion_score` (nullable), `cited_evidences_json` (`[{file, section_or_page, quote}]`), `justification` (text).
11. **`teacher_reviews`** (Trazabilidad HITL)
    - `id` (PK), `evaluation_id` (FK), `teacher_id` (FK → `users`), `decision` (`approved` | `adjusted`), `comments`, `score_diff_json`, `reviewed_at`.
12. **`topic_nodes`** y **`topic_edges`** (Base del Mapa Mental Interactivo)
    - `topic_nodes`: `id`, `portfolio_scope`, `label`, `category`, `mastery_level` (`inicial` | `intermedio` | `avanzado` | `por_profundizar`), `mastery_score` (0.0–5.0), `related_activity_ids_json`, `evidences_json`, `gaps_to_strengthen_json`.
    - `topic_edges`: `id`, `source_node_id`, `target_node_id`, `relation_label`.
13. **`audit_logs`**
    - `id`, `actor_user_id`, `action`, `entity_type`, `entity_id`, `metadata_json`, `created_at`.

---

## 4. Cálculo Determinista de la Calificación (Backend)

El modelo de IA **nunca** calcula ni decide la nota final en texto libre. El flujo matemático en `ScoringService` es:
1. Cada criterio $i$ de la rúbrica tiene ponderación $w_i \in (0, 100]$ tal que $\sum_{i=1}^{n} w_i = 100$.
2. El modelo de IA asigna por criterio un nivel de desempeño discreto (mapeado a un puntaje $s_i \in [0.0, 5.0]$ definido en la rúbrica) y su evidencia citada.
3. El backend calcula estrictamente:
   $$\text{Nota} = \text{round}\left(\sum_{i=1}^{n} s_i \cdot \frac{w_i}{100},\ 2\right)$$
   garantizando reproducibilidad exacta y acotamiento en $[0.00, 5.00]$.

---

## 5. Contrato Pydantic / JSON Schema de Salida de IA (Evaluación)

> **Nota (actualizada 2026-11-16):** este es el contrato **lógico** que valida el backend con Pydantic. Al modelo se le enviará una versión **plana y sin restricciones numéricas** (`minimum`/`maximum`), porque la API de Gemini puede rechazar esquemas complejos (ver `ADR-004`). Después de recibir la respuesta, el backend verifica: rango 0,0–5,0 por criterio, que cada `criterion_id` exista en la versión de rúbrica usada y que cada archivo citado pertenezca de verdad a la entrega. Si alguna comprobación falla, la evaluación no se guarda como válida.

```json
{
  "type": "object",
  "required": ["verificacion", "cuantificacion_por_criterio", "recomendaciones"],
  "properties": {
    "verificacion": {
      "type": "object",
      "required": ["objetivo_cumplido", "resumen_verificacion", "evidencias_citadas"],
      "properties": {
        "objetivo_cumplido": { "enum": ["cumplido", "parcial", "no_cumplido", "no_verificable"] },
        "resumen_verificacion": { "type": "string" },
        "evidencias_citadas": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["archivo", "ubicacion", "fragmento"],
            "properties": {
              "archivo": { "type": "string" },
              "ubicacion": { "type": "string" },
              "fragmento": { "type": "string" }
            }
          }
        },
        "faltantes_detectados": { "type": "array", "items": { "type": "string" } }
      }
    },
    "cuantificacion_por_criterio": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["criterion_id", "nivel_desempeno", "puntaje_criterio", "justificacion", "evidencias"],
        "properties": {
          "criterion_id": { "type": "string" },
          "nivel_desempeno": { "type": "string" },
          "puntaje_criterio": { "type": "number", "minimum": 0.0, "maximum": 5.0 },
          "justificacion": { "type": "string" },
          "evidencias": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "recomendaciones": {
      "type": "object",
      "required": ["fortalezas", "debilidades", "mejoras_tecnicas", "mejoras_conceptuales", "mejoras_metodologicas"],
      "properties": {
        "fortalezas": { "type": "array", "items": { "type": "string" } },
        "debilidades": { "type": "array", "items": { "type": "string" } },
        "mejoras_tecnicas": { "type": "array", "items": { "type": "string" } },
        "mejoras_conceptuales": { "type": "array", "items": { "type": "string" } },
        "mejoras_metodologicas": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## 6. Estructura Prevista de Carpetas del Proyecto (Sin implementar aún)

- `backend/app/`:
  - `core/` (configuración `.env`, seguridad JWT, RBAC)
  - `db/` (modelos SQLAlchemy/SQLModel, migraciones, seed del portafolio real)
  - `schemas/` (contratos Pydantic estrictos)
  - `services/` (`rubric_service.py`, `scoring_service.py`, `extractor_service.py`, `sandbox_service.py`, `evaluation_service.py`, `report_service.py`, `mindmap_service.py`)
  - `ai/` (`base.py`, `gemini_provider.py`, `groq_provider.py`, `ollama_provider.py`, `router.py`, `prompts/`)
  - `api/` (routers FastAPI v1)
- `frontend/src/`:
  - `api/`, `auth/`, `components/`, `pages/` (Portafolio, Rúbricas, Evaluación 3D, Revisión Docente, Informe Integral, Mapa Mental Interactivo, Equipo y Abstract).
- `tests/`: pruebas unitarias, de integración, validación de pesos 100 %, cálculo determinista y seguridad del sandbox.

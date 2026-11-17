# Asesor Pedagógico Inteligente

**Proyecto Final — Profundización I: Inteligencia Artificial**  
Ingeniería de Sistemas y Telecomunicaciones — Universidad de Manizales  
**Equipo desarrollador:** Juan José Muñoz Naranjo y Christopher Villa Noreña  
**Estado actual:** **Implementado, verificado (`10/10` pruebas pytest, compilación TypeScript/Vite limpia) y desplegado en Render Free Tier + PostgreSQL Neon.**

---

## 1. Descripción del proyecto

**Asesor Pedagógico Inteligente** es una plataforma web *full-stack* diseñada para analizar evidencias académicas reales de las **Cohortes 1 y 2** (6 actividades prácticas), evaluar el cumplimiento de objetivos mediante un método estructurado en **3 dimensiones**, verificar código fuente en sandbox aislado, habilitar la revisión y aprobación docente (*Human-in-the-Loop*) y consolidar los resultados en un informe integrado y un mapa mental interactivo de competencias en IA.

---

## 2. Método de evaluación obligatorio (3 Dimensiones)

Toda evaluación ejecutada en la plataforma se estructura bajo un contrato Pydantic/JSON Schema estricto:

| Dimensión | Qué hace la plataforma | Regla de confiabilidad |
|---|---|---|
| **1. Verificación** | Contrasta los objetivos de cada actividad contra citas concretas extraídas de PDFs, informes Markdown/Word, código fuente y resultados de sandbox. | Sin citas o evidencia real inventada. |
| **2. Cuantificación (`0,0 – 5,0`)** | Valora cada criterio y competencia según rúbricas versionadas cuya suma de ponderaciones es exactamente **100 %**. | **El LLM nunca calcula la nota final:** el cálculo ponderado se ejecuta determinísticamente en el backend (`scoring_service.py`). |
| **3. Recomendación** | Identifica fortalezas, debilidades, brechas y recomendaciones técnicas, conceptuales y metodológicas accionables. | Separado de los hechos verificables y sujeto a aprobación humana. |

---

## 3. Funcionalidades implementadas

1. **Presentación del proyecto y equipo (`/`, `GET /api/v1/public/overview`):** abstract, arquitectura, enlace al repositorio y perfiles con fotografía real y roles equivalentes del equipo.
2. **Portafolio académico por cohortes (`/portafolio`):** 6 actividades reales precargadas (**Cohorte 1:** Lab 1, Lab 2, Lab 3, Parcial 1; **Cohorte 2:** Lab 5/Coloquio y Lab 6), cálculo de hashes `SHA-256`, extracción textual de evidencias (`.pdf`, `.py`, `.ipynb`, `.md`, `.zip`) y carga de nuevas entregas (archivos/ZIP o URL de GitHub).
3. **Gestión de rúbricas versionadas al 100 % (`/rubricas`):** editor e historial de versiones por actividad con validación estricta (la suma de ponderaciones debe ser exactamente `100 %` antes de permitir evaluar). Parten de una plantilla editable propuesta (`25/25/30/20 %`) marcada como tal (`is_template_proposal=True`).
4. **Evaluación inteligente + Supervisión docente HITL (`/evaluacion/:id`, `/revision-docente`):** ejecución con IA activa o con **Auditor Determinista Offline**, trazabilidad completa (modelo, versión de rúbrica, hashes, salida de sandbox) y pantalla de revisión para que el docente ajuste criterios con justificación y apruebe la calificación definitiva.
5. **Informe integrado de aprendizaje (`/informe-integral`, `GET /api/v1/reports/integrated`):** consolidado entre Cohortes 1 y 2, nivel de dominio por competencia, brechas y plan personalizado de fortalecimiento, con exportación imprimible.
6. **Mapa mental interactivo de competencias (`/mapa-mental`, `GET /api/v1/mindmap`):** grafo jerárquico horizontal sin solapamiento (**33 nodos y 36 aristas**) implementado con `@xyflow/react`, filtros por cohorte/actividad/nivel de dominio y exportación en `.svg`, `.png` y `.json`.
7. **Administración de modelos de IA (`/admin/modelos`):** router intercambiable (*modelo intercambiable, harness permanente*) con soporte para **Gemini Free Tier**, **Groq Free Tier**, conectores locales **Ollama** / **LM Studio** y **Auditor Determinista Offline**.

---

## 4. Arquitectura y Stack Tecnológico (100 % Gratuito)

| Capa | Tecnología | Propósito |
|---|---|---|
| **Backend & API** | Python 3.12 + FastAPI + Pydantic v2 | API REST `/api/v1/*`, validación estricta, cálculo determinista de notas `0,0–5,0` y servidor estático del SPA en producción. |
| **Frontend & Mapa Mental** | React 19 + TypeScript + Vite 6 + Tailwind CSS v4 + `@xyflow/react` | Interfaz por roles, split-screen de revisión docente HITL y grafo interactivo exportable. |
| **Persistencia** | SQLModel + SQLAlchemy (`SQLite` local / `PostgreSQL` Neon Free Tier) | 14 tablas relacionales con trazabilidad de evidencias, rúbricas versionadas, auditoría (`AuditLog`) y configuración en caliente (`RuntimeAIConfig`). |
| **Sandbox y Verificación** | `SandboxService` dual (`static_only` en nube / `isolated_subprocess` local) | Análisis sintáctico AST sin ejecutar código en el host en contenedores cloud gratuitos, o ejecución aislada sin red (`socket` bloqueado) y timeout de `5 s` en entorno local. |
| **Modelos de IA** | `ModelRouter` (`gemini`, `groq`, `ollama`, `lmstudio`, `deterministic`) | Esquema JSON estructurado obligatorio y respaldo offline determinista sin dependencia de API keys. |
| **Despliegue** | Docker Todo-en-Uno (`Dockerfile` + `render.yaml`) en Render Free Tier | Una sola URL HTTPS pública sirviendo frontend compilado y API backend conectada a Neon PostgreSQL. |

---

## 5. Seguridad, privacidad y transparencia técnica

* **Protección de trabajos privados y credenciales:** la carpeta `source-material/`, archivos `.env`, entornos virtuales y bases `.db` locales están excluidos del repositorio público mediante `.gitignore`. No hay claves API hardcodeadas en el código.
* **Autenticación JWT + RBAC (`PUBLIC_DEMO_MODE`):** el backend implementa contraseñas con `bcrypt`, tokens `JWT` y control de acceso por roles (`student`, `teacher`, `admin`). Por defecto en `render.yaml` se habilita `PUBLIC_DEMO_MODE=true` para permitir la exploración inmediata durante la socialización sin barrera de login; al configurar `PUBLIC_DEMO_MODE=false` en las variables de entorno, la plataforma exige autenticación estricta en todas las rutas protegidas.
* **Alcance de extracción multimodal:** archivos multimedia o comprimidos binarios (`.mp4`, `.png`, `.jpeg`, binarios en `.zip`) se inventarían con su `SHA-256` y metadatos (`partial_metadata_only`); el análisis LLM actual procesa resúmenes textuales y código extraído, sin transcripción automática de audio ni OCR de imágenes.

---

## 6. Pruebas automatizadas y verificación

Ejecutadas tras los últimos cambios:

```powershell
# Backend (10 pruebas unitarias, sandbox, RBAC, scoring y E2E)
.\backend\.venv\Scripts\python.exe -m pytest tests -v
# Resultado verificado: 10 passed, 1 warning

# Frontend (compilación TypeScript + Vite)
cd frontend
npm.cmd run build
# Resultado verificado: tsc -b && vite build (exit code 0, 1631 modules transformed)
```

---

## 7. Estructura del repositorio y ejecución local

```text
├── ai-documentation/          # AI_USAGE_LOG.md (trazabilidad de uso de IA por fase)
├── backend/                   # API FastAPI, modelos SQLModel, servicios, router IA, sync_to_remote_db.py
├── docs/                      # Análisis académico, requisitos RF/RNF, arquitectura, ADRs, UX/UI y despliegue
├── frontend/                  # Aplicación React + TypeScript + Vite + Tailwind + @xyflow/react
├── tests/                     # Suite pytest (scoring, rúbricas, sandbox, Pydantic y API E2E)
├── AGENTS.md                  # Reglas obligatorias del proyecto y de evaluación en 3D
├── Dockerfile                 # Build multi-etapa Todo-en-Uno (Frontend + Backend)
└── render.yaml                # Blueprint de despliegue en Render Free Tier
```

### Ejecución rápida en local
1. **Backend:** desde `backend/`, ejecutar `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000` (el primer arranque crea `asesor_pedagogico.db` y ejecuta el seed idempotente).
2. **Frontend:** desde `frontend/`, ejecutar `npm run dev` y abrir `http://127.0.0.1:5173/`.
3. **Despliegue en Render + Neon:** consultar la guía detallada en [`docs/DESPLIEGUE_Y_OPERACION.md`](docs/DESPLIEGUE_Y_OPERACION.md).

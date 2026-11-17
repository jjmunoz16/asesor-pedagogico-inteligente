# Registro de Uso de Inteligencia Artificial (`AI_USAGE_LOG.md`)

Este archivo documenta de forma trazable qué agente o herramienta de IA realizó cada tarea del proyecto **Asesor Pedagógico Inteligente**, qué instrucciones recibió, qué archivos consultó o generó y qué resultados produjo.

---

## Convención de Registro

Cada entrada debe incluir:
- **ID y Fecha**
- **Fase del proyecto**
- **Agente / Herramienta / Modelo**
- **Instrucción resumida (Prompt / Misión)**
- **Fuentes y archivos consultados**
- **Entregables / Resultados producidos**
- **Limitaciones o hallazgos relevantes**
- **Estado de validación humana**

---

## Historial de Actividades

### [AI-LOG-001] 2026-11-15 — Misión 1: Preparación y Reconocimiento del Entorno
- **Fase:** Fase 1 — Preparación del entorno y organización documental.
- **Agente / Herramienta:** Agente Coordinador en Antigravity IDE (modelo: Gemini 4 Hydrogen Medium).
- **Instrucción recibida:** Ejecutar reconocimiento del workspace, leer `AGENTS.md`, `README.md` y el documento oficial en `docs/especificaciones/`, verificar capacidades reales de Antigravity IDE, revisar estructura de carpetas, proponer estrategia de agentes y crear documentación base (`DECISIONES_PENDIENTES.md`, `AI_USAGE_LOG.md`, `PLAN_DE_TRABAJO.md`) sin iniciar desarrollo ni modificar materiales originales.
- **Fuentes y archivos consultados:**
  - `AGENTS.md`
  - `README.md`
  - `docs/especificaciones/Proyecto_Final_IA_Asesor_Pedagogico_V3_Rubricas_Verificacion.docx`
  - Skills internas de Antigravity: `agy-customizations` (`SKILL.md`, `docs/rules.md`, `docs/skills.md`) y `antigravity-guide` (`SKILL.md`, `references/ide.md`, `references/app.md`).
  - Estructura de directorios de `docs/`, `source-material/`, `.agents/`, `ai-documentation/`, `backend/`, `frontend/`, `tests/`.
- **Entregables / Resultados producidos:**
  - `docs/DECISIONES_PENDIENTES.md`
  - `ai-documentation/AI_USAGE_LOG.md`
  - `docs/PLAN_DE_TRABAJO.md`
  - Informe final de Misión 1 con diagnóstico del entorno, capacidades verificadas/no verificadas, estrategia de agentes e inconsistencias detectadas.
- **Limitaciones o hallazgos relevantes:**
  - `python` no está accesible directamente en el `PATH` de la terminal sandbox; se extrajo el contenido del `.docx` oficial mediante PowerShell y `System.IO.Compression.ZipFile`.
  - El directorio `.agents/agents/` está vacío y no se encontró documentación que confirme autodescubrimiento de archivos de agentes en disco; la creación dinámica de subagentes está verificada vía `define_subagent` e `invoke_subagent`.
- **Validación humana:** Pendiente de revisión y aprobación por el responsable del proyecto.

### [AI-LOG-002] 2026-11-15 — Actualización de Decisiones e Inventario Inicial de `source-material/`
- **Fase:** Transición Fase 1 → Fase 2.
- **Agente / Herramienta:** Agente Coordinador en Antigravity IDE (modelo: Gemini 4 Hydrogen Medium).
- **Instrucción recibida:** Registrar aprobaciones del equipo sobre cohortes/cortes, alcance de rúbricas y evidencias, integrantes del equipo, y restricción de costo \$0 (gratuito) para la futura propuesta tecnológica.
- **Fuentes y archivos consultados:**
  - Respuesta del usuario (validación de `DP-01`, `DP-02`, `DP-04`, `DP-05` y directriz gratuita para `DP-06`–`DP-11`).
  - Inventario de archivos en `source-material/primer-corte/` y `source-material/segundo-corte/`.
- **Entregables / Resultados producidos:**
  - Actualización de `docs/DECISIONES_PENDIENTES.md`.
  - Listado completo de formatos reales existentes en las 6 actividades (`.pdf`, `.docx`, `.md`, `.xlsx`, `.py`, `.html`, `.json`, `.png`, `.jpeg`, `.mp4`, `.zip`).
- **Validación humana:** Pendiente iniciar Fase 2 (análisis académico detallado de cada una de las 6 actividades).

### [AI-LOG-003] 2026-11-16 — Fase 2: Análisis Académico de las 6 Actividades
- **Fase:** Fase 2 — Análisis académico de documentos y las 6 actividades.
- **Agente / Herramienta:** Agente de Análisis Académico / Coordinador en Antigravity IDE (modelo: Gemini 4 Hydrogen Medium).
- **Instrucción recibida:** Analizar en modo solo lectura los entregables reales de `source-material/primer-corte/` y `source-material/segundo-corte/` sin modificar originales ni inventar datos, identificando objetivos, evidencias, temáticas, competencias e inconsistencias.
- **Fuentes y archivos consultados:**
  - Lab 1: `MapaMentalAI.png`, `PrototipoManizalesResiliente.html` (hash), `VideoAI.mp4` (existencia).
  - Lab 2: `Solution Blueprint...pdf` (15 págs.), `BancodePrompts...xlsx`, `PrototipoManizalesResiliente.html`.
  - Lab 3: `INFORME_TÉCNICO_ANALÍTICO_IA.docx`.
  - Parcial: `index.html`, `cartografia_modelos/conclusion.md`, `modelos.xlsx`, `mapa_mental/mapa mental resumido.jpeg`, `modelos_locales/ollama_test.py`, `serie_temporal/app.py`, `model.py`.
  - Coloquio: `Observatorio de Proyectos de IA — Coloquio 2026-II (2).png`, `INFORME_TÉCNICO_ANALÍTICO_IA.docx` (comparación SHA-256).
  - Lab 6: `INFORME_LAB01.md`, `test_extension_rtf.py`, `auditoria/ejecucion_real.json`.
- **Entregables / Resultados producidos:**
  - `docs/analisis-documento/ANALISIS_ACTIVIDADES.md`
  - `docs/analisis-documento/MAPA_TEMATICAS_COMPETENCIAS.md`
- **Hallazgos clave:**
  - Se verificó duplicación exacta (mismo SHA-256) de `INFORME_TÉCNICO_ANALÍTICO_IA.docx` entre Lab 3 y Coloquio, y de `PrototipoManizalesResiliente.html` entre Lab 1 y Lab 2.
  - Se confirmó ausencia de archivos de rúbrica explícita dentro de `source-material/`.
- **Validación humana:** Pendiente revisión del equipo para avanzar a **Fase 3 (Requisitos)** y **Fase 4 (Arquitectura y propuesta de stack 100 % gratuito)**.

### [AI-LOG-004] 2026-11-16 — Fases 3 y 4: Requisitos, Trazabilidad, Arquitectura y Stack Gratuito
- **Fase:** Fase 3 (Requisitos) y Fase 4 (Arquitectura y Decisiones Técnicas).
- **Agente / Herramienta:** Agente de Requisitos / Arquitecto de Software en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Instrucción recibida:** Actualizar el análisis tras la corrección del archivo de Lab 3 (`Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf`) y completar las Fases 3 y 4 con una propuesta 100 % gratuita sin iniciar programación.
- **Fuentes y archivos consultados:**
  - `source-material/primer-corte/Lab_3 - VibeCode/Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf` (13 págs.).
  - `docs/especificaciones/Proyecto_Final_IA_Asesor_Pedagogico_V3_Rubricas_Verificacion.docx`.
  - `docs/analisis-documento/ANALISIS_ACTIVIDADES.md` y `MAPA_TEMATICAS_COMPETENCIAS.md`.
  - Verificación de runtimes locales en sandbox (`py`, `node`, `npm`, `git`, `docker` no presentes en `PATH` por defecto).
- **Entregables / Resultados producidos:**
  - Actualización de `docs/analisis-documento/ANALISIS_ACTIVIDADES.md` (Lab 3 corregido).
  - `docs/especificaciones/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md` (`RF-01`–`RF-11`, `RNF-01`–`RNF-08`, `HU-01`–`HU-10`).
  - `docs/especificaciones/MATRIZ_TRAZABILIDAD.md`.
  - `docs/arquitectura/ARQUITECTURA_SISTEMA.md` (capas, 13 tablas del modelo relacional, fórmula determinista de nota y JSON Schema de evaluación).
  - `docs/decisiones-tecnicas/ADR_STACK_GRATUITO.md` (`ADR-001` a `ADR-006`, 100 % gratuito).
  - Actualización de `docs/DECISIONES_PENDIENTES.md`.
- **Validación humana:** Pendiente aprobación formal de requisitos (`RF`/`RNF`) y arquitectura (`ADR-001`–`ADR-006`) para desbloquear Fase 5 (UX/UI) y Fase 6 (implementación).

### [AI-LOG-005] 2026-11-16 — Corrección de Exactitud en Fase 2/4 y Fase 5 (Diseño UX/UI)
- **Fase:** Corrección de exactitud documental + Fase 5 (Diseño UX/UI).
- **Agente / Herramienta:** Agente Coordinador / UX-UI en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Instrucción recibida:** Tras corrección de extracción real de PDFs (`Lab_2` y `Lab_3`), verificación de límites reales de free tiers (`DP-15`) y aprobación para continuar ("Dale pues"), completar el diseño UX/UI en `docs/diseno/`.
- **Fuentes y archivos consultados:**
  - `docs/especificaciones/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`
  - `docs/especificaciones/MATRIZ_TRAZABILIDAD.md`
  - `docs/arquitectura/ARQUITECTURA_SISTEMA.md`
  - `docs/analisis-documento/MAPA_TEMATICAS_COMPETENCIAS.md`
  - `docs/DECISIONES_PENDIENTES.md` (`DP-15`, `DP-16`, `DP-17`)
- **Entregables / Resultados producidos:**
  - `docs/diseno/DISENO_UX_UI.md` (navegación por roles, flujo E2E, wireframes de 8 vistas clave incluyendo Split-Screen HITL y Mapa Mental `@xyflow/react`, accesibilidad, `@media print` y §6 Plantilla base editable de rúbrica `DP-16`).
- **Validación humana:** Pendiente aprobación del diseño UX/UI y resolución de `DP-05` (roles/fotos), `DP-15` (privacidad Gemini Free), `DP-16` (plantilla base de rúbrica) y `DP-17` (entorno local Python/Node/Git) antes de iniciar Fase 6 (programación).

### [AI-LOG-006] 2026-11-16 — Fases 6, 7 y 8: Implementación Backend, Frontend, Harness IA y Pruebas
- **Fases:** Fase 6 (Backend y Frontend), Fase 7 (Integración IA y Sandbox) y Fase 8 (Pruebas y Auditoría).
- **Agente / Herramienta:** Agentes Backend, Frontend, IA Harness y QA en Antigravity IDE (modelo: Claude Opus 5.5 High / Gemini 4 Hydrogen High).
- **Instrucción recibida:** Tras aprobar diseño UX/UI (`DP-16`), Gemini Free Tier (`DP-15`) y entorno local (`DP-17`), instalar Python 3.12.10 y Node.js LTS 26.13.1, construir backend FastAPI + frontend React + suite de pruebas, y verificar build y tests.
- **Entregables / Resultados producidos:**
  - `.gitignore` y `.agents/skills/` (`backend-fastapi`, `frontend-react`, `ai-evaluation-harness`, `qa-security`).
  - `backend/`: API FastAPI, SQLModel (14 tablas incluyendo `RuntimeAIConfig`), seed automático de las 6 actividades reales de `source-material/`, `ScoringService` determinista (0,0–5,0), `SandboxService` dual (`static_only` + `isolated_subprocess`), `ModelRouter` (Gemini Free, Groq Free, Ollama, LM Studio, Auditor Determinista), revisión docente HITL, informes individuales/integral y grafo de mapa mental.
  - `frontend/`: React + TypeScript + Vite + Tailwind CSS v4 + `@xyflow/react` con las 8 vistas diseñadas en `DISENO_UX_UI.md`.
  - `tests/`: 9 pruebas automatizadas (`test_scoring_and_rubrics.py`, `test_sandbox_and_ai_validation.py`, `test_api_e2e.py`).
  - `docs/DESPLIEGUE_Y_OPERACION.md`: Guía local y de despliegue gratuito (Neon + Hugging Face Spaces + Vercel).
- **Verificación ejecutada:**
  - `pytest tests -v`: **9/9 pruebas aprobadas en 9.07s**.
  - `npm run build` (`tsc -b && vite build`): **compilación exitosa sin errores** (1631 módulos).
- **Validación humana:** Pendiente revisión del equipo y configuración de credenciales (`GEMINI_API_KEY`, Neon, HF Spaces, Vercel) para completar el despliegue público en la Fase 9.

### [AI-LOG-007] 2026-11-16 — Ajuste de Acceso Directo Sin Login (`PUBLIC_DEMO_MODE=true`)
- **Fase:** Ajustes post-Fase 8 (Experiencia de revisión abierta para socialización).
- **Agente / Herramienta:** Agentes Backend, Frontend y QA en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Instrucción recibida:** Eliminar la barrera obligatoria de inicio de sesión para que el docente pueda abrir la URL y explorar todo el contenido directamente, manteniendo implementado y documentado el módulo JWT/RBAC por si se solicita activarlo.
- **Entregables / Resultados producidos:**
  - `backend/app/core/config.py` y `security.py`: agregado `PUBLIC_DEMO_MODE=true` (default) con soporte `X-Demo-Role` y preservación estricta de JWT/RBAC cuando se envía Bearer token o cuando `PUBLIC_DEMO_MODE=false`.
  - `frontend/src/`: eliminada la redirección forzada a `/login`, agregado selector de vista por rol en cabecera y aviso informativo en `OverviewPage.tsx`.
  - `tests/test_api_e2e.py`: agregada prueba `test_open_demo_mode_vs_strict_auth`.
  - `docs/DECISIONES_PENDIENTES.md`: documentada la decisión `DP-18` frente a la Condición #5 del documento oficial.

### [AI-LOG-008] 2026-11-16 — Actualización de Objetivo de Lab 1 y Calibración de Evidencias
- **Fase:** Ajustes de calidad y trazabilidad académica.
- **Agente / Herramienta:** Agente Evaluador / Backend en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Instrucción recibida:** Incorporar el objetivo explícito de Lab 1 confirmado por el equipo (video con IA sobre historia de la IA, mapa mental y prototipo Manizales Resiliente) y calibrar `DeterministicOfflineAnalyzer` para no penalizar injustamente entregas multimedia o documentales sin errores sintácticos.
- **Entregables / Resultados producidos:**
  - `docs/analisis-documento/ANALISIS_ACTIVIDADES.md` y `backend/app/db/seed.py`: actualizado objetivo explícito de `lab1-historia-ia` y sincronización en `run_seed`.
  - `backend/app/ai/providers.py`: calibración basada en cobertura real de evidencias, verificación AST/pruebas y ausencia de fallos críticos.

### [AI-LOG-009] 2026-11-16 — Expansión del Mapa Mental Interactivo de Competencias (29 nodos)
- **Fase:** Mejora de visualización e interactividad (Funcionalidad Obligatoria #6).
- **Agente / Herramienta:** Agentes Backend y Frontend en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Instrucción recibida:** Ampliar la extensión y profundidad del mapa mental interactivo para reflejar todas las temáticas, subtemas, evidencias reales y brechas del curso.
- **Entregables / Resultados producidos:**
  - `backend/app/db/seed.py`: ampliado el grafo a **29 nodos jerárquicos** (1 núcleo, 4 macro-áreas, 8 ejes temáticos y 16 subtemas técnicos reales de las 6 actividades) y **32 aristas** (incluyendo relaciones transversales), con upsert idempotente.
  - `backend/app/services/mindmap_service.py` y `reports_admin.py`: agregado filtro por actividad (`?activity=`) y cálculo dinámico de dominio desde evaluaciones reales.
  - `frontend/src/pages/MindMapPage.tsx`: vista extensa/resumida conmutable, filtro por cohorte, actividad, nivel y búsqueda, exportación completa en `.svg`, `.png` y `.json`.
  - `tests/test_api_e2e.py`: validados `>= 28` nodos y `>= 30` aristas.

### [AI-LOG-010] 2026-11-16 — Organización Jerárquica del Mapa Mental (33 nodos) y Rediseño Integral UI/UX
- **Fase:** Mejora visual, layout sin solapamiento y ampliación de mapa mental.
- **Agente / Herramienta:** Agentes Backend y Frontend en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Instrucción recibida:** Eliminar solapamiento de nodos en el mapa mental, ampliar contenido faltante del curso y mejorar la interfaz visual general de la aplicación.
- **Entregables / Resultados producidos:**
  - `backend/app/services/mindmap_service.py`: algoritmo de árbol horizontal (`Izquierda → Derecha`) con cálculo determinista de coordenadas sin solapamiento incluso bajo filtros.
  - `backend/app/db/seed.py`: ampliado el grafo a **33 nodos** y **36 aristas** añadiendo aplicaciones sectoriales, CVDS iterativo, infraestructura Docker/Proxmox/Open-Meteo y gobernanza/riesgos.
  - `frontend/src/components/Layout.tsx` y páginas (`OverviewPage`, `PortfolioPage`, `EvaluationReportPage`, `IntegratedReportPage`, `MindMapPage`): rediseño con barra lateral oscura estructurada, tarjetas KPI, barras de progreso por criterio/cohorte/competencia y controles visuales del mapa mental (`Vista resumida/extensa`, `Mostrar/Ocultar cruces`).

### [AI-LOG-011] 2026-11-16 — Actualización de Despliegue Gratuito (`ADR-006`: HF Spaces → Render Free Tier)
- **Fase:** Fase 9 — Preparación de despliegue público gratuito.
- **Agente / Herramienta:** Agente Arquitecto / Despliegue en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Hallazgo:** Al intentar crear el Space Docker en Hugging Face, el usuario detectó que requiere plan de pago; se verificó mediante búsqueda web (2026-11-16) que Hugging Face restringió nuevos Spaces Docker/Gradio a planes PRO (\$9/mes) y Koyeb exige tarjeta de crédito, mientras **Render Free Tier** ofrece Web Services Docker gratuitos sin tarjeta.
- **Entregables / Resultados producidos:**
  - `render.yaml` (Blueprint Todo-en-Uno para Render Free Tier).
  - Actualización de `docs/decisiones-tecnicas/ADR_STACK_GRATUITO.md` (`ADR-006`) y `docs/DESPLIEGUE_Y_OPERACION.md`.

### [AI-LOG-012] 2026-11-16 — Fase 9: Publicación en GitHub Privado, Neon PostgreSQL y Render
- **Fase:** Fase 9 — Despliegue y documentación final.
- **Agente / Herramienta:** Agente de Despliegue en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Acciones ejecutadas:**
  - Instalación de MinGit 2.56.1 y GitHub CLI 2.104.0; creación y push del repositorio privado `jjmunoz16/asesor-pedagogico-inteligente` (rama `main`, excluyendo `source-material/`, `.env`, `.venv/`, `node_modules/` y `*.db`).
  - Sincronización directa hacia Neon PostgreSQL mediante `backend/sync_to_remote_db.py` (6 entregas reales, rúbricas, 6 evaluaciones base y mapa mental de 33 nodos).
  - Despliegue confirmado por el usuario en Render (Web Service Free Tier con `Dockerfile` Todo-en-Uno).
- **Estado:** Plataforma desplegada en línea y lista para socialización.

### [AI-LOG-013] 2026-11-16 — Fotografías Reales y Roles Equilibrados del Equipo
- **Fase:** Ajustes finales de presentación (Funcionalidad Obligatoria #7).
- **Agente / Herramienta:** Agentes Frontend, Backend y Despliegue en Antigravity IDE (modelo: Gemini 4 Hydrogen High).
- **Cambios aplicados:**
  - Incorporadas fotografías reales en `frontend/public/team/christopher.jpg` y `frontend/public/team/juan_jose.jpg`.
  - Actualizado `backend/app/api/reports_admin.py` y `frontend/src/pages/OverviewPage.tsx` con roles equivalentes de arquitectura, desarrollo full-stack, integración de IA, verificación y despliegue para **Juan José Muñoz Naranjo** y **Christopher Villa Noreña**.

# Decisiones Técnicas de Arquitectura — Stack 100 % Gratuito

**Fase:** Fase 4 — Decisiones técnicas (`DP-06` a `DP-11`)  
**Fecha:** 2026-11-16  
**Restricción rectora:** Cero costo operativo (herramientas Open Source + Free Tiers), cumplimiento estricto del documento del profesor y de `AGENTS.md`.

---

## ADR-001: Stack de Backend — Python 3.12 + FastAPI + Pydantic v2
- **Decisión propuesta:** Usar **Python 3.12** con **FastAPI** y **Pydantic v2**.
- **Justificación:**
  1. El documento del profesor cita explícitamente **Pydantic / JSON Schema** para validar salidas de IA (Condición #2).
  2. El portafolio real de `source-material/` incluye `.pdf`, `.docx`, `.xlsx`, `.py`, `.html`, `.json` e imágenes; Python ofrece librerías maduras y gratuitas (`pypdf`, `python-docx`, `openpyxl`, módulo estándar `ast` y `unittest`).
  3. Coherencia directa con los laboratorios previos del equipo (FastAPI en `Lab_2`, Python 3.12 en `Parcial` y `Lab 6`).
- **Alternativas descartadas:** Node.js/NestJS (requeriría librerías externas menos homogéneas para analizar AST de Python y documentos científicos `.docx`/`.xlsx`).
- **Riesgos / Mitigación:** Verificar instalación local de Python 3.12 en el equipo antes de Fase 6 (en el reconocimiento inicial `py` no apareció en el `PATH` del sandbox).

## ADR-002: Frontend y Mapa Mental Interactivo — React + TypeScript + Vite + `@xyflow/react`
- **Decisión propuesta:** **React + TypeScript + Vite** con **Tailwind CSS** y **`@xyflow/react`** (React Flow) para el mapa mental interactivo.
- **Justificación:**
  1. Compila a activos estáticos desplegables gratis con CDN en Vercel, Cloudflare Pages o Netlify.
  2. `@xyflow/react` (licencia MIT) soporta nativamente nodos personalizados, aristas etiquetadas, pan/zoom, minimapa, filtrado por cohorte/dominio y exportación a imagen/SVG, cubriendo íntegramente la Funcionalidad Obligatoria #6.
  3. Generación gratuita de informes descargables mediante vista de impresión PDF del navegador (`@media print`) + exportación Markdown/JSON.
- **Alternativas descartadas:** Streamlit/Gradio (limitado para autenticación RBAC profesional, UI split-screen docente y mapa mental interactivo avanzado).

## ADR-003: Persistencia y Almacenamiento — PostgreSQL (Neon/Supabase Free Tier) + SQLite en Local
- **Decisión propuesta:** **SQLModel / SQLAlchemy** con **SQLite** para desarrollo/tests locales y **PostgreSQL** gestionado en **Neon** o **Supabase (Free Tier \$0)** para producción.
- **Justificación:**
  1. Se requiere persistencia relacional ACID para usuarios, roles, versiones inmutables de rúbricas, cálculo de pesos = 100 %, evaluaciones y auditoría HITL (Condiciones #5 y #6).
  2. En PaaS gratuitos (como Render Free), el sistema de archivos local es efímero tras reinicios; usar PostgreSQL externo gratuito evita pérdida de datos.
  3. Archivos binarios: el portafolio real pesa **≈ 28 MB** (38 archivos sin `.venv`/`__pycache__`; el mayor es `VideoAI.mp4` con 13,7 MB). En producción se guardarán el texto extraído, los metadatos y el hash `SHA-256` en PostgreSQL. Los binarios originales irán a almacenamiento de objetos gratuito (Supabase Storage; **límite gratuito por confirmar en Fase 6**). `source-material/` se mantiene intacto y de solo lectura.
- **Límites de la capa gratuita (búsqueda web del 2026-11-16, reconfirmar en las páginas oficiales antes de desplegar):** Neon Free = 1 GB de Postgres por proyecto; Supabase Free = 500 MB de base de datos por proyecto. Ambos son suficientes para el volumen previsto.
- **Decisión de implementación:** se recomienda **Neon** como base de datos principal (más espacio gratuito).

## ADR-004: Modelos de IA — Arquitectura Híbrida Gratuita ("Modelo Intercambiable")
- **Decisión propuesta:** Implementar un `ModelRouter` con adaptadores gratuitos configurables vía variables de entorno:
  1. **Proveedor principal en la nube (gratuito):** **Google Gemini API (Free Tier)** con una clave de Google AI Studio. El nombre exacto del modelo se toma de una variable de entorno (`GEMINI_MODEL`), no se fija en el código. Según la búsqueda web del 2026-11-16, la capa gratuita incluye modelos de la familia **Gemini Flash / Flash-Lite**; los modelos insignia requieren facturación. Admite multimodalidad y *Structured Outputs* con JSON Schema.
  2. **Proveedor de respaldo en la nube (gratuito):** **Groq API (Free Tier)**, con el modelo también configurable (`GROQ_MODEL`). Los límites reportados para modelos grandes rondan 30 RPM, ~1.000 peticiones y ~100.000 tokens por día por organización.
  3. **Proveedor local gratuito (opcional):** **Ollama** (`http://localhost:11434`) y **LM Studio** (`http://localhost:1234`, API compatible con OpenAI), para uso privado sin red cuando la app corre en local. Coincide con el entorno que el equipo ya verificó en el Primer Parcial (`modelos.xlsx`).
- **Limitaciones documentadas:**
  - Las cuotas gratuitas en la nube varían y se aplican por proyecto u organización. Se mitigará con caché por hash `SHA-256`, extracción determinista previa (enviar texto, no binarios, cuando sea posible), una evaluación por actividad y reintentos con *backoff*.
  - **Privacidad (importante):** según la búsqueda del 2026-11-16, en la capa gratuita de Gemini **Google puede usar los prompts y las respuestas para mejorar sus productos**. Como se van a enviar trabajos académicos (`AGENTS.md` §8 y Condición #6), queda registrado como **`DP-15`** para que el equipo decida de forma explícita (ver `DECISIONES_PENDIENTES.md`).
  - **Esquemas complejos:** Gemini puede rechazar con error `400` los JSON Schema muy anidados o con muchas restricciones (`minimum`/`maximum`, enums largos). Por eso el esquema que se envía al modelo será **plano y sin límites numéricos**; los rangos (0,0–5,0), la existencia de los criterios y la validez de las citas se comprueban **después**, en el backend con Pydantic.
  - El despliegue público no incluirá Ollama en el servidor remoto (requiere RAM/GPU), así que en la nube se usará Gemini o Groq.

## ADR-005: Sandbox de Verificación Objetiva de Código — Estrategia Dual Segura y Gratuita
- **Decisión propuesta:** Módulo `SandboxService` con dos modos configurables (`SANDBOX_MODE`):
  - **Modo `static_only` (seguro por defecto en PaaS gratuitos sin Docker):** Análisis sin ejecución mediante `ast.parse` (sintaxis Python), detección de patrones inseguros (`eval`, `exec`, `os.system`, `subprocess`, acceso a red), métricas estructurales, validación JSON/HTML y verificación de tests mediante inspección estática.
  - **Modo `isolated_subprocess` / `docker` (entornos locales o contenedores con permisos):** Ejecución de pruebas unitarias (`unittest`/`pytest`) en directorio temporal limpio, con variables de entorno vacías (sin `DATABASE_URL` ni `API_KEY`), timeout duro de 5 segundos, bloqueo de módulos de red en harness de prueba y eliminación inmediata del directorio temporal.
- **Justificación:** Cumple Condición #3 y `AGENTS.md` §8 ("nunca ejecutar código de estudiantes directamente en el sistema principal") sin requerir servicios pagos de sandboxing (como E2B o Modal de pago) ni privilegios Docker-in-Docker que los PaaS gratuitos bloquean.

## ADR-006: Estrategia de Despliegue Web Público Gratuito (Actualizada 2026-11-16)
- **Decisión propuesta:** Despliegue **Todo-en-Uno** 100 % gratuito sin tarjeta de crédito:
  - **Aplicación Web (Frontend compilado + Backend FastAPI):** **Render (Web Service Free Tier)** mediante `Dockerfile` multi-etapa raíz + `render.yaml` (`512 MB RAM`, `750 h/mes` gratis, sin tarjeta de crédito; duerme tras 15 min sin tráfico con arranque de 30–50 s).
  - **Base de datos:** **Neon** (PostgreSQL Free, 1 GB). Supabase queda como alternativa.
  - **Motivo de cambio respecto a Hugging Face Spaces:** se verificó el 2026-11-16 que la creación de nuevos Spaces con Docker SDK en Hugging Face pasó a requerir plan PRO (\$9/mes) y Koyeb exige tarjeta de crédito, mientras Render Free Tier permite Web Services Docker/Python sin tarjeta.
- **Consecuencia para la seguridad:** un repositorio público no debe contener trabajos académicos privados ni claves. `.gitignore` y `.dockerignore` excluyen `source-material/`, `.env` y bases `.db`; se recomienda repositorio **privado** en GitHub conectado a Render, cargando el portafolio y evaluaciones directamente a Neon con `backend/sync_to_remote_db.py`. Las claves van en Environment Variables de Render.

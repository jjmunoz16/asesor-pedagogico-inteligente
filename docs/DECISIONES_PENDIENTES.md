# Decisiones Pendientes de Aprobación — Asesor Pedagógico Inteligente

**Estado:** **Fases 1 a 9 completadas** — Requisitos, arquitectura, implementación, pruebas, despliegue en Render/Neon y repositorio público en GitHub verificados.  
**Última actualización:** 2026-11-17  
**Fuente rectora:** `docs/especificaciones/Proyecto_Final_IA_Asesor_Pedagogico_V3_Rubricas_Verificacion.docx`

Este documento registra las decisiones técnicas, arquitectónicas, funcionales y operativas y su estado de aprobación.

> **Aprobación del 2026-11-16:** el responsable del proyecto aprobó "todo" lo presentado al cierre de las Fases 3 y 4: requisitos `RF-01`–`RF-11`, `RNF-01`–`RNF-08`, historias `HU-01`–`HU-10`, arquitectura, modelo de datos y `ADR-001`–`ADR-006`. Después de esa aprobación se hicieron **correcciones de exactitud** (no de alcance) al `ADR-003`, `ADR-004` y `ADR-006`: nombres de modelo configurables, límites reales de las capas gratuitas y la recomendación concreta HF Spaces + Neon. Esas correcciones generaron la decisión nueva **`DP-15`**.

---

## 1. Decisiones de Alcance y Requisitos Académicos

| ID | Tema | Decisión | Estado |
|---|---|---|---|
| **DP-01** | Cortes vs. cohortes | **Cohorte 1 = Primer corte** (4 actividades) y **Cohorte 2 = Segundo corte** (2 actividades). | **Aprobada** |
| **DP-02** | Rúbricas de las 6 actividades | Solo existe lo que dice el documento oficial del profesor; no hay rúbricas por separado (verificado: ninguna carpeta de `source-material/` contiene una). La plataforma incluirá un editor de rúbricas y una **plantilla base editable** que el docente debe revisar antes de evaluar. | **Aprobada (con restricción)** |
| **DP-03** | Usuarios y roles | Roles `Estudiante`, `Docente` y `Administrador` con flujo HITL implementados con JWT/RBAC, revocación (`/logout`) y rate limiting (`REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`). **Actualización 2026-11-17:** activado **`PUBLIC_DEMO_MODE=false`** por defecto y en `render.yaml` para exigir inicio de sesión estricto, control BOLA/IDOR y cabeceras HTTP de seguridad (Condición #5). | **Aprobada (login estricto activo)** |
| **DP-04** | Evidencias multimodales | Se usan todos los trabajos reales de `source-material/`. | **Aprobada** |
| **DP-05** | Presentación y equipo | Integrantes: **Juan José Muñoz Naranjo** y **Christopher Villa Noreña**. Fotografías reales (`/team/juan_jose.jpg` y `/team/christopher.jpg`) y roles equivalentes de arquitectura, full-stack, IA, verificación y despliegue integrados en la plataforma. | **Aprobada e implementada** |
| **DP-16** | Contenido de la plantilla base de rúbrica | Aprobada la plantilla base editable de `docs/diseno/DISENO_UX_UI.md` §6 (25 % / 25 % / 30 % / 20 %), claramente marcada como propuesta del equipo editable por el docente. | **Aprobada** |

---

## 2. Decisiones de Arquitectura y Stack (Restricción: 100 % gratuito)

| ID | Tema | Decisión | Estado |
|---|---|---|---|
| **DP-06** | Backend | Python 3.12 + FastAPI + Pydantic v2 (`ADR-001`). | **Aprobada** |
| **DP-07** | Frontend y mapa mental | React + TypeScript + Vite + Tailwind + `@xyflow/react` (`ADR-002`). | **Aprobada** |
| **DP-08** | Persistencia | SQLModel/SQLAlchemy; SQLite en local y **Neon** (PostgreSQL Free, 1 GB) en producción (`ADR-003`). | **Aprobada** |
| **DP-09** | Modelos de IA | Gemini Free Tier (principal) + Groq Free Tier (respaldo) + Ollama/LM Studio (local, opcional). Modelos configurables por variable de entorno (`ADR-004`). | **Aprobada** |
| **DP-10** | Sandbox | `SandboxService` dual: `static_only` en producción + `isolated_subprocess` en local (`ADR-005`). | **Aprobada** |
| **DP-11** | Despliegue | **Render Free Tier** (Docker Todo-en-Uno: React + FastAPI) + **Neon PostgreSQL Free** + GitHub público `jjmunoz16/asesor-pedagogico-inteligente` (`ADR-006`). | **Aprobada y desplegada** |
| **DP-15** | **Privacidad de la capa gratuita de Gemini** | Aprobada opción **(a)**: usar **Gemini Free Tier** como proveedor principal en nube (con respaldo Groq y opción local Ollama/LM Studio), dado que los trabajos son del propio equipo y se acepta su política de uso gratuito. | **Aprobada** |

---

## 3. Estructura del Workspace y Agentes

| ID | Tema | Decisión | Estado |
|---|---|---|---|
| **DP-12** | `docs/diseno/` vs `docs/diseño/` | Se mantiene `docs/diseno/` (sin `ñ`). | **Aprobada** |
| **DP-13** | `.venv/` y `__pycache__/` dentro de `source-material/` | Excluirlos con `.gitignore` sin borrarlos. Además, **`source-material/` completo queda fuera de cualquier repositorio público** (`AGENTS.md` §8; ver `ADR-006`). | **Aprobada** |
| **DP-14** | Agentes en `.agents/` | Crear Skills y Rules en `.agents/` por rol al iniciar la Fase 6. | **Aprobada** |
| **DP-17** | Entorno de desarrollo local | Instalados y verificados: **Python 3.12.10**, **Node.js LTS 26.13.1**, **MinGit 2.56.1** y **GitHub CLI 2.104.0**. | **Resuelta y operativa** |

---

## Criterio de cierre
Todas las fases (1 a 9) han sido completadas, probadas (`10/10` pytest y build limpio) y desplegadas en Render + Neon PostgreSQL con repositorio público en GitHub.

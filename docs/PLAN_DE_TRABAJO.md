# Plan de Trabajo — Asesor Pedagógico Inteligente

**Proyecto:** Plataforma web *Asesor Pedagógico Inteligente* (Profundización I – Inteligencia Artificial, Universidad de Manizales).  
**Enfoque:** Desarrollo por fases con compuertas de validación humana, alineado con `AGENTS.md`, `README.md` y el documento oficial del profesor.

---

## Resumen de Fases y Dependencias

```text
Fase 1 (Preparación) ──► Fase 2 (Análisis Académico) ──► Fase 3 (Requisitos)
                                                               │
                                                               ▼
Fase 5 (UX/UI) ◄── Fase 4 (Arquitectura y Datos) ◄─────────────┘
      │                       │
      └───────────┬───────────┘
                  ▼
      Fase 6 (Backend y Frontend) ──► Fase 7 (Integración IA y Sandbox)
                                                  │
                                                  ▼
                                      Fase 8 (Pruebas y Auditoría)
                                                  │
                                                  ▼
                                      Fase 9 (Despliegue y Documentación Final)
```

---

## Detalle por Fase

### Fase 1: Preparación del entorno y organización documental (ACTUAL)
- **Objetivo:** Reconocer el workspace, verificar capacidades del IDE, documentar inconsistencias, definir estrategia de agentes y preparar artefactos de control.
- **Dependencias:** Ninguna.
- **Entregables:**
  - `docs/DECISIONES_PENDIENTES.md`
  - `ai-documentation/AI_USAGE_LOG.md`
  - `docs/PLAN_DE_TRABAJO.md`
  - Informe de reconocimiento (Misión 1).
- **Criterio de avance (Gate 1):** Aprobación humana del diagnóstico, la estrategia de agentes y las reglas de trabajo antes de analizar en profundidad `source-material/`.

### Fase 2: Análisis académico de documentos y las 6 actividades
- **Objetivo:** Inventariar y analizar el contenido real de las 4 actividades de `source-material/primer-corte/` y las 2 actividades de `source-material/segundo-corte/`, identificando objetivos, evidencias disponibles, formatos de archivo, temáticas, competencias y disponibilidad real de rúbricas.
- **Dependencias:** Fase 1 aprobada.
- **Entregables:**
  - Fichas de análisis en `docs/analisis-documento/` por cada actividad (sin inventar datos ni alterar archivos originales).
  - Mapa preliminar de temáticas y competencias extraído de las evidencias reales.
  - Reporte de brechas (información faltante, rúbricas ausentes, archivos no legibles).
- **Criterio de avance (Gate 2):** Validación de los hallazgos académicos y resolución de las decisiones `DP-01` a `DP-05`.

### Fase 3: Definición de requisitos funcionales y no funcionales
- **Objetivo:** Traducir el documento oficial del profesor y los hallazgos de la Fase 2 en requisitos verificables (RF, RNF), historias de usuario, reglas de evaluación (Verificación, Cuantificación 0,0–5,0 y Recomendación) y criterios de aceptación.
- **Dependencias:** Fase 2 validada.
- **Entregables:**
  - Especificación de requisitos en `docs/especificaciones/` (sin modificar el `.docx` oficial).
  - Matriz de trazabilidad entre requisitos del profesor y funcionalidades de la plataforma.
- **Criterio de avance (Gate 3):** Aprobación formal de los requisitos y criterios de aceptación.

### Fase 4: Diseño de arquitectura, modelo de datos y decisiones técnicas
- **Objetivo:** Evaluar alternativas y definir arquitectura del sistema, modelo de datos (portafolio, rúbricas versionadas, evidencias, evaluaciones, trazabilidad), contratos JSON Schema/Pydantic para respuestas de IA, estrategia de sandbox para código y selección de stack.
- **Dependencias:** Fase 3 aprobada.
- **Entregables:**
  - Documentos de arquitectura y diagramas en `docs/arquitectura/`.
  - ADRs (Architecture Decision Records) en `docs/decisiones-tecnicas/` resolviendo `DP-06` a `DP-11`.
- **Criterio de avance (Gate 4):** Aprobación explícita de la arquitectura y tecnologías (requisito obligatorio de `AGENTS.md` antes de programar).

### Fase 5: Diseño de experiencia de usuario e interfaces (UX/UI)
- **Objetivo:** Diseñar los flujos de usuario (estudiante y docente), wireframes/prototipos de carga de trabajos, gestión de rúbricas, informe individual de retroalimentación, informe integral, mapa mental interactivo y sección de presentación del proyecto y equipo.
- **Dependencias:** Fase 3 aprobada y coordinación con Fase 4.
- **Entregables:**
  - Especificaciones y diseños de interfaz en `docs/diseno/`.
- **Criterio de avance (Gate 5):** Aprobación de flujos y vistas clave.

### Fase 6: Desarrollo base de Backend y Frontend
- **Objetivo:** Implementar la estructura base en `backend/` y `frontend/`, autenticación y roles, gestión de portafolio y rúbricas (con validación de ponderaciones al 100 %), almacenamiento seguro y vistas principales.
- **Dependencias:** Fases 4 y 5 aprobadas.
- **Entregables:**
  - Código fuente modular en `backend/` y `frontend/`.
  - Cálculo determinístico de notas en backend (0,0 a 5,0).
- **Criterio de avance (Gate 6):** Pruebas unitarias e integración básicas pasando sin errores.

### Fase 7: Integración de Inteligencia Artificial y verificación objetiva
- **Objetivo:** Integrar conectores configurables a modelos de IA (locales/nube), validación estricta de salidas con JSON Schema/Pydantic, motor de evaluación en 3 dimensiones (Verificación, Cuantificación, Recomendación), sandbox aislado para análisis/ejecución de código y generador del mapa mental interactivo.
- **Dependencias:** Fase 6 completada.
- **Entregables:**
  - Módulos de orquestación IA, validadores y sandbox operativo.
  - Flujo de revisión y aprobación docente implementado.
- **Criterio de avance (Gate 7):** Evaluaciones reproducibles y trazables sobre casos de prueba reales de `source-material/`.

### Fase 8: Pruebas, validación, seguridad y auditoría
- **Objetivo:** Ejecutar pruebas automatizadas en `tests/`, auditoría de seguridad (aislamiento de código de estudiantes, protección de credenciales y datos privados), verificación de coherencia entre rúbricas y notas calculadas, y pruebas de usabilidad.
- **Dependencias:** Fase 7 completada.
- **Entregables:**
  - Suite de pruebas en `tests/` y reporte de resultados.
  - Checklist de seguridad y conformidad con el documento del profesor.
- **Criterio de avance (Gate 8):** Cero fallos críticos y validación de todas las funcionalidades obligatorias.

### Fase 9: Despliegue, documentación final y socialización
- **Objetivo:** Desplegar la plataforma en un servidor web con URL pública y funcional, completar la documentación técnica y el registro de herramientas de IA (`ai-documentation/AI_USAGE_LOG.md`), y preparar la demostración.
- **Dependencias:** Fase 8 aprobada.
- **Entregables:**
  - URL web pública y funcional.
  - Documentación final actualizada y lista para socialización.
- **Criterio de cierre:** Verificación en vivo de la plataforma desplegada frente a los requisitos oficiales.

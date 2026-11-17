# Matriz de Trazabilidad de Requisitos

Esta matriz garantiza que cada requisito del documento oficial del profesor (`Proyecto_Final_IA_Asesor_Pedagogico_V3_Rubricas_Verificacion.docx`) y de `AGENTS.md` esté cubierto por requisitos funcionales (`RF`), no funcionales (`RNF`) e historias de usuario (`HU`).

| Fuente Oficial | Requisito / Lineamiento Original | Requisitos del Sistema | Historias de Usuario | Componente Arquitectónico Principal |
|---|---|---|---|---|
| **Func. Obligatoria #1** | Entrada de información (descripción/objetivos, rúbrica y solución del estudiante) | `RF-02`, `RF-03` | `HU-02`, `HU-03` | Servicio de Portafolio y Rúbricas |
| **Func. Obligatoria #2** | Portafolio académico (cohortes 1 y 2, PDF legible, código fuente GitHub/ZIP, rúbrica versionada, opcionales) | `RF-02`, `RNF-04` | `HU-02` | Gestión de Evidencias + Hashing `SHA-256` |
| **Func. Obligatoria #3** | Gestión de rúbricas (competencias, criterios, niveles, suma 100 %, detección de inconsistencias) | `RF-03`, `RNF-01` | `HU-03` | Motor de Validación de Rúbricas |
| **Func. Obligatoria #4** | Evaluación inteligente de cada laboratorio (citas concretas, nota 0,0–5,0, fortalezas/debilidades, revisión docente) | `RF-04`, `RF-05`, `RF-06`, `RF-07` | `HU-04`, `HU-05`, `HU-06` | Harness IA + Calculadora Determinista + HITL |
| **Func. Obligatoria #5** | Informe integrado del aprendizaje (consolidado cohortes 1 y 2, evolución, brechas, plan, descarga) | `RF-08` | `HU-07` | Servicio de Analítica Integral + Exportador |
| **Func. Obligatoria #6** | Mapa mental interactivo de competencias (relaciones, laboratorios, evidencias, dominio, navegación, descarga) | `RF-09` | `HU-08` | Generador de Grafo + UI React Flow |
| **Func. Obligatoria #7** | Presentación del proyecto y equipo desarrollador (abstract, foto, nombre y rol) | `RF-10` | `HU-09` | Vista Pública de Proyecto y Equipo |
| **Condición Ing. #1** | Uso intensivo de IA y registro de herramientas, aportes, limitaciones y decisiones | `RNF-07` | N/A (proceso) | `ai-documentation/AI_USAGE_LOG.md` + ADRs |
| **Condición Ing. #2** | Salida estructurada (JSON Schema / Pydantic) y cálculo de nota 0,0–5,0 solo en backend | `RF-05`, `RNF-01` | `HU-04` | Contratos Pydantic + `ScoringService` |
| **Condición Ing. #3** | Verificación objetiva del código (sintaxis, análisis estático, tests en sandbox sin red) | `RF-04`, `RNF-03` | `HU-04` | `CodeVerificationSandbox` |
| **Condición Ing. #4** | Conexión configurable con modelos locales o en la nube y justificación técnica | `RF-11`, `RNF-05` | `HU-10` | `ModelRouter` + `LLMProvider` |
| **Condición Ing. #5** | Despliegue en servidor web con URL funcional, autenticación, usuarios y persistencia segura | `RF-01`, `RNF-03`, `RNF-08` | `HU-01` | Auth JWT + PostgreSQL + Hosting Free Tier |
| **Condición Ing. #6** | Trazabilidad completa y supervisión docente (revisar, ajustar, aprobar antes de publicar) | `RF-06`, `RNF-02` | `HU-05` | `AuditLog` + Flujo HITL |
| **`AGENTS.md` §3** | Método obligatorio: Verificación, Cuantificación (0,0–5,0), Recomendación | `RF-05`, `RF-07` | `HU-04`, `HU-06` | Schema de Evaluación en 3 Dimensiones |
| **`AGENTS.md` §4 y §8** | No inventar evidencias, citar archivo/página/sección, seguridad y sin secretos expuestos | `RNF-02`, `RNF-03` | `HU-04` | Context Builder + Sanitización + `.env` |

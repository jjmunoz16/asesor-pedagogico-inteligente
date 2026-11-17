# Especificación de Requisitos Funcionales y No Funcionales — Asesor Pedagógico Inteligente

**Fase:** Fase 3 — Definición de requisitos  
**Fecha:** 2026-11-16  
**Fuente rectora:** `docs/especificaciones/Proyecto_Final_IA_Asesor_Pedagogico_V3_Rubricas_Verificacion.docx`  
**Insumos académicos:** `docs/analisis-documento/ANALISIS_ACTIVIDADES.md` y `docs/analisis-documento/MAPA_TEMATICAS_COMPETENCIAS.md`

---

## 1. Actores y Roles del Sistema (`DP-03` propuesto)

| Rol | Descripción | Responsabilidades principales |
|---|---|---|
| **Estudiante** | Integrante del curso (ej. Juan José Muñoz Naranjo, Christopher Villa Noreña). | Gestionar su portafolio por cohorte/actividad, cargar entregas y objetivos, solicitar autoevaluación preliminar, consultar retroalimentación, informe integrado y mapa mental interactivo. |
| **Docente** | Evaluador académico de la asignatura. | Definir/validar rúbricas (100 %), revisar evaluaciones generadas por IA, ajustar puntajes o conceptos, **aprobar y publicar** calificaciones oficiales (*Human-in-the-Loop*). |
| **Administrador** | Gestor técnico de la plataforma. | Administrar usuarios, configurar proveedores/modelos de IA permitidos, monitorear trazabilidad y auditoría. |

---

## 2. Requisitos Funcionales (RF)

| ID | Nombre | Descripción detallada | Origen en Documento Oficial / `AGENTS.md` |
|---|---|---|---|
| **RF-01** | Autenticación y gestión de usuarios | Registro, inicio de sesión seguro (JWT + contraseñas con hash seguro) y control de acceso basado en roles (Estudiante, Docente, Administrador). | Condición de ingeniería #5 |
| **RF-02** | Portafolio académico por cohortes/cortes | Organizar actividades en **Cohorte 1 (Primer corte)** y **Cohorte 2 (Segundo corte)** por estudiante/equipo. Permitir registrar descripción y objetivos de la actividad, cargar informes (`.pdf`, `.docx`, `.md`), código fuente (`.py`, `.html`, `.zip`, URL de GitHub), datos/logs (`.xlsx`, `.json`) y evidencias opcionales (`.png`, `.jpeg`, `.mp4`), asociando cada archivo a su actividad y calculando su hash `SHA-256`. | Funcionalidades obligatorias #1 y #2; `DP-01`, `DP-04` |
| **RF-03** | Gestión y versionado de rúbricas | Permitir crear, cargar (JSON/CSV/formulario) y parametrizar rúbricas por actividad con competencias, criterios, descriptores de desempeño, niveles de valoración y ponderaciones. **Validar obligatoriamente que las ponderaciones sumen exactamente 100 %**, detectando inconsistencias y bloqueando la evaluación hasta corregirlas. Conservar el historial de versiones de cada rúbrica. Incluir una plantilla base editable para actividades sin rúbrica previa (`DP-02`). | Funcionalidad obligatoria #3; Condición #6 |
| **RF-04** | Verificación objetiva del código en sandbox | Ejecutar verificaciones técnicas sobre el código fuente entregado: validación de sintaxis (AST/parsers), análisis estático básico y ejecución de pruebas unitarias cuando aplique. Toda ejecución deberá realizarse en un entorno aislado (sandbox) sin acceso a la red, con límites estrictos de CPU, memoria y tiempo, y sin riesgo para el servidor principal. | Condición de ingeniería #3; `AGENTS.md` §8 |
| **RF-05** | Evaluación inteligente en 3 dimensiones | Evaluar cada entrega combinando análisis conceptual con IA y verificación objetiva (`RF-04`) bajo tres dimensiones obligatorias: **1) VERIFICACIÓN** (cumplimiento del objetivo con citas explícitas a archivo, página, sección o fragmento), **2) CUANTIFICACIÓN** (valoración estructurada por criterio mediante JSON Schema/Pydantic; **el backend calcula la nota final entre 0,0 y 5,0** aplicando las ponderaciones de la rúbrica, nunca el LLM) y **3) RECOMENDACIÓN** (fortalezas, debilidades y mejoras técnicas, conceptuales y metodológicas). | Funcionalidad obligatoria #4; Condición #2; `AGENTS.md` §3 y §6 |
| **RF-06** | Supervisión docente (HITL) y trazabilidad | Toda evaluación generada por IA nace en estado `Borrador IA`. El sistema debe conservar: evidencias analizadas, versión exacta de la rúbrica, proveedor/modelo de IA utilizado, resultados de pruebas objetivas y justificaciones. El docente podrá revisar, ajustar observaciones/niveles (quedando trazabilidad del cambio humano vs. IA) y aprobar/publicar la evaluación final. | Condición de ingeniería #6; `AGENTS.md` §6 |
| **RF-07** | Informes individuales de retroalimentación | Generar, visualizar y permitir descargar (PDF/imprimible y JSON/Markdown) el informe individual por actividad con objetivo, evidencias citadas, desglose por criterio, nota calculada (0,0–5,0), estado de aprobación docente y recomendaciones. | Objetivo principal (`AGENTS.md` §2); Funcionalidad #4 |
| **RF-08** | Informe integral del aprendizaje | Consolidar los resultados de todas las actividades de Cohorte 1 y Cohorte 2 por estudiante/equipo: promedio ponderado/global, competencias desarrolladas, niveles de dominio alcanzados, evolución entre cortes, brechas identificadas y plan personalizado de fortalecimiento, con visualización web y descarga. | Funcionalidad obligatoria #5 |
| **RF-09** | Mapa mental interactivo de competencias | Generar automáticamente un grafo/mapa mental interactivo de las temáticas, conceptos y categorías de IA abordadas en ambas cohortes, mostrando relaciones conceptuales, laboratorios donde se aplicó cada temática, evidencias vinculadas, nivel de dominio y aspectos por profundizar. Debe permitir navegación (pan/zoom, búsqueda, filtros), exploración por nodo y descarga (SVG/PNG/JSON). | Funcionalidad obligatoria #6; `AGENTS.md` §2 |
| **RF-10** | Presentación del proyecto y equipo | Incluir vista pública/dedicada con el *abstract* del proyecto (objetivos, funcionalidades, tecnologías y aportes) y tarjetas profesionales con fotografía, nombre y rol de **Juan José Muñoz Naranjo** y **Christopher Villa Noreña**. | Funcionalidad obligatoria #7; `DP-05` |
| **RF-11** | Configuración intercambiable de modelos IA | Permitir configurar proveedores de IA gratuitos en la nube (ej. Gemini API Free Tier, Groq Free Tier) y/o modelos locales (Ollama / LM Studio) desde variables de entorno o panel administrativo seguro, registrando requisitos, límites y sin exponer credenciales en el frontend ni en repositorios. | Condición de ingeniería #4; `AGENTS.md` §8 |

---

## 3. Requisitos No Funcionales (RNF)

| ID | Categoría | Requisito verificable |
|---|---|---|
| **RNF-01** | **Confiabilidad y determinismo** | 100 % de las salidas del LLM deben validarse contra esquemas **Pydantic / JSON Schema** antes de persistirse; si fallan, se reintenta de forma acotada o se marca error controlado sin inventar datos. La nota 0,0–5,0 siempre se calcula de forma determinista en el backend. |
| **RNF-02** | **No alucinación y trazabilidad** | Toda afirmación evaluativa debe referenciar archivos reales de la entrega. Si falta un insumo (ej. rúbrica específica o transcripción de video), el sistema debe declararlo expresamente. |
| **RNF-03** | **Seguridad y aislamiento** | Contraseñas cifradas (bcrypt/argon2), tokens JWT con expiración, CORS restringido, validación de tipos/tamaños de archivos cargados, secretos solo en variables de entorno, y prohibición de ejecutar código estudiantil directamente en el proceso principal del backend. |
| **RNF-04** | **Privacidad académica** | Los trabajos de estudiantes y evaluaciones solo son accesibles a usuarios autenticados según su rol (RBAC), salvo el abstract/equipo (`RF-10`) y la demostración controlada definida para la socialización. |
| **RNF-05** | **Costo cero (Free Tier)** | Toda la arquitectura (backend, frontend, base de datos, modelos de IA y despliegue público) debe operar en modalidad **100 % gratuita** (open source / free tier). |
| **RNF-06** | **Usabilidad y claridad pedagógica** | Interfaz responsiva, en español, con separación visual clara entre hechos/evidencias verificadas, puntaje determinista, recomendaciones de IA y estado de revisión docente. |
| **RNF-07** | **Mantenibilidad y modularidad** | Arquitectura desacoplada ("modelo intercambiable, harness permanente"), sin duplicación de lógica y con cobertura de pruebas automatizadas en `tests/`. |
| **RNF-08** | **Despliegue y disponibilidad** | Aplicación publicada en servidor web con URL HTTPS pública, endpoint `/health` de diagnóstico y manejo elegante de *cold starts* o indisponibilidad temporal del proveedor de IA. |

---

## 4. Historias de Usuario y Criterios de Aceptación (MVP)

- **HU-01 (Autenticación):** *Como* usuario, *quiero* iniciar sesión con mi rol (Estudiante o Docente) *para* acceder a mi portafolio o al panel de revisión según permisos.
  - *CA:* Credenciales inválidas retornan `401`; rutas docentes retornan `403` a estudiantes.
- **HU-02 (Carga de portafolio):** *Como* estudiante, *quiero* ver precargadas o subir mis entregas de Cohorte 1 y Cohorte 2 *para* organizar mis evidencias por actividad.
  - *CA:* Cada archivo queda asociado a una actividad y cohorte, con hash `SHA-256` y metadatos verificables.
- **HU-03 (Parametrización de rúbrica):** *Como* docente, *quiero* crear o editar una rúbrica con criterios y pesos *para* evaluar objetivamente cada laboratorio.
  - *CA:* El sistema rechaza (`422`) cualquier rúbrica cuya suma de pesos ≠ 100 % y guarda nueva versión sin sobrescribir evaluaciones históricas.
- **HU-04 (Evaluación IA + Verificación de código):** *Como* estudiante/docente, *quiero* lanzar la evaluación de una entrega *para* obtener análisis en 3 dimensiones y verificación técnica del código.
  - *CA:* El backend ejecuta el análisis estático/sandbox primero, valida la salida IA con Pydantic, calcula la nota 0,0–5,0 matemáticamente y guarda el resultado en estado `Borrador IA`.
- **HU-05 (Revisión y aprobación docente HITL):** *Como* docente, *quiero* revisar, ajustar y aprobar la evaluación generada por IA *para* garantizar justicia y rigor académico antes de publicarla.
  - *CA:* Se registra usuario docente, fecha, campos ajustados y estado cambia a `Aprobada`.
- **HU-06 (Informe individual descargable):** *Como* estudiante, *quiero* consultar y descargar el informe de cada actividad *para* entender mis fortalezas, evidencias citadas y mejoras.
  - *CA:* El informe muestra las 3 dimensiones, nota 0,0–5,0, citas de archivos y permite descarga/impresión limpia.
- **HU-07 (Informe integral de cohortes):** *Como* estudiante, *quiero* ver mi consolidado entre Cohorte 1 y Cohorte 2 *para* conocer mi evolución y plan de fortalecimiento.
  - *CA:* Consolida únicamente actividades evaluadas, muestra evolución por competencia y permite descarga.
- **HU-08 (Mapa mental interactivo):** *Como* estudiante/docente, *quiero* explorar un mapa mental interactivo de temáticas de IA *para* visualizar qué competencias se dominan y cuáles profundizar.
  - *CA:* Permite zoom, clic en nodo (mostrando actividades, evidencias reales y nivel de dominio), filtrado y descarga en SVG/PNG/JSON.
- **HU-09 (Presentación y equipo):** *Como* evaluador/visitante, *quiero* ver el abstract del proyecto y el equipo desarrollador *para* conocer el alcance, tecnologías y autores.
  - *CA:* Muestra resumen técnico y fichas de **Juan José Muñoz Naranjo** y **Christopher Villa Noreña** con foto, nombre y rol.
- **HU-10 (Selección de proveedor IA):** *Como* administrador, *quiero* elegir entre proveedor en nube gratuito o modelo local *para* adaptar costos, privacidad y disponibilidad.
  - *CA:* Cambiar de proveedor no altera el esquema de salida ni la lógica de cálculo de notas.

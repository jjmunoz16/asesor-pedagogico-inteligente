# Diseño de Experiencia de Usuario e Interfaces (UX/UI) — Asesor Pedagógico Inteligente

**Fase:** Fase 5 — Diseño UX/UI  
**Fecha:** 2026-11-16  
**Basado en:** `REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`, `MATRIZ_TRAZABILIDAD.md`, `ARQUITECTURA_SISTEMA.md` y `MAPA_TEMATICAS_COMPETENCIAS.md`  
**Stack UI aprobado (`ADR-002`):** React + TypeScript + Vite + Tailwind CSS + `@xyflow/react`

---

## 1. Principios Rectores de Diseño

1. **Separación visual entre hecho verificable, sugerencia IA y decisión humana:**
   - Las **evidencias citadas** (`archivo / sección o página`) y los **resultados técnicos del sandbox** se muestran con etiqueta de verificación objetiva.
   - Los análisis generados por LLM muestran un badge `Borrador IA` + proveedor/modelo utilizado, hasta ser aprobados por el docente (`Aprobada por Docente`).
   - La calificación numérica (`0,0` a `5,0`) siempre muestra un desglose matemático transparente de los pesos de la rúbrica (`calculada por backend`).
2. **Transparencia ante información faltante (`AGENTS.md` §4):**
   - Cuando falte una rúbrica específica, un enunciado oficial o el procesamiento de un archivo binario/video (ej. `VideoAI.mp4` o `iperf3.21_64.zip`), la interfaz muestra un aviso explícito *"Información no disponible en las evidencias cargadas"* en lugar de simular datos.
3. **Resiliencia visual en capa gratuita (`RNF-08`):**
   - Indicador de estado del backend (`/health`) para informar de forma amable si el servidor gratuito está saliendo de reposo (*cold start*), sin bloquear la navegación estática.

---

## 2. Arquitectura de Información y Navegación por Roles

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ BARRA SUPERIOR: Asesor Pedagógico Inteligente  | Rol activo | Estado API │
├───────────────────────────┬─────────────────────────────────────────────┤
│ MENÚ LATERAL              │ VISTAS PRINCIPALES                          │
│                           │                                             │
│ • Proyecto y Equipo (Púb) │  /                 → Abstract + Equipo      │
│ • Portafolio (C1 y C2)    │  /portafolio       → Cortes y Actividades   │
│ • Gestión de Rúbricas     │  /rubricas         → Editor + Versiones     │
│ • Evaluación / Informes   │  /actividades/:id  → Informe Individual     │
│ • Revisión Docente (HITL) │  /docente/revision → Split-Screen HITL      │
│ • Informe Integral        │  /informe-integral → Consolidado Cohortes   │
│ • Mapa Mental Interactivo │  /mapa-mental      → Grafo @xyflow/react    │
│ • Config. Modelos IA      │  /admin/modelos    → Router Gemini/Groq/Loc │
└───────────────────────────┴─────────────────────────────────────────────┘
```

### Matriz de visibilidad por rol (`RF-01`)
| Vista / Acción | Visitante | Estudiante | Docente | Administrador |
|---|---|---|---|---|
| Proyecto y Equipo (`/`) | Sí | Sí | Sí | Sí |
| Login (`/login`) | Sí | — | — | — |
| Portafolio y carga de entregas (`/portafolio`) | No | Ver / Subir propias | Ver todas | Ver todas |
| Gestión y edición de rúbricas (`/rubricas`) | No | Solo lectura | Crear / Editar / Versionar | Sí |
| Lanzar evaluación IA + Sandbox | No | Autoevaluación preliminar (`Borrador IA`) | Sí | Sí |
| Revisión y aprobación HITL (`/docente/revision`) | No | No (`403`) | **Sí (exclusivo)** | Solo auditoría |
| Informe Individual, Integral y Mapa Mental | No | Ver y descargar | Ver y descargar | Sí |
| Configuración de proveedores IA (`/admin/modelos`) | No | No (`403`) | Lectura | **Sí** |

---

## 3. Flujo Principal de Evaluación (End-to-End)

```text
[1. Portafolio] Cargar / seleccionar actividad (Cohorte 1 o 2) y evidencias
       │
       ▼
[2. Rúbrica] Validar que exista versión activa con suma de pesos == 100 %
       │
       ▼
[3. Verificación Técnica] SandboxService analiza código (.py/.html/.json)
       │
       ▼
[4. Harness IA] Context Builder + LLM (JSON Schema) -> Validación Pydantic
       │
       ▼
[5. Cálculo Backend] ScoringService calcula nota 0.00–5.00 -> Estado: Borrador IA
       │
       ├──► [Vista Estudiante]: Consulta autoevaluación preliminar + recomendaciones
       │
       ▼
[6. Revisión Docente (HITL)] Split-Screen: compara evidencias vs. sugerencia IA
       │   (Ajusta puntajes/texto si aplica; registra diff)
       ▼
[7. Publicación y Analítica] Estado: Aprobada -> Actualiza Informe Integral y Mapa Mental
```

---

## 4. Diseño Detallado de Vistas Clave (Wireframes)

### 4.1. Presentación del Proyecto y Equipo (`/`) — `RF-10`
- **Bloque 1 (Hero + Abstract):** Título *"Asesor Pedagógico Inteligente"*, contexto académico (*Profundización I – Inteligencia Artificial, Universidad de Manizales*), síntesis de objetivos, las 3 dimensiones de evaluación, arquitectura *"modelo intercambiable, harness permanente"* y stack gratuito utilizado.
- **Bloque 2 (Equipo Desarrollador):** Dos tarjetas simétricas con fotografía, nombre completo y rol (`DP-05`, roles/fotos finales pendientes de entrega del equipo):
  - **Juan José Muñoz Naranjo** — `[Rol pendiente]` + `[Placeholder de foto]`
  - **Christopher Villa Noreña** — `[Rol pendiente]` + `[Placeholder de foto]`
- **Acceso rápido:** Botón `Ingresar a la plataforma` (`/login`).

### 4.2. Portafolio Académico por Cohortes (`/portafolio`) — `RF-02`
- **Pestañas de corte:** `Cohorte 1 — Primer Corte (4 actividades)` | `Cohorte 2 — Segundo Corte (2 actividades)` | `+ Nueva actividad`.
- **Tarjetas por actividad** (precargadas con las 6 actividades reales en modo solo lectura sobre `source-material/`):
  - Estado de rúbrica (`Validada 100 %` / `Usando plantilla base pendiente de revisión`).
  - Estado de evaluación (`Sin evaluar` / `Borrador IA` / `Aprobada`).
  - Lista de archivos asociados con icono por tipo (`.pdf`, `.docx`, `.md`, `.xlsx`, `.py`, `.html`, `.json`, imagen, video, `.zip`), tamaño, **hash SHA-256** truncado (copiable) y estado de extracción (`Extraído` / `Solo metadatos`).
- **Modal/Formulario de nueva entrega:** Permite adjuntar objetivo/descripción, archivo PDF legible, código fuente (ZIP o URL de GitHub) y evidencias opcionales.

### 4.3. Editor de Rúbricas y Validador 100 % (`/rubricas`) — `RF-03`
- Selector de actividad + selector de versión (`v1`, `v2`, ...).
- **Barra de integridad en vivo:** Indicador persistente `Suma actual: XX % / 100 %`.
  - Si `!= 100 %`: borde rojo, mensaje de error exacto (*"La suma actual es 85 %. Ajuste los criterios para sumar 100 % antes de guardar o evaluar"*) y botón `Guardar nueva versión` deshabilitado.
  - Si `== 100 %`: badge verde `Rúbrica válida`.
- Tabla editable de criterios: Competencia, Criterio, Descriptor, Ponderación (%), Niveles de valoración (`0.0` a `5.0`) y botón `+ Usar plantilla base editable`.

### 4.4. Informe Individual por Actividad (`/actividades/:id`) — `RF-04`, `RF-05`, `RF-07`
Distribuido en **4 bloques claros** + cabecera resumen:
- **Cabecera:** Nombre de la actividad, Cohorte, Nota (`X.XX / 5.00` — badge `Calculada por backend`), Estado (`Borrador IA` o `Aprobada por Docente`), Modelo IA usado, Versión de rúbrica y botones `Descargar PDF (Imprimir)` / `Exportar JSON` / `Exportar Markdown`.
- **Bloque A — VERIFICACIÓN (Cumplimiento de Objetivo):** Badge (`Cumplido` / `Parcial` / `No cumplido` / `No verificable`), resumen y lista de **evidencias citadas** con tarjetas clicables (`archivo`, `página/sección`, `fragmento literal`) + lista de faltantes detectados si existen.
- **Bloque B — VERIFICACIÓN TÉCNICA OBJETIVA (Sandbox):** Acordeón/panel con resultado de `SandboxService`: modo (`static_only` o `isolated_subprocess`), validez sintáctica AST, hallazgos estáticos y conteo de pruebas unitarias (ej. `11/11` si aplica).
- **Bloque C — CUANTIFICACIÓN (Rúbrica):** Tabla con cada criterio, peso (%), nivel asignado, puntaje (`0,0–5,0`), aporte ponderado, justificación y citas que lo respaldan.
- **Bloque D — RECOMENDACIÓN:** Columnas o tarjetas diferenciadas para **Fortalezas**, **Debilidades** y **Mejoras** (*Técnicas*, *Conceptuales* y *Metodológicas*).

### 4.5. Panel de Revisión Docente — Split-Screen HITL (`/docente/revision/:evalId`) — `RF-06`
Inspirado directamente en el patrón *Split-Screen HITL* que el propio equipo diseñó en `Lab_2`:
- **Panel izquierdo (50 % — Evidencia y Contexto):** Visor de texto extraído del documento, código fuente resaltado, imágenes/diagramas y log del sandbox técnico, sincronizado al hacer clic en cualquier cita.
- **Panel derecho (50 % — Dictamen Docente):**
  - Criterios pre-diligenciados por la IA con nota preliminar.
  - Controles por criterio: `[Aceptar puntaje IA]` o input numérico ajustado (`0,0–5,0`) + justificación del docente.
  - Recálculo inmediato en vivo de la nota final ponderada.
  - Campo obligatorio de observaciones cuando se modifique un puntaje IA (para trazabilidad).
  - Acciones finales: `Aprobar y Publicar Evaluación` | `Solicitar Nueva Evaluación IA`.

### 4.6. Informe Integral del Aprendizaje (`/informe-integral`) — `RF-08`
- **KPIs superiores:** Promedio global (`0,0–5,0`), actividades evaluadas (`X / 6`), nivel de dominio predominante y brecha principal detectada.
- **Comparativa Cohorte 1 vs. Cohorte 2:** Gráfico de evolución temporal y barras por eje temático/competencia.
- **Matriz de Competencias:** Tabla con competencia, actividades donde se aplicó, nivel alcanzado (`Inicial`, `Intermedio`, `Avanzado`, `Por profundizar`) y evidencias clave.
- **Plan Personalizado de Fortalecimiento:** Acciones concretas ordenadas por prioridad (alta/media) vinculadas a las debilidades detectadas en las actividades reales.
- **Acciones:** `Descargar Informe Integral (PDF / Impresión)` y `Exportar JSON`.

### 4.7. Mapa Mental Interactivo de Competencias (`/mapa-mental`) — `RF-09`
Implementado con **`@xyflow/react`**:
```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Filtros: [Todas las cohortes v] [Nivel: Todos v] [Buscar concepto...]   │
│ Acciones: [Centrar] [Expandir/Colapsar] [Descargar SVG] [Descargar PNG] │
├──────────────────────────────────────────────┬──────────────────────────┤
│ LIENZO INTERACTIVO (@xyflow/react)           │ PANEL LATERAL DE NODO    │
│                                              │                          │
│         [Asesor / Competencias IA]           │ Nodo: Harness Engineering│
│          /          |           \            │ Dominio: Avanzado (4.5)  │
│   [Prompt/Ctx]  [Harness]   [ML & Series]    │                          │
│      /   \          |          /     \       │ Aplicado en:             │
│   [Lab2][Lab3]   [Lab6]    [Parcial][Coloq.] │ • Lab 3 (VibeCode)       │
│                                              │ • Lab 6 (Organizador)    │
│  Leyenda colores:                            │                          │
│  ● Verde: Avanzado  ● Azul: Intermedio       │ Evidencias reales:       │
│  ● Ámbar: Inicial   ● Rojo: Por profundizar  │ - INFORME_LAB01.md       │
│                                              │ - organizador_archivos.py│
│  Controles: (+ / - / Fit / Minimap)          │                          │
│                                              │ Por profundizar:         │
│                                              │ - Tool calling con sandbox│
└──────────────────────────────────────────────┴──────────────────────────┘
```
- Al hacer clic en cualquier nodo del mapa se abre el panel lateral con: definición del concepto, laboratorios/actividades vinculados, lista de archivos de evidencia reales, nivel de dominio calculado y recomendaciones específicas de profundización.

### 4.8. Configuración de Modelos IA (`/admin/modelos`) — `RF-11`
- Selector de proveedor activo: `Gemini Free Tier (Nube)` | `Groq Free Tier (Nube)` | `Ollama / LM Studio (Local)`.
- Muestra nombre de modelo configurado vía entorno (sin mostrar nunca valores de `API_KEY`), límites conocidos de cuota, estado de conectividad y botón `Probar conexión`.

---

## 5. Responsive, Accesibilidad y Descarga de Reportes

- **Desktop-first con soporte móvil:** El *Split-Screen* docente apila los paneles verticalmente (`flex-col`) en pantallas `< 1024px`. El mapa mental permite gestos táctiles de arrastre y zoom.
- **Impresión / PDF limpia (`@media print`):** Tanto el **Informe Individual** como el **Informe Integral** cuentan con hoja de estilo `@media print` dedicada que oculta menús laterales, conserva encabezados institucionales, tablas y citas, y permite guardar en PDF nativo sin librerías pesadas de pago.
- **Accesibilidad:** Contraste AA mínimo, navegación por teclado en formularios y atributos `aria-label` en nodos y acciones críticas.

---

## 6. Plantilla Base Editable de Rúbrica (`DP-16` — Propuesta para Aprobación)

> **Advertencia de trazabilidad (`AGENTS.md` §4 y `DP-16`):** El documento oficial del profesor exige rúbricas con ponderaciones que sumen 100 %, pero **no define criterios ni porcentajes específicos para cada uno de los 6 laboratorios**. Esta plantilla base es una **propuesta del equipo (no un requisito oficial del profesor)** pensada para usarse únicamente como punto de partida editable en la UI cuando el docente cree o cargue la rúbrica de una actividad.

| # | Competencia / Dimensión | Criterio propuesto | Peso (%) | Qué verifica / evidencia |
|---|---|---|---|---|
| 1 | **Verificación de Objetivos (`AGENTS.md` §3)** | Cumplimiento del objetivo y entregables de la actividad | **25 %** | Coherencia entre objetivo planteado y artefactos entregados (citas concretas). |
| 2 | **Rigor Conceptual en IA (Func. #4)** | Dominio teórico, conceptual y metodológico | **25 %** | Uso correcto de conceptos de IA, justificación técnica y análisis crítico en informes/mapas. |
| 3 | **Calidad Técnica y Evidencia Objetiva (Cond. #3)** | Calidad del código, estructura, pruebas y verificación en sandbox | **30 %** | Sintaxis válida, modularidad, ejecución de pruebas unitarias, logs y reproducibilidad. |
| 4 | **Trazabilidad, Seguridad y Uso Responsable (Func. #4, Cond. #6)** | Documentación de herramientas IA, manejo de riesgos/datos y presentación | **20 %** | Registro de prompts/modelos, declaración de limitaciones, control de errores y claridad. |
| — | **TOTAL** | — | **100 %** | Validado obligatoriamente por el motor de rúbricas. |

- **Escala de valoración sugerida por criterio:** `0.0` (No evidencia) · `1.5` (Insuficiente) · `3.0` (Básico) · `4.0` (Satisfactorio) · `5.0` (Sobresaliente). El docente puede modificar criterios, pesos, niveles y escalas libremente en el editor (`/rubricas`) siempre que la suma total sea **100 %**.

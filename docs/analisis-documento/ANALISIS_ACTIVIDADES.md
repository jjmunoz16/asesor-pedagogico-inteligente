# Análisis Académico de las 6 Actividades (`source-material/`)

**Fase:** Fase 2 — Análisis académico de documentos y actividades  
**Fecha:** 2026-11-16  
**Integrantes identificados en las entregas:** Juan José Muñoz Naranjo y Christopher Villa Noreña  
**Fuente rectora de requisitos:** `docs/especificaciones/Proyecto_Final_IA_Asesor_Pedagogico_V3_Rubricas_Verificacion.docx`

> **Regla de trazabilidad (`AGENTS.md`):** Todas las conclusiones se respaldan en archivos reales de `source-material/`. Donde falta información explícita (como rúbricas individuales o enunciados oficiales de cada laboratorio), se indica expresamente sin inventar datos.

---

## Resumen Ejecutivo de Hallazgos y Brechas

1. **Rúbricas individuales ausentes en `source-material/`:** Ninguna de las 6 carpetas contiene un archivo de rúbrica explícita con criterios y ponderaciones al 100 %. Por tanto, la plataforma deberá permitir parametrizar/cargar rúbricas por actividad (conforme a la Funcionalidad Obligatoria #3 del documento del profesor) y/o aplicar una rúbrica base configurable cuando no exista una específica.
2. **Sin duplicación en Lab 3 vs. Coloquio (actualizado tras corrección):**
   - `Lab_3 - VibeCode/` contiene ahora el documento fuente `Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf` (13 páginas), distinto de `Coloquio de investigaciones/INFORME_TÉCNICO_ANALÍTICO_IA.docx`.
   - `LAB1 - HISTORIA DE LA IA/.../PrototipoManizalesResiliente.html` y `Lab_2 - Mzles Resiliente/.../PrototipoManizalesResiliente.html` mantienen el **mismo hash SHA-256** (`4D45C93E5E092D5A5674581688A4692FF3B8CF612E39FBAD1494D6C39DC880C3`).
3. **Multimedia y binarios no analizados en profundidad en esta fase:**
   - `LAB1/.../VideoAI.mp4` (requiere procesamiento de audio/video si se desea transcripción automática en la plataforma).
   - `Primer Parcial/Parcial/cartografia_modelos/iperf3.21_64.zip` (herramienta/binario empaquetado).

---

## Cohorte 1 — Primer Corte

### Actividad 1: `LAB1 - HISTORIA DE LA IA`
- **Ubicación:** `source-material/primer-corte/LAB1 - HISTORIA DE LA IA/Grupo5_JuanJoséMuñoz_ChristopherVilla/`
- **Objetivo explícito confirmado por el equipo (2026-11-16):** Realizar un video con ayuda de la IA sobre la historia de la IA, un mapa mental de la temática y el prototipo de Manizales Resiliente. *(Nota: el enunciado no venía en un archivo de texto dentro de la carpeta; fue confirmado directamente por los autores y coincide 1:1 con los tres entregables presentes: `VideoAI.mp4`, `MapaMentalAI.png` y `PrototipoManizalesResiliente.html`).*
- **Evidencias reales:**
  1. `MapaMentalAI.png` — Mapa mental titulado **"IA en Ingeniería de Software: Evolución y Futuro"** con 7 ramas:
     - *1. Historia y Evolución* (1950–1960, Test de Turing, McCarthy 1956, Stanford AI Lab 1962, inviernos de IA).
     - *2. Paradigmas Tecnológicos* (IA Clásica, Machine Learning, Deep Learning, IA Generativa/LLMs).
     - *3. Áreas de Aplicación Actual* (IA de Internet, Comercial, de Percepción, Autónoma).
     - *4. IA en el Ciclo de Software* (Requisitos, Diseño, Programación, QA).
     - *5. El Futuro del Ingeniero* (cambio de rol a arquitecto/supervisor, pensamiento sistémico y gobernanza).
     - *6. Ética, Riesgos y Regulación* (sesgos, tecno-solucionismo, políticas globales, transparencia).
     - *7. Impacto Sectorial y Local* (salud, finanzas, movilidad y contexto local como gestión sísmica).
  2. `PrototipoManizalesResiliente.html` — Prototipo HTML (idéntico por hash al de Lab 2).
  3. `VideoAI.mp4` — Video de entrega (sin transcripción textual en la carpeta).
- **Temáticas y competencias:** Fundamentos e historia de la IA, paradigmas (simbólico, ML, DL, GenAI), ética y regulación, rol del ingeniero en desarrollo aumentado.

---

### Actividad 2: `Lab_2 - Mzles Resiliente`
- **Ubicación:** `source-material/primer-corte/Lab_2 - Mzles Resiliente/Grupo5_JuanJoséMuñoz_ChristopherVilla/`
- **Objetivo explícito encontrado (verificado por extracción de texto):** `Solution Blueprint ... .pdf`, sección *1. Resumen Ejecutivo de la Solución*: *"Su objetivo fundamental es optimizar, digitalizar y agilizar el proceso de inspección, clasificación y certificación de habitabilidad de edificaciones afectadas, alineándose estrictamente con los protocolos de la Evaluación de Daños y Análisis de Necesidades (EDAN-Estructural) de la Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD) y el Consejo Municipal para la Gestión del Riesgo de Desastres (CMGRD)."*
- **Evidencias reales:**
  1. `Solution Blueprint - Manizales Resiliente_ Juan José Muñoz Naranjo - Christopher Villa Noreña.pdf` (15 páginas detectadas en la estructura del PDF). Secciones verificadas:
     - *2. Problema y Contexto (Problem Canvas)*: valor esperado de reducir 60 % el tiempo de triaje estructural inicial; análisis del impacto de falsos negativos y falsos positivos.
     - *3. Usuarios y Stakeholders*, *4. Casos de Uso Prioritarios* y *5. Data Map*.
     - *6. Technology Landscape y Decisiones*: YOLOv8 (segmentación de fisuras), XGBoost (Índice de Prioridad de Intervención, IPI), PostgreSQL + PostGIS, PWA React/Vite offline-first, NLP/NER para notas de campo. Alternativas descartadas: LLM multimodal en la nube (costo y latencia), reglas fijas, MongoDB, desarrollo nativo y sistemas de voz.
     - *7. Mapa de Aplicación de Capacidades de IA*: validación humana (HITL) **obligatoria** en IA generativa, ML, visión y drones; voz/Speech AI descartada por *"Ruido ambiental extremo en zonas de derrumbe, variación de modismos y latencia inaceptable"*.
     - *8. Arquitectura Conceptual End-to-End*: capa de IA aislada en contenedores FastAPI, *quality gate* de confianza visual > 80 % e interfaz HITL para el Ingeniero Estructural.
     - *9. Diseño de Aplicación Moderna*: RBAC de 4 roles e interfaz de control humano en pantalla dividida (*Split-Screen*).
     - *10. Riesgos, Privacidad, Seguridad y HITL*, *11. Resiliencia y Failure Injection* (Circuit Breaker con latencia > 3 s, deduplicación geoespacial < 5 m) y *12. Quality Gates y Métricas* (confianza > 80 %, aceptación humana > 90 %, falsos negativos < 1 %, respuesta degradada < 200 ms).
     - *13.2 Declaración de Uso Responsable de IA* (Gemini) y *14. Conclusiones y Hoja de Ruta de Aprendizaje*.
     - **Hallazgo:** el documento pasa de la sección 12 a la *13.2*. No se encontró una sección *13* ni *13.1* en el texto extraído.
  2. `BancodePrompts_JuanJoséMuñoz_ChristopherVilla.xlsx` (`sheet1.xml`): registro trazable de 6 prompts (`P-001` a `P-006`) con Gemini y Claude, con validación humana y decisiones derivadas.
  3. `PrototipoManizalesResiliente.html`: según `P-005` del banco de prompts, es un prototipo *Split-Screen* con interruptor para simular la caída del servicio de IA y mostrar el patrón HITL. *(El HTML en sí no se inspeccionó línea por línea en esta fase.)*
- **Temáticas y competencias:** Arquitectura de sistemas con IA, visión por computador (YOLOv8), ML tabular (XGBoost), NLP/NER, diseño offline-first y resiliente, PromptOps y gobernanza HITL.

> **Nota de corrección (2026-11-16):** La versión anterior de esta ficha citaba números de página por sección que **no estaban verificados**, porque el PDF no se había podido leer. Se reemplazaron por los títulos de sección reales, tomados del texto extraído (`scratch/pdf_extract_v2.ps1`, solo lectura).

---

### Actividad 3: `Lab_3 - VibeCode`
- **Ubicación:** `source-material/primer-corte/Lab_3 - VibeCode/`
- **Objetivo explícito encontrado:** *El documento no tiene una sección titulada "Objetivo".* Su propósito se deduce del título: *"Informe analítico: impacto de Prompt, Context y Harness Engineering en el CVDS y comparación de modelos de código para producción"* (encabezado del PDF).
- **Evidencias reales:**
  1. `Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf` (13 páginas detectadas en la estructura del PDF). Secciones verificadas:
     - *Introducción*: tendencias de Artificial Analysis y *Coding Agent Index v1.5*, que integra DeepSWE v1.1, Terminal-Bench 4.0 y SWE-Atlas-QnA.
     - *1. Las tres capas de ingeniería*: *"Prompt Engineering → qué debe hacer el modelo; Context Engineering → qué debe saber el modelo; Harness Engineering → qué puede hacer, cómo puede hacerlo y cómo se verifica que lo hizo correctamente. Estas capas no se sustituyen. Se acumulan."*
     - *2. Transformación de las fases tradicionales del CVDS*: tabla por fase y transición de un flujo lineal a uno iterativo (*"objetivo → recuperar contexto → planificar → ejecutar → probar → observar → corregir → verificar"*).
     - *3. Cambio en el rol del ingeniero de software*: el ingeniero pasa a *"diseñar un entorno donde humanos y agentes puedan producir código verificable de forma segura"*.
     - *4. Matriz comparativa de modelos comerciales y de pesos abiertos/locales* (Coding Agent Index v1.5, septiembre 2026): GPT-6 Astra (max) + Codex (62; US\$7,47; 29,4 min), Claude Fable 5.1 + Claude Code (62; US\$12,39; 34,8 min), DeepSeek V4 Pro + Codex (43; US\$0,24; 40,3 min) y Qwen3.8 27B (no listado; 256k de contexto; Apache 2.0). GLM-5.3 y Kimi K3 se mencionan en la sección 5. Distinción entre *open source* y *open weights*.
     - *5. Criterio técnico para elegir un modelo en producción*: tres escenarios (cloud de alta exigencia, producción privada de alta capacidad y local con recursos moderados).
     - *6. La arquitectura recomendada: modelo intercambiable, harness permanente* y *model routing*.
     - *7. Conclusiones*: *"el modelo aislado ya no constituye la unidad adecuada de evaluación para desarrollo de software"*.
     - **Diferencia con el informe del Coloquio:** este PDF dice *"256k contexto"* para Qwen3.8 27B; el `INFORME_TÉCNICO_ANALÍTICO_IA.docx` del Coloquio lo corrige a 262K nativos y lo audita explícitamente.
- **Temáticas y competencias:** Prompt/Context/Harness Engineering, evolución del CVDS con agentes, comparación crítica de LLMs y agentes de código, *model routing* y diseño de harnesses verificables.

> **Nota de corrección (2026-11-16):** La versión anterior citaba rangos de páginas y un "objetivo explícito" que **no estaban verificados**. Se reemplazaron por títulos de sección y citas textuales reales del PDF.

---

### Actividad 4: `Primer Parcial`
- **Ubicación:** `source-material/primer-corte/Primer Parcial/Parcial/`
- **Objetivo explícito encontrado:** En `index.html` (líneas 170–173) y `mapa_mental/mapa mental resumido.jpeg`: *Laboratorio Integrador: Desarrollo de Software Aumentado con IA* (infraestructura y modelos locales, reto de series temporales, Vibe Coding comparativo y resiliencia).
- **Evidencias reales:**
  1. `index.html`: Reporte técnico web con comparativa de *Vibe Coding* (Llama 3.2 3B vs. Qwen 2.5 Coder 1.5B vs. Claude Code/Sonnet) y métricas del reto de serie temporal (Baseline Persistencia MAE ~1.45 °C / RMSE ~2.10 °C vs. Ridge + Lags MAE ~1.15 °C / RMSE ~1.68 °C).
  2. `cartografia_modelos/modelos.xlsx` y `conclusion.md`: Registro de modelos locales verificados (Ollama `Llama 3.2 3B` en puerto 11434, ~2.0 GB, latencia 17s; LM Studio `Qwen 2.5 Coder 1.5B` en puerto 1234, ~1.1 GB, latencia 3s) y conclusión a favor de arquitectura híbrida local + cloud.
  3. `modelos_locales/ollama_test.py` y `lmstudio_test.py`: Scripts Python de consumo REST local.
  4. `serie_temporal/` (`api_client.py`, `preprocessing.py`, `model.py`, `evaluation.py`, `app.py`): Pipeline ML de predicción de temperatura horaria (API Open-Meteo, generación de lags, split temporal 80/20 sin fuga de datos, `BaselinePersistence` vs. `LagLinearModel` con `Ridge`).
  5. `evidence/*.png` (5 imágenes) y `mapa_mental/` (`mapa mental.jpeg`, `mapa mental resumido.jpeg`).
  6. *Nota de ruta:* `index.html` (línea 266) referencia `evidence/graficaserietemporal.png`, mientras el archivo en disco se llama `evidence/Grafica_serie_temporal.png` (inconsistencia menor de nombre).
- **Temáticas y competencias:** Inferencia local (Ollama, LM Studio), series temporales y ML supervisado (Ridge, MAE/RMSE, prevención de data leakage), Vibe Coding comparativo, arquitectura híbrida.

---

## Cohorte 2 — Segundo Corte

### Actividad 5: `Coloquio de investigaciones`
- **Ubicación:** `source-material/segundo-corte/Coloquio de investigaciones/`
- **Objetivo explícito encontrado:** *No consta un enunciado escrito propio de la actividad en la carpeta; la síntesis del coloquio está en el mapa mental.*
- **Evidencias reales:**
  1. `Observatorio de Proyectos de IA — Coloquio 2026-II (2).png`: Mapa mental generado con Mapify que sintetiza 3 proyectos del coloquio:
     - **P3-62 (Auditorías y Consultorías — IA Contable):** OCR Tesseract + LLM local (`qwen2.5:7b`) para JSON tributario, stack Ollama + FastAPI + React + SQLite, flujo HITL en pantalla dividida, 100 % On-Premise (\$0 en APIs), reducción de 8 min a <1 min y 90 % de precisión.
     - **P3-63 (Rutas Logísticas — VRP y Analítica):** Random Forest + Algoritmos Genéticos, telemetría GPS/clima, Python + Scikit-Learn + Leaflet.js, reducción estimada de 15 % de combustible.
     - **P3-AGX (Agilixa — Gestión de Monitorías):** Solución tradicional No-IA multiplataforma con autenticación por código único, Scrum, validada con pruebas t-Student y Wilcoxon.
  2. `INFORME_TÉCNICO_ANALÍTICO_IA.docx`: Informe técnico y analítico elaborado por Juan José Muñoz Naranjo y Christopher Villa Noreña que sintetiza las tres capas (Prompt, Context, Harness), calidad en sistemas probabilísticos, gobernanza HITL, auditoría crítica de benchmarks (`SWE-bench Verified`, `HumanEval`, `Coding Agent Index v1.5`), arquitectura híbrida y protocolo de evaluación del aporte real de la IA.
- **Temáticas y competencias:** Análisis crítico de soluciones reales de IA vs. software tradicional, arquitecturas Local-First (OCR + LLM local), optimización (VRP/Random Forest/Algoritmos Genéticos), evaluación empírica y gobernanza de costos/privacidad.

---

### Actividad 6: `Lab Harness Organizador de archivos`
- **Ubicación:** `source-material/segundo-corte/Lab Harness Organizador de archivos/LAB_01_Grupo02/`
- **Objetivo explícito encontrado:** En `INFORME_LAB01.md` (sección 2): *"Comprobar el funcionamiento de un organizador de archivos en Python mediante inventario, simulación, ejecución real, prevención de sobrescrituras, verificación de integridad, pruebas automatizadas e incorporación de una nueva extensión."*
- **Evidencias reales:**
  1. `INFORME_LAB01.md` (394 líneas): Informe técnico completo con evidencias de ejecución en PowerShell, simulación (`--simular`), ejecución real (12 archivos, 11 movidos, 1 colisión resuelta sin sobrescritura, 0 errores), verificación de integridad con huellas `SHA-256`, idempotencia, ampliación para `.rtf` y respuestas a 8 preguntas técnicas (incluyendo diferenciación entre reglas deterministas y agentes con *Tool Calling*).
  2. `organizador_archivos.py` y `test_extension_rtf.py`: Código Python y prueba unitaria (`unittest`) que pasa junto a las 10 pruebas base (`Ran 11 tests in 0.267s — OK`).
  3. `auditoria/ejecucion_real.json` y `auditoria/ejecucion_rtf.json`: Registros JSON estructurados de auditoría.
  4. `evidencia/Evidencia 1.jpeg` a `Evidencia 6.jpeg`: Capturas de pantalla de respaldo.
- **Temáticas y competencias:** Programación determinista en Python, pruebas unitarias (`unittest`), auditoría e integridad (`SHA-256`, logs JSON), idempotencia, comparación entre software determinista y agentes con *Tool Calling* (Harness y permisos).

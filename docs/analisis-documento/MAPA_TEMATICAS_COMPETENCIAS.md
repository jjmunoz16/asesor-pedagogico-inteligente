# Mapa Preliminar de Temáticas y Competencias (`source-material/`)

Este documento consolida las temáticas y competencias reales evidenciadas en las 6 actividades de las Cohortes 1 y 2. Servirá como base verificable para el **Informe Integrado del Aprendizaje** y el **Mapa Mental Interactivo de Competencias en IA**.

---

## 1. Taxonomía de Temáticas y Evidencias por Actividad

| Eje Temático | Subtemas / Tecnologías Evidenciadas | Actividades donde aparece | Evidencia Principal |
|---|---|---|---|
| **1. Fundamentos e Historia de la IA** | Test de Turing, McCarthy (1956), inviernos de IA, IA Simbólica vs. ML vs. DL vs. GenAI, ética y sesgos. | Lab 1 | `MapaMentalAI.png` |
| **2. Ingeniería de Prompts y Contexto** | Banco de prompts versionado (`P-001`–`P-006`), PromptOps, Prompt Engineering, Context Engineering, selección de contexto útil. | Lab 2, Lab 3, Parcial | `BancodePrompts...xlsx`, `INFORME_TÉCNICO_ANALÍTICO_IA.docx` |
| **3. Harness Engineering y Agentes** | Control de herramientas, permisos mínimos, sandbox, quality gates, guardrails, Tool Calling vs. código determinista, auditoría JSON/SHA-256. | Lab 3, Lab 6 (Harness) | `INFORME_TÉCNICO_ANALÍTICO_IA.docx`, `INFORME_LAB01.md`, `organizador_archivos.py` |
| **4. Modelos Locales y Arquitectura Híbrida** | Ollama (`Llama 3.2 3B`), LM Studio (`Qwen 2.5 Coder 1.5B`), `qwen2.5:7b`, latencia vs. calidad, soberanía de datos, *model routing*. | Lab 3, Parcial, Coloquio | `modelos.xlsx`, `conclusion.md`, `ollama_test.py`, `Observatorio...png` |
| **5. Machine Learning y Series Temporales** | Preprocesamiento temporal, *lags*, split sin fuga de datos, `BaselinePersistence`, `Ridge Regression`, métricas `MAE`/`RMSE`, `Random Forest`, `XGBoost`, VRP. | Lab 2, Parcial, Coloquio | `serie_temporal/*.py`, `index.html`, `Solution Blueprint.pdf`, `Observatorio...png` |
| **6. Visión por Computador y NLP** | Segmentación de daños (YOLOv8), OCR Tesseract, extracción de entidades (NER), parsing a JSON estructurado. | Lab 2, Coloquio | `Solution Blueprint.pdf`, `Observatorio...png` |
| **7. Arquitectura Resiliente y HITL** | *Human-in-the-Loop* (HITL), *Circuit Breaker*, modo degradado, *offline-first* (PWA + IndexedDB), *Failure Injection*, *Plan → Autorización → Act*. | Lab 2, Lab 3, Coloquio | `Solution Blueprint.pdf`, `PrototipoManizalesResiliente.html`, `INFORME_TÉCNICO...docx` |
| **8. Calidad, Pruebas y Verificación** | Pruebas unitarias (`unittest`), idempotencia, integridad (`SHA-256`), validación estructural (JSON Schema/Pydantic), evals semánticas, pruebas estadísticas (`t-Student`, `Wilcoxon`). | Lab 3, Coloquio, Lab 6 | `test_extension_rtf.py`, `INFORME_LAB01.md`, `INFORME_TÉCNICO...docx` |

---

## 2. Evolución del Aprendizaje (Cohorte 1 → Cohorte 2)

1. **Inicio conceptual (Lab 1):** Comprensión panorámica de la evolución de la IA, sus paradigmas y el cambio de rol del ingeniero.
2. **Diseño arquitectónico con IA (Lab 2):** Aplicación a un problema real (Manizales Resiliente / EDAN), integrando gobernanza HITL, trazabilidad de prompts y resiliencia ante fallos.
3. **Formalización metodológica y experimental (Lab 3 y Parcial):** Paso del *Vibe Coding* empírico a la ingeniería disciplinada (Prompt + Context + Harness), contraste cuantitativo entre modelos locales y en la nube, y construcción de un pipeline ML reproducible (series temporales).
4. **Consolidación aplicada y verificación rigurosa (Coloquio y Lab 6):** Evaluación crítica de soluciones reales en producción (incluyendo cuándo **no** usar IA) y validación determinista de sistemas con pruebas unitarias, auditoría JSON y control de integridad.

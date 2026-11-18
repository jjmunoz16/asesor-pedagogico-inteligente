"""Carga inicial idempotente de usuarios, cohortes, 6 actividades, rúbricas base y mapa mental."""

import json
from pathlib import Path
import secrets

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models import (
    Activity,
    ActivityType,
    Cohort,
    EvidenceFile,
    RuntimeAIConfig,
    Submission,
    TopicEdge,
    TopicNode,
    User,
    UserRole,
)
from app.schemas.rubric import CriterionInput, RubricUpsertRequest
from app.services.extractor_service import (
    classify_file,
    compute_sha256_file,
    extract_content_from_path,
)
from app.services.rubric_service import create_or_version_rubric


ACTIVITIES_CATALOG = [
    {
        "cohort_code": "C1",
        "slug": "lab1-historia-ia",
        "title": "Lab 1 — Historia y Evolución de la IA",
        "activity_type": ActivityType.LAB,
        "rel_dir": "primer-corte/LAB1 - HISTORIA DE LA IA",
        "official_objective": (
            "Realizar un video con ayuda de la IA sobre la historia de la IA, un mapa mental "
            "de la temática y el prototipo de Manizales Resiliente."
        ),
        "objective_source": "Confirmado explícitamente por el equipo (2026-11-16) y respaldado por VideoAI.mp4, MapaMentalAI.png y PrototipoManizalesResiliente.html.",
        "description": "Video sobre historia de la IA, mapa mental de evolución de la IA y prototipo HTML Manizales Resiliente.",
    },
    {
        "cohort_code": "C1",
        "slug": "lab2-mzles-resiliente",
        "title": "Lab 2 — Manizales Resiliente (Solution Blueprint)",
        "activity_type": ActivityType.LAB,
        "rel_dir": "primer-corte/Lab_2 - Mzles Resiliente",
        "official_objective": (
            "Optimizar, digitalizar y agilizar el proceso de inspección, clasificación y certificación "
            "de habitabilidad de edificaciones afectadas, alineándose con los protocolos EDAN-Estructural "
            "de la UNGRD y el CMGRD."
        ),
        "objective_source": "Solution Blueprint - Manizales Resiliente.pdf (Sección 1).",
        "description": "Blueprint arquitectónico EDAN/HITL, banco de prompts versionado y prototipo Split-Screen HTML.",
    },
    {
        "cohort_code": "C1",
        "slug": "lab3-vibecode",
        "title": "Lab 3 — Prompt, Context y Harness Engineering",
        "activity_type": ActivityType.LAB,
        "rel_dir": "primer-corte/Lab_3 - VibeCode",
        "official_objective": (
            "Analizar el impacto de Prompt, Context y Harness Engineering en el Ciclo de Vida del "
            "Desarrollo de Software (CVDS) y comparar modelos de código para producción."
        ),
        "objective_source": "Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf (Título e Introducción).",
        "description": "Informe analítico comparativo sobre capas de ingeniería con IA y Coding Agent Index.",
    },
    {
        "cohort_code": "C1",
        "slug": "primer-parcial",
        "title": "Primer Parcial — Desarrollo Aumentado, Modelos Locales y Series Temporales",
        "activity_type": ActivityType.EXAM,
        "rel_dir": "primer-corte/Primer Parcial",
        "official_objective": (
            "Integrar infraestructura y modelos locales (Ollama / LM Studio), comparativa de Vibe Coding "
            "y pipeline de predicción de serie temporal meteorológica."
        ),
        "objective_source": "Parcial/index.html y Parcial/mapa_mental/mapa mental resumido.jpeg.",
        "description": "Cartografía de modelos locales, pruebas REST, reporte HTML y reto de series temporales en Python.",
    },
    {
        "cohort_code": "C2",
        "slug": "coloquio-investigaciones",
        "title": "Coloquio de Investigaciones — Observatorio de Proyectos de IA",
        "activity_type": ActivityType.COLLOQUIUM,
        "rel_dir": "segundo-corte/Coloquio de investigaciones",
        "official_objective": (
            "Analizar críticamente proyectos reales de IA (Local-First, VRP/ML y software tradicional) "
            "y sintetizar criterios de calidad, gobernanza y selección de modelos en producción."
        ),
        "objective_source": "INFORME_TÉCNICO_ANALÍTICO_IA.docx y Observatorio de Proyectos de IA — Coloquio 2026-II (2).png.",
        "description": "Informe técnico analítico con auditoría de benchmarks y mapa mental del coloquio 2026-II.",
    },
    {
        "cohort_code": "C2",
        "slug": "lab6-harness-organizador",
        "title": "Lab Harness — Organizador de Archivos en Python",
        "activity_type": ActivityType.LAB,
        "rel_dir": "segundo-corte/Lab Harness Organizador de archivos",
        "official_objective": (
            "Comprobar el funcionamiento de un organizador de archivos en Python mediante inventario, "
            "simulación, ejecución real, prevención de sobrescrituras, verificación de integridad SHA-256, "
            "pruebas automatizadas e incorporación de la extensión .rtf."
        ),
        "objective_source": "INFORME_LAB01.md (Sección 2. Objetivo).",
        "description": "Script Python determinista, pruebas unitarias unittest, logs JSON de auditoría e informe técnico.",
    },
]


DEFAULT_TEMPLATE_CRITERIA = [
    CriterionInput(
        code="CRIT-VERIF",
        competency_name="Verificación de Objetivos",
        criterion_name="Cumplimiento del objetivo y entregables",
        description="Coherencia entre el objetivo planteado y los artefactos reales entregados con citas concretas.",
        weight_percent=25.0,
    ),
    CriterionInput(
        code="CRIT-CONCEPT",
        competency_name="Rigor Conceptual en IA",
        criterion_name="Dominio teórico, conceptual y metodológico",
        description="Uso correcto de conceptos de IA, justificación técnica y análisis crítico en informes/mapas.",
        weight_percent=25.0,
    ),
    CriterionInput(
        code="CRIT-TECH",
        competency_name="Calidad Técnica y Verificación",
        criterion_name="Calidad del código, pruebas y verificación en sandbox",
        description="Sintaxis válida, modularidad, ejecución de pruebas unitarias, logs y reproducibilidad.",
        weight_percent=30.0,
    ),
    CriterionInput(
        code="CRIT-TRACE",
        competency_name="Trazabilidad y Uso Responsable",
        criterion_name="Documentación IA, riesgos y presentación",
        description="Registro de herramientas/prompts, declaración de limitaciones, seguridad y claridad.",
        weight_percent=20.0,
    ),
]


TOPIC_NODES_SEED = [
    # Nivel 0: Núcleo
    ("root", "Competencias en IA — Profundización I", "Núcleo", "Mapa consolidado de temáticas, tecnologías, evidencias y brechas de las Cohortes 1 y 2.", "avanzado", 0.0, ["lab1-historia-ia", "lab2-mzles-resiliente", "lab3-vibecode", "primer-parcial", "coloquio-investigaciones", "lab6-harness-organizador"], ["MapaMentalAI.png", "INFORME_TÉCNICO_ANALÍTICO_IA.docx", "INFORME_LAB01.md"], ["Integrar transcripción automática de VideoAI.mp4"], 0, 0),

    # Nivel 1: 4 Macro-Áreas
    ("cat-fundamentos", "A. Fundamentos, Ética e Historia", "Macro-Área", "Evolución conceptual de la IA, paradigmas clásicos vs. generativos, aplicaciones e implicaciones éticas.", "avanzado", 4.67, ["lab1-historia-ia", "lab3-vibecode"], ["MapaMentalAI.png", "VideoAI.mp4"], ["Profundizar en marcos regulatorios locales y auditoría de sesgos"], 0, 0),
    ("cat-ing-ia", "B. Prompts, Contexto y Agentes", "Macro-Área", "Las tres capas de ingeniería con IA: Prompt, Context y Harness Engineering en el CVDS.", "avanzado", 4.67, ["lab2-mzles-resiliente", "lab3-vibecode", "primer-parcial", "lab6-harness-organizador"], ["BancodePrompts_JuanJoséMuñoz_ChristopherVilla.xlsx", "Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf", "organizador_archivos.py"], ["Medición sistemática de eficiencia de tokens y costo por tarea"], 0, 0),
    ("cat-modelos-ml", "C. Modelos Locales, ML y Visión/NLP", "Macro-Área", "Infraestructura local/nube, series temporales, ML tabular, visión por computador y NLP.", "avanzado", 4.70, ["lab2-mzles-resiliente", "lab3-vibecode", "primer-parcial", "coloquio-investigaciones"], ["modelos.xlsx", "serie_temporal/app.py", "Solution Blueprint - Manizales Resiliente.pdf"], ["Validación en producción con datasets reales de grietas y clima"], 0, 0),
    ("cat-arquitectura-qa", "D. Resiliencia, Gobernanza y QA", "Macro-Área", "Supervisión humana HITL, tolerancia a fallos, mitigación de riesgos, pruebas y quality gates.", "avanzado", 4.73, ["lab2-mzles-resiliente", "lab3-vibecode", "coloquio-investigaciones", "lab6-harness-organizador"], ["PrototipoManizalesResiliente.html", "test_extension_rtf.py", "ejecucion_real.json"], ["Automatizar evals semánticas y pruebas de caos en CI/CD"], 0, 0),

    # Nivel 2: 8 Ejes Temáticos
    ("historia-ia", "1. Historia y Paradigmas de la IA", "Eje Temático", "De los orígenes simbólicos (Turing, McCarthy 1956) al Deep Learning y los LLMs.", "avanzado", 4.67, ["lab1-historia-ia"], ["MapaMentalAI.png", "VideoAI.mp4"], ["Transcripción estructurada de VideoAI.mp4"], 0, 0),
    ("prompt-context", "2. Prompt & Context Engineering", "Eje Temático", "Formulación estructurada de instrucciones, transformación del CVDS y selección dinámica del contexto.", "avanzado", 4.64, ["lab2-mzles-resiliente", "lab3-vibecode", "primer-parcial"], ["BancodePrompts_JuanJoséMuñoz_ChristopherVilla.xlsx", "Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf"], ["Estrategias formales de compactación de contexto"], 0, 0),
    ("harness-agentes", "3. Harness Engineering y Agentes", "Eje Temático", "Control de herramientas, permisos mínimos, sandbox, límites y trazabilidad de ejecución.", "avanzado", 4.65, ["lab3-vibecode", "lab6-harness-organizador"], ["INFORME_LAB01.md", "organizador_archivos.py", "ejecucion_real.json"], ["Sandbox con contenedores aislados para múltiples lenguajes"], 0, 0),
    ("modelos-locales", "4. Modelos Locales y Router Híbrido", "Eje Temático", "Inferencia local en Ollama/LM Studio, infraestructura contenerizada y arquitectura híbrida.", "avanzado", 4.62, ["lab3-vibecode", "primer-parcial", "coloquio-investigaciones"], ["modelos.xlsx", "conclusion.md", "ollama_test.py", "lmstudio_test.py"], ["Benchmarks reproducibles de RAM y tokens/segundo"], 0, 0),
    ("ml-series", "5. Machine Learning y Series Temporales", "Eje Temático", "Predicción supervisada sin fuga de datos, baselines, métricas MAE/RMSE y optimización.", "avanzado", 4.70, ["lab2-mzles-resiliente", "primer-parcial", "coloquio-investigaciones"], ["serie_temporal/app.py", "serie_temporal/model.py", "index.html"], ["Validación cruzada temporal (TimeSeriesSplit)"], 0, 0),
    ("vision-nlp", "6. Visión por Computador y NLP", "Eje Temático", "Detección visual de daños, OCR, extracción de entidades y salidas JSON estructuradas.", "avanzado", 4.69, ["lab2-mzles-resiliente", "coloquio-investigaciones"], ["Solution Blueprint - Manizales Resiliente.pdf", "Observatorio de Proyectos de IA — Coloquio 2026-II (2).png"], ["Implementación y métricas IoU/mAP sobre dataset real"], 0, 0),
    ("resiliencia-hitl", "7. Arquitectura Resiliente y HITL", "Eje Temático", "Patrón Human-in-the-Loop, Circuit Breaker, gobernanza de riesgos y diseño offline-first.", "avanzado", 4.62, ["lab2-mzles-resiliente", "lab3-vibecode", "coloquio-investigaciones"], ["Solution Blueprint - Manizales Resiliente.pdf", "PrototipoManizalesResiliente.html"], ["Pruebas automatizadas de inyección de fallos"], 0, 0),
    ("calidad-pruebas", "8. Calidad, Pruebas y Verificación", "Eje Temático", "Pruebas unitarias, integridad SHA-256, validación Pydantic/JSON Schema y pruebas estadísticas.", "avanzado", 4.65, ["lab3-vibecode", "coloquio-investigaciones", "lab6-harness-organizador"], ["test_extension_rtf.py", "INFORME_LAB01.md", "INFORME_TÉCNICO_ANALÍTICO_IA.docx"], ["Cobertura de evals semánticas en flujos con LLM"], 0, 0),

    # Nivel 3: 20 Subtemas / Técnicas Reales Evidenciadas
    ("sub-simbolica-genai", "IA Simbólica vs. ML / DL / GenAI", "Subtema", "Comparación de paradigmas: lógica/reglas explícitas, aprendizaje estadístico, redes profundas y LLMs.", "avanzado", 4.67, ["lab1-historia-ia"], ["MapaMentalAI.png"], ["Profundizar en arquitecturas neuro-simbólicas"], 0, 0),
    ("sub-aplicaciones-ia", "Áreas de Aplicación e Impacto Local", "Subtema", "IA de internet, comercial, de percepción y autónoma; adaptación a gestión sísmica en Manizales.", "avanzado", 4.67, ["lab1-historia-ia", "lab2-mzles-resiliente"], ["MapaMentalAI.png", "Solution Blueprint - Manizales Resiliente.pdf"], ["Evaluar impacto social con métricas de cobertura territorial"], 0, 0),
    ("sub-etica-rol", "Ética, Sesgos y Nuevo Rol del Ingeniero", "Subtema", "De codificador a diseñador de sistemas, permisos, verificación y gobernanza responsable.", "avanzado", 4.58, ["lab1-historia-ia", "lab3-vibecode"], ["MapaMentalAI.png", "Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf"], ["Métricas formales de equidad algorítmica (<5 % disparidad)"], 0, 0),
    ("sub-promptops", "Banco de Prompts Versionado (P-001–P-006)", "Subtema", "Trazabilidad de prompts, validación humana y decisiones derivadas por versión.", "avanzado", 4.72, ["lab2-mzles-resiliente"], ["BancodePrompts_JuanJoséMuñoz_ChristopherVilla.xlsx"], ["Automatizar regresión de prompts ante cambios de modelo"], 0, 0),
    ("sub-context-window", "Contexto Útil y Just-in-Time", "Subtema", "Priorización de tokens pertinentes, esquemas y compactación frente a saturación de ventana.", "avanzado", 4.57, ["lab3-vibecode", "coloquio-investigaciones"], ["Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf", "INFORME_TÉCNICO_ANALÍTICO_IA.docx"], ["Implementar recuperación híbrida (BM25 + embeddings)"], 0, 0),
    ("sub-vibecoding-cvds", "CVDS Iterativo Aumentado con Agentes", "Subtema", "Evolución del flujo lineal al ciclo Objetivo → Contexto → Plan → Ejecución → Pruebas → Verificación.", "avanzado", 4.57, ["lab3-vibecode", "primer-parcial"], ["Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf", "index.html"], ["Medir ahorro neto de tiempo descontando revisión humana"], 0, 0),
    ("sub-tool-calling", "Tool Calling vs. Reglas Deterministas", "Subtema", "Cuándo usar reglas predecibles en Python frente a agentes con selección dinámica de herramientas.", "avanzado", 4.81, ["lab6-harness-organizador"], ["INFORME_LAB01.md", "organizador_archivos.py"], ["Construir agente con confirmación HITL para tool calling"], 0, 0),
    ("sub-auditoria-harness", "Auditoría JSON, SHA-256 y Permisos", "Subtema", "Registros inmutables de ejecución, prevención de colisiones, idempotencia y mínimo privilegio.", "avanzado", 4.65, ["lab3-vibecode", "lab6-harness-organizador"], ["auditoria/ejecucion_real.json", "auditoria/ejecucion_rtf.json", "INFORME_LAB01.md"], ["Firmado criptográfico de logs de auditoría"], 0, 0),
    ("sub-ollama-lmstudio", "Ollama y LM Studio (Inferencia Local)", "Subtema", "Llama 3.2 3B (11434, 17s) y Qwen 2.5 Coder 1.5B (1234, 3s) para privacidad y cero costo API.", "avanzado", 4.72, ["primer-parcial"], ["modelos.xlsx", "ollama_test.py", "lmstudio_test.py", "evidencia_ollama_test.png"], ["Evaluar modelos locales multimodales (visión)"], 0, 0),
    ("sub-model-routing", "Model Routing y Auditoría de Benchmarks", "Subtema", "Enrutamiento híbrido local/cloud y lectura crítica de SWE-bench, HumanEval y Coding Agent Index.", "avanzado", 4.62, ["lab3-vibecode", "primer-parcial", "coloquio-investigaciones"], ["conclusion.md", "INFORME_TÉCNICO_ANALÍTICO_IA.docx"], ["Medir costo real por tarea incluyendo reintentos"], 0, 0),
    ("sub-infra-virtualizacion", "Infraestructura, Docker y APIs Externas", "Subtema", "Contenedores Docker, Proxmox VE, PostgreSQL y consumo programático de Open-Meteo y REST.", "avanzado", 4.72, ["primer-parcial"], ["mapa mental resumido.jpeg", "serie_temporal/api_client.py"], ["Orquestación reproducible con Docker Compose"], 0, 0),
    ("sub-ridge-lags", "Series Temporales: Lags, Ridge y Persistencia", "Subtema", "API Open-Meteo, split temporal 80/20 sin fuga de datos; Ridge (~1.15 °C MAE) vs. Persistencia (~1.45 °C).", "avanzado", 4.72, ["primer-parcial"], ["serie_temporal/app.py", "serie_temporal/model.py", "serie_temporal/preprocessing.py", "index.html"], ["Probar modelos no lineales (XGBoost/LightGBM) sobre lags"], 0, 0),
    ("sub-ml-aplicado", "ML Tabular y Optimización (XGBoost / VRP)", "Subtema", "Priorización de intervención IPI (XGBoost), predicción logística (Random Forest) y ruteo VRP.", "avanzado", 4.69, ["lab2-mzles-resiliente", "coloquio-investigaciones"], ["Solution Blueprint - Manizales Resiliente.pdf", "Observatorio de Proyectos de IA — Coloquio 2026-II (2).png"], ["Explicabilidad SHAP por predicción individual"], 0, 0),
    ("sub-yolov8", "Visión por Computador (YOLOv8 Fisuras)", "Subtema", "Detección y segmentación de grietas estructurales con umbral de confianza (>80 %) y baja latencia.", "avanzado", 4.72, ["lab2-mzles-resiliente"], ["Solution Blueprint - Manizales Resiliente.pdf"], ["Fine-tuning con aumento de datos por polvo y baja luz"], 0, 0),
    ("sub-ocr-ner", "OCR Tesseract, NER y JSON Estructurado", "Subtema", "Extracción de notas de campo y documentos contables hacia esquemas JSON estrictos.", "avanzado", 4.69, ["lab2-mzles-resiliente", "coloquio-investigaciones"], ["Observatorio de Proyectos de IA — Coloquio 2026-II (2).png", "Solution Blueprint - Manizales Resiliente.pdf"], ["Mejorar precisión OCR en documentos degradados (>95 %)"], 0, 0),
    ("sub-hitl", "Human-in-the-Loop (Split-Screen y Firma)", "Subtema", "La IA sugiere preliminarmente; el humano revisa en pantalla dividida, ajusta y valida/firma.", "avanzado", 4.62, ["lab2-mzles-resiliente", "lab3-vibecode", "coloquio-investigaciones"], ["PrototipoManizalesResiliente.html", "Observatorio de Proyectos de IA — Coloquio 2026-II (2).png"], ["Medir tasa de aceptación humana (>90 %) en uso real"], 0, 0),
    ("sub-circuit-offline", "Circuit Breaker y Offline-First (PWA/IndexedDB)", "Subtema", "Conmutación a modo manual si falla la IA (>3s) y sincronización diferida geoespacial (<5m).", "avanzado", 4.72, ["lab2-mzles-resiliente"], ["Solution Blueprint - Manizales Resiliente.pdf", "BancodePrompts_JuanJoséMuñoz_ChristopherVilla.xlsx"], ["Resolución de conflictos concurrentes offline-online"], 0, 0),
    ("sub-gobernanza-riesgos", "Gobernanza, Privacidad y Mitigación de Riesgos", "Subtema", "Control de inyección de prompts, filtración de secretos, alucinaciones y soberanía On-Premise.", "avanzado", 4.57, ["lab3-vibecode", "coloquio-investigaciones"], ["INFORME_TÉCNICO_ANALÍTICO_IA.docx", "Observatorio de Proyectos de IA — Coloquio 2026-II (2).png"], ["Pruebas adversas automatizadas de prompt injection"], 0, 0),
    ("sub-pydantic-evals", "Validación Pydantic, JSON Schema y Evals", "Subtema", "Control determinista de esquemas de salida LLM, evals de factualidad y observabilidad.", "avanzado", 4.57, ["lab3-vibecode", "coloquio-investigaciones"], ["INFORME_TÉCNICO_ANALÍTICO_IA.docx", "Impacto de Prompt, Context y Harness Engineering en el CVDS.pdf"], ["Definir suite de evals semánticas repetibles"], 0, 0),
    ("sub-unittest-stats", "Pruebas Unitarias, Idempotencia y Estadística", "Subtema", "11/11 pruebas unittest en Python (.rtf), idempotencia verificada y pruebas t-Student / Wilcoxon.", "avanzado", 4.73, ["coloquio-investigaciones", "lab6-harness-organizador"], ["test_extension_rtf.py", "INFORME_LAB01.md", "Observatorio de Proyectos de IA — Coloquio 2026-II (2).png"], ["Integrar pruebas de propiedad e integración E2E"], 0, 0),
]

TOPIC_EDGES_SEED = [
    # Núcleo -> Macro-Áreas
    ("root", "cat-fundamentos", "Base conceptual"),
    ("root", "cat-ing-ia", "Ingeniería de IA"),
    ("root", "cat-modelos-ml", "Modelos y datos"),
    ("root", "cat-arquitectura-qa", "Confiabilidad"),
    # Macro-Áreas -> Ejes Temáticos
    ("cat-fundamentos", "historia-ia", "Evolución"),
    ("cat-ing-ia", "prompt-context", "Capas 1 y 2"),
    ("cat-ing-ia", "harness-agentes", "Capa 3"),
    ("cat-modelos-ml", "modelos-locales", "Inferencia"),
    ("cat-modelos-ml", "ml-series", "ML Predictivo"),
    ("cat-modelos-ml", "vision-nlp", "Multimodalidad"),
    ("cat-arquitectura-qa", "resiliencia-hitl", "Gobernanza"),
    ("cat-arquitectura-qa", "calidad-pruebas", "Verificación"),
    # Ejes -> Subtemas reales
    ("historia-ia", "sub-simbolica-genai", "Paradigmas"),
    ("historia-ia", "sub-aplicaciones-ia", "Aplicaciones"),
    ("historia-ia", "sub-etica-rol", "Impacto"),
    ("prompt-context", "sub-promptops", "Trazabilidad"),
    ("prompt-context", "sub-context-window", "Relevancia"),
    ("prompt-context", "sub-vibecoding-cvds", "Ciclo CVDS"),
    ("harness-agentes", "sub-tool-calling", "Agentes"),
    ("harness-agentes", "sub-auditoria-harness", "Controles"),
    ("modelos-locales", "sub-ollama-lmstudio", "Local-First"),
    ("modelos-locales", "sub-model-routing", "Arquitectura"),
    ("modelos-locales", "sub-infra-virtualizacion", "Infraestructura"),
    ("ml-series", "sub-ridge-lags", "Series"),
    ("ml-series", "sub-ml-aplicado", "Tabular/VRP"),
    ("vision-nlp", "sub-yolov8", "Visión"),
    ("vision-nlp", "sub-ocr-ner", "Lenguaje"),
    ("resiliencia-hitl", "sub-hitl", "Supervisión"),
    ("resiliencia-hitl", "sub-circuit-offline", "Tolerancia"),
    ("resiliencia-hitl", "sub-gobernanza-riesgos", "Seguridad"),
    ("calidad-pruebas", "sub-pydantic-evals", "Contratos IA"),
    ("calidad-pruebas", "sub-unittest-stats", "Testing"),
    # Relaciones transversales clave entre temáticas
    ("sub-context-window", "sub-pydantic-evals", "Contexto + Validación"),
    ("sub-model-routing", "sub-circuit-offline", "Fallback híbrido"),
    ("sub-yolov8", "sub-hitl", "Confianza >80 % → HITL"),
    ("sub-auditoria-harness", "sub-unittest-stats", "Evidencia objetiva"),
]


def run_seed(session: Session) -> None:
    """Inicializa datos base sin duplicar registros ni modificar source-material/."""
    settings = get_settings()

    # 1. Usuarios base (nunca usa contraseñas débiles fijas en el código fuente)
    users_spec = [
        ("estudiante@umanizales.edu.co", "Juan José Muñoz & Christopher Villa", UserRole.STUDENT, settings.demo_student_password),
        ("docente@umanizales.edu.co", "Docente Profundización I", UserRole.TEACHER, settings.demo_teacher_password),
        ("admin@umanizales.edu.co", "Administrador Plataforma", UserRole.ADMIN, settings.demo_admin_password),
    ]
    student_user: User | None = None
    teacher_user: User | None = None
    for email, name, role, env_pwd in users_spec:
        existing = session.exec(select(User).where(User.email == email)).first()
        if not existing:
            raw_pwd = env_pwd.strip() if env_pwd and env_pwd.strip() else f"{secrets.token_urlsafe(14)}Aa1"
            existing = User(
                email=email,
                full_name=name,
                role=role,
                password_hash=hash_password(raw_pwd),
            )
            session.add(existing)
            session.flush()
        elif env_pwd and env_pwd.strip() and not existing.password_hash:
            existing.password_hash = hash_password(env_pwd.strip())
            session.add(existing)
            session.flush()
        if role == UserRole.STUDENT:
            student_user = existing
        elif role == UserRole.TEACHER:
            teacher_user = existing

    # 2. Configuración IA runtime por defecto
    if not session.exec(select(RuntimeAIConfig)).first():
        session.add(
            RuntimeAIConfig(
                active_provider=settings.ai_provider,
                active_model=settings.gemini_model if settings.ai_provider == "gemini" else settings.groq_model,
            )
        )

    # 3. Cohortes (Cortes 1 y 2)
    cohorts: dict[str, Cohort] = {}
    for code, name, order_idx in [
        ("C1", "Cohorte 1 — Primer Corte", 1),
        ("C2", "Cohorte 2 — Segundo Corte", 2),
    ]:
        c = session.exec(select(Cohort).where(Cohort.code == code)).first()
        if not c:
            c = Cohort(code=code, name=name, order_index=order_idx)
            session.add(c)
            session.flush()
        cohorts[code] = c

    session.commit()

    # 4. Actividades + Plantilla base de rúbrica (DP-16) + Evidencias reales de source-material/
    source_root = settings.source_material_dir
    for spec in ACTIVITIES_CATALOG:
        act = session.exec(select(Activity).where(Activity.slug == spec["slug"])).first()
        if not act:
            act = Activity(
                cohort_id=cohorts[spec["cohort_code"]].id,
                slug=spec["slug"],
                title=spec["title"],
                activity_type=spec["activity_type"],
                official_objective=spec["official_objective"],
                objective_source=spec["objective_source"],
                description=spec["description"],
            )
            session.add(act)
            session.commit()
            session.refresh(act)
        else:
            act.official_objective = spec["official_objective"]
            act.objective_source = spec["objective_source"]
            act.description = spec["description"]
            session.add(act)
            session.commit()

        if not act.active_rubric_version_id:
            create_or_version_rubric(
                session,
                RubricUpsertRequest(
                    activity_id=act.id,
                    name=f"Rúbrica Base Editable — {act.title}",
                    is_template_proposal=True,
                    notes="Plantilla base propuesta por el equipo (DP-16). Revisable y editable por el docente.",
                    criteria=DEFAULT_TEMPLATE_CRITERIA,
                ),
                user_id=teacher_user.id if teacher_user else None,
            )

        act_dir = source_root / spec["rel_dir"]
        existing_sub = session.exec(
            select(Submission).where(Submission.activity_id == act.id)
        ).first()
        if not existing_sub and act_dir.exists():
            sub = Submission(
                activity_id=act.id,
                student_group_name="Juan José Muñoz Naranjo & Christopher Villa Noreña",
                owner_user_id=student_user.id if student_user else None,
                notes="Entrega original precargada desde source-material/ en modo solo lectura.",
                is_preloaded_portfolio=True,
            )
            session.add(sub)
            session.flush()

            for file_path in sorted(act_dir.rglob("*")):
                if not file_path.is_file():
                    continue
                rel_str = file_path.relative_to(source_root).as_posix()
                if "/.venv/" in rel_str or "/__pycache__/" in rel_str:
                    continue
                category, mime = classify_file(file_path)
                sha256 = compute_sha256_file(file_path)
                summary, ext_status = extract_content_from_path(file_path)
                session.add(
                    EvidenceFile(
                        submission_id=sub.id,
                        filename=file_path.name,
                        relative_path=rel_str,
                        mime_type=mime,
                        file_category=category,
                        size_bytes=file_path.stat().st_size,
                        sha256_hash=sha256,
                        storage_uri=str(file_path),
                        extracted_text_summary=summary,
                        extraction_status=ext_status,
                    )
                )
            session.commit()

    # 5. Mapa mental extendido (upsert para mantener sincronizados nodos y aristas)
    for key, label, cat, desc, level, score, slugs, evs, gaps, px, py in TOPIC_NODES_SEED:
        existing_node = session.exec(select(TopicNode).where(TopicNode.node_key == key)).first()
        if not existing_node:
            existing_node = TopicNode(node_key=key)
        existing_node.label = label
        existing_node.category = cat
        existing_node.description = desc
        existing_node.mastery_level = level
        existing_node.mastery_score = score
        existing_node.related_activity_slugs_json = json.dumps(slugs, ensure_ascii=False)
        existing_node.evidences_json = json.dumps(evs, ensure_ascii=False)
        existing_node.gaps_to_strengthen_json = json.dumps(gaps, ensure_ascii=False)
        existing_node.pos_x = px
        existing_node.pos_y = py
        session.add(existing_node)

    for src, dst, rel in TOPIC_EDGES_SEED:
        exists_edge = session.exec(
            select(TopicEdge).where(TopicEdge.source_key == src, TopicEdge.target_key == dst)
        ).first()
        if not exists_edge:
            session.add(TopicEdge(source_key=src, target_key=dst, relation_label=rel))
        else:
            exists_edge.relation_label = rel
            session.add(exists_edge)
    session.commit()

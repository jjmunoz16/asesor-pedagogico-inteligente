"""Contratos base, construcción de prompts y esquema JSON plano compatible con Gemini."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.schemas.evaluation import AIEvaluationPayload


# Esquema plano sin minimum/maximum ni $defs profundos para evitar rechazo 400 en Gemini
FLAT_EVALUATION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["verificacion", "cuantificacion_por_criterio", "recomendaciones"],
    "properties": {
        "verificacion": {
            "type": "object",
            "required": [
                "objetivo_cumplido",
                "resumen_verificacion",
                "evidencias_citadas",
                "faltantes_detectados",
            ],
            "properties": {
                "objetivo_cumplido": {
                    "type": "string",
                    "enum": ["cumplido", "parcial", "no_cumplido", "no_verificable"],
                },
                "resumen_verificacion": {"type": "string"},
                "evidencias_citadas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["archivo", "ubicacion", "fragmento"],
                        "properties": {
                            "archivo": {"type": "string"},
                            "ubicacion": {"type": "string"},
                            "fragmento": {"type": "string"},
                        },
                    },
                },
                "faltantes_detectados": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "cuantificacion_por_criterio": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "criterion_id",
                    "nivel_desempeno",
                    "puntaje_criterio",
                    "justificacion",
                    "evidencias",
                ],
                "properties": {
                    "criterion_id": {"type": "string"},
                    "nivel_desempeno": {"type": "string"},
                    "puntaje_criterio": {"type": "number"},
                    "justificacion": {"type": "string"},
                    "evidencias": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "recomendaciones": {
            "type": "object",
            "required": [
                "fortalezas",
                "debilidades",
                "mejoras_tecnicas",
                "mejoras_conceptuales",
                "mejoras_metodologicas",
            ],
            "properties": {
                "fortalezas": {"type": "array", "items": {"type": "string"}},
                "debilidades": {"type": "array", "items": {"type": "string"}},
                "mejoras_tecnicas": {"type": "array", "items": {"type": "string"}},
                "mejoras_conceptuales": {"type": "array", "items": {"type": "string"}},
                "mejoras_metodologicas": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


@dataclass
class EvaluationContext:
    activity_title: str
    cohort_name: str
    official_objective: str | None
    criteria: list[dict[str, Any]]
    evidences: list[dict[str, Any]]
    sandbox_result: dict[str, Any]


def build_system_and_user_prompts(ctx: EvaluationContext) -> tuple[str, str]:
    """Construye prompts estrictos en 3 dimensiones prohibiendo inventar evidencias o notas."""
    system_prompt = (
        "Eres un evaluador académico riguroso de Ingeniería de Sistemas e Inteligencia Artificial. "
        "Debes evaluar la entrega únicamente con base en las evidencias reales proporcionadas.\n"
        "REGLAS ESTRICTAS:\n"
        "1. Evalúa las 3 dimensiones obligatorias: VERIFICACIÓN, CUANTIFICACIÓN por criterio y RECOMENDACIONES.\n"
        "2. NUNCA calcules ni devuelvas una nota final global; solo asigna nivel_desempeno y puntaje_criterio (entre 0.0 y 5.0) para cada criterion_id exacto.\n"
        "3. Cita únicamente nombres de archivo reales presentes en la lista de evidencias y fragmentos verificables.\n"
        "4. Si falta el objetivo oficial o algún archivo no tiene texto extraído (ej. video o binario), indícalo expresamente en faltantes_detectados sin inventar contenido.\n"
        "5. Responde exclusivamente en JSON válido que cumpla la estructura solicitada."
    )

    objective_text = (
        ctx.official_objective
        if ctx.official_objective
        else "NO CONSTA OBJETIVO OFICIAL EXPLÍCITO EN LAS EVIDENCIAS CARGADAS."
    )

    criteria_lines = "\n".join(
        f"- criterion_id={c['code']} | Competencia={c['competency_name']} | "
        f"Criterio={c['criterion_name']} | Peso={c['weight_percent']}% | "
        f"Descripción={c['description']} | Niveles={c['performance_levels']}"
        for c in ctx.criteria
    )

    evidence_blocks = []
    for ev in ctx.evidences:
        snippet = ev["extracted_text_summary"][:2800]
        evidence_blocks.append(
            f"### ARCHIVO: {ev['filename']} (Categoría: {ev['file_category']}, "
            f"Estado extracción: {ev['extraction_status']}, SHA-256: {ev['sha256_hash'][:12]}...)\n"
            f"{snippet}"
        )

    user_prompt = (
        f"ACTIVIDAD: {ctx.activity_title} ({ctx.cohort_name})\n"
        f"OBJETIVO PLANTEADO: {objective_text}\n\n"
        f"CRITERIOS DE RÚBRICA (usa exactamente estos criterion_id):\n{criteria_lines}\n\n"
        f"VERIFICACIÓN TÉCNICA OBJETIVA (SANDBOX):\n{ctx.sandbox_result}\n\n"
        f"EVIDENCIAS REALES DE LA ENTREGA:\n" + "\n\n".join(evidence_blocks)
    )
    return system_prompt, user_prompt


class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    async def evaluate(self, ctx: EvaluationContext, model_name: str) -> AIEvaluationPayload:
        """Ejecuta evaluación estructurada y retorna AIEvaluationPayload validado."""

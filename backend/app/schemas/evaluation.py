"""Esquemas Pydantic estrictos para evaluación IA en 3 dimensiones y revisión docente."""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class CitedEvidence(BaseModel):
    archivo: str = Field(min_length=1)
    ubicacion: str = Field(min_length=1)
    fragmento: str = Field(min_length=1)


class VerificationDimension(BaseModel):
    objetivo_cumplido: Literal["cumplido", "parcial", "no_cumplido", "no_verificable"]
    resumen_verificacion: str = Field(min_length=1)
    evidencias_citadas: list[CitedEvidence] = Field(default_factory=list)
    faltantes_detectados: list[str] = Field(default_factory=list)


class CriterionQuantification(BaseModel):
    criterion_id: str = Field(min_length=1)
    nivel_desempeno: str = Field(min_length=1)
    puntaje_criterio: float = Field(ge=0.0, le=5.0)
    justificacion: str = Field(min_length=1)
    evidencias: list[str] = Field(default_factory=list)

    @field_validator("puntaje_criterio")
    @classmethod
    def round_score(cls, value: float) -> float:
        return round(float(value), 2)


class RecommendationDimension(BaseModel):
    fortalezas: list[str] = Field(default_factory=list)
    debilidades: list[str] = Field(default_factory=list)
    mejoras_tecnicas: list[str] = Field(default_factory=list)
    mejoras_conceptuales: list[str] = Field(default_factory=list)
    mejoras_metodologicas: list[str] = Field(default_factory=list)


class AIEvaluationPayload(BaseModel):
    """Contrato obligatorio que toda respuesta de modelo IA debe satisfacer."""

    verificacion: VerificationDimension
    cuantificacion_por_criterio: list[CriterionQuantification] = Field(min_length=1)
    recomendaciones: RecommendationDimension


class RunEvaluationRequest(BaseModel):
    provider_override: str | None = None
    model_override: str | None = None


class CriterionAdjustment(BaseModel):
    criterion_evaluation_id: int
    teacher_criterion_score: float = Field(ge=0.0, le=5.0)
    justification_note: str = ""


class TeacherReviewRequest(BaseModel):
    decision: Literal["approved", "adjusted", "rejected"]
    comments: str = ""
    adjustments: list[CriterionAdjustment] = Field(default_factory=list)

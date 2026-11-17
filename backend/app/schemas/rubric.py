"""Esquemas Pydantic para creación, versionado y validación 100 % de rúbricas."""

from pydantic import BaseModel, Field, model_validator


class CriterionInput(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    competency_name: str = Field(min_length=1, max_length=160)
    criterion_name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    weight_percent: float = Field(gt=0.0, le=100.0)
    performance_levels: dict[str, float] = Field(
        default_factory=lambda: {
            "No evidencia": 0.0,
            "Insuficiente": 1.5,
            "Básico": 3.0,
            "Satisfactorio": 4.0,
            "Sobresaliente": 5.0,
        }
    )


class RubricUpsertRequest(BaseModel):
    activity_id: int
    name: str = Field(min_length=1, max_length=200)
    is_template_proposal: bool = False
    notes: str = ""
    criteria: list[CriterionInput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_weights_sum_100(self) -> "RubricUpsertRequest":
        total = round(sum(c.weight_percent for c in self.criteria), 4)
        if abs(total - 100.0) > 0.01:
            raise ValueError(
                f"La suma de ponderaciones de la rúbrica debe ser exactamente 100 % (actual: {total:.2f} %)."
            )
        codes = [c.code.strip() for c in self.criteria]
        if len(codes) != len(set(codes)):
            raise ValueError("Los códigos de criterio dentro de una rúbrica deben ser únicos.")
        return self

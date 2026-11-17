"""Pruebas de cálculo determinista de notas y validación 100 % de rúbricas."""

import pytest
from pydantic import ValidationError

from app.schemas.rubric import CriterionInput, RubricUpsertRequest
from app.services.scoring_service import calculate_weighted_score, validate_rubric_weights


def test_rubric_weights_must_sum_100():
    assert validate_rubric_weights([25.0, 25.0, 30.0, 20.0]) == 100.0
    with pytest.raises(ValueError, match="100 %"):
        validate_rubric_weights([50.0, 30.0])


def test_rubric_schema_rejects_invalid_sum():
    with pytest.raises(ValidationError):
        RubricUpsertRequest(
            activity_id=1,
            name="Rúbrica inválida",
            criteria=[
                CriterionInput(
                    code="C1",
                    competency_name="Comp",
                    criterion_name="Crit 1",
                    description="Desc",
                    weight_percent=60.0,
                ),
                CriterionInput(
                    code="C2",
                    competency_name="Comp",
                    criterion_name="Crit 2",
                    description="Desc",
                    weight_percent=30.0,
                ),
            ],
        )


def test_calculate_weighted_score_deterministic_range():
    score = calculate_weighted_score([(5.0, 25.0), (4.0, 25.0), (3.0, 30.0), (4.0, 20.0)])
    # 1.25 + 1.00 + 0.90 + 0.80 = 3.95
    assert score == 3.95
    assert calculate_weighted_score([(0.0, 100.0)]) == 0.0
    assert calculate_weighted_score([(5.0, 100.0)]) == 5.0

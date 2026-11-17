"""Cálculo determinista de calificaciones (0.0 a 5.0) a partir de rúbricas."""

from collections.abc import Iterable


def validate_rubric_weights(weights: Iterable[float]) -> float:
    """Valida que las ponderaciones sumen 100.00 % y retorna la suma."""
    total = round(sum(float(w) for w in weights), 4)
    if abs(total - 100.0) > 0.01:
        raise ValueError(
            f"Las ponderaciones de la rúbrica deben sumar 100 % (suma actual: {total:.2f} %)."
        )
    return total


def calculate_weighted_score(criterion_scores: list[tuple[float, float]]) -> float:
    """
    Calcula la nota final determinista entre 0.00 y 5.00.

    Args:
        criterion_scores: lista de tuplas (puntaje_criterio [0..5], peso_porcentaje [0..100]).
    """
    if not criterion_scores:
        raise ValueError("Se requiere al menos un criterio para calcular la calificación.")

    validate_rubric_weights(weight for _, weight in criterion_scores)

    weighted_sum = 0.0
    for score, weight in criterion_scores:
        clamped_score = max(0.0, min(5.0, float(score)))
        weighted_sum += clamped_score * (float(weight) / 100.0)

    return round(max(0.0, min(5.0, weighted_sum)), 2)

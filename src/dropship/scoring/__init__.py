"""Winner score (0–100) and written rationale for each pick."""

from .narrative import write_pick
from .score import WEIGHTS, ScoreBreakdown, score_product

__all__ = ["WEIGHTS", "ScoreBreakdown", "score_product", "write_pick"]

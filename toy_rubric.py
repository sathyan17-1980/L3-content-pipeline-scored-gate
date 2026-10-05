"""A TOY scorer so the harness runs out of the box. Replace with your own rubric.

Two made-up dimensions:
  - clarity:      penalised by hedge/filler words.
  - completeness: rewarded for covering a few required points.

This is intentionally simplistic — it exists to make the LOOP runnable, not to
be a good rubric. Your real rubric is the thing you tune (and the cohort covers).
"""

from __future__ import annotations

from scored_gate import Score

_HEDGES = ("maybe", "sort of", "kind of", "i think", "probably", "stuff", "things")
_REQUIRED_POINTS = ("problem", "approach", "result")


def toy_score(draft: str) -> Score:
    text = draft.lower()

    hedges = sum(text.count(h) for h in _HEDGES)
    clarity = max(0.0, 100.0 - hedges * 15.0)

    covered = sum(1 for p in _REQUIRED_POINTS if p in text)
    completeness = 100.0 * covered / len(_REQUIRED_POINTS)

    overall = round(0.5 * clarity + 0.5 * completeness, 1)
    return Score(overall=overall, dimensions={"clarity": clarity, "completeness": completeness})

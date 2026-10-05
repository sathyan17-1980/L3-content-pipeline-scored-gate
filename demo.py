"""Run the scored gate on the shipped sample draft and print what it decided.

    python demo.py

You'll see a flawed draft get ITERATE'd to a pass, and the decision trail that
got it there. 'Done' is the score clearing the bar — not the model's opinion.
"""

from __future__ import annotations

from pathlib import Path

from scored_gate import Score, run_gate
from toy_rubric import toy_score

# A stand-in reviser: a real one would use score.dimensions to target the weak
# spots. Here we just show a fixed, improved draft so the demo runs offline.
_FIXED = "Problem: junk shipped. Approach: a scored gate. Result: nothing sub-threshold ships."


def _reviser(draft: str, score: Score) -> str:
    return _FIXED


def _generator() -> str:
    return _FIXED


def main() -> None:
    flawed = (Path(__file__).parent / "sample_draft.md").read_text(encoding="utf-8")
    print("DRAFT IN:\n" + flawed.strip() + "\n")

    result = run_gate(flawed, toy_score, reviser=_reviser, generator=_generator)

    print("decision trail :", [d.value for d in result.decision_trail])
    print("iterations     :", result.iterations)
    print("final score    :", result.final_score.overall, result.final_score.dimensions)
    print("shipped        :", result.shipped)
    print("parked for human:", result.parked_for_human)


if __name__ == "__main__":
    main()

"""A scored gate for generative output: measure, then accept / iterate / regenerate.

'Done' is a number clearing a threshold — never the model's opinion of its own
work. The loop is bounded by a hard cap (it PARKS for a human instead of spinning)
and a human-gate hook covers the last mile a score can't.

Teaching artifact: bring your own Scorer and threshold. The rubric shipped here
is a toy (see toy_rubric.py).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class Decision(str, Enum):
    ACCEPT = "accept"
    ITERATE = "iterate"
    REGENERATE = "regenerate"


@dataclass(frozen=True)
class Score:
    """A rolled-up quality score.

    Args:
        overall: The single number the gate compares to the threshold (0–100).
        dimensions: Per-dimension breakdown (name → 0–100). Kept for the audit
            trail and for deciding WHICH parts to revise on ITERATE.
    """

    overall: float
    dimensions: dict[str, float] = field(default_factory=dict)


# A Scorer takes the draft text and returns a Score. Swap in your own.
Scorer = Callable[[str], Score]
# A Reviser takes (draft, score) and returns an improved draft (for ITERATE).
Reviser = Callable[[str, Score], str]
# A Generator returns a fresh draft from scratch (for REGENERATE).
Generator = Callable[[], str]


def decide(score: Score, *, pass_mark: float, regen_floor: float) -> Decision:
    """Map a score to a decision.

    - overall >= pass_mark          → ACCEPT (clears the bar).
    - regen_floor <= overall < pass_mark → ITERATE (close; fix weak spots).
    - overall < regen_floor         → REGENERATE (too far off to polish).

    Deny-by-default: anything not clearly ACCEPT is held back from shipping.
    """
    if score.overall >= pass_mark:
        return Decision.ACCEPT
    if score.overall >= regen_floor:
        return Decision.ITERATE
    return Decision.REGENERATE


@dataclass
class GateResult:
    """Outcome of running the gate."""

    shipped: bool
    draft: str
    final_score: Score
    iterations: int
    parked_for_human: bool
    decision_trail: list[Decision] = field(default_factory=list)


def run_gate(
    initial_draft: str,
    scorer: Scorer,
    reviser: Reviser,
    generator: Generator,
    *,
    pass_mark: float = 80.0,      # TOY threshold — set your own, defensibly.
    regen_floor: float = 50.0,
    max_iterations: int = 3,      # the cap: PARK, don't spin.
    human_gate: Callable[[str, Score], bool] | None = None,
) -> GateResult:
    """Score → decide → (accept | revise | regenerate), bounded by a cap.

    On hitting the cap without an ACCEPT, the loop PARKS (shipped=False,
    parked_for_human=True) rather than force-shipping a sub-threshold draft.
    If a human_gate is supplied, an ACCEPT still requires it to return True.
    """
    draft = initial_draft
    trail: list[Decision] = []

    for i in range(1, max_iterations + 1):
        score = scorer(draft)
        decision = decide(score, pass_mark=pass_mark, regen_floor=regen_floor)
        trail.append(decision)

        if decision is Decision.ACCEPT:
            if human_gate is not None and not human_gate(draft, score):
                # Human vetoed the last mile — treat as parked, not shipped.
                return GateResult(False, draft, score, i, True, trail)
            return GateResult(True, draft, score, i, False, trail)

        if decision is Decision.ITERATE:
            draft = reviser(draft, score)
        else:  # REGENERATE
            draft = generator()

    # Cap reached without an ACCEPT: park for a human. Never force-ship.
    final_score = scorer(draft)
    return GateResult(False, draft, final_score, max_iterations, True, trail)

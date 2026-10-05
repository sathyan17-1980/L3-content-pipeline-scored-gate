from pathlib import Path

from scored_gate import Decision, Score, decide, run_gate
from toy_rubric import toy_score


def test_decide_three_way() -> None:
    assert decide(Score(90), pass_mark=80, regen_floor=50) is Decision.ACCEPT
    assert decide(Score(65), pass_mark=80, regen_floor=50) is Decision.ITERATE
    assert decide(Score(20), pass_mark=80, regen_floor=50) is Decision.REGENERATE


def test_iterate_then_accept() -> None:
    # Read the SHIPPED sample draft — the same file the live demo uses — so this
    # test proves the demoed artifact, not a hand-tuned proxy.
    flawed = (Path(__file__).parent / "sample_draft.md").read_text(encoding="utf-8")
    fixed = "Problem: junk shipped. Approach: a scored gate. Result: nothing sub-threshold ships."
    result = run_gate(flawed, toy_score, reviser=lambda d, s: fixed, generator=lambda: fixed)
    assert result.shipped is True
    assert result.decision_trail[0] is Decision.ITERATE   # sample scores ~60.9 → ITERATE
    assert result.final_score.overall >= 80


def test_cap_parks_instead_of_spinning() -> None:
    # a reviser that never improves → must PARK at the cap, not loop forever
    stuck = "maybe maybe maybe sort of stuff things"
    result = run_gate(stuck, toy_score, reviser=lambda d, s: stuck, generator=lambda: stuck,
                      max_iterations=3)
    assert result.shipped is False
    assert result.parked_for_human is True
    assert result.iterations == 3

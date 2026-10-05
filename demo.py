"""Run the scored gate on the sample draft and show every step.

    python demo.py

A flawed draft is scored, ITERATEd, re-scored, and ACCEPTed. The revision is
DERIVED FROM YOUR DRAFT (it cuts the hedge words 'clarity' penalises and names
the Problem if 'completeness' says it's missing) — not a canned string. So the
score climbs because the actual text got better. 'Done' = the number clears the bar.

Edit sample_draft.md and re-run to watch the gate respond to your own content.
"""

from __future__ import annotations

import re
from pathlib import Path

from scored_gate import Score, decide, run_gate
from toy_rubric import toy_score

# The toy rubric penalises these hedges (clarity) and rewards naming
# problem/approach/result (completeness). A real reviser would be smarter; this
# one is deterministic and visibly derived from the input so the demo is honest.
_HEDGES = ("maybe", "sort of", "sort-of", "kind of", "i think", "probably", "stuff", "things")

_PASS_MARK = 80.0
_REGEN_FLOOR = 50.0


def _reviser(draft: str, score: Score) -> str:
    """Targeted revision of THIS draft: cut hedges, then name the Problem if absent."""
    text = draft.strip()
    for h in _HEDGES:
        text = re.sub(re.escape(h), "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+([,.])", r"\1", text)   # no space before , or .
    text = re.sub(r",\s*\.", ".", text)         # ",." -> "."
    text = re.sub(r"\s{2,}", " ", text).strip()
    if "problem" not in text.lower():
        text = "Problem: " + text
    return text


def _generator() -> str:
    """REGENERATE: too far off to polish — a fresh attempt from scratch."""
    return ("Problem: the draft shipped weak. Approach: score every draft "
            "against a rubric. Result: nothing sub-threshold ships.")


def main() -> None:
    flawed = (Path(__file__).parent / "sample_draft.md").read_text(encoding="utf-8")

    step = {"n": 0}

    def show_scorer(draft: str) -> Score:
        step["n"] += 1
        s = toy_score(draft)
        d = decide(s, pass_mark=_PASS_MARK, regen_floor=_REGEN_FLOOR)
        print(f"iteration {step['n']}")
        print(f"  text     : {' '.join(draft.split())[:88]}")
        print(f"  clarity {s.dimensions['clarity']:.0f} | completeness {s.dimensions['completeness']:.0f} "
              f"| OVERALL {s.overall:.1f}   (pass {_PASS_MARK:.0f} / regen-floor {_REGEN_FLOOR:.0f})")
        print(f"  DECISION : {d.value.upper()}\n")
        return s

    result = run_gate(flawed, show_scorer, _reviser, _generator,
                      pass_mark=_PASS_MARK, regen_floor=_REGEN_FLOOR)

    print("RESULT")
    print(f"  shipped          : {result.shipped}")
    print(f"  iterations       : {result.iterations}")
    print(f"  parked_for_human : {result.parked_for_human}")
    print(f"  decision trail   : {[d.value for d in result.decision_trail]}")
    print()
    print('  "Done" = the number cleared the bar — and the revision came from YOUR draft.')


if __name__ == "__main__":
    main()

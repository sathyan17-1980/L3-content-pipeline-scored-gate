# content-pipeline-scored-gate

A tiny, dependency-free **scored gate** for generative output: measure a draft,
then **accept / iterate / regenerate** against a threshold — with a hard cap that
**parks for a human** instead of spinning, and a **human-gate** hook for the last
mile a score can't catch.

> "'Good enough to ship' can't be the agent's opinion — it has to be a number
> that clears a gate you can defend."

This is the take-home from the free Maven lightning lesson **"A Content Pipeline
That Won't Ship Junk."** Once your agent can *publish*, "looked good" stops being
a vibe and becomes a liability — because the thing that judged the output is the
same model that wrote it. This harness makes "done" a number, not a mood.

## What it is

~70 lines of Python, no dependencies. You bring a `Scorer` (any callable that
returns per-dimension scores); the harness rolls them up, compares to a
threshold, and returns one of three decisions:

- **ACCEPT** — the score clears the pass mark. Ship it (optionally behind a human-gate).
- **ITERATE** — close; revise the weak spots and re-score.
- **REGENERATE** — too far off to polish; start fresh.

Deny-by-default: anything not clearly ACCEPT is held back. The loop is bounded by
`max_iterations` — on the cap without an ACCEPT, it **parks** (never force-ships).

## Quick start

```bash
# run the demo (scores a flawed draft, iterates it to a pass)
python demo.py

# run the tests (3 pass: the three-way decision, iterate→accept, cap→park)
python -m pytest test_scored_gate.py -q
```

## Files

| File | What it is |
|------|-----------|
| `scored_gate.py` | the harness (decide + run_gate + the cap/park + human-gate hook) |
| `toy_rubric.py` | a **toy** 2-dimension scorer (`clarity`, `completeness`) so it runs out of the box |
| `sample_draft.md` | a flawed draft that scores ~60.9 → ITERATE |
| `test_scored_gate.py` | proves the branch + the cap |
| `demo.py` | runs the gate on the sample draft and prints the decision trail |

## How to use it on your own workflow

1. Write a real `Scorer` — start with 2–3 dimensions you can define crisply; roll them into one `overall`.
2. Set a `pass_mark` you'd defend to a stakeholder, and a `regen_floor` below which polishing is wasted.
3. Wire `reviser` (targeted revision using the per-dimension breakdown) and `generator` (a fresh attempt).
4. Keep `max_iterations` small — the cap is what stops runaway cost and metric-gaming.
5. Add a `human_gate` for high-stakes outputs.

## The honest limit

This is a **behavioral** gate — a model scoring output against a rubric. It's only
trustworthy because the rubric is **explicit, versioned, and enforced** — not
because the model has good taste. For anything that must be mechanically
un-gameable (like stopping an irreversible command), you'd use a hard block, not
a score — a different tool for a different job.

## What this deliberately does NOT include

The **rubric here is a deliberate toy** — two made-up dimensions and an arbitrary
pass mark. The reusable value is the loop around it, not the rubric. A rubric
you'd trust in production is months of tuning: watching each naive version get
*gamed* by the loop, and re-tuning until the number actually tracks quality. That
tuning is the skill — and it's what the paid cohort builds, on your own content.

## License

**Source-available, no-resale — NOT MIT.** Use/modify/deploy it anywhere,
including in your own commercial products; you may **not** resell it as a
standalone product or bundle it into a competing paid course. See [`LICENSE`](LICENSE).

© 2026 Sathyan Nandagopal ([sathyan.ai](https://sathyan.ai)) · the full free
lesson series: <https://maven.com/sathyan-nandagopal>

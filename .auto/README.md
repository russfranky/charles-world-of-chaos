# Autoresearch session (pi-autoresearch pattern)

This folder implements the [pi-autoresearch](https://github.com/davebcn87/pi-autoresearch) experiment loop for **Brindal & Grayson Cow World**:

> Try an idea → measure → keep what works → revert regressions → repeat.

## Files

| File | Purpose |
|------|---------|
| `prompt.md` | Living playbook — goal, metrics, scope, what's been tried |
| `measure.sh` | Benchmark — outputs `METRIC name=value` lines |
| `checks.sh` | Backpressure — validation, barn sim, mob approvals (must pass to **keep**) |
| `config.json` | Optional caps (`maxIterations`) |
| `log.jsonl` | Append-only experiment log (gitignored — local/CI sessions) |
| `hooks/before.sh` | Anti-thrash steer after consecutive discards |
| `hooks/after.sh` | Append human-readable learnings journal |

## Quick start (terminal)

```bash
# Baseline
./.auto/measure.sh
./.auto/checks.sh

# After a change, measure again and log manually:
python3 scripts/autoresearch/log_experiment.py \
  --metric 713 --status keep --description "smaller PNG palette"

# Summary + MAD confidence (≥2.0× = likely real improvement)
python3 scripts/autoresearch/summarize.py
```

## With pi + pi-autoresearch

```bash
pi install npm:pi-autoresearch
/skill:autoresearch-create
```

Point the skill at this repo — it will reuse `.auto/prompt.md` and `.auto/measure.sh`.

## Primary metric

**`mcaddon_kb`** (lower is better) — shipped `.mcaddon` size on lite overlay build.

Secondary: `build_sec`, `texture_count`, `barn_sim_ok`, `validate_ok`.

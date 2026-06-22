# Testing — Cel Band Pack

## Automated

| Check | Command |
|-------|---------|
| Assemble pack | `./scripts/build_pack.sh` |
| Validate | `python3 scripts/validate_pack.py` |
| Full QA registry | `python3 qa/run_qa_suite.py` |

CI uploads `dist/Cel_Band_Pack.mcpack` on every PR.

## Manual

1. Import `dist/Cel_Band_Pack.mcpack`.
2. Activate under global resources.
3. Confirm cel-band blocks, relic blocks, and pack metadata in-game.

## Local

```bash
./scripts/build_pack.sh
python3 scripts/validate_pack.py
python3 variants/cel-band/scripts/convert_level.py --level variants/cel-band/levels/sample_level.json
```

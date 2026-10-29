# STATUS

## What was built

A local-first Python CLI for FFXIV players: `ffxiv_duty.py`. It logs duty and
trial completions, tracks weekly lockouts and caps (weekly reset on Tuesdays
UTC), and helps plan which duties are still available this week. Data lives in
plain JSON under `data/` (`data/duties.json` registry, `data/duty_log.json`
log) and can be exported to JSON or CSV. No game assets, no network access, no
secrets or personal data.

Commands:
- `log DUTY_ID [--at ISO]` — log a completion
- `list [--duty ID] [--limit N]` — list completions
- `lockouts [--at ISO]` — per-duty lockout status
- `caps [--at ISO]` — weekly cap progress
- `plan [--at ISO]` — duties not yet capped this week
- `export FILE.json|FILE.csv` — export the log

Tests: `tests/test_lockouts.py` (11 tests) covering weekly windows, caps, lock
status, and remaining counts.

Licensed under MIT, Copyright (c) 2026 Asdale Dynamics, LLC. Fan project
credited to Asdale Dynamics, LLC in the README; not affiliated with Square Enix.

## How to run

Requires Python 3.8+, no external packages.

```
python3 ffxiv_duty.py --help
python3 ffxiv_duty.py lockouts
python3 ffxiv_duty.py log raid_savage_t1 --at 2026-10-27T10:00:00+00:00
python3 ffxiv_duty.py plan
python3 ffxiv_duty.py export my_duties.csv
```

Data directory can be overridden with `FFXIV_DUTY_DATA_DIR`.

## Verification results

- `python3 -m pytest tests/`: 11 passed
- CLI smoke test: all six commands (`lockouts`, `log`, `list`, `caps`, `plan`,
  `export` to both `.json` and `.csv`) ran successfully; invalid export
  extension exits with an error
- Post-commit `git status` is clean

## Known gaps

- Weekly reset is modeled as Tuesday 00:00 UTC; real FFXIV reset times vary by
  datacenter/region
- Duty registry (`data/duties.json`) is a small starter list, not a complete
  duty database
- No recurring reminders, notifications, or sync across devices
- Timestamps without timezone are treated as UTC

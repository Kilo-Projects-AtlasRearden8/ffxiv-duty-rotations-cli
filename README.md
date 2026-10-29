# FFXIV Duty & Trial Log

A local-first Python CLI for FFXIV players to log duty and trial completions,
track weekly lockouts and caps, and plan the week ahead. Data stays on your
machine in plain JSON, and you can export it to CSV or JSON whenever you like.

No game assets, no network access, no accounts, no secrets. Just a small tool
to help you keep track of your weekly rhythm in Eorzea.

## Who this is for

FFXIV players who want a simple, private way to remember which duties they ran
this week, which are locked out, and what's still available before the weekly
reset. Built to be beginner-friendly: plain commands, no setup beyond Python.

## Credit

Created by **Asdale Dynamics, LLC** (Indiana, formed October 2026) — a fan
project for the FFXIV community. Asdale Dynamics publishes beginner-friendly AI
education, small-business tools, and occasional fun extras like gaming tools.
Learn more at https://dylanasdale.github.io

This is an unofficial fan project. It is not affiliated with or endorsed by
Square Enix or the Final Fantasy XIV team. No game assets are included.

## Features

- Log duty and trial completions with a timestamp (`log`)
- View your completion history (`list`)
- See weekly lockout status for every duty (`lockouts`)
- Track weekly cap progress (`caps`)
- Plan which duties are still available this week (`plan`)
- Export your log to JSON or CSV (`export`)
- Everything stored locally in `data/` as plain JSON; no external services

## Requirements

Python 3.8 or later. No external packages.

## Install

There is nothing to install. Run the module directly:

```
python3 ffxiv_duty.py --help
```

## Quick start

```
# See lockout status for all duties (weekly resets Tuesdays UTC)
python3 ffxiv_duty.py lockouts

# Log a completion
python3 ffxiv_duty.py log raid_savage_t1 --at 2026-10-27T10:00:00+00:00

# See what's still available this week
python3 ffxiv_duty.py plan

# Export your log
python3 ffxiv_duty.py export my_duties.csv
```

## Commands

- `log DUTY_ID [--at ISO]` — log a completion (defaults to now)
- `list [--duty ID] [--limit N]` — list completions, newest first
- `lockouts [--at ISO]` — lockout status for every registered duty
- `caps [--at ISO]` — weekly cap usage per duty
- `plan [--at ISO]` — duties not yet capped this week
- `export FILE.json|FILE.csv` — export the full log

## Data

The tool creates a `data/` folder next to the script:

- `data/duties.json` — duty registry with names, categories, and weekly caps
- `data/duty_log.json` — your completion log (created when you first log)

You can edit `data/duties.json` to add or change duties. Point
`FFXIV_DUTY_DATA_DIR` at another folder to store data elsewhere.

## Tests

```
python3 -m pytest
```

Tests cover the lockout math: weekly windows, caps, lock status, and remaining
counts.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

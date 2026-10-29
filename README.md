# FFXIV Duty & Trial Log

A friendly, local-first Python command line tool for Final Fantasy XIV players.
Log your duty and trial completions, keep track of weekly lockouts and caps, and
plan what's still available before the weekly reset — all on your own computer,
with nothing sent anywhere.

## Who this is for

This is for FFXIV players who want a simple, private way to remember:

- Which duties and trials they ran this week
- Which ones are locked out because they hit the weekly cap
- What's still open to run before reset on Tuesday

It's built to be beginner-friendly: plain commands, no accounts, no setup
beyond having Python on your computer. If you can type a command, you can use
this tool.

## Credit

Created by **Asdale Dynamics, LLC** (Indiana, formed October 2026) — a fan
project for the FFXIV community. Asdale Dynamics publishes beginner-friendly AI
education, small-business tools, and occasional fun extras like gaming tools.
Learn more at https://dylanasdale.github.io

This is an unofficial fan project. It is not affiliated with or endorsed by
Square Enix or the Final Fantasy XIV team. No game assets are included.

## Features

- **Log** a duty or trial completion with a timestamp
- **List** your completion history, newest first
- **Lockouts** — see lockout status for every duty (weekly cap reached or open)
- **Caps** — see how close you are to each weekly cap
- **Plan** — see which duties are still available this week
- **Export** your log to JSON or CSV so you can open it in a spreadsheet
- Everything stored locally in plain JSON files; no network, no accounts, no
  secrets

## Requirements

Python 3.8 or later. No external packages to install.

## Quick start

Run the tool straight from the folder:

```bash
python3 ffxiv_duty.py --help
```

See what's locked this week (weekly resets on Tuesdays UTC):

```bash
python3 ffxiv_duty.py lockouts
```

Log a completion:

```bash
python3 ffxiv_duty.py log raid_savage_t1 --at 2026-10-27T10:00:00+00:00
```

See what's still available to run:

```bash
python3 ffxiv_duty.py plan
```

Export your log to a spreadsheet-friendly CSV:

```bash
python3 ffxiv_duty.py export my_duties.csv
```

## Commands

| Command | What it does |
|---------|--------------|
| `log DUTY_ID [--at ISO]` | Log a completion (defaults to now) |
| `list [--duty ID] [--limit N]` | List completions, newest first |
| `lockouts [--at ISO]` | Lockout status for every registered duty |
| `caps [--at ISO]` | Weekly cap usage per duty |
| `plan [--at ISO]` | Duties not yet capped this week |
| `export FILE.json\|FILE.csv` | Export the full log |
| `--version` | Show the version number |

## Data

The tool creates a `data/` folder next to the script:

- `data/duties.json` — the duty registry (names, categories, weekly caps). You
  can edit this to add or change duties.
- `data/duty_log.json` — your completion log, created the first time you log a
  completion.

To store your data somewhere else, set the `FFXIV_DUTY_DATA_DIR` environment
variable to the folder you want.

## Tests

The lockout math is covered by automated tests:

```bash
python3 -m pytest
```

Tests check weekly windows, caps, lock status, and remaining counts.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

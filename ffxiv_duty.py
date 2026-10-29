#!/usr/bin/env python3
"""FFXIV Duty & Trial Log.

A local-first command line tool for FFXIV players to log duty and trial
completions, track weekly lockouts and caps, and plan the week ahead.
Data is stored in local JSON files and can be exported to CSV.

No game assets, no network access, no secrets.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# FFXIV weekly reset day: Tuesday (1 = Monday ... 6 = Sunday in ISO weekday).
RESET_WEEKDAY = 1

DEFAULT_REGISTRY = {
    "duties": [
        {"id": "dungeon_leveling_01", "name": "Stone Vigil", "category": "dungeon", "weekly_cap": None},
        {"id": "dungeon_leveling_02", "name": "Brayflox's Longstop", "category": "dungeon", "weekly_cap": None},
        {"id": "trial_ifrit", "name": "Trial: Ifrit", "category": "trial", "weekly_cap": None},
        {"id": "trial_titan", "name": "Trial: Titan", "category": "trial", "weekly_cap": None},
        {"id": "raid_coil_bahamut", "name": "The Binding Coil of Bahamut", "category": "raid", "weekly_cap": 1},
        {"id": "raid_turn_bahamut", "name": "The Final Steps of Bahamut", "category": "raid", "weekly_cap": 1},
        {"id": "raid_savage_01", "name": "Savage Raid: Tier 1", "category": "raid", "weekly_cap": 1},
        {"id": "raid_ultimate_01", "name": "Ultimate Raid: Tier 1", "category": "raid", "weekly_cap": 1},
        {"id": "dungeon_mythic_01", "name": "Mythic Dungeon: Tier 1", "category": "dungeon", "weekly_cap": 3},
    ]
}


def data_dir() -> Path:
    env = os.environ.get("FFXIV_DUTY_DATA_DIR")
    if env:
        return Path(env)
    return Path("data")


def registry_path() -> Path:
    return data_dir() / "duties.json"


def log_path() -> Path:
    return data_dir() / "duty_log.json"


def parse_timestamp(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def reset_weekday_name() -> str:
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][RESET_WEEKDAY]


def week_start(dt: datetime) -> datetime:
    """Return the most recent weekly reset (Tuesday 00:00 UTC) at or before dt."""
    base = dt.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    days_back = (base.weekday() - RESET_WEEKDAY) % 7
    return base - timedelta(days=days_back)


def next_reset(dt: datetime) -> datetime:
    """Return the next weekly reset strictly after dt."""
    start = week_start(dt)
    candidate = start + timedelta(days=7)
    while candidate <= dt:
        candidate += timedelta(days=7)
    return candidate


def load_json(path: Path, default):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as exc:
        print(f"warning: corrupt JSON in {path}: {exc}", file=sys.stderr)
        return default


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(value, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load_registry() -> dict:
    return load_json(registry_path(), DEFAULT_REGISTRY)


def save_registry(registry: dict) -> None:
    save_json(registry_path(), registry)


def load_log() -> list:
    return load_json(log_path(), [])


def save_log(entries: list) -> None:
    save_json(log_path(), entries)


def duty_by_id(registry: dict, duty_id: str):
    for duty in registry.get("duties", []):
        if duty.get("id") == duty_id:
            return duty
    return None


def weekly_completions(duty_id: str, entries: list, start: datetime) -> int:
    """Count completions of duty_id in the weekly window [start, start+7d)."""
    end = start + timedelta(days=7)
    count = 0
    for entry in entries:
        if entry.get("duty_id") != duty_id:
            continue
        try:
            occurred = parse_timestamp(entry.get("at", ""))
        except (ValueError, TypeError):
            continue
        if start <= occurred < end:
            count += 1
    return count


def is_locked(duty_id: str, entries: list, now: datetime | None = None) -> bool:
    """True if the duty's weekly cap has been reached in the current week."""
    if now is None:
        now = now_utc()
    duty = duty_by_id(load_registry(), duty_id)
    if duty is None:
        return False
    cap = duty.get("weekly_cap")
    if cap is None:
        return False
    return weekly_completions(duty_id, entries, week_start(now)) >= cap


def remaining(duty_id: str, entries: list, now: datetime | None = None) -> int | None:
    """Remaining completions allowed this week, or None if uncapped."""
    if now is None:
        now = now_utc()
    duty = duty_by_id(load_registry(), duty_id)
    if duty is None:
        return None
    cap = duty.get("weekly_cap")
    if cap is None:
        return None
    used = weekly_completions(duty_id, entries, week_start(now))
    return max(0, cap - used)


def lockout_status(duty_id: str, entries: list, now: datetime | None = None) -> dict:
    if now is None:
        now = now_utc()
    duty = duty_by_id(load_registry(), duty_id)
    if duty is None:
        return {"duty_id": duty_id, "name": duty_id, "category": "unknown", "locked": False, "used": 0, "cap": None, "remaining": None, "resets_at": next_reset(now).isoformat()}
    cap = duty.get("weekly_cap")
    used = weekly_completions(duty_id, entries, week_start(now))
    rem = None if cap is None else max(0, cap - used)
    return {
        "duty_id": duty_id,
        "name": duty.get("name", duty_id),
        "category": duty.get("category", "unknown"),
        "locked": (cap is not None and used >= cap),
        "used": used,
        "cap": cap,
        "remaining": rem,
        "resets_at": next_reset(now).isoformat(),
    }


def cmd_log(args) -> int:
    entries = load_log()
    occurred = parse_timestamp(args.at) if args.at else now_utc()
    entries.append({"duty_id": args.duty, "at": occurred.isoformat()})
    save_log(entries)
    duty = duty_by_id(load_registry(), args.duty)
    name = duty.get("name", args.duty) if duty else args.duty
    print(f"Logged {name} ({args.duty}) at {occurred.isoformat()}")
    return 0


def cmd_list(args) -> int:
    entries = load_log()
    if args.duty:
        entries = [e for e in entries if e.get("duty_id") == args.duty]
    entries = sorted(entries, key=lambda e: e.get("at", ""), reverse=True)
    if args.limit is not None:
        entries = entries[: args.limit]
    if not entries:
        print("No completions logged.")
        return 0
    print(f"{'DUTY ID':<30} {'AT (UTC)':<28}")
    print("-" * 60)
    for entry in entries:
        print(f"{entry.get('duty_id',''):<30} {entry.get('at',''):<28}")
    return 0


def cmd_lockouts(args) -> int:
    now = parse_timestamp(args.at) if args.at else now_utc()
    entries = load_log()
    registry = load_registry()
    print(f"Weekly reset: {reset_weekday_name()}s. Next reset: {next_reset(now).isoformat()}")
    print(f"{'DUTY ID':<30} {'NAME':<34} {'CAT':<10} {'USED':<5} {'CAP':<5} {'LEFT':<6} {'STATUS'}")
    print("-" * 100)
    for duty in registry.get("duties", []):
        status = lockout_status(duty["id"], entries, now)
        left = "unlimited" if status["remaining"] is None else str(status["remaining"])
        cap = "-" if status["cap"] is None else str(status["cap"])
        status_text = "LOCKED" if status["locked"] else "open"
        print(f"{status['duty_id']:<30} {status['name']:<34} {status['category']:<10} {status['used']:<5} {cap:<5} {left:<6} {status_text}")
    return 0


def cmd_caps(args) -> int:
    now = parse_timestamp(args.at) if args.at else now_utc()
    entries = load_log()
    registry = load_registry()
    start = week_start(now)
    print(f"Week starting {start.date()} (resets {reset_weekday_name()}s)")
    print(f"{'DUTY ID':<30} {'NAME':<34} {'USED/CAP':<12} {'PCT':<6}")
    print("-" * 84)
    for duty in registry.get("duties", []):
        duty_id = duty["id"]
        used = weekly_completions(duty_id, entries, start)
        cap = duty.get("weekly_cap")
        if cap is None:
            used_cap = f"{used}/\u221e"
            pct = "-"
        else:
            used_cap = f"{used}/{cap}"
            pct = f"{int(round(100 * used / cap))}%" if cap else "-"
        print(f"{duty_id:<30} {duty.get('name', duty_id):<34} {used_cap:<12} {pct:<6}")
    return 0


def cmd_plan(args) -> int:
    now = parse_timestamp(args.at) if args.at else now_utc()
    entries = load_log()
    registry = load_registry()
    print(f"Plan for week resetting {reset_weekday_name()} {next_reset(now).date()} (UTC)")
    print("Duties available this week (not yet at weekly cap):")
    print(f"{'DUTY ID':<30} {'NAME':<34} {'CAT':<10} {'LEFT'}")
    print("-" * 84)
    anything = False
    for duty in registry.get("duties", []):
        status = lockout_status(duty["id"], entries, now)
        if status["locked"]:
            continue
        anything = True
        left = "unlimited" if status["remaining"] is None else str(status["remaining"])
        print(f"{status['duty_id']:<30} {status['name']:<34} {status['category']:<10} {left}")
    if not anything:
        print("  (nothing available -- everything capped this week)")
    return 0


def cmd_export(args) -> int:
    entries = load_log()
    out_path = Path(args.path)
    suffix = out_path.suffix.lower()
    if suffix == ".json":
        save_json(out_path, entries)
        print(f"Exported {len(entries)} entries to {out_path}")
    elif suffix == ".csv":
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["duty_id", "at_utc"])
            for entry in entries:
                writer.writerow([entry.get("duty_id", ""), entry.get("at", "")])
        print(f"Exported {len(entries)} entries to {out_path}")
    else:
        print("error: export path must end in .json or .csv", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ffxiv_duty", description="Log FFXIV duty and trial completions, track lockouts and weekly caps.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_log = sub.add_parser("log", help="Log a duty or trial completion")
    p_log.add_argument("duty", help="Duty ID (see lockouts/caps/plan)")
    p_log.add_argument("--at", help="Completion time in ISO-8601 (default: now)")
    p_log.set_defaults(func=cmd_log)

    p_list = sub.add_parser("list", help="List logged completions")
    p_list.add_argument("--duty", help="Filter by duty ID")
    p_list.add_argument("--limit", type=int, help="Max entries to show")
    p_list.set_defaults(func=cmd_list)

    p_lockouts = sub.add_parser("lockouts", help="Show lockout status for all duties")
    p_lockouts.add_argument("--at", help="Evaluate as of this ISO-8601 time (default: now)")
    p_lockouts.set_defaults(func=cmd_lockouts)

    p_caps = sub.add_parser("caps", help="Show weekly cap progress")
    p_caps.add_argument("--at", help="Evaluate as of this ISO-8601 time (default: now)")
    p_caps.set_defaults(func=cmd_caps)

    p_plan = sub.add_parser("plan", help="Plan duties available this week")
    p_plan.add_argument("--at", help="Evaluate as of this ISO-8601 time (default: now)")
    p_plan.set_defaults(func=cmd_plan)

    p_export = sub.add_parser("export", help="Export the duty log to JSON or CSV")
    p_export.add_argument("path", help="Output file (.json or .csv)")
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

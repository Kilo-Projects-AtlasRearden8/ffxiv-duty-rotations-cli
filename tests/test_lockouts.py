"""Tests for lockout math in ffxiv_duty.py."""

from datetime import datetime, timedelta, timezone

import ffxiv_duty


def test_week_start_is_tuesday_midnight_utc():
    dt = datetime(2026, 10, 28, 15, 30, tzinfo=timezone.utc)  # Wednesday
    start = ffxiv_duty.week_start(dt)
    assert start == datetime(2026, 10, 27, 0, 0, tzinfo=timezone.utc)
    assert start.weekday() == 1  # Tuesday


def test_week_start_before_reset_uses_previous_tuesday():
    dt = datetime(2026, 10, 27, 1, 0, tzinfo=timezone.utc)  # Tuesday, after reset
    start = ffxiv_duty.week_start(dt)
    assert start == datetime(2026, 10, 27, 0, 0, tzinfo=timezone.utc)


def test_next_reset_is_strictly_after_now_and_tuesday():
    dt = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)  # Tuesday midday
    nxt = ffxiv_duty.next_reset(dt)
    assert nxt > dt
    assert nxt.weekday() == 1
    assert nxt.hour == 0


def test_weekly_completions_counts_only_current_window():
    start = datetime(2026, 10, 27, 0, 0, tzinfo=timezone.utc)
    entries = [
        {"duty_id": "raid_savage_t1", "at": "2026-10-27T10:00:00+00:00"},
        {"duty_id": "raid_savage_t1", "at": "2026-10-30T10:00:00+00:00"},
        {"duty_id": "raid_savage_t1", "at": "2026-11-03T10:00:00+00:00"},  # next week
        {"duty_id": "raid_ultimate_t1", "at": "2026-10-28T10:00:00+00:00"},  # other duty
    ]
    assert ffxiv_duty.weekly_completions("raid_savage_t1", entries, start) == 2


def test_is_locked_false_under_cap():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    entries = [
        {"duty_id": "dungeon_mythic_t1", "at": "2026-10-28T10:00:00+00:00"},
    ]
    assert ffxiv_duty.is_locked("dungeon_mythic_t1", entries, now) is False


def test_is_locked_true_at_cap():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    entries = [
        {"duty_id": "raid_savage_t1", "at": "2026-10-27T10:00:00+00:00"},
    ]
    assert ffxiv_duty.is_locked("raid_savage_t1", entries, now) is True


def test_is_locked_true_over_cap():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    entries = [
        {"duty_id": "dungeon_mythic_t1", "at": "2026-10-27T10:00:00+00:00"},
        {"duty_id": "dungeon_mythic_t1", "at": "2026-10-28T08:00:00+00:00"},
        {"duty_id": "dungeon_mythic_t1", "at": "2026-10-28T10:00:00+00:00"},
    ]
    assert ffxiv_duty.is_locked("dungeon_mythic_t1", entries, now) is True


def test_remaining_decrements_to_zero():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    entries = [
        {"duty_id": "dungeon_mythic_t1", "at": "2026-10-27T10:00:00+00:00"},
        {"duty_id": "dungeon_mythic_t1", "at": "2026-10-28T08:00:00+00:00"},
        {"duty_id": "dungeon_mythic_t1", "at": "2026-10-28T10:00:00+00:00"},
    ]
    assert ffxiv_duty.remaining("dungeon_mythic_t1", entries, now) == 0


def test_remaining_none_for_uncapped_duty():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    entries = []
    assert ffxiv_duty.remaining("trial_ifrit", entries, now) is None


def test_lockout_status_shape():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    entries = [
        {"duty_id": "raid_savage_t1", "at": "2026-10-27T10:00:00+00:00"},
    ]
    status = ffxiv_duty.lockout_status("raid_savage_t1", entries, now)
    assert status["locked"] is True
    assert status["used"] == 1
    assert status["cap"] == 1
    assert status["remaining"] == 0
    assert status["category"] == "raid"
    assert status["resets_at"].endswith("+00:00")


def test_unknown_duty_not_locked():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    assert ffxiv_duty.is_locked("nonexistent_duty", [], now) is False
    assert ffxiv_duty.remaining("nonexistent_duty", [], now) is None

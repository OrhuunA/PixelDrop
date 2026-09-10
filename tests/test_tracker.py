"""core.tracker.roll_day icin testler (gun donumu, seri, gecmis budama).

`today` her zaman parametre olarak verildigi icin gece yarisini beklemeye
gerek yok - bkz. pixeldropyolharitasi.md, bolum 4.2."""

from datetime import date

from pixeldrop.core.tracker import HISTORY_DAYS_KEPT, roll_day


def _cfg(**overrides):
    base = {
        "drank_today": 0,
        "daily_goal": 8,
        "last_reset_date": "2026-01-01",
        "streak": 0,
        "history": {},
    }
    base.update(overrides)
    return base


def test_same_day_is_a_no_op():
    cfg = _cfg(last_reset_date="2026-01-01")
    result = roll_day(cfg, date(2026, 1, 1))
    assert result is cfg


def test_next_day_goal_met_increments_streak():
    cfg = _cfg(last_reset_date="2026-01-01", drank_today=8, daily_goal=8, streak=3)
    result = roll_day(cfg, date(2026, 1, 2))
    assert result["streak"] == 4
    assert result["drank_today"] == 0
    assert result["last_reset_date"] == "2026-01-02"
    assert result["history"]["2026-01-01"] == 8


def test_next_day_goal_exceeded_still_increments_streak():
    cfg = _cfg(last_reset_date="2026-01-01", drank_today=12, daily_goal=8, streak=1)
    result = roll_day(cfg, date(2026, 1, 2))
    assert result["streak"] == 2


def test_next_day_goal_missed_resets_streak():
    cfg = _cfg(last_reset_date="2026-01-01", drank_today=3, daily_goal=8, streak=5)
    result = roll_day(cfg, date(2026, 1, 2))
    assert result["streak"] == 0
    assert result["history"]["2026-01-01"] == 3


def test_skipped_day_resets_streak_even_if_goal_was_met():
    # Uygulama iki gun boyunca hic acilmadi; aradaki gun kaydedilmemis
    # olsa da atlanan gun oldugu icin seri sifirlanmali.
    cfg = _cfg(last_reset_date="2026-01-01", drank_today=8, daily_goal=8, streak=5)
    result = roll_day(cfg, date(2026, 1, 3))
    assert result["streak"] == 0


def test_history_pruned_to_max_days_kept():
    history = {f"2025-12-{d:02d}": 8 for d in range(1, 15)}  # 14 gun
    assert len(history) == HISTORY_DAYS_KEPT
    cfg = _cfg(last_reset_date="2025-12-31", drank_today=5, history=history)
    result = roll_day(cfg, date(2026, 1, 1))
    assert len(result["history"]) == HISTORY_DAYS_KEPT
    assert "2025-12-01" not in result["history"]  # en eski budandi
    assert result["history"]["2025-12-31"] == 5


def test_missing_last_reset_date_treated_as_today():
    cfg = _cfg(last_reset_date=None)
    today = date(2026, 3, 15)
    result = roll_day(cfg, today)
    assert result is cfg


def test_corrupted_last_reset_date_does_not_crash():
    cfg = _cfg(last_reset_date="bozuk-tarih", drank_today=8, daily_goal=8, streak=2)
    result = roll_day(cfg, date(2026, 1, 2))
    # Tarih parse edilemeyince gap_days=1 varsayilir, normal bir gunluk
    # gecis gibi islenir - uygulama comez, seri mantigi calisir.
    assert result["streak"] == 3
    assert result["drank_today"] == 0


def test_roll_day_does_not_mutate_input():
    original_history = {"2026-01-01": 4}
    cfg = _cfg(last_reset_date="2026-01-01", drank_today=4, history=original_history)
    roll_day(cfg, date(2026, 1, 2))
    assert cfg["drank_today"] == 4
    assert cfg["history"] is original_history
    assert original_history == {"2026-01-01": 4}

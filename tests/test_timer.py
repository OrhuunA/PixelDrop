"""core.timer icin testler (susama orani ve widget durumu)."""

import pytest

from pixeldrop.core.timer import current_fraction, state_for_fraction


def test_fraction_at_start_is_zero():
    now = 1_000_000.0
    interval_minutes = 45
    next_at = now + interval_minutes * 60
    assert current_fraction(next_at, interval_minutes, now) == pytest.approx(0.0)


def test_fraction_halfway():
    now = 1_000_000.0
    interval_minutes = 60
    next_at = now + interval_minutes * 60
    halfway = now + interval_minutes * 60 / 2
    assert current_fraction(next_at, interval_minutes, halfway) == pytest.approx(0.5)


def test_fraction_overdue_can_exceed_one():
    now = 1_000_000.0
    interval_minutes = 30
    next_at = now - 15 * 60  # 15 dakika once gecmis olmasi gerekiyordu
    fraction = current_fraction(next_at, interval_minutes, now)
    assert fraction > 1.0


def test_fraction_never_negative():
    now = 1_000_000.0
    interval_minutes = 45
    next_at = now + 999999  # cok uzak gelecek
    assert current_fraction(next_at, interval_minutes, now) == pytest.approx(0.0)


def test_paused_always_wins_regardless_of_fraction():
    assert state_for_fraction(0.0, paused=True) == "paused"
    assert state_for_fraction(1.5, paused=True) == "paused"


@pytest.mark.parametrize(
    "fraction, expected",
    [
        (0.0, "happy"),
        (0.49, "happy"),
        (0.5, "neutral"),
        (0.79, "neutral"),
        (0.8, "thirsty"),
        (0.99, "thirsty"),
        (1.0, "urgent"),
        (2.0, "urgent"),
    ],
)
def test_state_thresholds(fraction, expected):
    assert state_for_fraction(fraction, paused=False) == expected

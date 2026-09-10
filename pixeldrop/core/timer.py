"""Hatirlatma zamanlamasi ve erteleme - saf fonksiyonlar (bkz. core.tracker
icin ayni gerekce: `now`/zaman hep parametre olarak alinir)."""

SNOOZE_MINUTES = 5
AUTO_PAUSE_IDLE_MINUTES = 10


def current_fraction(next_at, interval_minutes, now):
    """0..1+ arasi "susama orani": `next_at` zamanina ne kadar
    yaklasildigini `interval_minutes` uzunlugundaki pencereye oranlar."""
    total = max(1, interval_minutes * 60)
    remaining = next_at - now
    elapsed = total - remaining
    return max(0.0, elapsed / total)


def state_for_fraction(fraction, paused):
    if paused:
        return "paused"
    if fraction < 0.5:
        return "happy"
    if fraction < 0.8:
        return "neutral"
    if fraction < 1.0:
        return "thirsty"
    return "urgent"

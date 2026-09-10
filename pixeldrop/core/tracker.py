"""Gunluk sayac, hedef, seri (streak) ve gecmis - saf fonksiyonlar.

Bu modul bilerek `datetime.now()`/`date.today()` cagirmaz: "bugun" hep
disaridan parametre olarak alinir, boylece gun donumu/seri mantigi gece
yarisini beklemeden pytest ile test edilebilir (bkz.
pixeldropyolharitasi.md, bolum 4)."""

from datetime import date

HISTORY_DAYS_KEPT = 14


def roll_day(cfg, today):
    """`cfg`'nin gun donumu uygulanmis YENI bir kopyasini dondurur.

    `today` (bir `datetime.date`) ile `cfg["last_reset_date"]` ayniysa
    hicbir sey yapmadan ayni `cfg` referansini dondurur (cagiran taraf
    bunu "degisiklik yok, kaydetme" sinyali olarak kullanabilir).

    Farkliysa: onceki gunun sayacini `history`'ye yazar (14 gunden
    fazlasi varsa en eskisini budar), tam olarak bir gun once hedefe
    ulasilmissa seriyi bir arttirir, aksi halde (hedef tutmadi ya da
    uygulama bir ya da daha fazla gun hic acilmadi) seriyi sifirlar, ve
    gunluk sayaci sifirlayip `last_reset_date`'i gunceller."""
    today_str = str(today)
    last_str = cfg.get("last_reset_date") or today_str
    if last_str == today_str:
        return cfg

    new_cfg = dict(cfg)

    try:
        last_dt = date.fromisoformat(last_str)
        gap_days = (today - last_dt).days
    except Exception:
        gap_days = 1

    prev_count = cfg.get("drank_today", 0)
    goal = cfg.get("daily_goal", 8)

    history = dict(cfg.get("history", {}))
    history[last_str] = prev_count
    if len(history) > HISTORY_DAYS_KEPT:
        for k in sorted(history.keys())[:-HISTORY_DAYS_KEPT]:
            del history[k]
    new_cfg["history"] = history

    if gap_days == 1 and prev_count >= goal:
        new_cfg["streak"] = cfg.get("streak", 0) + 1
    else:
        # bir gun atlandi (uygulama kapaliyken) ya da hedefe ulasilamadi
        new_cfg["streak"] = 0

    new_cfg["drank_today"] = 0
    new_cfg["last_reset_date"] = today_str
    return new_cfg

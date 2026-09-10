"""config.py icin testler: varsayilanlar, bozuk config'ten kurtarma,
eski (SuIcmeHatirlatici) klasorden goc."""

import json
import os

import pytest

import pixeldrop.config as config


@pytest.fixture
def isolated_appdata(tmp_path, monkeypatch):
    """Her testte config.py'nin gercekten kullanicinin %APPDATA%'sina
    dokunmamasi icin gecici bir klasoru APPDATA olarak ayarlar.
    config_path()/_old_config_path() APPDATA'yi her cagrida os.getenv ile
    tazeden okudugu icin modulu yeniden yuklemeye gerek yok."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    yield tmp_path


def test_load_config_defaults_when_no_file(isolated_appdata):
    cfg = config.load_config()
    assert cfg["interval_minutes"] == config.DEFAULT_CONFIG["interval_minutes"]
    assert cfg["daily_goal"] == 8
    assert cfg["history"] == {}


def test_save_then_load_roundtrip(isolated_appdata):
    cfg = config.load_config()
    cfg["daily_goal"] = 12
    cfg["drank_today"] = 3
    config.save_config(cfg)

    reloaded = config.load_config()
    assert reloaded["daily_goal"] == 12
    assert reloaded["drank_today"] == 3


def test_corrupted_config_falls_back_to_defaults(isolated_appdata):
    path = config.config_path()
    with open(path, "w", encoding="utf-8") as f:
        f.write("{ bu gecerli json degil ]")

    cfg = config.load_config()  # comemeli
    assert cfg["daily_goal"] == config.DEFAULT_CONFIG["daily_goal"]


def test_partial_config_is_layered_over_defaults(isolated_appdata):
    path = config.config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"daily_goal": 15}, f)

    cfg = config.load_config()
    assert cfg["daily_goal"] == 15
    # eksik alanlar varsayilanlardan geliyor
    assert cfg["interval_minutes"] == config.DEFAULT_CONFIG["interval_minutes"]


def test_migration_copies_old_config_once(isolated_appdata, monkeypatch):
    old_dir = os.path.join(str(isolated_appdata), config.OLD_APP_NAME)
    os.makedirs(old_dir, exist_ok=True)
    old_data = {"daily_goal": 10, "streak": 7, "drank_today": 2}
    with open(os.path.join(old_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(old_data, f)

    cfg = config.load_config()
    assert cfg["daily_goal"] == 10
    assert cfg["streak"] == 7


def test_migration_does_not_overwrite_existing_new_config(isolated_appdata):
    # Yeni config zaten var - eski klasor olsa bile ustune yazilmamali.
    new_path = config.config_path()
    with open(new_path, "w", encoding="utf-8") as f:
        json.dump({"daily_goal": 4}, f)

    old_dir = os.path.join(str(isolated_appdata), config.OLD_APP_NAME)
    os.makedirs(old_dir, exist_ok=True)
    with open(os.path.join(old_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump({"daily_goal": 99}, f)

    cfg = config.load_config()
    assert cfg["daily_goal"] == 4

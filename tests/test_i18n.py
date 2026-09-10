"""i18n.tr_text icin testler (bkz. pixeldrop/i18n/tr.json, en.json)."""

from pixeldrop.i18n import available_languages, tr_text


def test_available_languages_includes_tr_and_en():
    langs = available_languages()
    assert "tr" in langs
    assert "en" in langs


def test_default_language_is_turkish():
    cfg = {"language": "tr"}
    assert tr_text(cfg, "settings_close") == "Kapat"


def test_english_language_selection():
    cfg = {"language": "en"}
    assert tr_text(cfg, "settings_close") == "Close"


def test_format_kwargs_are_substituted():
    cfg = {"language": "tr"}
    assert tr_text(cfg, "tray_snooze", m=5) == "5 dk ertele"


def test_missing_key_falls_back_to_key_itself():
    cfg = {"language": "en"}
    assert tr_text(cfg, "this_key_does_not_exist") == "this_key_does_not_exist"


def test_missing_language_falls_back_to_turkish():
    cfg = {"language": "fr"}  # hic olmayan bir dil
    assert tr_text(cfg, "settings_close") == "Kapat"

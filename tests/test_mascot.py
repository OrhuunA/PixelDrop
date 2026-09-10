"""ui.mascot icin testler - sadece Pillow'a bagli, Windows gerektirmez."""

from pixeldrop.ui.mascot import cups_row_image, draw_character, rounded_bar_image


def test_draw_character_returns_requested_size():
    img = draw_character("happy", size=64)
    assert img.size == (64, 64)


def test_draw_character_unknown_state_falls_back_to_neutral():
    # PALETTES'te olmayan bir state verilirse comemeli, "neutral" gibi
    # davranmali.
    img = draw_character("bilinmeyen-durum", size=32)
    assert img.size == (32, 32)


def test_rounded_bar_image_has_requested_dimensions():
    img = rounded_bar_image(100, 8, 0.5, "#4fa8e8")
    assert img.size == (100, 8)


def test_cups_row_image_width_grows_with_extra_cups():
    base = cups_row_image(drank=4, goal=8, cup_w=9, cup_h=11, gap=2)
    with_extra = cups_row_image(drank=10, goal=8, cup_w=9, cup_h=11, gap=2)
    assert with_extra.width > base.width

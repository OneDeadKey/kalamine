from kalamine import KeyboardLayout

from .util import get_layout_dict


def load_layout(filename: str, angle_mod: bool = False) -> KeyboardLayout:
    return KeyboardLayout(get_layout_dict(filename), angle_mod)


def test_ansi():
    layout = load_layout("ansi")
    assert layout.layers[0]["ad01"] == "q"
    assert layout.layers[1]["ad01"] == "Q"
    assert layout.layers[0]["tlde"] == "`"
    assert layout.layers[1]["tlde"] == "~"
    assert not layout.has_altgr
    assert not layout.has_1dk
    assert "**" not in layout.dead_keys

    # ensure angle mod is NOT applied
    layout = load_layout("ansi", angle_mod=True)
    assert layout.layers[0]["ab01"] == "z"
    assert layout.layers[1]["ab01"] == "Z"


def test_prog():  # AltGr + dead keys
    layout = load_layout("prog")
    assert layout.layers[0]["ad01"] == "q"
    assert layout.layers[1]["ad01"] == "Q"
    assert layout.layers[0]["tlde"] == "`"
    assert layout.layers[1]["tlde"] == "~"
    assert layout.layers[4]["tlde"] == "*`"
    assert layout.layers[5]["tlde"] == "*~"
    assert layout.has_altgr
    assert not layout.has_1dk
    assert "**" not in layout.dead_keys
    assert len(layout.dead_keys["*`"]) == 18
    assert len(layout.dead_keys["*~"]) == 21


def test_intl():  # 1dk + dead keys
    layout = load_layout("intl")
    assert layout.layers[0]["ad01"] == "q"
    assert layout.layers[1]["ad01"] == "Q"
    assert layout.layers[0]["tlde"] == "*`"
    assert layout.layers[1]["tlde"] == "*~"
    assert not layout.has_altgr
    assert layout.has_1dk
    assert "**" in layout.dead_keys

    assert len(layout.dead_keys) == 5
    assert "**" in layout.dead_keys
    assert "*`" in layout.dead_keys
    assert "*^" in layout.dead_keys
    assert "*¨" in layout.dead_keys
    assert "*~" in layout.dead_keys
    assert len(layout.dead_keys["**"]) == 15
    assert len(layout.dead_keys["*`"]) == 18
    assert len(layout.dead_keys["*^"]) == 43
    assert len(layout.dead_keys["*¨"]) == 21
    assert len(layout.dead_keys["*~"]) == 21

    # ensure the 1dk parser does not accumulate values from a previous run
    layout = load_layout("intl")
    assert len(layout.dead_keys["*`"]) == 18
    assert len(layout.dead_keys["*~"]) == 21

    assert len(layout.dead_keys) == 5
    assert "**" in layout.dead_keys
    assert "*`" in layout.dead_keys
    assert "*^" in layout.dead_keys
    assert "*¨" in layout.dead_keys
    assert "*~" in layout.dead_keys
    assert len(layout.dead_keys["**"]) == 15
    assert len(layout.dead_keys["*`"]) == 18
    assert len(layout.dead_keys["*^"]) == 43
    assert len(layout.dead_keys["*¨"]) == 21
    assert len(layout.dead_keys["*~"]) == 21

    # ensure angle mod is working correctly
    layout = load_layout("intl", angle_mod=True)
    assert layout.layers[0]["lsgt"] == "z"
    assert layout.layers[1]["lsgt"] == "Z"
    assert layout.layers[0]["ab01"] == "x"
    assert layout.layers[1]["ab01"] == "X"

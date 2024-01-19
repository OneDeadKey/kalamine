import os

from kalamine import KeyboardLayout


def load_layout(filename):
    return KeyboardLayout(os.path.join(".", "layouts", filename + ".toml"))


def test_layouts():
    layout = load_layout("ansi")
    assert layout.layers[0]["ad01"] == "q"
    assert layout.layers[1]["ad01"] == "Q"
    assert layout.layers[0]["tlde"] == "`"
    assert layout.layers[1]["tlde"] == "~"
    assert not layout.has_altgr
    assert not layout.has_1dk
    assert "**" not in layout.dead_keys

    # AltGr + dead keys
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

    # 1dk + dead keys
    layout = load_layout("intl")
    assert layout.layers[0]["ad01"] == "q"
    assert layout.layers[1]["ad01"] == "Q"
    assert layout.layers[0]["tlde"] == "*`"
    assert layout.layers[1]["tlde"] == "*~"
    assert not layout.has_altgr
    assert layout.has_1dk
    assert "**" in layout.dead_keys
    assert layout.dead_keys["**"]["base"] == "euioac.EUIOAC"
    assert layout.dead_keys["**"]["alt"] == "éúíóáç…ÉÚÍÓÁÇ"
    assert layout.dead_keys["**"]["alt_self"] == "´"

    # ensure the 1dk parser does not accumulate values from a previous run
    layout = load_layout("intl")
    assert layout.dead_keys["**"]["base"] == "euioac.EUIOAC"
    assert layout.dead_keys["**"]["alt"] == "éúíóáç…ÉÚÍÓÁÇ"

"""
Windows: AHK
To be used by AutoHotKey v1.1: https://autohotkey.com
During our tests, AHK 2.0 has raised serious performance and stability issues.
FWIW, PKL and EPKL still rely on AHK 1.1, too.
"""

import json
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..template import load_tpl, substitute_lines
from ..utils import LAYER_KEYS, SCAN_CODES, Layer, load_data


def ahk_keymap(layout: "KeyboardLayout", altgr: bool = False) -> List[str]:
    """AHK layout, main and AltGr layers."""

    prefixes = [" ", "+", "", "", " <^>!", "<^>!+"]
    specials = " \u00a0\u202f‘’'\"^`~"
    esc_all = True  # set to False to ease the debug (more readable AHK script)

    def ahk_escape(key: str) -> str:
        if len(key) == 1:
            return f"U+{ord(key):04x}" if (esc_all or key in specials) else key
        return f"{key}`" if key.endswith("`") else key  # deadkey identifier

    def ahk_actions(symbol: str) -> Dict[str, str]:
        actions = {}
        for key, dk in layout.dead_keys.items():
            dk_id = ahk_escape(key)
            if symbol == "spce":
                actions[dk_id] = ahk_escape(dk[" "])
            elif symbol in dk:
                actions[dk_id] = ahk_escape(dk[symbol])
        return actions

    output = []
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            output.append(f"; {key_name[1:]}")
            output.append("")
            continue

        if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
            continue  # these two keys are not supported yet

        sc = f"SC{SCAN_CODES['klc'][key_name]}"
        for i in (
            [Layer.ALTGR, Layer.ALTGR_SHIFT] if altgr else [Layer.BASE, Layer.SHIFT]
        ):
            layer = layout.layers[i]
            if key_name not in layer:
                continue

            symbol = layer[key_name]
            sym = ahk_escape(symbol)

            if symbol in layout.dead_keys:
                actions = {sym: layout.dead_keys[symbol][symbol]}
            elif key_name == "spce":
                actions = ahk_actions(key_name)
            else:
                actions = ahk_actions(symbol)

            desc = f" ; {symbol}" if symbol != sym else ""
            act = json.dumps(actions, ensure_ascii=False)
            output.append(f'{prefixes[i]}{sc}::SendKey("{sym}", {act}){desc}')

        if output[-1]:
            output.append("")

    return output


def ahk_shortcuts(layout: "KeyboardLayout") -> List[str]:
    """AHK layout, shortcuts."""

    prefixes = [" ^", "^+"]
    enabled = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    qwerty_vk = load_data("qwerty_vk")

    output = []
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            output.append(f"; {key_name[1:]}")
            output.append("")
            continue

        if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
            continue  # these two keys are not supported yet

        scan_code = SCAN_CODES["klc"][key_name]
        for i in [Layer.BASE, Layer.SHIFT]:
            layer = layout.layers[i]
            if key_name not in layer:
                continue

            symbol = layer[key_name]
            if layout.qwerty_shortcuts:
                symbol = qwerty_vk[scan_code]
            if symbol in enabled:
                output.append(f"{prefixes[i]}SC{scan_code}::Send {prefixes[i]}{symbol}")

        if output[-1]:
            output.append("")

    return output


def ahk(layout: "KeyboardLayout") -> str:
    """Windows AHK driver"""

    # fmt: off
    out = load_tpl(layout, ".ahk")
    out = substitute_lines(out, "LAYOUT",    ahk_keymap(layout))
    out = substitute_lines(out, "ALTGR",     ahk_keymap(layout, True))
    out = substitute_lines(out, "SHORTCUTS", ahk_shortcuts(layout))
    # fmt: on
    return out

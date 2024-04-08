"""
Windows: AHK
To be used by AutoHotKey v1.1: https://autohotkey.com
During our tests, AHK 2.0 has raised serious performance and stability issues.
FWIW, PKL and EPKL still rely on AHK 1.1, too.
"""

import json
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..key import KEYS, Key, KeyCategory
from ..template import load_tpl, substitute_lines
from ..utils import Layer, load_data


def ahk_keymap(layout: "KeyboardLayout", altgr: bool = False) -> List[str]:
    """AHK layout, main and AltGr layers."""

    prefixes = [" ", "+", "", "", " <^>!", "<^>!+"]
    specials = " \u00a0\u202f‘’'\"^`~"
    esc_all = True  # set to False to ease the debug (more readable AHK script)
    layers = (Layer.ALTGR, Layer.ALTGR_SHIFT) if altgr else (Layer.BASE, Layer.SHIFT)

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
    prev_category: Optional[KeyCategory] = None
    for key in KEYS.values():
        # TODO: delete test?
        # if key.id in ["ae13", "ab11"]:  # ABNT / JIS keys
        #     continue  # these two keys are not supported yet
        # TODO: add support for all scan codes
        if key.windows is None or not key.windows.startswith("T"):
            continue

        # Skip key if not defined and is not alphanumeric
        if not any(key.id in layout.layers[i] for i in layers) and not key.alphanum:
            continue

        if key.category is not prev_category:
            output.append(f";  {key.category.description}")
            output.append("")
            prev_category = key.category

        sc = f"SC{key.windows[1:].lower()}"
        for i in layers:
            layer = layout.layers[i]
            if key.id not in layer:
                continue

            symbol = layer[key.id]
            sym = ahk_escape(symbol)

            if symbol in layout.dead_keys:
                actions = {sym: layout.dead_keys[symbol][symbol]}
            elif key.id == "spce":
                actions = ahk_actions(key.id)
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
    layers = (Layer.BASE, Layer.SHIFT)

    output = []
    prev_category: Optional[KeyCategory] = None
    for key in KEYS.values():
        # if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
        #     continue  # these two keys are not supported yet
        # TODO: add support for all scan codes
        if key.windows is None or not key.windows.startswith("T"):
            continue

        # Skip key if not defined and is not alphanumeric
        if not any(key.id in layout.layers[i] for i in layers) and not key.alphanum:
            continue

        if key.category is not prev_category:
            output.append(f";  {key.category.description}")
            output.append("")
            prev_category = key.category

        scan_code = key.windows[1:].lower()
        for i in layers:
            layer = layout.layers[i]
            if key.id not in layer:
                continue

            symbol = layer[key.id]
            if layout.qwerty_shortcuts:
                symbol = qwerty_vk[key.windows]
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

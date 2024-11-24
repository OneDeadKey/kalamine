"""
JSON & SVG outputs
To be used with the <x-keyboard> web component.
https://github.com/OneDeadKey/x-keyboard
"""

import json
import pkgutil
from typing import TYPE_CHECKING, Dict, List, Optional
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..utils import LAYER_KEYS, ODK_ID, SCAN_CODES, Layer, upper_key


def raw_json(layout: "KeyboardLayout") -> Dict:
    """JSON layout descriptor"""

    # flatten the keymap: each key has an array of 2-4 characters
    # correcponding to Base, Shift, AltGr, AltGr+Shift
    keymap: Dict[str, List[str]] = {}
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            continue
        chars = list("")
        for i in [Layer.BASE, Layer.SHIFT, Layer.ALTGR, Layer.ALTGR_SHIFT]:
            if key_name in layout.layers[i]:
                chars.append(layout.layers[i][key_name])
        if chars:
            keymap[SCAN_CODES["web"][key_name]] = chars

    return {
        # fmt: off
        "name":        layout.meta["name"],
        "description": layout.meta["description"],
        "geometry":    layout.meta["geometry"].lower(),
        "keymap":      keymap,
        "deadkeys":    layout.dead_keys,
        "altgr":       layout.has_altgr,
        # fmt: on
    }


def pretty_json(layout: "KeyboardLayout") -> str:
    """Pretty-print the JSON layout."""

    return (
        json.dumps(raw_json(layout), indent=2, ensure_ascii=False)
        .replace("\n      ", " ")
        .replace("\n    ]", " ]")
        .replace("\n    }", " }")
    )


def svg(layout: "KeyboardLayout") -> ET.ElementTree:
    """SVG drawing"""

    svg_ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", svg_ns)
    ns = {"": svg_ns}

    def set_key_label(key: Optional[ET.Element], lvl: int, char: str) -> None:
        if not key:
            return
        for label in key.findall(f'g/text[@class="level{lvl}"]', ns):
            if char not in layout.dead_keys:
                label.text = char
            else:  # only show last char for deadkeys
                if char == ODK_ID:
                    label.text = "★"
                elif char == "*µ":
                    label.text = "α"
                else:
                    label.text = char[-1]
                label.set("class", f"{label.get('class')} deadKey")

    def same_symbol(key_name: str, lower: Layer, upper: Layer):
        up = layout.layers[upper]
        low = layout.layers[lower]
        if key_name not in up or key_name not in low:
            return False
        return up[key_name] == upper_key(low[key_name], blank_if_obvious=False)

    # Parse the SVG template
    # res = pkgutil.get_data(__package__, "templates/x-keyboard.svg")
    res = pkgutil.get_data("kalamine", "templates/x-keyboard.svg")
    if res is None:
        return ET.ElementTree()
    svg = ET.ElementTree(ET.fromstring(res.decode("utf-8")))

    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            continue

        level = 0
        for i in [
            Layer.BASE,
            Layer.SHIFT,
            Layer.ALTGR,
            Layer.ALTGR_SHIFT,
            Layer.ODK,
            Layer.ODK_SHIFT,
        ]:
            level += 1
            if key_name not in layout.layers[i]:
                continue
            if level == 1 and same_symbol(key_name, Layer.BASE, Layer.SHIFT):
                continue
            if level == 4 and same_symbol(key_name, Layer.ALTGR, Layer.ALTGR_SHIFT):
                continue
            if level == 6 and same_symbol(key_name, Layer.ODK, Layer.ODK_SHIFT):
                continue

            key = svg.find(f".//g[@id=\"{SCAN_CODES['web'][key_name]}\"]", ns)
            set_key_label(key, level, layout.layers[i][key_name])

    return svg

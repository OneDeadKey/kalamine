"""
JSON & SVG outputs
To be used with the <x-keyboard> web component.
https://github.com/OneDeadKey/x-keyboard
"""

import pkgutil
from typing import TYPE_CHECKING, Dict, List
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..utils import LAYER_KEYS, ODK_ID, SCAN_CODES, Layer, upper_key


def _web_keymap(layout: "KeyboardLayout") -> Dict[str, List[str]]:
    """Web layout, main part.

    Returns
    -------
    dict[str, list[str]]
        A dict whose keys are key ids and values are list of characters (length 2-4).
    """

    keymap = {}
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            continue
        chars = list("")
        for i in [Layer.BASE, Layer.SHIFT, Layer.ALTGR, Layer.ALTGR_SHIFT]:
            if key_name in layout.layers[i]:
                chars.append(layout.layers[i][key_name])
        if chars:
            keymap[SCAN_CODES["web"][key_name]] = chars

    return keymap


def json(layout: "KeyboardLayout") -> Dict:
    """JSON layout descriptor"""
    return {
        # fmt: off
        "name":        layout.meta["name"],
        "description": layout.meta["description"],
        "geometry":    layout.meta["geometry"].lower(),
        "keymap":      _web_keymap(layout),
        "deadkeys":    layout.dead_keys,
        "altgr":       layout.has_altgr,
        # fmt: on
    }


def svg(layout: "KeyboardLayout") -> ET.ElementTree:
    """SVG drawing"""

    svg_ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", svg_ns)
    ns = {"": svg_ns}

    # Parse the SVG template
    # res = pkgutil.get_data(__package__, "templates/x-keyboard.svg")
    res = pkgutil.get_data("kalamine", "templates/x-keyboard.svg")
    if res is None:
        return ET.ElementTree()
    svg = ET.ElementTree(ET.fromstring(res.decode("utf-8")))

    def set_key_label(key: ET.Element, lvl: int, char: str) -> None:
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

    # Fill-in with layout
    for name, chars in _web_keymap(layout).items():
        for key in svg.findall(f'.//g[@id="{name}"]', ns):

            # Print 1-4 level chars
            for level_num, char in enumerate(chars, start=1):
                if level_num == 1:
                    if chars[1] == upper_key(chars[0], blank_if_obvious=False):
                        continue
                if level_num == 4:
                    if chars[3] == upper_key(chars[2], blank_if_obvious=False):
                        continue
                set_key_label(key, level_num, char)

            # Print 5-6 levels (1dk deadkeys)
            if layout.dead_keys and (odk := layout.dead_keys.get(ODK_ID)):
                level5 = odk.get(chars[0])
                level6 = odk.get(chars[1])
                if level5:
                    set_key_label(key, 5, level5)
                if level6 and level6 != upper_key(level5, blank_if_obvious=False):
                    set_key_label(key, 6, level6)

    return svg

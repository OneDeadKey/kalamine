from pathlib import Path
from typing import Dict, List

from .layout import KeyboardLayout
from .template import SCAN_CODES
from .utils import Layer, load_data

SEPARATOR = (
    "--------------------------------------------------------------------------------"
)

MARKDOWN_HEADER = """Defining a Keyboard Layout
================================================================================

Kalamine keyboard layouts are defined with TOML files including this kind of
ASCII-art layer templates:

```KALAMINE_LAYOUT```
"""

TOML_HEADER = """# kalamine keyboard layout descriptor
name        = "qwerty-custom"  # full layout name, displayed in the keyboard settings
name8       = "custom"         # short Windows filename: no spaces, no special chars
locale      = "us"             # locale/language id
variant     = "custom"         # layout variant id
author      = "nobody"         # author name
description = "custom QWERTY layout"
url         = "https://OneDeadKey.github.com/kalamine"
version     = "0.0.1"
geometry    = """

TOML_FOOTER = """
[spacebar]
1dk         = "'"  # apostrophe
1dk_shift   = "'"  # apostrophe"""


def dead_key_table() -> str:
    out = f"\n    id  XKB name          base -> accented chars\n    {SEPARATOR[4:]}"
    for item in load_data("dead_keys"):
        if (item["char"]) != "**":
            out += f"\n    {item['char']}  {item['name']:<17} {item['base']}"
            out += f"\n                       -> {item['alt']}"
    return out


def core_guide() -> List[str]:
    sections: List[str] = []

    for title, content in load_data("user_guide").items():
        out = f"\n{title.replace('_', ' ')}\n{SEPARATOR}"

        if isinstance(content, dict):
            for subtitle, subcontent in content.items():
                out += f"\n\n### {subtitle.replace('_', ' ')}"
                out += f"\n\n{subcontent}"
                if subtitle == "Standard_Dead_Keys":
                    out += dead_key_table()
        else:
            out += f"\n\n{content}"

        sections.append(out)

    return sections


def dummy_layout(
    geometry: str = "ISO",
    altgr: bool = False,
    odk: bool = False,
    meta: Dict[str, str] = {},
) -> KeyboardLayout:
    """Create a dummy (QWERTY) layout with the given characteristics."""

    # load the descriptor, but only keep the layers we need
    descriptor = load_data("layout")
    if not altgr:
        del descriptor["altgr"]
    if not odk:
        del descriptor["1dk"]
        descriptor["base"] = descriptor.pop("alpha")
    else:
        del descriptor["alpha"]
        descriptor["base"] = descriptor.pop("1dk")

    # XXX this should be a dataclass
    for key, val in meta.items():
        descriptor[key] = val

    # make a KeyboardLayout matching the input parameters
    descriptor["geometry"] = "ANSI"  # layout.yaml has an ANSI geometry
    layout = KeyboardLayout(descriptor)
    layout.geometry = geometry

    # ensure there is no empty keys (XXX maybe this should be in layout.py)
    for key in SCAN_CODES["web"].keys():
        if key not in layout.layers[Layer.BASE].keys():
            layout.layers[Layer.BASE][key] = "\\"
            layout.layers[Layer.SHIFT][key] = "|"

    return layout


def draw_layout(geometry: str = "ISO", altgr: bool = False, odk: bool = False) -> str:
    """Draw a ASCII art description of a default layout."""

    # make a KeyboardLayout, just to get the ASCII arts
    layout = dummy_layout(geometry, altgr, odk)

    def keymap(layer_name: str) -> str:
        layer = "\n".join(getattr(layout, layer_name))
        return f"\n{layer_name} = '''\n{layer}\n'''\n"

    content = ""
    if odk:
        content += keymap("base")
        if altgr:
            content += keymap("altgr")
    elif altgr:
        content += keymap("full")
    else:
        content += keymap("base")

    return content


###
# Public API
##


def user_guide() -> str:
    """Create a user guide with a sample layout description."""

    header = MARKDOWN_HEADER.replace(
        "KALAMINE_LAYOUT", draw_layout(geometry="ANSI", altgr=True)
    )
    return header + "\n" + "\n".join(core_guide())


def create_layout(output_file: Path, geometry: str, altgr: bool, odk: bool) -> None:
    """Create a new TOML layout description."""

    content = f'{TOML_HEADER}"{geometry.upper()}"\n'
    content += draw_layout(geometry, altgr, odk)
    if odk:
        content += TOML_FOOTER

    for topic in core_guide():
        content += f"\n\n\n# {SEPARATOR}"
        content += "\n# ".join(topic.rstrip().split("\n"))

    with open(output_file, "w", encoding="utf-8", newline="\n") as file:
        file.write(content.replace(" \n", "\n"))

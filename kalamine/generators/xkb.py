"""
GNU/Linux: XKB
- standalone xkb keymap file to be used by `xkbcomp` (XOrg only)
- xkb symbols/patch for XOrg (system-wide) & Wayland (system-wide/user-space)
"""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..key import KEYS, KeyCategory
from ..template import load_tpl, substitute_lines
from ..utils import DK_INDEX, ODK_ID, hex_ord, load_data

XKB_KEY_SYM = load_data("key_sym")


def xkb_table(layout: "KeyboardLayout", xkbcomp: bool = False) -> List[str]:
    """GNU/Linux layout."""

    if layout.qwerty_shortcuts:
        print("WARN: keeping qwerty shortcuts is not yet supported for xkb")

    show_description = True
    eight_level = layout.has_altgr and layout.has_1dk and not xkbcomp
    odk_symbol = "ISO_Level5_Latch" if eight_level else "ISO_Level3_Latch"
    max_length = 16  # `ISO_Level3_Latch` should be the longest symbol name

    output: List[str] = []
    prev_category: Optional[KeyCategory] = None
    for key in KEYS.values():
        descs = []
        symbols = []
        has_symbols = False
        for keys in layout.layers.values():
            if key.id in keys:
                keysym = keys[key.id]
                desc = keysym
                # dead key?
                if keysym in DK_INDEX:
                    name = DK_INDEX[keysym].name
                    desc = layout.dead_keys[keysym][keysym]
                    symbol = odk_symbol if keysym == ODK_ID else f"dead_{name}"
                # regular key: use a keysym if possible, utf-8 otherwise
                elif keysym in XKB_KEY_SYM and len(XKB_KEY_SYM[keysym]) <= max_length:
                    symbol = XKB_KEY_SYM[keysym]
                else:
                    symbol = f"U{hex_ord(keysym).upper()}"
                has_symbols = True
            else:
                desc = " "
                symbol = "VoidSymbol"

            descs.append(desc)
            symbols.append(symbol.ljust(max_length))

        if not has_symbols:
            continue

        if key.category is not prev_category:
            if output:
                output.append("")
            output.append("// " + key.category.description)
            prev_category = key.category

        key_template = "{{[ {0}, {1}, {2}, {3}]}}"  # 4-level layout by default
        description = "{0} {1} {2} {3}"
        if layout.has_altgr and layout.has_1dk:
            # 6 layers are needed: they won't fit on the 4-level format.
            if xkbcomp:  # user-space XKB keymap file (standalone)
                # standalone XKB files work best with a dual-group solution:
                # one 4-level group for base+1dk, one two-level group for AltGr
                key_template = "{{[ {}, {}, {}, {}],[ {}, {}]}}"
                description = "{} {} {} {} {} {}"
            else:  # eight_level XKB symbols (Neo-like)
                key_template = "{{[ {0}, {1}, {4}, {5}, {2}, {3}]}}"
                description = "{0} {1} {4} {5} {2} {3}"
        elif layout.has_altgr:
            del symbols[3]
            del symbols[2]
            del descs[3]
            del descs[2]

        keycode = f"<{key.xkb.upper()}>"
        line = f"key {keycode: <6} {key_template.format(*symbols)};"
        if show_description:
            line += (" // " + description.format(*descs)).rstrip()
            if line.endswith("\\"):
                line += " "  # escape trailing backslash
        output.append(line)

    return output


def xkb_keymap(self) -> str:  # will not work with Wayland
    """GNU/Linux driver (standalone / user-space)"""

    out = load_tpl(self, ".xkb_keymap")
    out = substitute_lines(out, "LAYOUT", xkb_table(self, xkbcomp=True))
    return out


def xkb_symbols(self) -> str:
    """GNU/Linux driver (xkb patch, system or user-space)"""

    out = load_tpl(self, ".xkb_symbols")
    out = substitute_lines(out, "LAYOUT", xkb_table(self, xkbcomp=False))
    return out.replace("//#", "//")

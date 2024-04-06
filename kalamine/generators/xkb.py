"""
GNU/Linux: XKB
- standalone xkb keymap file to be used by `xkbcomp` (XOrg only)
- xkb symbols/patch for XOrg (system-wide) & Wayland (system-wide/user-space)
"""

from dataclasses import dataclass
import itertools
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Generator, List, Optional

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..template import load_tpl, substitute_lines
from ..utils import DK_INDEX, LAYER_KEYS, ODK_ID, SystemSymbol, hex_ord, load_data

XKB_KEY_SYM = load_data("key_sym")
XKB_SPECIAL_KEYSYMS = {
    SystemSymbol.Alt.value: "Alt_L",
    SystemSymbol.AltGr.value: "ISO_Level3_Shift",
    SystemSymbol.BackSpace.value: "BackSpace",
    SystemSymbol.CapsLock.value: "Caps_Lock",
    SystemSymbol.Compose.value: "Multi_key",
    SystemSymbol.Control.value: "Control_L",
    SystemSymbol.Escape.value: "Escape",
    SystemSymbol.Return.value: "Return",
    SystemSymbol.Shift.value: "Shift_L",
}
assert all(s.value in XKB_SPECIAL_KEYSYMS for s in SystemSymbol), \
       tuple(s for s in SystemSymbol if s.value not in XKB_SPECIAL_KEYSYMS)
XKB_KEY_SYM.update(XKB_SPECIAL_KEYSYMS)

SPARE_KEYSYMS = (
    "F20",
    "F21",
    "F22",
    "F23",
    "F24",
    "F25",
    "F26",
    "F27",
    "F28",
    "F29",
    "F30",
    "F31",
    "F32",
    "F33",
    "F34",
    "F35",
)


@dataclass
class XKB_Output:
    symbols: str
    compose: str


def xkb_make_strings(layout: "KeyboardLayout") -> Dict[str, str]:
    layoutSymbols = layout.symbols
    forbiden = set(itertools.chain(layoutSymbols.strings, layoutSymbols.deadKeys))
    spares = list(SPARE_KEYSYMS)
    mapping = {}
    for s in layoutSymbols.strings:
        if len(s) >= 2:
            # Try to use one of the characters of the string
            if candidates := tuple((cʹ, keysym) for c in s for cʹ in (c.lower(), c.upper()) if len(cʹ) == 1 and cʹ not in forbiden and (keysym := XKB_KEY_SYM.get(cʹ))):
                mapping[s] = candidates[0][1]
                forbiden.add(candidates[0][0])
            elif spares:
                mapping[s] = spares.pop(0)
            else:
                raise ValueError(f"Cannot encode string: “{s}”")
    return mapping


def xkb_table(layout: "KeyboardLayout", xkbcomp: bool = False, strings: Optional[Dict[str, str]]=None) -> List[str]:
    """GNU/Linux layout."""

    if layout.qwerty_shortcuts:
        print("WARN: keeping qwerty shortcuts is not yet supported for xkb")

    show_description = True
    eight_level = layout.has_altgr and layout.has_1dk and not xkbcomp
    odk_symbol = "ISO_Level5_Latch" if eight_level else "ISO_Level3_Latch"
    max_length = 16  # `ISO_Level3_Latch` should be the longest symbol name

    if strings is None:
        strings = {}

    output: List[str] = []
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):  # separator
            if output:
                output.append("")
            output.append("//" + key_name[1:])
            continue

        descs = []
        symbols = []
        for layer in layout.layers.values():
            if key_name in layer:
                keysym = layer[key_name]
                desc = keysym
                if keysymʹ := strings.get(keysym):
                    symbol = keysymʹ
                # dead key?
                elif keysym in DK_INDEX:
                    name = DK_INDEX[keysym].name
                    desc = layout.dead_keys[keysym][keysym]
                    symbol = odk_symbol if keysym == ODK_ID else f"dead_{name}"
                # regular key: use a keysym if possible, utf-8 otherwise
                elif keysym in XKB_KEY_SYM and len(XKB_KEY_SYM[keysym]) <= max_length:
                    symbol = XKB_KEY_SYM[keysym]
                else:
                    symbol = f"U{hex_ord(keysym).upper()}"
            else:
                desc = " "
                symbol = "VoidSymbol"

            descs.append(desc)
            symbols.append(symbol.ljust(max_length))

        key_type = ""
        key = "{{[ {0}, {1}, {2}, {3}]}}"  # 4-level layout by default
        description = "{0} {1} {2} {3}"
        if all(s.startswith("VoidSymbol") for s in symbols):
            continue
        elif not symbols[0].startswith("VoidSymbol") and all(s == symbols[0] for s in symbols):
            key = "{{{type}[{0}]}}"
            description = "{0}"
            key_type = "ONE_LEVEL"
            symbols = [symbols[0]]
            descs = [descs[0]]
        elif layout.has_altgr and layout.has_1dk:
            # 6 layers are needed: they won't fit on the 4-level format.
            if xkbcomp:  # user-space XKB keymap file (standalone)
                # standalone XKB files work best with a dual-group solution:
                # one 4-level group for base+1dk, one two-level group for AltGr
                key = "{{[ {}, {}, {}, {}],[ {}, {}]}}"
                description = "{} {} {} {} {} {}"
            else:  # eight_level XKB symbols (Neo-like)
                key = "{{[ {0}, {1}, {4}, {5}, {2}, {3}]}}"
                description = "{0} {1} {4} {5} {2} {3}"
        elif layout.has_altgr:
            del symbols[3]
            del symbols[2]
            del descs[3]
            del descs[2]

        if key_type:
            key_type = f"""type[Group1] = "{key_type}", """
        line = f"key <{key_name.upper()}> {key.format(*symbols, type=key_type)};"
        if show_description:
            line += (" // " + description.format(*descs)).rstrip()
            if line.endswith("\\"):
                line += " "  # escape trailing backslash
        output.append(line)

    return output


def xkb_keymap(layout: "KeyboardLayout") -> XKB_Output:  # will not work with Wayland
    """GNU/Linux driver (standalone / user-space)"""

    strings = xkb_make_strings(layout)

    symbols = load_tpl(layout, ".xkb_keymap")
    symbols = substitute_lines(symbols, "LAYOUT", xkb_table(layout, xkbcomp=True, strings=strings))

    compose = "\n".join(xcompose(strings)) if strings else ""

    return XKB_Output(symbols, compose)


def xkb_symbols(layout: "KeyboardLayout") -> XKB_Output:
    """GNU/Linux driver (xkb patch, system or user-space)"""

    strings = xkb_make_strings(layout)

    symbols = load_tpl(layout, ".xkb_symbols")
    symbols = substitute_lines(symbols, "LAYOUT", xkb_table(layout, xkbcomp=False, strings=strings))

    compose = "\n".join(xcompose(strings)) if strings else ""
    
    return XKB_Output(symbols.replace("//#", "//"), compose)


def escapeString(s: str) -> Generator[str, None, None]:
    for c in s:
        if (cp := ord(c)) < 0x20:
            yield f"\\x{cp:0>2x}"
        match c:
            case "\\":
                yield "\\\\"
            case "\"":
                yield "\\\""
            case _:
                # FIXME escape all relevant chars
                yield c


def xcompose(strings: Dict[str, str]) -> Generator[str, None, None]:
    for s, keysym in strings.items():
        s = "".join(escapeString(s))
        yield f"<{keysym}> : \"{s}\""
    yield ""


def xkb_write_files(path: Path, result: XKB_Output):
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(result.symbols)
    if result.compose is None:
        return
    path = path.with_suffix(".xkb_compose")
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(result.compose)
"""
GNU/Linux: XKB
- standalone xkb keymap file to be used by `xkbcomp` (XOrg only)
- xkb symbols/patch for XOrg (system-wide) & Wayland (system-wide/user-space)
"""

from dataclasses import dataclass
import functools
import itertools
import locale
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Generator, List, Optional, Tuple

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..key import KEYS, Hand, KeyCategory
from ..template import load_tpl, substitute_lines
from ..utils import DK_INDEX, ODK_ID, DeadKeyDescr, SystemSymbol, hex_ord, load_data

XKB_KEY_SYM = load_data("key_sym")
XKB_SPECIAL_KEYSYMS = {
    SystemSymbol.Alt.value: {Hand.Left: "Alt_L", Hand.Right: "Alt_R"},
    SystemSymbol.AltGr.value: {Hand.Left: "ISO_Level3_Shift"},
    SystemSymbol.BackSpace.value: {Hand.Left: "BackSpace"},
    SystemSymbol.CapsLock.value: {Hand.Left: "Caps_Lock"},
    SystemSymbol.Compose.value: {Hand.Left: "Multi_key"},
    SystemSymbol.Control.value: {Hand.Left: "Control_L", Hand.Right: "Control_R"},
    SystemSymbol.Delete.value: {Hand.Left: "Delete"},
    SystemSymbol.Escape.value: {Hand.Left: "Escape"},
    SystemSymbol.Return.value: {Hand.Left: "Return"},
    SystemSymbol.Shift.value: {Hand.Left: "Shift_L", Hand.Right: "Shift_R"},
    SystemSymbol.Super.value: {Hand.Left: "Super_L", Hand.Right: "Super_R"},
    SystemSymbol.Tab.value: {Hand.Left: "Tab"},
    SystemSymbol.RightTab.value: {Hand.Left: "Tab"},
    SystemSymbol.LeftTab.value: {Hand.Left: "ISO_Left_Tab"},
    SystemSymbol.ArrowUp.value: {Hand.Left: "Up"},
    SystemSymbol.ArrowDown.value: {Hand.Left: "Down"},
    SystemSymbol.ArrowLeft.value: {Hand.Left: "Left"},
    SystemSymbol.ArrowRight.value: {Hand.Left: "Right"},
    SystemSymbol.PageUp.value: {Hand.Left: "Prior"},
    SystemSymbol.PageDown.value: {Hand.Left: "Next"},
    SystemSymbol.Home.value: {Hand.Left: "Home"},
    SystemSymbol.End.value: {Hand.Left: "End"},
    SystemSymbol.Menu.value: {Hand.Left: "Menu"},
}
assert all(s.value in XKB_SPECIAL_KEYSYMS for s in SystemSymbol), \
       tuple(s for s in SystemSymbol if s.value not in XKB_SPECIAL_KEYSYMS)

def xkb_keysym(char: str, max_length: Optional[int] = None, hand: Optional[Hand]=None) -> str:
    if char in XKB_SPECIAL_KEYSYMS:
        keysyms = XKB_SPECIAL_KEYSYMS[char]
        if hand in keysyms:
            return keysyms[hand]
        else:
            return keysyms[Hand.Left]
    elif char in XKB_KEY_SYM and (max_length is None or len(XKB_KEY_SYM[char]) <= max_length):
        return XKB_KEY_SYM[char]
    else:
        return f"U{hex_ord(char).upper()}"


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
class XKB_Custom_Keysyms:
    strings: Dict[str, str]
    deadKeys: Dict[str, str]


@dataclass
class XKB_Output:
    symbols: str
    compose: str


def _collate(s1: str, s2: str) -> int:
    s1ʹ = s1.casefold()
    s2ʹ = s2.casefold()
    if s1ʹ < s2ʹ:
        return -1
    elif s1ʹ > s2ʹ:
        return +1
    else:
        # Note: inverted on purpose, to get lower case before upper case
        return locale.strcoll(s2, s1)


def xkb_make_custom_dead_keys_keysyms(layout: "KeyboardLayout") -> XKB_Custom_Keysyms:
    layoutSymbols = layout.symbols
    forbiden = set(itertools.chain(layoutSymbols.strings, layoutSymbols.deadKeys))
    spares = list(SPARE_KEYSYMS)
    strings = {}
    deadKeys = {}
    for s in sorted(layoutSymbols.strings, key=functools.cmp_to_key(_collate)):
        if len(s) >= 2:
            # Try to use one of the characters of the string
            candidates = tuple(
                (cʹ, keysym)
                for c in s
                for cʹ in (c.lower(), c.upper())
                if len(cʹ) == 1 and cʹ not in forbiden and (keysym := XKB_KEY_SYM.get(cʹ))
            )
            if candidates:
                strings[s] = candidates[0][1]
                forbiden.add(candidates[0][0])
            elif spares:
                strings[s] = spares.pop(0)
            else:
                raise ValueError(f"Cannot encode string: “{s}”")
    for c in sorted(layoutSymbols.deadKeys, key=functools.cmp_to_key(_collate)):
        dk = f"*{c}"
        if dk in DK_INDEX:
            continue
        elif c not in forbiden and (keysym := XKB_KEY_SYM.get(c)):
            deadKeys[dk] = keysym
            forbiden.add(c)
        elif spares:
            deadKeys[dk] = spares.pop(0)
        else:
            raise ValueError(f"Cannot encode dead key: “{dk}”")

    return XKB_Custom_Keysyms(strings, deadKeys)


def xkb_table(layout: "KeyboardLayout", xkbcomp: bool = False, customDeadKeys: Optional[XKB_Custom_Keysyms]=None) -> List[str]:
    """GNU/Linux layout."""

    if layout.qwerty_shortcuts:
        print("WARN: keeping qwerty shortcuts is not yet supported for xkb")

    show_description = True
    eight_level = layout.has_altgr and layout.has_1dk and not xkbcomp
    odk_symbol = "ISO_Level5_Latch" if eight_level else "ISO_Level3_Latch"
    max_length = 16  # `ISO_Level3_Latch` should be the longest symbol name

    if customDeadKeys is None:
        customDeadKeys = XKB_Custom_Keysyms({}, {})

    output: List[str] = []
    prev_category: Optional[KeyCategory] = None
    for key in KEYS.values():
        descs = []
        symbols = []
        defined = False
        for layer, keys in layout.layers.items():
            if key.id in keys:
                keysym = keys[key.id]
                # Hack for Tab
                if layer.value % 2 == 1 and keysym in ("↹", "⇥"):
                    keysym = "⇤"
                desc = keysym
                if keysymʹ := customDeadKeys.strings.get(keysym):
                    symbol = keysymʹ
                elif keysymʹ := customDeadKeys.deadKeys.get(keysym):
                    name = layout.custom_dead_keys[keysym].name
                    desc = layout.dead_keys[keysym][keysym]
                    symbol = keysymʹ
                # predefined dead key?
                elif keysym in DK_INDEX:
                    name = layout.custom_dead_keys[keysym].name
                    desc = layout.dead_keys[keysym][keysym]
                    symbol = odk_symbol if keysym == ODK_ID else f"dead_{name}"
                # regular key: use a keysym if possible, utf-8 otherwise
                else:
                    symbol = xkb_keysym(keysym, max_length=max_length, hand=key.hand)
                defined = True
            else:
                desc = " "
                symbol = "VoidSymbol"

            descs.append(desc)
            symbols.append(symbol.ljust(max_length))

        if not symbols or not defined:
            continue

        if key.category is not prev_category:
            if output:
                output.append("")
            output.append("// " + key.category.description)
            prev_category = key.category

        key_template = "{{[ {0}, {1}, {2}, {3}]}}"  # 4-level layout by default
        description = "{0} {1} {2} {3}"
        if all(s == symbols[0] for s in symbols):
            key_template = """{{type[Group1] = \"ONE_LEVEL\",\n                [ {0} ]}}"""
            description = "{0}"
            symbols = symbols[0:1]
            descs = descs[0:1]
        elif all((i % 2 == 0 and s == symbols[0]) or (i % 2 == 1 and s == symbols[1]) for i, s in enumerate(symbols)):
            key_template = """{{type[Group1] = \"TWO_LEVEL\",\n                [ {0}, {1} ]}}"""
            description = "{0} {1}"
            symbols = symbols[:2]
            descs = descs[:2]
        elif layout.has_altgr and layout.has_1dk:
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


def xkb_keymap(layout: "KeyboardLayout") -> XKB_Output:  # will not work with Wayland
    """GNU/Linux driver (standalone / user-space)"""

    customDeadKeysKeysyms = xkb_make_custom_dead_keys_keysyms(layout)

    symbols = load_tpl(layout, ".xkb_keymap")
    symbols = substitute_lines(symbols, "LAYOUT", xkb_table(layout, xkbcomp=True, customDeadKeys=customDeadKeysKeysyms))

    compose = "\n".join(xcompose(layout, customDeadKeysKeysyms)) if customDeadKeysKeysyms else ""

    return XKB_Output(symbols, compose)


def xkb_symbols(layout: "KeyboardLayout") -> XKB_Output:
    """GNU/Linux driver (xkb patch, system or user-space)"""

    customDeadKeysKeysyms = xkb_make_custom_dead_keys_keysyms(layout)

    symbols = load_tpl(layout, ".xkb_symbols")
    symbols = substitute_lines(symbols, "LAYOUT", xkb_table(layout, xkbcomp=False, customDeadKeys=customDeadKeysKeysyms))

    compose = "\n".join(xcompose(layout, customDeadKeysKeysyms)) if customDeadKeysKeysyms else ""

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


def _compose_sequences(dk: DeadKeyDescr) -> Generator[Tuple[str, str], None, None]:
    yield from zip(dk.base, dk.alt)
    yield (dk.char, dk.alt_self)
    yield (" ", dk.alt_space)


def xcompose(layout: "KeyboardLayout", customDeadKeys: XKB_Custom_Keysyms) -> Generator[str, None, None]:
    # Strings
    for s, keysym in sorted(customDeadKeys.strings.items(), key=lambda x: x[1]):
        s = "".join(escapeString(s))
        yield f"<{keysym}> : \"{s}\""
    # Dead keys sequences
    for dk in layout.custom_dead_keys.values():
        if dk.char == ODK_ID:
            continue
        # Predefined dk
        if (dkʹ := DK_INDEX.get(dk.char)):
            predefined = dict(_compose_sequences(dkʹ))
        else:
            predefined = {}
        # Dead key keysym
        if (dk_keysym := customDeadKeys.deadKeys.get(dk.char)) is None:
            # dk_keysym = xkb_keysym(dk.char[-1])
            dk_keysym = f"dead_{dk.name}"
        # Sequences
        for base, result in _compose_sequences(dk):
            if predefined.get(base) == result:
                # Skip predefined sequence
                continue
            # TODO: general chained dead keys?
            if base == dk.char:
                base_keysym = dk_keysym
            else:
                base_keysym = xkb_keysym(base)
            result_keysym = xkb_keysym(result)
            result_string = "".join(escapeString(result))
            yield f"<{dk_keysym}> <{base_keysym}> : \"{result_string}\" {result_keysym}"
    yield ""

def xkb_write_files(path: Path, result: XKB_Output):
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(result.symbols)
    if not result.compose:
        return
    path = path.with_suffix(".xkb_compose")
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(result.compose)
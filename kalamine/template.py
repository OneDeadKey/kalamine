#!/usr/bin/env python3
import json
from typing import TYPE_CHECKING, Dict, List, Tuple

from .utils import DEAD_KEYS, LAYER_KEYS, ODK_ID, Layer, load_data

if TYPE_CHECKING:
    from .layout import KeyboardLayout

DK_INDEX = {}
for dk in DEAD_KEYS:
    DK_INDEX[dk.char] = dk


###
# Helpers
#

KEY_CODES = load_data("key_codes.yaml")
XKB_KEY_SYM = load_data("key_sym.yaml")


def hex_ord(char: str) -> str:
    return hex(ord(char))[2:].zfill(4)


def xml_proof(char: str) -> str:
    if char not in '<&"\u0020\u00a0\u202f>':
        return char
    return f"&#x{hex_ord(char)};"


def xml_proof_id(symbol: str) -> str:
    return symbol[2:-1] if symbol.startswith("&#x") else symbol


###
# GNU/Linux: XKB
# - standalone xkb file to be used by `xkbcomp` (XOrg only)
# - xkb patch for XOrg (system-wide) & Wayland (system-wide/user-space)
#


def xkb_keymap(layout: "KeyboardLayout", xkbcomp: bool = False) -> List[str]:
    """Linux layout."""

    show_description = True
    eight_level = layout.has_altgr and layout.has_1dk and not xkbcomp
    odk_symbol = "ISO_Level5_Latch" if eight_level else "ISO_Level3_Latch"
    max_length = 16  # `ISO_Level3_Latch` should be the longest symbol name

    output: List[str] = []
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):  # separator
            if output:
                output.append("")
            output.append("//" + key_name[1:])
            continue

        symbols = []
        description = " //"
        for layer in layout.layers.values():
            if key_name in layer:
                keysym = layer[key_name]
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
            else:
                desc = " "
                symbol = "VoidSymbol"

            description += " " + desc
            symbols.append(symbol.ljust(max_length))

        key = "key <{}> {{[ {}, {}, {}, {}]}};"  # 4-level layout by default
        if layout.has_altgr and layout.has_1dk:
            # 6 layers are needed: they won't fit on the 4-level format.
            if xkbcomp:  # user-space XKB file (standalone)
                # standalone XKB files work best with a dual-group solution:
                # one 4-level group for base+1dk, one two-level group for AltGr
                key = "key <{}> {{[ {}, {}, {}, {}],[ {}, {}]}};"
            else:  # eight_level XKB patch (Neo-like)
                key = "key <{0}> {{[ {1}, {2}, {5}, {6}, {3}, {4}, {7}, {8}]}};"
                symbols.append("VoidSymbol".ljust(max_length))
                symbols.append("VoidSymbol".ljust(max_length))
        elif layout.has_altgr:
            del symbols[3]
            del symbols[2]

        line = key.format(*[key_name.upper()] + symbols)
        if show_description:
            line += description.rstrip()
            if line.endswith("\\"):
                line += " "  # escape trailing backslash
        output.append(line)

    return output


###
# Windows: AHK
# To be used by AutoHotKey v1.1: https://autohotkey.com
# During our tests, AHK 2.0 has raised serious performance and stability issues.
# FWIW, PKL and EPKL still rely on AHK 1.1, too.


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

        sc = f"SC{KEY_CODES['klc'][key_name][:2]}"
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

    output = []
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            output.append(f"; {key_name[1:]}")
            output.append("")
            continue

        if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
            continue  # these two keys are not supported yet

        sc = f"SC{KEY_CODES['klc'][key_name][:2]}"
        for i in [Layer.BASE, Layer.SHIFT]:
            layer = layout.layers[i]
            if key_name not in layer:
                continue

            symbol = layer[key_name]
            if symbol in enabled:
                output.append(f"{prefixes[i]}{sc}::Send {prefixes[i]}{symbol}")

        if output[-1]:
            output.append("")

    return output


###
# Windows: KLC
# To be used by the MS Keyboard Layout Creator to generate an installer.
# https://www.microsoft.com/en-us/download/details.aspx?id=102134
# https://levicki.net/articles/2006/09/29/HOWTO_Build_keyboard_layouts_for_Windows_x64.php
# Also supported by KbdEdit: http://www.kbdedit.com/ (non-free).
# Note: blank lines and comments in KLC sections are removed from the output
# file because they are not recognized by KBDEdit (as of v19.8.0).
#


def klc_keymap(layout: "KeyboardLayout") -> List[str]:
    """Windows layout, main part."""

    supported_symbols = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    output = []
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            continue

        if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
            continue  # these two keys are not supported yet

        symbols = []
        description = "//"
        alpha = False

        for i in [Layer.BASE, Layer.SHIFT, Layer.ALTGR, Layer.ALTGR_SHIFT]:
            layer = layout.layers[i]

            if key_name in layer:
                symbol = layer[key_name]
                desc = symbol
                if symbol in layout.dead_keys:
                    desc = layout.dead_keys[symbol][" "]
                    symbol = hex_ord(desc) + "@"
                else:
                    if i == Layer.BASE:
                        alpha = symbol.upper() != symbol
                    if symbol not in supported_symbols:
                        symbol = hex_ord(symbol)
                symbols.append(symbol)
            else:
                desc = " "
                symbols.append("-1")
            description += " " + desc

        if layout.has_altgr:
            output.append(
                "\t".join(
                    [
                        KEY_CODES["klc"][key_name],  # scan code & virtual key
                        "1" if alpha else "0",  # affected by CapsLock?
                        symbols[0],
                        symbols[1],  # base layer
                        "-1",
                        "-1",  # ctrl layer
                        symbols[2],
                        symbols[3],  # altgr layer
                        description.strip(),
                    ]
                )
            )
        else:
            output.append(
                "\t".join(
                    [
                        KEY_CODES["klc"][key_name],  # scan code & virtual key
                        "1" if alpha else "0",  # affected by CapsLock?
                        symbols[0],
                        symbols[1],  # base layer
                        "-1",
                        "-1",  # ctrl layer
                        description.strip(),
                    ]
                )
            )

    return output


def klc_deadkeys(layout: "KeyboardLayout") -> List[str]:
    """Windows layout, dead keys."""

    output = []

    for k in DK_INDEX:
        if k not in layout.dead_keys:
            continue
        dk = layout.dead_keys[k]

        output.append(f"// DEADKEY: {DK_INDEX[k].name.upper()} //" + "{{{")
        output.append(f"DEADKEY\t{hex_ord(dk[' '])}")

        for base, alt in dk.items():
            if base == k:
                continue

            if base in layout.dead_keys:
                base = layout.dead_keys[base][" "]

            if alt in layout.dead_keys:
                alt = layout.dead_keys[alt][" "]
                ext = hex_ord(alt) + "@"
            else:
                ext = hex_ord(alt)

            output.append(f"{hex_ord(base)}\t{ext}\t// {base} -> {alt}")

        output.append("//}}}")
        output.append("")

    return output[:-1]


def klc_dk_index(layout: "KeyboardLayout") -> List[str]:
    """Windows layout, dead key index."""

    output = []
    for k in DK_INDEX:
        if k not in layout.dead_keys:
            continue
        dk = layout.dead_keys[k]
        output.append(f"{hex_ord(dk[' '])}\t\"{DK_INDEX[k].name.upper()}\"")
    return output


###
# macOS: keylayout
# https://developer.apple.com/library/content/technotes/tn2056/
#


def osx_keymap(layout: "KeyboardLayout") -> List[List[str]]:
    """macOS layout, main part."""

    ret_str = []
    for index in range(5):
        layer = layout.layers[
            [Layer.BASE, Layer.SHIFT, Layer.BASE, Layer.ALTGR, Layer.ALTGR_SHIFT][index]
        ]
        caps = index == 2

        def has_dead_keys(letter: str) -> bool:
            if letter in "\u0020\u00a0\u202f":  # space
                return True
            for k in layout.dead_keys:
                if letter in layout.dead_keys[k]:
                    return True
            return False

        output: List[str] = []
        for key_name in LAYER_KEYS:
            if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
                continue  # these two keys are not supported yet

            if key_name.startswith("-"):
                if output:
                    output.append("")
                output.append("<!--" + key_name[1:] + " -->")
                continue

            symbol = "&#x0010;"
            final_key = True

            if key_name in layer:
                key = layer[key_name]
                if key in layout.dead_keys:
                    symbol = f"dead_{DK_INDEX[key].name}"
                    final_key = False
                else:
                    symbol = xml_proof(key.upper() if caps else key)
                    final_key = not has_dead_keys(key.upper())

            char = f"code=\"{KEY_CODES['osx'][key_name]}\"".ljust(10)
            if final_key:
                action = f'output="{symbol}"'
            else:
                action = f'action="{xml_proof_id(symbol)}"'
            output.append(f"<key {char} {action} />")

        ret_str.append(output)
    return ret_str


def osx_actions(layout: "KeyboardLayout") -> List[str]:
    """macOS layout, dead key actions."""

    ret_actions = []

    def when(state: str, action: str) -> str:
        state_attr = f'state="{state}"'.ljust(18)
        if action in layout.dead_keys:
            action_attr = f'next="{DK_INDEX[action].name}"'
        elif action.startswith("dead_"):
            action_attr = f'next="{action[5:]}"'
        else:
            action_attr = f'output="{xml_proof(action)}"'
        return f"  <when {state_attr} {action_attr} />"

    def append_actions(symbol: str, actions: List[Tuple[str, str]]) -> None:
        ret_actions.append(f'<action id="{xml_proof_id(symbol)}">')
        ret_actions.append(when("none", symbol))
        for state, out in actions:
            ret_actions.append(when(state, out))
        ret_actions.append("</action>")

    # dead key definitions
    for key in layout.dead_keys:
        name = DK_INDEX[key].name
        term = layout.dead_keys[key][key]
        ret_actions.append(f'<action id="dead_{name}">')
        ret_actions.append(f'  <when state="none" next="{name}" />')
        if name == "1dk" and term in layout.dead_keys:
            nested_dk = DK_INDEX[term].name
            ret_actions.append(f'  <when state="1dk" next="{nested_dk}" />')
        ret_actions.append("</action>")
        continue

    # normal key actions
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            ret_actions.append("")
            ret_actions.append(f"<!--{key_name[1:]} -->")
            continue

        for i in [Layer.BASE, Layer.SHIFT]:
            if key_name == "spce" or key_name not in layout.layers[i]:
                continue

            key = layout.layers[i][key_name]
            if i and key == layout.layers[Layer.BASE][key_name]:
                continue
            if key in layout.dead_keys:
                continue

            actions: List[Tuple[str, str]] = []
            for k in DK_INDEX:
                if k in layout.dead_keys:
                    if key in layout.dead_keys[k]:
                        actions.append((DK_INDEX[k].name, layout.dead_keys[k][key]))
            if actions:
                append_actions(xml_proof(key), actions)

    # spacebar actions
    actions = []
    for k in DK_INDEX:
        if k in layout.dead_keys:
            actions.append((DK_INDEX[k].name, layout.dead_keys[k][" "]))
    append_actions("&#x0020;", actions)  # space
    append_actions("&#x00a0;", actions)  # no-break space
    append_actions("&#x202f;", actions)  # fine no-break space

    return ret_actions


def osx_terminators(layout: "KeyboardLayout") -> List[str]:
    """macOS layout, dead key terminators."""

    ret_terminators = []
    for key in DK_INDEX:
        if key not in layout.dead_keys:
            continue
        dk = layout.dead_keys[key]
        name = DK_INDEX[key].name
        term = dk[key]
        if name == "1dk" and term in layout.dead_keys:
            term = dk[" "]
        state = f'state="{name}"'.ljust(18)
        output = f'output="{xml_proof(term)}"'
        ret_terminators.append(f"<when {state} {output} />")
    return ret_terminators


###
# Web: JSON
# To be used with the <x-keyboard> web component.
# https://github.com/OneDeadKey/x-keyboard
#


def web_keymap(layout: "KeyboardLayout") -> Dict[str, List[str]]:
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
            keymap[KEY_CODES["web"][key_name]] = chars

    return keymap


def web_deadkeys(layout: "KeyboardLayout") -> Dict[str, Dict[str, str]]:
    """Web layout, dead keys.

    Returns
    -------
    dict[str, dict[str, str]]
        A dict whose keys are deadkeys and values are key mapping.
    """

    return layout.dead_keys

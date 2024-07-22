"""
Windows: KLC

To be used by the MS Keyboard Layout Creator to generate an installer.
https://www.microsoft.com/en-us/download/details.aspx?id=102134
https://levicki.net/articles/2006/09/29/HOWTO_Build_keyboard_layouts_for_Windows_x64.php

Also supported by KbdEdit: http://www.kbdedit.com (non-free).
Note: blank lines and comments in KLC sections are removed from the output file
because they are not recognized by KBDEdit (as of v19.8.0).
"""

import re
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..template import load_tpl, substitute_lines, substitute_token
from ..utils import DK_INDEX, LAYER_KEYS, SCAN_CODES, Layer, hex_ord, load_data


# return the corresponding char for a symbol
def _get_chr(symbol: str) -> str:
    if len(symbol) > 1 and symbol.endswith("@"):
        # remove dead key symbol for dict access
        key = symbol[:-1]
    else:
        key = symbol

    if len(symbol) == 4:
        char = chr(int(key, base=16))
    else:
        char = symbol

    return char


def _get_langid(locale: str) -> str:
    locale_codes = load_data("win_locales")
    if locale not in locale_codes:
        raise ValueError(f"`{locale}` is not a valid locale")
    return locale_codes[locale]


oem_idx = 0


def klc_virtual_key(layout: "KeyboardLayout", symbols: list, scan_code: str) -> str:
    oem_102_scan_code = "56"
    if layout.angle_mod:
        oem_102_scan_code = "30"
    if scan_code == oem_102_scan_code:
        # manage the ISO key (between shift and Z on ISO keyboards).
        # We're assuming that its scancode is always 56
        # https://www.win.tue.nl/~aeb/linux/kbd/scancodes.html
        return "OEM_102"

    base = _get_chr(symbols[0])
    shifted = _get_chr(symbols[1])

    # Can’t use `isdigit()` because `²` is a digit but we don't want that as a VK
    allowed_digit = "0123456789"
    # We assume that digit row always have digit as VK
    if base in allowed_digit:
        return base
    elif shifted in allowed_digit:
        return shifted

    if shifted.isascii() and shifted.isalpha():
        return shifted

    # VK_OEM_* case
    if base == "," or shifted == ",":
        return "OEM_COMMA"
    elif base == "." or shifted == ".":
        return "OEM_PERIOD"
    elif base == "+" or shifted == "+":
        return "OEM_PLUS"
    elif base == "-" or shifted == "-":
        return "OEM_MINUS"
    elif base == " ":
        return "SPACE"
    else:
        MAX_OEM = 9
        # We affect abitrary OEM VK and it will not match the one
        # in distributed layout. It can cause issue if a application
        # is awaiting a particular OEM_ for a hotkey
        global oem_idx
        oem_idx += 1
        if oem_idx <= MAX_OEM:
            return "OEM_" + str(oem_idx)
        else:
            raise Exception("Too many OEM keys")


def klc_keymap(layout: "KeyboardLayout") -> List[str]:
    """Windows layout, main part."""

    supported_symbols = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    global oem_idx
    oem_idx = 0  # Python trick to do equivalent of C static variable
    output = []
    qwerty_vk = load_data("qwerty_vk")

    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            continue

        if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
            continue  # these two keys are not supported yet

        symbols = []
        description = "//"
        is_alpha = False

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
                        is_alpha = symbol.upper() != symbol
                    if symbol not in supported_symbols:
                        symbol = hex_ord(symbol)
                symbols.append(symbol)
            else:
                desc = " "
                symbols.append("-1")
            description += " " + desc

        scan_code = SCAN_CODES["klc"][key_name]

        virtual_key = qwerty_vk[scan_code]
        if not layout.qwerty_shortcuts:
            virtual_key = klc_virtual_key(layout, symbols, scan_code)

        if layout.has_altgr:
            output.append(
                "\t".join(
                    [
                        scan_code,
                        virtual_key,
                        "1" if is_alpha else "0",  # affected by CapsLock?
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
                        scan_code,
                        virtual_key,
                        "1" if is_alpha else "0",  # affected by CapsLock?
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
            if base == k and alt in base:
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


def c_keymap(layout: "KeyboardLayout") -> List[str]:
    """Windows C layout, main part."""

    supported_symbols = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    qwerty_vk = load_data("qwerty_vk")

    global oem_idx
    oem_idx = 0  # Python trick to do equivalent of C static variable
    output = []
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            continue

        if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
            continue  # these two keys are not supported yet

        symbols = []
        dead_symbols = []
        is_alpha = False
        has_dead_key = False

        for i in [Layer.BASE, Layer.SHIFT, Layer.ALTGR, Layer.ALTGR_SHIFT]:
            layer = layout.layers[i]

            if key_name in layer:
                symbol = layer[key_name]
                desc = symbol
                dead = "WCH_NONE"
                if symbol in layout.dead_keys:
                    desc = layout.dead_keys[symbol][" "]
                    symbol = "WCH_DEAD"
                    dead = hex_ord(desc)
                    has_dead_key = True
                else:
                    if i == Layer.BASE:
                        is_alpha = symbol.upper() != symbol
                    if symbol not in supported_symbols:
                        symbol = hex_ord(symbol)
                symbols.append(symbol)
                dead_symbols.append(dead)
            else:
                desc = " "
                symbols.append("WCH_NONE")
                dead_symbols.append("WCH_NONE")

        scan_code = SCAN_CODES["klc"][key_name]

        virtual_key = qwerty_vk[scan_code]
        if not layout.qwerty_shortcuts:
            virtual_key = klc_virtual_key(layout, symbols, scan_code)

        if len(virtual_key) == 1:
            virtual_key_id = f"'{virtual_key}'"
        else:
            virtual_key_id = f"VK_{virtual_key}"

        def process_symbol(symbol: str) -> str:
            if len(symbol) == 4:
                return f"0x{symbol}"
            if len(symbol) == 1:
                return f"'{symbol}'"
            return symbol

        symbols[:] = [process_symbol(symbol) for symbol in symbols]
        dead_symbols[:] = [process_symbol(symbol) for symbol in dead_symbols]

        def key_list(
            key_syms: List[str],
            virt_key: str = "0xff",
            has_altgr: bool = False,
            is_alpha: bool = False,
        ) -> str:
            cols = [
                virt_key,
                "CAPLOK" if is_alpha else "0",  # affected by CapsLock?
                key_syms[0],
                key_syms[1],  # base layer
                "WCH_NONE",
                "WCH_NONE",  # ctrl layer
            ]
            if has_altgr:
                cols += [
                    key_syms[2],
                    key_syms[3],
                ]
            return "\t,".join(cols)

        output.append(
            f"\t{{{key_list(symbols, virtual_key_id, layout.has_altgr, is_alpha)}}},"
        )
        if has_dead_key:
            output.append(
                f"\t{{{key_list(dead_symbols, has_altgr=layout.has_altgr, is_alpha=is_alpha)}}},"
            )

    return output


def c_deadkeys(layout: "KeyboardLayout") -> List[str]:
    """Windows C layout, dead keys."""

    output = []

    for k in DK_INDEX:
        if k not in layout.dead_keys:
            continue
        dk = layout.dead_keys[k]

        output.append(f"// DEADKEY: {DK_INDEX[k].name.upper()}")

        for base, alt in dk.items():
            if base == k and alt in base:
                continue

            if base in layout.dead_keys:
                base = layout.dead_keys[base][" "]

            if alt in layout.dead_keys:
                alt = layout.dead_keys[alt][" "]
                dead_alt = "0x0001"
            else:
                dead_alt = "0x0000"
            ext = hex_ord(alt)

            output.append(
                f"DEADTRANS(0x{hex_ord(base)}\t, 0x{hex_ord(dk[' '])}\t, 0x{ext}\t, {dead_alt}), /* {base} -> {alt} */"
            )

        output.append("")

    return output[:-1]


def c_dk_index(layout: "KeyboardLayout") -> List[str]:
    """Windows layout, dead key index."""

    output = []
    for k in DK_INDEX:
        if k not in layout.dead_keys:
            continue
        term = layout.dead_keys[k][" "]
        output.append(f'L"\\\\x{hex_ord(term)}"\tL"{DK_INDEX[k].name.upper()}",')
    return output


def klc(layout: "KeyboardLayout") -> str:
    """Windows driver (warning: requires CR/LF + UTF16LE encoding)"""

    if len(layout.meta["name8"]) > 8:
        raise ValueError("`name8` max length is 8 charaters")

    # check `version` format
    # it must be `a.b.c[.d]`
    version = re.compile(r"^\d+\.\d+\.\d+(\.\d+)?$")
    if version.match(layout.meta["version"]) is None:
        raise ValueError("`version` must be in `a.b.c[.d]` form")
    locale = layout.meta["locale"]
    langid = _get_langid(locale)

    # fmt: off
    out = load_tpl(layout, ".klc")
    out = substitute_lines(out, "LAYOUT",         klc_keymap(layout))
    out = substitute_lines(out, "DEAD_KEYS",      klc_deadkeys(layout))
    out = substitute_lines(out, "DEAD_KEY_INDEX", klc_dk_index(layout))
    out = substitute_token(out, "localeid",       f"0000{langid}")
    out = substitute_token(out, "locale",         locale)
    out = substitute_token(out, "encoding",       "utf-16le")
    # fmt: on
    return out


def klc_rc(layout: "KeyboardLayout") -> str:
    """Windows resource file for C drivers"""
    out = load_tpl(layout, ".RC")
    # version numbers are in "a,b,c,d" format
    version = layout.meta["version"].replace(".", ",")
    out = substitute_token(out, "rc_version", version)
    return out


def klc_c(layout: "KeyboardLayout") -> str:
    """Windows keymap file for C drivers"""
    out = load_tpl(layout, ".C")
    out = substitute_lines(out, "LAYOUT", c_keymap(layout))
    out = substitute_lines(out, "DEAD_KEYS", c_deadkeys(layout))
    out = substitute_lines(out, "DEAD_KEY_INDEX", c_dk_index(layout))
    return out

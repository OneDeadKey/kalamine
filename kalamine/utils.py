import pkgutil
from dataclasses import dataclass
from enum import Enum, IntEnum, unique
from typing import Dict, List, Optional, Self

import yaml


def hex_ord(char: str) -> str:
    # assert len(char) == 1, char
    if len(char) != 1:
        print(f"ERROR: hex_ord: “{char}”")
        char = char[0]
    return hex(ord(char))[2:].zfill(4)


def lines_to_text(lines: List[str], indent: str = "") -> str:
    """
    From a list lines of string, produce a string concatenating the elements
    of lines indented by prepending indent and followed by a new line.
    Example: lines_to_text(["one", "two", "three"], "  ") returns
    '  one\n  two\n  three'
    """
    out = ""
    for line in lines:
        if len(line):
            out += indent + line
        out += "\n"
    return out[:-1]


def text_to_lines(text: str) -> List[str]:
    """Split given text into lines"""
    return text.split("\n")


def load_data(filename: str) -> Dict:
    descriptor = pkgutil.get_data(__package__, f"data/{filename}.yaml")
    if not descriptor:
        return {}
    return yaml.safe_load(descriptor.decode("utf-8"))


class Layer(IntEnum):
    """A layer designation."""

    BASE = 0
    SHIFT = 1
    ODK = 2
    ODK_SHIFT = 3
    ALTGR = 4
    ALTGR_SHIFT = 5

    @classmethod
    def parse(cls, raw: str) -> Self | None:
        match raw.casefold():
            case "1dk":
                return cls(cls.ODK)
            case "1dk_shift":
                return cls(cls.ODK_SHIFT)
            case _:
                for l in cls:
                    if raw.casefold() == l.name.casefold():
                        return l
                    try:
                        if int(raw, base=10) == l.value:
                            return l
                    except:
                        pass
                return None

    def next(self) -> "Layer":
        """The next layer in the layer ordering."""
        return Layer(int(self) + 1)

    def necromance(self) -> "Layer":
        """Remove the effect of the dead key if any."""
        if self == Layer.ODK:
            return Layer.BASE
        elif self == Layer.ODK_SHIFT:
            return Layer.SHIFT
        return self


def upper_key(letter: Optional[str]) -> Optional[str]:
    if not letter:
        return None
    
    special_symbols = {s.value for s in SystemSymbol}
    if letter in special_symbols:
        return letter

    custom_alpha = {
        "\u00df": "\u1e9e",  # ß ẞ
        "\u007c": "\u00a6",  # | ¦
        "\u003c": "\u2264",  # < ≤
        "\u003e": "\u2265",  # > ≥
        "\u2020": "\u2021",  # † ‡
        "\u2190": "\u21d0",  # ← ⇐
        "\u2191": "\u21d1",  # ↑ ⇑
        "\u2192": "\u21d2",  # → ⇒
        "\u2193": "\u21d3",  # ↓ ⇓
        # FIXME: strange behavior
        "\u00b5": None,      # µ (to avoid getting `Μ` as uppercase)
    }
    if letter in custom_alpha:
        return custom_alpha[letter]

    if len(letter) == 1 and letter.upper() != letter.lower():
        return letter.upper()
    
    return None


def pretty_upper_key(letter: Optional[str], blank_if_obvious: bool = True) -> str:
    """This is used for presentation purposes: in a key, the upper character
    becomes blank if it's an obvious uppercase version of the base character."""

    if (letterʹ := upper_key(letter)) is None:
        return " "

    # dead key or non-letter character
    return " " if blank_if_obvious else letterʹ


@dataclass
class DeadKeyDescr:
    char: str
    name: str
    base: str
    alt: str
    alt_space: str
    alt_self: str

    @staticmethod
    def is_dead_key(raw: str) -> bool:
        return len(raw) == 2 and raw[0] == "*"
    
    @staticmethod
    def parse_dead_key(raw: str) -> Optional[str]:
        if len(raw) == 2 and raw[0] == "*":
            return raw
        else:
            return None


DEAD_KEYS = [DeadKeyDescr(**data) for data in load_data("dead_keys")]

DK_INDEX: Dict[str, DeadKeyDescr] = {}
for dk in DEAD_KEYS:
    DK_INDEX[dk.char] = dk

SCAN_CODES = load_data("scan_codes")

ODK_ID = "**"  # must match the value in dead_keys.yaml

@unique
class SystemSymbol(Enum):
    Alt = "⎇"
    AltGr = "⇮"
    BackSpace = "⌫"
    CapsLock = "⇬"
    Compose = "⎄"
    Control = "⎈"
    Escape = "⎋"
    Return = "⏎"
    Shift = "⇧"

    @classmethod
    def parse(cls, raw: str) -> Optional[Self]:
        for s in cls:
            if raw == s.value:
                return s
        else:
            return None

@dataclass
class SpecialSymbolEntry:
    value: str
    pretty: str

class SpecialSymbol(Enum):
    NarrowNoBreakSpace = SpecialSymbolEntry("\u202F", "n⍽")
    NoBreakSpace = SpecialSymbolEntry("\u00A0", "⍽")
    Space = SpecialSymbolEntry(" ", "␣")

    @classmethod
    def parse(cls, raw: str) -> str:
        for s in cls:
            if raw == s.value.pretty:
                return s.value.value
        else:
            return raw
        
    @classmethod
    def prettify(cls, raw: str) -> str:
        for s in cls:
            if raw == s.value.value:
                return s.value.pretty
        else:
            return raw

LAYER_KEYS = [
    "- Digits",
    "ae01",
    "ae02",
    "ae03",
    "ae04",
    "ae05",
    "ae06",
    "ae07",
    "ae08",
    "ae09",
    "ae10",
    "- Letters, first row",
    "ad01",
    "ad02",
    "ad03",
    "ad04",
    "ad05",
    "ad06",
    "ad07",
    "ad08",
    "ad09",
    "ad10",
    "- Letters, second row",
    "ac01",
    "ac02",
    "ac03",
    "ac04",
    "ac05",
    "ac06",
    "ac07",
    "ac08",
    "ac09",
    "ac10",
    "- Letters, third row",
    "ab01",
    "ab02",
    "ab03",
    "ab04",
    "ab05",
    "ab06",
    "ab07",
    "ab08",
    "ab09",
    "ab10",
    "- Pinky keys",
    "ae11",
    "ae12",
    "ae13",
    "ad11",
    "ad12",
    "ac11",
    "ab11",
    "tlde",
    "bksl",
    "lsgt",
    "- Space bar",
    "spce",
    "menu",
    "lfsh",
    "rtsh",
    "lalt",
    "ralt",
    "lctl",
    "rctl",
    "muhe",
    "henk",
    "- Miscellaneous",
    "i172",
    "rtrn",
    "bksp",
    "esc",
]

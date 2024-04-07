import pkgutil
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional

import yaml


def hex_ord(char: str) -> str:
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
    def parse(cls, raw: str) -> Optional["Layer"]:
        rawʹ = raw.casefold()
        if rawʹ == "1dk":
            return cls(cls.ODK)
        elif rawʹ == "1dk_shift":
            return cls(cls.ODK_SHIFT)
        else:
            for layer in cls:
                if rawʹ == layer.name.casefold():
                    return layer
                try:
                    if int(raw, base=10) == layer.value:
                        return layer
                except ValueError:
                    pass
            return None

    def next(self) -> "Layer":
        """The next layer in the layer ordering."""
        return Layer(int(self) + 1)

    def necromance(self) -> "Layer":
        """Remove the effect of the dead key if any."""
        if self is Layer.ODK:
            return Layer.BASE
        elif self is Layer.ODK_SHIFT:
            return Layer.SHIFT
        return self


def upper_key(letter: Optional[str], blank_if_obvious: bool = True) -> str:
    """This is used for presentation purposes: in a key, the upper character
    becomes blank if it's an obvious uppercase version of the base character."""

    if letter is None:
        return " "

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
        "\u00b5": " ",  # µ (to avoid getting `Μ` as uppercase)
    }
    if letter in custom_alpha:
        return custom_alpha[letter]

    if len(letter) == 1 and letter.upper() != letter.lower():
        return letter.upper()

    # dead key or non-letter character
    return " " if blank_if_obvious else letter


@dataclass
class DeadKeyDescr:
    char: str
    name: str
    base: str
    alt: str
    alt_space: str
    alt_self: str


DEAD_KEYS = [DeadKeyDescr(**data) for data in load_data("dead_keys")]

DK_INDEX = {}
for dk in DEAD_KEYS:
    DK_INDEX[dk.char] = dk

ODK_ID = "**"  # must match the value in dead_keys.yaml

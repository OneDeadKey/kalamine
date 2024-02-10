import pkgutil
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List

import yaml


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


@dataclass
class DeadKeyDescr:
    char: str
    name: str
    base: str
    alt: str
    alt_space: str
    alt_self: str


DEAD_KEYS = [DeadKeyDescr(**data) for data in load_data("dead_keys")]

ODK_ID = "**"  # must match the value in dead_keys.yaml
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
]

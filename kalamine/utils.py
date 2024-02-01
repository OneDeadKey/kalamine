#!/usr/bin/env python3
import os
from enum import IntEnum
from pathlib import Path
from typing import Dict, List

import yaml


def lines_to_text(lines: List[str], indent: str = ""):
    out = ""
    for line in lines:
        if len(line):
            out += indent + line
        out += "\n"
    return out[:-1]


def text_to_lines(text: str) -> List[str]:
    return text.split("\n")


def load_data(filename: str) -> Dict:
    filepath = Path(__file__).parent / "data" / filename
    return yaml.load(filepath.open(encoding="utf-8"), Loader=yaml.SafeLoader)


class Layer(IntEnum):
    """A layer designation."""

    BASE = 0
    SHIFT = 1
    ODK = 2
    ODK_SHIFT = 3
    ALTGR = 4
    ALTGR_SHIFT = 5


DEAD_KEYS = load_data("dead_keys.yaml")
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

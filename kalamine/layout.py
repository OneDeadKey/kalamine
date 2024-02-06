#!/usr/bin/env python3
import copy
import datetime
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, TypeVar

import click
import tomli
import yaml
from lxml import etree  # type: ignore

from .template import (
    ahk_keymap,
    ahk_shortcuts,
    klc_deadkeys,
    klc_dk_index,
    klc_keymap,
    osx_actions,
    osx_keymap,
    osx_terminators,
    web_deadkeys,
    web_keymap,
    xkb_keymap,
)
from .utils import (
    DEAD_KEYS,
    LAYER_KEYS,
    ODK_ID,
    Layer,
    lines_to_text,
    load_data,
    text_to_lines,
)

###
# Helpers
#


def upper_key(letter: str, blank_if_obvious: bool = True) -> str:
    """This is used for presentation purposes: in a key, the upper character
    becomes blank if it's an obvious uppercase version of the base character."""

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


def substitute_lines(text: str, variable: str, lines: List[str]) -> str:
    prefix = "KALAMINE::"
    exp = re.compile(".*" + prefix + variable + ".*")

    indent = ""
    for line in text.split("\n"):
        m = exp.match(line)
        if m:
            indent = m.group().split(prefix)[0]
            break

    return exp.sub(lines_to_text(lines, indent), text)


def substitute_token(text: str, token: str, value: str) -> str:
    exp = re.compile("\\$\\{" + token + "(=[^\\}]*){0,1}\\}")
    return exp.sub(value, text)


def load_tpl(layout: "KeyboardLayout", ext: str) -> str:
    tpl = "base"
    if layout.has_altgr:
        tpl = "full"
        if layout.has_1dk and ext.startswith(".xkb"):
            tpl = "full_1dk"
    out = (Path(__file__).parent / "tpl" / (tpl + ext)).read_text(encoding="utf-8")
    out = substitute_lines(out, "GEOMETRY_base", layout.base)
    out = substitute_lines(out, "GEOMETRY_full", layout.full)
    out = substitute_lines(out, "GEOMETRY_altgr", layout.altgr)
    for key, value in layout.meta.items():
        out = substitute_token(out, key, value)
    return out


def load_descriptor(file_path: Path) -> Dict:
    if file_path.suffix in [".yaml", ".yml"]:
        with file_path.open(encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.SafeLoader)

    with file_path.open(mode="rb") as dfile:
        return tomli.load(dfile)


###
# Constants
#


CONFIG = {
    "author": "nobody",
    "license": "WTFPL - Do What The Fuck You Want Public License",
    "geometry": "ISO",
}

SPACEBAR = {
    "shift": " ",
    "altgr": " ",
    "altgr_shift": " ",
    "1dk": "'",
    "1dk_shift": "'",
}


@dataclass
class RowDescr:
    offset: int
    keys: List[str]


T = TypeVar("T", bound="GeometryDescr")


@dataclass
class GeometryDescr:
    template: str
    rows: List[RowDescr]

    @classmethod
    def from_dict(cls: Type[T], src: Dict) -> T:
        return cls(
            template=src["template"], rows=[RowDescr(**row) for row in src["rows"]]
        )


geometry_data = load_data("geometry.yaml")

GEOMETRY = {key: GeometryDescr.from_dict(val) for key, val in geometry_data.items()}


###
# Main
#


class KeyboardLayout:
    """Lafayette-style keyboard layout: base + 1dk + altgr layers."""

    def __init__(self, filepath: Path, angle_mod: bool = False) -> None:
        """Import a keyboard layout to instanciate the object."""

        # initialize a blank layout
        self.layers: Dict[Layer, Dict[str, str]] = {layer: {} for layer in Layer}
        self.dk_set: Set[str] = set()
        self.dead_keys: Dict[str, Dict[str, str]] = {}  # dictionary subset of DEAD_KEYS
        self.meta = CONFIG.copy()  # default parameters, hardcoded
        self.has_altgr = False
        self.has_1dk = False

        # load the YAML data (and its ancessor, if any)
        try:
            cfg = load_descriptor(filepath)
            if "extends" in cfg:
                path = filepath.parent / cfg["extends"]
                ext = load_descriptor(path)
                ext.update(cfg)
                cfg = ext
        except Exception as exc:
            click.echo("File could not be parsed.", err=True)
            click.echo(f"Error: {exc}.", err=True)
            sys.exit(1)

        # metadata: self.meta
        for k in cfg:
            if (
                k != "base"
                and k != "full"
                and k != "altgr"
                and not isinstance(cfg[k], dict)
            ):
                self.meta[k] = cfg[k]
        filename = filepath.stem
        self.meta["name"] = cfg["name"] if "name" in cfg else filename
        self.meta["name8"] = cfg["name8"] if "name8" in cfg else self.meta["name"][0:8]
        self.meta["fileName"] = self.meta["name8"].lower()
        self.meta["lastChange"] = datetime.date.today().isoformat()

        # keyboard layers: self.layers & self.dead_keys
        rows = copy.deepcopy(GEOMETRY[self.meta["geometry"]].rows)

        # Angle Mod permutation
        if angle_mod:
            last_row = rows[3]
            if last_row.keys[0] == "lsgt":
                # should bevome ['ab05', 'lsgt', 'ab01', 'ab02', 'ab03', 'ab04']
                last_row.keys[:6] = [last_row.keys[5]] + last_row.keys[:5]
            else:
                click.echo(
                    "Warning: geometry does not support angle-mod; ignoring the --angle-mod argument"
                )

        if "full" in cfg:
            full = text_to_lines(cfg["full"])
            self._parse_template(full, rows, Layer.BASE)
            self._parse_template(full, rows, Layer.ALTGR)
            self.has_altgr = True
        else:
            base = text_to_lines(cfg["base"])
            self._parse_template(base, rows, Layer.BASE)
            self._parse_template(base, rows, Layer.ODK)
            if "altgr" in cfg:
                self.has_altgr = True
                self._parse_template(text_to_lines(cfg["altgr"]), rows, Layer.ALTGR)

        # space bar
        spc = SPACEBAR.copy()
        if "spacebar" in cfg:
            for k in cfg["spacebar"]:
                spc[k] = cfg["spacebar"][k]
        self.layers[Layer.BASE]["spce"] = " "
        self.layers[Layer.SHIFT]["spce"] = spc["shift"]
        if True or self.has_1dk:  # XXX self.has_1dk is not defined yet
            self.layers[Layer.ODK]["spce"] = spc["1dk"]
            self.layers[Layer.ODK_SHIFT]["spce"] = (
                spc["shift_1dk"] if "shift_1dk" in spc else spc["1dk"]
            )
        if self.has_altgr:
            self.layers[Layer.ALTGR]["spce"] = spc["altgr"]
            self.layers[Layer.ALTGR_SHIFT]["spce"] = spc["altgr_shift"]

        self._parse_dead_keys(spc)

    def _parse_dead_keys(self, spc: Dict[str, str]) -> None:
        """Build a deadkey dict."""

        def layout_has_char(char: str) -> bool:
            all_layers = [Layer.BASE, Layer.SHIFT]
            if self.has_altgr:
                all_layers += [Layer.ALTGR, Layer.ALTGR_SHIFT]

            for layer_index in all_layers:
                for id in self.layers[layer_index]:
                    if self.layers[layer_index][id] == char:
                        return True
            return False

        all_spaces: List[str] = []
        for space in ["\u0020", "\u00a0", "\u202f"]:
            if layout_has_char(space):
                all_spaces.append(space)

        self.dead_keys = {}
        for dk in DEAD_KEYS:
            id = dk.char
            if id not in self.dk_set:
                continue

            self.dead_keys[id] = {}
            deadkey = self.dead_keys[id]
            deadkey[id] = dk.alt_self

            if id == ODK_ID:
                self.has_1dk = True
                for key_name in LAYER_KEYS:
                    if key_name.startswith("-"):
                        continue
                    for layer in [Layer.ODK_SHIFT, Layer.ODK]:
                        if key_name in self.layers[layer]:
                            deadkey[self.layers[layer.necromance()][key_name]] = (
                                self.layers[layer][key_name]
                            )
                for space in all_spaces:
                    deadkey[space] = spc["1dk"]

            else:
                base = dk.base
                alt = dk.alt
                for i in range(len(base)):
                    if layout_has_char(base[i]):
                        deadkey[base[i]] = alt[i]
                for space in all_spaces:
                    deadkey[space] = dk.alt_space

    def _parse_template(
        self, template: List[str], rows: List[RowDescr], layer_number: Layer
    ) -> None:
        """Extract a keyboard layer from a template."""

        j = 0
        col_offset = 0 if layer_number == Layer.BASE else 2
        for row in rows:
            i = row.offset + col_offset
            keys = row.keys

            base = list(template[2 + j * 3])
            shift = list(template[1 + j * 3])

            for key in keys:
                base_key = ("*" if base[i - 1] == "*" else "") + base[i]
                shift_key = ("*" if shift[i - 1] == "*" else "") + shift[i]

                # in the BASE layer, if the base character is undefined, shift prevails
                if base_key == " ":
                    if layer_number == Layer.BASE:
                        base_key = shift_key.lower()

                # in other layers, if the shift character is undefined, base prevails
                elif shift_key == " ":
                    if layer_number == Layer.ALTGR:
                        shift_key = upper_key(base_key)
                    elif layer_number == Layer.ODK:
                        shift_key = upper_key(base_key)
                        # shift_key = upper_key(base_key, blank_if_obvious=False)

                if base_key != " ":
                    self.layers[layer_number][key] = base_key
                if shift_key != " ":
                    self.layers[layer_number.next()][key] = shift_key

                for dk in DEAD_KEYS:
                    if base_key == dk.char or shift_key == dk.char:
                        self.dk_set.add(dk.char)

                i += 6
            j += 1

    ###
    # Geometry: base, full, altgr
    #

    def _fill_template(
        self, template: List[str], rows: List[RowDescr], layer_number: Layer
    ) -> List[str]:
        """Fill a template with a keyboard layer."""

        if layer_number == Layer.BASE:
            col_offset = 0
            shift_prevails = True
        else:  # AltGr or 1dk
            col_offset = 2
            shift_prevails = False

        j = 0
        for row in rows:
            i = row.offset + col_offset
            keys = row.keys

            base = list(template[2 + j * 3])
            shift = list(template[1 + j * 3])

            for key in keys:
                base_key = " "
                if key in self.layers[layer_number]:
                    base_key = self.layers[layer_number][key]

                shift_key = " "
                if key in self.layers[layer_number.next()]:
                    shift_key = self.layers[layer_number.next()][key]

                dead_base = len(base_key) == 2 and base_key[0] == "*"
                dead_shift = len(shift_key) == 2 and shift_key[0] == "*"

                if shift_prevails:
                    shift[i] = shift_key[-1]
                    if dead_shift:
                        shift[i - 1] = "*"
                    if upper_key(base_key) != shift_key:
                        base[i] = base_key[-1]
                        if dead_base:
                            base[i - 1] = "*"
                else:
                    base[i] = base_key[-1]
                    if dead_base:
                        base[i - 1] = "*"
                    if upper_key(base_key) != shift_key:
                        shift[i] = shift_key[-1]
                        if dead_shift:
                            shift[i - 1] = "*"

                i += 6

            template[2 + j * 3] = "".join(base)
            template[1 + j * 3] = "".join(shift)
            j += 1

        return template

    def _get_geometry(self, layers: Optional[List[Layer]] = None) -> List[str]:
        """`geometry` view of the requested layers."""
        layers = layers or [Layer.BASE]

        rows = GEOMETRY[self.geometry].rows
        template = GEOMETRY[self.geometry].template.split("\n")[:-1]
        for i in layers:
            template = self._fill_template(template, rows, i)
        return template

    @property
    def geometry(self) -> str:
        """ANSI, ISO, ERGO."""
        return self.meta["geometry"].upper()

    @geometry.setter
    def geometry(self, value: str) -> None:
        """ANSI, ISO, ERGO."""
        shape = value.upper()
        if shape not in ["ANSI", "ISO", "ERGO"]:
            shape = "ISO"
        self.meta["geometry"] = shape

    @property
    def base(self) -> List[str]:
        """Base + 1dk layers."""
        return self._get_geometry([Layer.BASE, Layer.ODK])

    @property
    def full(self) -> List[str]:
        """Base + AltGr layers."""
        return self._get_geometry([Layer.BASE, Layer.ALTGR])

    @property
    def altgr(self) -> List[str]:
        """AltGr layer only."""
        return self._get_geometry([Layer.ALTGR])

    ###
    # OS-specific drivers: keylayout, klc, xkb, xkb_patch
    #

    @property
    def keylayout(self) -> str:
        """macOS driver"""
        out = load_tpl(self, ".keylayout")
        for i, layer in enumerate(osx_keymap(self)):
            out = substitute_lines(out, "LAYER_" + str(i), layer)
        out = substitute_lines(out, "ACTIONS", osx_actions(self))
        out = substitute_lines(out, "TERMINATORS", osx_terminators(self))
        return out

    @property
    def ahk(self) -> str:
        """Windows AHK driver"""
        out = load_tpl(self, ".ahk")
        out = substitute_lines(out, "LAYOUT", ahk_keymap(self))
        out = substitute_lines(out, "ALTGR", ahk_keymap(self, True))
        out = substitute_lines(out, "SHORTCUTS", ahk_shortcuts(self))
        return out

    @property
    def klc(self) -> str:
        """Windows driver (warning: requires CR/LF + UTF16LE encoding)"""
        out = load_tpl(self, ".klc")
        out = substitute_lines(out, "LAYOUT", klc_keymap(self))
        out = substitute_lines(out, "DEAD_KEYS", klc_deadkeys(self))
        out = substitute_lines(out, "DEAD_KEY_INDEX", klc_dk_index(self))
        out = substitute_token(out, "encoding", "utf-16le")
        return out

    @property
    def xkb(self) -> str:  # will not work with Wayland
        """GNU/Linux driver (standalone / user-space)"""
        out = load_tpl(self, ".xkb")
        out = substitute_lines(out, "LAYOUT", xkb_keymap(self, xkbcomp=True))
        return out

    @property
    def xkb_patch(self) -> str:
        """GNU/Linux driver (xkb patch, system or user-space)"""
        out = load_tpl(self, ".xkb_patch")
        out = substitute_lines(out, "LAYOUT", xkb_keymap(self, xkbcomp=False))
        return out

    ###
    # JSON output: keymap (base+altgr layers) and dead keys
    #

    @property
    def json(self) -> Dict:
        """JSON layout descriptor"""
        return {
            "name": self.meta["name"],
            "description": self.meta["description"],
            "geometry": self.meta["geometry"].lower(),
            "keymap": web_keymap(self),
            "deadkeys": web_deadkeys(self),
            "altgr": self.has_altgr,
        }

    ###
    # SVG output
    #

    @property
    def svg(self) -> etree.ElementTree:
        """SVG drawing"""

        # Parse SVG data
        filepath = Path(__file__).parent / "tpl" / "x-keyboard.svg"
        svg = etree.parse(str(filepath), etree.XMLParser(remove_blank_text=True))
        ns = {"svg": "http://www.w3.org/2000/svg"}

        # Get Layout data
        keymap = web_keymap(self)
        deadkeys = web_deadkeys(self)
        # breakpoint()

        def set_key_label(label_element, char: str):
            if char not in deadkeys:
                label_element.text = char
            else:  # only last char for deadkeys
                label_element.text = "★" if char == "**" else char[-1]
                label_element.set(  # Apply special class for deadkeys
                    "class", label_element.get("class") + " deadKey diacritic"
                )

        # Fill-in with layout
        for name, chars in keymap.items():
            for key in svg.xpath(f'//svg:g[@id="{name}"]', namespaces=ns):
                # Print 1-4 level chars
                for level_num, char in enumerate(chars, start=1):
                    # Do not print the same label twice (lower and upper)
                    if level_num == 1 and chars[0] == chars[1].lower():
                        continue

                    for location in key.xpath(
                        f"svg:g/svg:text[@class='level{level_num}']", namespaces=ns
                    ):
                        set_key_label(location, char)

                # Print 5-6 levels (1dk deadkeys)
                if deadkeys and (main_deadkey := deadkeys.get("**")):
                    for level_num, char in enumerate(chars[:2], start=5):
                        dead_char = main_deadkey.get(char)
                        if level_num == Layer.ODK_SHIFT:
                            # Do not print the same label twice (lower and upper)
                            if dead_char_previous := main_deadkey.get(chars[0]):
                                if upper_key(dead_char_previous) == dead_char:
                                    continue

                        if dead_char:
                            for location in key.xpath(
                                f"svg:g/svg:text[@class='level{level_num} dk']",
                                namespaces=ns,
                            ):
                                set_key_label(location, dead_char)

        return svg

import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, TypeVar

import click
import tomli
import yaml

from .utils import (
    DEAD_KEYS,
    LAYER_KEYS,
    ODK_ID,
    Layer,
    load_data,
    text_to_lines,
    upper_key,
)

###
# Helpers
#


def load_layout(layout_path: Path) -> Dict:
    """Load the TOML/YAML layout description data (and its ancessor, if any)."""

    def load_descriptor(file_path: Path) -> Dict:
        if file_path.suffix in [".yaml", ".yml"]:
            with file_path.open(encoding="utf-8") as file:
                return yaml.load(file, Loader=yaml.SafeLoader)

        with file_path.open(mode="rb") as dfile:
            return tomli.load(dfile)

    try:
        cfg = load_descriptor(layout_path)
        if "name" not in cfg:
            cfg["name"] = layout_path.stem
        if "extends" in cfg:
            parent_path = layout_path.parent / cfg["extends"]
            ext = load_descriptor(parent_path)
            ext.update(cfg)
            cfg = ext
        return cfg

    except Exception as exc:
        click.echo("File could not be parsed.", err=True)
        click.echo(f"Error: {exc}.", err=True)
        sys.exit(1)


###
# Constants
#


# fmt: off
@dataclass
class MetaDescr:
    name:        str = "custom"
    name8:       str = "custom"
    variant:     str = "custom"
    fileName:    str = "custom"
    locale:      str = "us"
    geometry:    str = "ISO"
    description: str = ""
    author:      str = "nobody"
    license:     str = ""
    version:     str = "0.0.1"


@dataclass
class SpacebarDescr:
    shift:       str = " "
    altgr:       str = " "
    altgt_shift: str = " "
    odk:         str = "'"
    odk_shift:   str = "'"
# fmt: on


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


GEOMETRY = {
    key: GeometryDescr.from_dict(val) for key, val in load_data("geometry").items()
}


###
# Main
#


class KeyboardLayout:
    """Lafayette-style keyboard layout: base + 1dk + altgr layers."""

    # self.meta = {key: MetaDescr.from_dict(val) for key, val in geometry_data.items()}

    def __init__(
        self, layout_data: Dict, angle_mod: bool = False, qwerty_shortcuts: bool = False
    ) -> None:
        """Import a keyboard layout to instanciate the object."""

        # initialize a blank layout
        self.layers: Dict[Layer, Dict[str, str]] = {layer: {} for layer in Layer}
        self.dk_set: Set[str] = set()
        self.dead_keys: Dict[str, Dict[str, str]] = {}  # dictionary subset of DEAD_KEYS
        # self.meta = Dict[str, str] = {} # default parameters, hardcoded
        self.meta = CONFIG.copy()  # default parameters, hardcoded
        self.has_altgr = False
        self.has_1dk = False
        self.qwerty_shortcuts = qwerty_shortcuts
        self.angle_mod = angle_mod

        # metadata: self.meta
        for k in layout_data:
            if (
                k != "base"
                and k != "full"
                and k != "altgr"
                and not isinstance(layout_data[k], dict)
            ):
                self.meta[k] = layout_data[k]
        self.meta["name8"] = (
            layout_data["name8"] if "name8" in layout_data else self.meta["name"][0:8]
        )
        self.meta["fileName"] = self.meta["name8"].lower()

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
                self.angle_mod = False

        if "full" in layout_data:
            full = text_to_lines(layout_data["full"])
            self._parse_template(full, rows, Layer.BASE)
            self._parse_template(full, rows, Layer.ALTGR)
            self.has_altgr = True
        else:
            base = text_to_lines(layout_data["base"])
            self._parse_template(base, rows, Layer.BASE)
            self._parse_template(base, rows, Layer.ODK)
            if "altgr" in layout_data:
                self.has_altgr = True
                self._parse_template(
                    text_to_lines(layout_data["altgr"]), rows, Layer.ALTGR
                )

        # space bar
        spc = SPACEBAR.copy()
        if "spacebar" in layout_data:
            for k in layout_data["spacebar"]:
                spc[k] = layout_data["spacebar"][k]
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

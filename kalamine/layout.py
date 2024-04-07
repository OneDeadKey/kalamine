import copy
import itertools
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar

import click
import tomli
import yaml

from .key import KEYS
from .utils import (
    DEAD_KEYS,
    DK_INDEX,
    ODK_ID,
    DeadKeyDescr,
    Layer,
    SpecialSymbol,
    SystemSymbol,
    load_data,
    text_to_lines,
    pretty_upper_key,
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
    digit_row: int = 0

    @classmethod
    def from_dict(cls: Type[T], src: Dict) -> T:
        return cls(
            template=src["template"], rows=[RowDescr(**row) for row in src["rows"]]
        )


GEOMETRY = {
    key: GeometryDescr.from_dict(val) for key, val in load_data("geometry").items()
}


@dataclass
class LayoutSymbols:
    strings: Set[str]
    deadKeys: Set[str]


TEMPLATE_DUMMY_KEY = "xxxx"
TEMPLATE_KEY_WIDTH = 6


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

        # Custom dead keys
        self.custom_dead_keys = self._parse_dead_keys(layout_data.get("dead_keys", {}))

        # keyboard layers: self.layers & self.dead_keys
        rows = copy.deepcopy(GEOMETRY[self.meta["geometry"]].rows)

        # Angle Mod permutation
        if angle_mod:
            last_row = rows[GEOMETRY[self.meta["geometry"]].digit_row + 3]
            if last_row.keys[0] == "lsgt":
                # should bevome ['ab05', 'lsgt', 'ab01', 'ab02', 'ab03', 'ab04']
                last_row.keys[:6] = [last_row.keys[5]] + last_row.keys[:5]
            else:
                click.echo(
                    "Warning: geometry does not support angle-mod; ignoring the --angle-mod argument"
                )

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
        # FIXME: dead key in space bar?
        spc = SPACEBAR.copy()
        if "spacebar" in layout_data:
            for k in layout_data["spacebar"]:
                spc[k] = self._parse_value(layout_data["spacebar"][k])
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

        # Extra mapping
        if mapping := layout_data.get("mapping"):
            self._parse_extra_mapping(mapping)

        # Fill special symbols
        for key in KEYS.values():
            if base_symbol := self.layers[Layer.BASE].get(key.id):
                if not SystemSymbol.is_system_symbol(base_symbol):
                    continue
                shift_symbol = self.layers[Layer.SHIFT].get(key.id, "")
                if not SystemSymbol.is_system_symbol(shift_symbol):
                    shift_symbol = base_symbol
                for layer, keys in self.layers.items():
                    if key.id not in keys:
                        keys[key.id] = base_symbol if layer.value % 2 == 0 else shift_symbol

        self._make_dead_keys(spc)

    def _parse_dead_keys(self, raw: Dict[str, Any]) -> Dict[str, DeadKeyDescr]:
        custom_dead_keys: Dict[str, DeadKeyDescr] = DK_INDEX.copy()
        for dk_char, definition in raw.items():
            if dk_char == ODK_ID:
                raise ValueError("Cannot redefine 1dk")
            name = definition.get("name")
            base = definition.get("base")
            alt = definition.get("alt")
            alt_space = definition.get("alt_space")
            alt_self = definition.get("alt_self")
            if dk := DK_INDEX.get(dk_char):
                # Redefine existing predefined dead key
                mapping = dict(zip(dk.base, dk.alt))
                if base and alt:
                    mapping.update(dict(zip(base, alt)))
                custom_dead_keys[dk_char] = DeadKeyDescr(
                    char=dk_char,
                    name=name or dk.name,
                    base="".join(mapping.keys()),
                    alt="".join(mapping.values()),
                    alt_space=alt_space or dk.alt_space,
                    alt_self=alt_self or dk.alt_self
                )
            elif not dk_char or not name or not base or not alt or not alt_space or not alt_self:
                raise ValueError(f"Invalid custom dead key definition: {definition}")
            else:
                custom_dead_keys[dk_char] = DeadKeyDescr(
                    char=dk_char,
                    name=name,
                    base=base,
                    alt=alt,
                    alt_space=alt_space,
                    alt_self=alt_self
                )
        return custom_dead_keys

    def _parse_value(self, raw: str, strip=False) -> str:
        return SpecialSymbol.parse(raw.strip() if strip else raw)

    @staticmethod
    def _parse_key_ref(raw: str) -> Optional[str]:
        if raw.startswith("(") and raw.endswith(")"):
            if (clone := raw[1:-1]) and clone in KEYS:
                return clone
        return None

    def _parse_extra_mapping(self, mapping: Dict[str, str | Dict[str, str]]):
        layer: Layer | None
        for raw_key, levels in mapping.items():
            # TODO: parse key in various ways (XKB, Linux keycode)
            if raw_key not in KEYS:
                raise ValueError(f"Unknown key: “{raw_key}”")
            key = raw_key
            # Check for key clone
            if isinstance(levels, str):
                # Check for clone
                if clone := self._parse_key_ref(levels):
                    for layer, keys in self.layers.items():
                        if value := keys.get(clone):
                            self.layers[layer][key] = value
                    continue
                raise ValueError(f"Unsupported key mapping: {raw_key}: {levels}")
            for raw_layer, raw_value in levels.items():
                if (layer := Layer.parse(raw_layer)) is None:
                    raise ValueError(f"Cannot parse layer: “{raw_layer}”")
                if clone := self._parse_key_ref(raw_value):
                    if (value := self.layers[layer].get(clone)) is None:
                        continue
                else:
                    value = self._parse_value(raw_value)
                self.layers[layer][key] = value

    def _make_dead_keys(self, spc: Dict[str, str]) -> None:
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
        for dk in itertools.chain(DEAD_KEYS, self.custom_dead_keys.values()):
            id = dk.char
            if id not in self.dk_set:
                continue

            self.dead_keys[id] = {}
            deadkey = self.dead_keys[id]
            deadkey[id] = dk.alt_self

            if id == ODK_ID:
                self.has_1dk = True
                for key_name in KEYS:
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

        col_offset = 0 if layer_number == Layer.BASE else 2
        for j, row in enumerate(rows):
            keys = row.keys

            base = template[2 + j * 3]
            shift = template[1 + j * 3]

            for i, key in zip(itertools.count(row.offset + col_offset, TEMPLATE_KEY_WIDTH), keys):
                if key == TEMPLATE_DUMMY_KEY:
                    continue

                base_key: Optional[str] = self._parse_value(base[i-1:i+1], strip=True)
                shift_key: Optional[str] = self._parse_value(shift[i-1:i+1], strip=True)

                # in the BASE layer, if the base character is undefined, shift prevails
                if not base_key:
                    if layer_number is Layer.BASE and shift_key:
                        base_key = shift_key.lower()

                # in other layers, if the shift character is undefined, base prevails
                elif not shift_key:
                    if layer_number is Layer.ALTGR:
                        shift_key = upper_key(base_key)
                    elif layer_number is Layer.ODK:
                        shift_key = upper_key(base_key)
                        # shift_key = upper_key(base_key, blank_if_obvious=False)

                if base_key:
                    self.layers[layer_number][key] = base_key
                    if DeadKeyDescr.is_dead_key(base_key):
                        if (base_key in DK_INDEX) or (base_key in self.custom_dead_keys):
                            self.dk_set.add(base_key)
                        else:
                            raise ValueError(f"Undefined dead key: {base_key}")

                if shift_key:
                    self.layers[layer_number.next()][key] = shift_key
                    if DeadKeyDescr.is_dead_key(shift_key):
                        if (shift_key in DK_INDEX) or (shift_key in self.custom_dead_keys):
                            self.dk_set.add(shift_key)
                        else:
                            raise ValueError(f"Undefined dead key: {shift_key}")

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

        for j, row in enumerate(rows):
            keys = row.keys

            base = list(template[2 + j * 3])
            shift = list(template[1 + j * 3])

            for i, key in zip(itertools.count(row.offset + col_offset, TEMPLATE_KEY_WIDTH), keys):
                if key == TEMPLATE_DUMMY_KEY:
                    continue

                indexes = slice(i - 1, i + 1)

                base_key = " "
                if key in self.layers[layer_number]:
                    base_key = SpecialSymbol.prettify(self.layers[layer_number][key])

                shift_key = " "
                if key in self.layers[layer_number.next()]:
                    shift_key = SpecialSymbol.prettify(self.layers[layer_number.next()][key])

                if shift_prevails:
                    shift[indexes] = shift_key.rjust(2)
                    if pretty_upper_key(base_key, blank_if_obvious=False) != shift_key:
                        base[indexes] = base_key.rjust(2)
                else:
                    base[indexes] = base_key.rjust(2)
                    if pretty_upper_key(base_key, blank_if_obvious=False) != shift_key:
                        shift[indexes] = shift_key.rjust(2)

            template[2 + j * 3] = "".join(base)
            template[1 + j * 3] = "".join(shift)

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

    @property
    def symbols(self) -> LayoutSymbols:
        strings = set()
        deadKeys = set()
        for levels in self.layers.values():
            for value in levels.values():
                if len(value) == 2 and value[0] == "*":
                    deadKeys.add(value[1])
                elif SystemSymbol.parse(value) is None:
                    strings.add(value)
        return LayoutSymbols(strings, deadKeys)

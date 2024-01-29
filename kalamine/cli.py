#!/usr/bin/env python3
import json
import os
import shutil
from importlib import metadata
from pathlib import Path

import click

from .layout import KeyboardLayout
from .server import keyboard_server


@click.group()
def cli():
    pass


def pretty_json(layout, path):
    """Pretty-prints the JSON layout."""
    text = (
        json.dumps(layout.json, indent=2, ensure_ascii=False)
        .replace("\n      ", " ")
        .replace("\n    ]", " ]")
        .replace("\n    }", " }")
    )
    with open(path, "w", encoding="utf8") as file:
        file.write(text)


def make_all(layout, subdir):
    def out_path(ext=""):
        return os.path.join(subdir, layout.meta["fileName"] + ext)

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    # AHK driver
    ahk_path = out_path(".ahk")
    with open(ahk_path, "w", encoding="utf-8", newline="\n") as file:
        file.write("\uFEFF")  # AHK scripts require a BOM
        file.write(layout.ahk)
    print("... " + ahk_path)

    # Windows driver
    klc_path = out_path(".klc")
    with open(klc_path, "w", encoding="utf-16le", newline="\r\n") as file:
        file.write(layout.klc)
    print("... " + klc_path)

    # macOS driver
    osx_path = out_path(".keylayout")
    with open(osx_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(layout.keylayout)
    print("... " + osx_path)

    # Linux driver, user-space
    xkb_path = out_path(".xkb")
    with open(xkb_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(layout.xkb)
    print("... " + xkb_path)

    # Linux driver, root
    xkb_custom_path = out_path(".xkb_custom")
    with open(xkb_custom_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(layout.xkb_patch)
    print("... " + xkb_custom_path)

    # JSON data
    json_path = out_path(".json")
    pretty_json(layout, json_path)
    print("... " + json_path)

    # SVG data
    svg_path = out_path(".svg")
    layout.svg.write(svg_path, pretty_print=True, encoding="utf-8")
    print("... " + svg_path)


@cli.command()
@click.argument("layout_descriptors", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--out", default="all", type=click.Path(), help="Keyboard drivers to generate."
)
def make(layout_descriptors, out):
    """Convert TOML/YAML descriptions into OS-specific keyboard drivers."""

    for input_file in layout_descriptors:
        layout = KeyboardLayout(input_file)

        # default: build all in the `dist` subdirectory
        if out == "all":
            make_all(layout, "dist")
            continue

        # quick output: reuse the input name and change the file extension
        if out in ["keylayout", "klc", "xkb", "xkb_custom", "svg"]:
            output_file = os.path.splitext(input_file)[0] + "." + out
        else:
            output_file = out

        # detailed output
        if output_file.endswith(".ahk"):
            with open(output_file, "w", encoding="utf-8", newline="\n") as file:
                file.write("\uFEFF")  # AHK scripts require a BOM
                file.write(layout.ahk)
        elif output_file.endswith(".klc"):
            with open(output_file, "w", encoding="utf-16le", newline="\r\n") as file:
                file.write(layout.klc)
        elif output_file.endswith(".keylayout"):
            with open(output_file, "w", encoding="utf-8", newline="\n") as file:
                file.write(layout.keylayout)
        elif output_file.endswith(".xkb"):
            with open(output_file, "w", encoding="utf-8", newline="\n") as file:
                file.write(layout.xkb)
        elif output_file.endswith(".xkb_custom"):
            with open(output_file, "w", encoding="utf-8", newline="\n") as file:
                file.write(layout.xkb_patch)
        elif output_file.endswith(".json"):
            pretty_json(layout, output_file)
        elif output_file.endswith(".svg"):
            layout.svg.write(output_file, pretty_print=True, encoding="utf-8")
        else:
            print("Unsupported output format.")
            return

        # successfully converted, display file name
        print("... " + output_file)


TOML_HEADER = """# kalamine keyboard layout descriptor
name        = "qwerty-custom"  # full layout name, displayed in the keyboard settings
name8       = "custom"         # short Windows filename: no spaces, no special chars
locale      = "us"             # locale/language id
variant     = "custom"         # layout variant id
author      = "nobody"         # author name
description = "custom QWERTY layout"
url         = "https://fabi1cazenave.github.com/kalamine"
version     = "0.0.1"
geometry    = """

TOML_FOOTER = """
[spacebar]
1dk         = "'"  # apostrophe
1dk_shift   = "'"  # apostrophe"""

@cli.command()
@click.argument("output_file", nargs=1, type=click.Path(exists=False))
@click.option("--geometry", default="ISO", help="Specify keyboard geometry.")
@click.option("--altgr/--no-altgr", default=False, help="Set an AltGr layer.")
@click.option("--1dk/--no-1dk", "odk", default=False, help="Set a custom dead key.")
def create(output_file, geometry, altgr, odk):
    """Create a new TOML layout description."""

    root = Path(__file__).resolve(strict=True).parent.parent

    def get_layout(name):
        layout = KeyboardLayout(str(root / "layouts" / f"{name}.toml"))
        layout.geometry = geometry
        return layout

    def keymap(layout_name, layout_layer, layer_name=""):
        layer = "\n"
        layer += f"\n{layer_name or layout_layer} = '''"
        layer += "\n"
        layer += "\n".join(getattr(get_layout(layout_name), layout_layer))
        layer += "\n'''"
        return layer

    content = f'{TOML_HEADER}"{geometry.upper()}"'
    if odk:
        content += keymap("intl", "base")
        if altgr:
            content += keymap("prog", "altgr")
        content += "\n"
        content += TOML_FOOTER
    elif altgr:
        content += keymap("prog", "full")
    else:
        content += keymap("ansi", "base")

    # append user guide sections
    with (root / "docs" / "README.md").open() as f:
        sections = "".join(f.readlines()).split("\n\n\n")
    for topic in sections[1:]:
        content += "\n\n"
        content += "\n# "
        content += "\n# ".join(topic.rstrip().split("\n"))

    with open(output_file, "w", encoding="utf-8", newline="\n") as file:
        file.write(content)
    print("... " + output_file)


@cli.command()
@click.argument("input", nargs=1, type=click.Path(exists=True))
def watch(input):
    """Watch a TOML/YAML layout description and display it in a web server."""

    keyboard_server(input)


@cli.command()
def version():
    """Show version number and exit."""

    print(f"kalamine { metadata.version('kalamine') }")

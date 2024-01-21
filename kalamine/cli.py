#!/usr/bin/env python3
import json
import os
from importlib import metadata

import click

from .layout import KeyboardLayout
from .server import keyboard_server


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


@click.command()
@click.argument("input", nargs=-1, type=click.Path(exists=True))
@click.option("--version", "-v", is_flag=True)
@click.option("--watch", "-w", is_flag=True)
@click.option(
    "--out", default="all", type=click.Path(), help="Keyboard driver(s) to generate."
)
def make(input, version, watch, out):
    """Convert toml/yaml descriptions into OS-specific keyboard layouts."""

    if version:
        print(f"kalamine { metadata.version('kalamine') }")

    if watch:
        keyboard_server(input[0])

    for input_file in input:
        layout = KeyboardLayout(input_file)

        # default: build all in the `dist` subdirectory
        if out == "all":
            make_all(layout, "dist")
            continue

        # quick output: reuse the input name and change the file extension
        if out in ["keylayout", "klc", "xkb", "xkb_custom"]:
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
        else:
            print("Unsupported output format.")
            return

        # successfully converted, display file name
        print("... " + output_file)


if __name__ == "__main__":
    make()

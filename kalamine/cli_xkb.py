#!/usr/bin/env python3
import os
import platform
import sys
import tempfile

import click

from .layout import KeyboardLayout
from .xkb_manager import WAYLAND, XKBManager


@click.group()
def cli():
    if platform.system() != "Linux":
        sys.exit("This command is only compatible with GNU/Linux, sorry.")


@cli.command()
@click.argument("input", nargs=1, type=click.Path(exists=True))
def apply(input):
    """Apply a Kalamine layout."""

    if WAYLAND:
        sys.exit(
            "You appear to be running Wayland, which does not support this operation."
        )

    layout = KeyboardLayout(input)
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".xkb", encoding="utf-8"
    ) as temp_file:
        try:
            temp_file.write(layout.xkb)
            os.system(f"xkbcomp -w0 {temp_file.name} $DISPLAY")
        finally:
            temp_file.close()


@cli.command()
@click.argument("layouts", nargs=-1, type=click.Path(exists=True))
def install(layouts):
    """Install a list of Kalamine layouts."""

    if not layouts:
        return

    kb_locales = set()
    kb_layouts = []
    for file in layouts:
        layout = KeyboardLayout(file)
        kb_layouts.append(layout)
        kb_locales.add(layout.meta["locale"])

    def xkb_install(xkb):
        for layout in kb_layouts:
            xkb.add(layout)
        index = xkb.index  # gets erased with xkb.update()
        xkb.clean()
        xkb.update()
        print()
        print("Successfully installed.")
        return index

    # EAFP (Easier to Ask Forgiveness than Permission)
    try:
        xkb_root = XKBManager(root=True)
        xkb_index = xkb_install(xkb_root)
        print(f"On XOrg, you can try the layout{'s' if len(layouts) > 1 else ''} with:")
        for locale, variants in xkb_index:
            for name in variants.keys():
                print(f"    setxkbmap {locale} -variant {name}")
        print()

    except PermissionError:
        print("    Not writable: switching to user-space.")
        print()
        xkb_home = XKBManager()
        xkb_home.ensure_xkb_config_is_ready()
        xkb_install(xkb_home)
        print("Warning: user-space layouts only work with Wayland.")
        print()


@cli.command()
@click.argument("mask")  # [locale]/[name]
def remove(mask):
    """Remove a list of Kalamine layouts."""

    def xkb_remove(root=False):
        xkb = XKBManager(root=root)
        xkb.clean()
        for locale, variants in xkb.list(mask).items():
            for name in variants.keys():
                xkb.remove(locale, name)
        xkb.update()

    # EAFP (Easier to Ask Forgiveness than Permission)
    try:
        xkb_remove(root=True)
    except PermissionError:
        xkb_remove()


@cli.command()
@click.argument("mask", default="*")
@click.option("--all", "-a", is_flag=True)
def list(mask, all):
    """List installed Kalamine layouts."""

    for root in [True, False]:
        filtered = {}

        xkb = XKBManager(root=root)
        layouts = xkb.list_all(mask) if all else xkb.list(mask)
        for locale, variants in sorted(layouts.items()):
            for name, desc in sorted(variants.items()):
                filtered[f"{locale}/{name}"] = desc

        if mask == "*" and root and xkb.has_custom_symbols():
            filtered["custom"] = ""

        if bool(filtered):
            print(xkb.path)
            for id, desc in filtered.items():
                print(f"    {id:<24} {desc}")

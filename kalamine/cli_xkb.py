#!/usr/bin/env python3

import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import click

from .layout import KeyboardLayout, load_layout
from .xkb_manager import WAYLAND, KbdIndex, XKBManager


@click.group()
def cli() -> None:
    if platform.system() != "Linux":
        sys.exit("This command is only compatible with GNU/Linux, sorry.")


@cli.command()
@click.argument(
    "filepath", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--angle-mod/--no-angle-mod",
    default=False,
    help="Apply Angle-Mod (which is a [ZXCVB] permutation with the LSGT key (a.k.a. ISO key))",
)
def apply(filepath: Path, angle_mod: bool) -> None:
    """Apply a Kalamine layout."""

    if WAYLAND:
        sys.exit(
            "You appear to be running Wayland, which does not support this operation."
        )

    layout = KeyboardLayout(load_layout(filepath), angle_mod)
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".xkb_keymap", encoding="utf-8"
    ) as temp_file:
        temp_file.write(layout.xkb_keymap)
        os.system(f"xkbcomp -w0 {temp_file.name} $DISPLAY")


@cli.command()
@click.argument(
    "layouts", nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--angle-mod/--no-angle-mod",
    default=False,
    help="Apply Angle-Mod (which is a [ZXCVB] permutation with the LSGT key (a.k.a. ISO key))",
)
def install(layouts: List[Path], angle_mod: bool) -> None:
    """Install a list of Kalamine layouts."""

    if not layouts:
        return

    kb_locales = set()
    kb_layouts = []
    for file in layouts:
        layout_file = load_layout(file)
        layout = KeyboardLayout(layout_file, angle_mod)
        kb_layouts.append(layout)
        kb_locales.add(layout.meta["locale"])

    def xkb_install(xkb: XKBManager) -> KbdIndex:
        for layout in kb_layouts:
            xkb.add(layout)
        index = xkb.index  # gets erased with xkb.update()
        xkb.clean()
        xkb.update()
        print()
        print("Successfully installed.")
        return dict(index)

    # EAFP (Easier to Ask Forgiveness than Permission)
    try:
        xkb_root = XKBManager(root=True)
        xkb_index = xkb_install(xkb_root)
        print(f"On XOrg, you can try the layout{'s' if len(layouts) > 1 else ''} with:")
        for locale, variants in xkb_index.items():
            for name in variants.keys():
                print(f"    setxkbmap {locale} -variant {name}")
        print()

    except PermissionError:
        print(xkb_root.path)
        print("    Not writable: switching to user-space.")
        print()
        if not WAYLAND:
            print(
                "You appear to be running XOrg. You need sudo privileges to install keyboard layouts:"
            )
            for filepath in layouts:
                print(f'    sudo env "PATH=$PATH" xkalamine install {filepath}')
            sys.exit(1)

        xkb_home = XKBManager()
        xkb_home.ensure_xkb_config_is_ready()
        xkb_install(xkb_home)
        print("Warning: user-space layouts only work with Wayland.")
        print()


@cli.command()
@click.argument("mask")  # [locale]/[name]
def remove(mask: str) -> None:
    """Remove a list of Kalamine layouts."""

    def xkb_remove(root: bool = False) -> None:
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
        if not WAYLAND:
            print(
                "You appear to be running XOrg. You need sudo privileges to remove keyboard layouts:"
            )
            print(f'    sudo env "PATH=$PATH" xkalamine remove {mask}')
            sys.exit(1)
        xkb_remove()


@cli.command(name="list")
@click.option("-a", "--all", "all_flag", is_flag=True)
@click.argument("mask", default="*")
def list_command(mask: str, all_flag: bool) -> None:
    """List installed Kalamine layouts."""

    for root in [True, False]:
        # XXX this very weird type means we've done something silly here
        filtered: Dict[str, Union[Optional[KeyboardLayout], str]] = {}
        xkb = XKBManager(root=root)
        layouts = xkb.list_all(mask) if all_flag else xkb.list(mask)
        for locale, variants in sorted(layouts.items()):
            for name, desc in sorted(variants.items()):
                filtered[f"{locale}/{name}"] = desc

        if mask == "*" and root and xkb.has_custom_symbols():
            filtered["custom"] = ""

        if filtered:
            print(xkb.path)
            for key, value in filtered.items():
                print(f"    {key:<24} {value}")


if __name__ == "__main__":
    cli()

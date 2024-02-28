#!/usr/bin/env python3

import platform
import sys
from pathlib import Path
from typing import List

import click

from .layout import KeyboardLayout, load_layout
from .msklc_manager import MsklcManager


@click.group()
def cli() -> None: ...


DEFAULT_MSKLC_DIR = "C:\\Program Files (x86)\\Microsoft Keyboard Layout Creator 1.4\\"


@cli.command()
@click.argument(
    "layout_descriptors",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--angle-mod/--no-angle-mod",
    default=False,
    help="Apply Angle-Mod (which is a [ZXCVB] permutation with the LSGT key (a.k.a. ISO key))",
)
@click.option(
    "--msklc",
    default=DEFAULT_MSKLC_DIR,
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Directory where MSKLC is installed",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose mode")
def build(
    layout_descriptors: List[Path],
    angle_mod: bool,
    msklc: Path,
    verbose: bool,
) -> None:
    """Convert TOML/YAML descriptions into Windows MSKLC keyboard drivers."""

    if platform.system() != "Windows":
        sys.exit("This command is only compatible with Windows, sorry.")

    for input_file in layout_descriptors:
        layout = KeyboardLayout(load_layout(input_file), angle_mod)
        msklc_mgr = MsklcManager(layout, msklc, verbose=verbose)
        if msklc_mgr.build_msklc_installer():
            if msklc_mgr.build_msklc_dll():
                output_dir = f'{msklc_mgr._working_dir}\\{layout.meta["name8"]}\\'
                click.echo(
                    "MSKLC drivers successfully built.\n"
                    f"Execute `{output_dir}setup.exe` to install.\n"
                    "Log out and log back in to apply the changes."
                )


@cli.command()
@click.argument(
    "input_file",
    nargs=1,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose mode")
def dummy(input_file: Path, verbose: bool) -> None:
    """Dump a dummy TOML layout descriptor."""

    input_layout = KeyboardLayout(load_layout(input_file))
    msklc_mgr = MsklcManager(input_layout, Path(DEFAULT_MSKLC_DIR), verbose=verbose)
    print(msklc_mgr._create_dummy_layout())


if __name__ == "__main__":
    cli()

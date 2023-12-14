#!/usr/bin/env python3
import os
import platform
import sys
import tempfile

import click

from .layout import KeyboardLayout
from .xkb_manager import XKBManager


@click.group()
def cli():
    if platform.system() != 'Linux':
        sys.exit('This command is only compatible with GNU/Linux, sorry.')


@cli.command()
@click.argument('input', nargs=1, type=click.Path(exists=True))
def apply(input):
    """ Apply a Kalamine layout. """

    layout = KeyboardLayout(input)
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.xkb', encoding='utf-8') as temp_file:
        try:
            temp_file.write(layout.xkb)
            os.system(f"xkbcomp -w0 {temp_file.name} $DISPLAY")
        finally:
            temp_file.close()


@cli.command()
@click.argument('layouts', nargs=-1, type=click.Path(exists=True))
def install(layouts):
    """ Install a list of Kalamine layouts. """
    if len(layouts) == 0:
        return

    xkb = XKBManager()
    for file in layouts:
        xkb.add(KeyboardLayout(file))
    index = xkb.index
    xkb.update()

    print()
    print(f"Successfully installed. You can try the layout{'s' if len(layouts) > 1 else ''} with:")
    for locale, variants in index:
        for name in variants.keys():
            print(f"    setxkbmap {locale} -variant {name}")
    print()


@cli.command()
def clean():
    """ Clean all installed Kalamine layouts: drop the obsolete 'type' attr. """

    xkb = XKBManager()
    xkb.clean()


@cli.command()
@click.argument('mask', default='*')
@click.option('--all', '-a', is_flag=True)
def list(mask, all):
    """ List all installed Kalamine layouts. """

    xkb = XKBManager()
    layouts = xkb.list_all(mask) if all else xkb.list(mask)
    for locale, variants in sorted(layouts.items()):
        for name, desc in sorted(variants.items()):
            id = f"{locale}/{name}"
            print(f"{id:<24}   {desc}")


@cli.command()
@click.argument('mask')  # [locale]/[name]
def remove(mask):
    """ Remove an existing Kalamine layout. """

    xkb = XKBManager()
    for locale, variants in xkb.list(mask).items():
        for name in variants.keys():
            xkb.remove(locale, name)
    xkb.update()

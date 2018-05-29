#!/usr/bin/env python3
import click
import os
import platform
import tempfile

from .layout import KeyboardLayout
from .xkb_manager import XKBManager


@click.group()
def cli():
    if platform.system() != 'Linux':
        exit('This command is only compatible with GNU/Linux, sorry.')


@cli.command()
@click.argument('input', nargs=1, type=click.Path(exists=True))
def apply(input):
    """ Apply a Kalamine layout. """

    layout = KeyboardLayout(input)
    f = tempfile.NamedTemporaryFile(mode='w+', suffix='.xkb')
    try:
        f.write(layout.xkb)
        os.system('xkbcomp -w0 %s $DISPLAY' % f.name)
    finally:
        f.close()


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
    print('Successfully installed. You can try the layout{} with:'.format(
        's' if len(layouts) > 1 else ''
    ))
    for locale, named_layouts in index:
        for name in named_layouts.keys():
            print('    setxkbmap {} -variant {}'.format(locale, name))
    print()


@cli.command(name='list')
@click.argument('mask', default='*')
@click.option('--all', '-a', is_flag=True)
def list_layouts(mask, all):
    """ List all installed Kalamine layouts. """

    xkb = XKBManager()
    list = xkb.list_all(mask) if all else xkb.list(mask)
    for id, desc in sorted(list.items()):
        print('{:<24}   {}'.format(id, desc))


@cli.command()
@click.argument('mask')  # [locale]/[name]
def remove(mask):
    """ Remove an existing Kalamine layout. """

    xkb = XKBManager()
    for layout_id in xkb.list(mask):
        xkb.remove(layout_id)
    xkb.update()

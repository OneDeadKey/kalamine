#!/usr/bin/env python3
import click
import os
import platform
import tempfile

from .layout import KeyboardLayout
from .xkb_manager import update_symbols, update_rules, list_rules

HELP_EXTENDS = 'Optional, keyboard layout to extend.'


@click.group()
def cli():
    if platform.system() != 'Linux':
        exit('This command is only compatible with GNU/Linux, sorry.')


@cli.command()
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--extends', default='', type=click.Path(), help=HELP_EXTENDS)
def apply(input, extends):
    """ Apply a Kalamine layout. """

    layout = KeyboardLayout(input, extends)

    f = tempfile.NamedTemporaryFile(mode='w+', suffix='.xkb')
    try:
        f.write(layout.xkb)
        os.system('xkbcomp -w9 %s $DISPLAY' % f.name)
    finally:
        f.close()


@cli.command()
@click.argument('layouts', nargs=-1, type=click.Path(exists=True))
@click.option('--extends', default='', type=click.Path(), help=HELP_EXTENDS)
def install(layouts, extends):
    """ Install a list of Kalamine layouts. """
    if len(layouts) == 0:
        return

    kbindex = {}
    for file in layouts:
        layout = KeyboardLayout(file, extends)
        locale = layout.meta['locale']
        variant = layout.meta['variant']
        if locale not in kbindex:
            kbindex[locale] = {}
        kbindex[locale][variant] = layout

    update_symbols(kbindex)  # XKB/symbols/{locales}
    update_rules(kbindex)    # XKB/rules/{base,evdev}.xml

    print()
    print('Successfully installed. You can try the layout{} with:'.format(
        's' if len(layouts) > 1 else ''
    ))
    for locale, named_layouts in kbindex.items():
        for name in named_layouts.keys():
            print('    setxkbmap {} -variant {}'.format(locale, name))
    print()


@cli.command(name='list')
@click.argument('mask', default='*')
def list_layouts(mask):
    """ List all installed Kalamine layouts. """

    for id, desc in sorted(list_rules(mask).items()):
        print('{:<24}   {}'.format(id, desc))


@cli.command()
@click.argument('mask')  # [locale]/[name]
def remove(mask):
    """ Remove an existing Kalamine layout. """

    kbindex = {}
    for layout_id in list_rules(mask):
        locale, variant = layout_id.split('/')
        if locale not in kbindex:
            kbindex[locale] = {}
        kbindex[locale][variant] = None

    update_symbols(kbindex)  # XKB/symbols/{locales}
    update_rules(kbindex)    # XKB/rules/{base,evdev}.xml

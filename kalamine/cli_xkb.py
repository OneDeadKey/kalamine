#!/usr/bin/env python3
import os
import platform
import sys
import tempfile

import click

from .layout import KeyboardLayout
from .xkb_manager import XKBManager

CFG_HOME = os.environ.get('XDG_CONFIG_HOME') or \
    os.path.join(os.environ.get('HOME'), '.config')
XKB_HOME = os.path.join(CFG_HOME, 'xkb')
XKB_ROOT = '/usr/share/X11/xkb/'


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

    if not layouts:
        return

    def xkb_install(root):
        xkb = XKBManager(root)
        for file in layouts:
            xkb.add(KeyboardLayout(file))
        index = xkb.index
        xkb.update()
        print()
        print('Successfully installed.')

    # EAFP (Easier to Ask Forgiveness than Permission)
    try:
        xkb_install(XKB_ROOT)
        print(f"You can try the layout{'s' if len(layouts) > 1 else ''} with:")
        for locale, variants in index:
            for name in variants.keys():
                print(f"    setxkbmap {locale} -variant {name}")
        print()

    except PermissionError:
        print('    Not writable: switching to user-space.')
        print()
        xkb_install(XKB_HOME)
        print('Warning: user-space layouts only work with Wayland.')
        print()


@cli.command()
@click.argument('mask')  # [locale]/[name]
def remove(mask):
    """ Remove a list of Kalamine layouts. """

    def xkb_remove(root):
        xkb = XKBManager(root)
        for locale, variants in xkb.list(mask).items():
            for name in variants.keys():
                xkb.remove(locale, name)
        xkb.update()

    # EAFP (Easier to Ask Forgiveness than Permission)
    try:
        xkb_remove(XKB_ROOT)
    except PermissionError:
        xkb_remove(XKB_HOME)


@cli.command()
def clean():
    """ Clean installed Kalamine layouts: drop the obsolete 'type' attr. """

    # EAFP (Easier to Ask Forgiveness than Permission)
    # XXX irrelevant, as this issue has only happened for XKB_ROOT
    try:
        XKBManager(XKB_ROOT).clean()
    except PermissionError:
        XKBManager(XKB_HOME).clean()

    # # EAFP (Easier to Ask Forgiveness than Permission)
    # try:
    #     XKBManager(XKB_ROOT)
    #     xkb.clean()
    # except PermissionError:
    #     xkb = XKBManager(XKB_HOME)
    #     xkb.clean()


@cli.command()
@click.argument('mask', default='*')
@click.option('--all', '-a', is_flag=True)
def list(mask, all):
    """ List installed Kalamine layouts. """

    for root in [XKB_ROOT, XKB_HOME]:
        filtered = {}

        xkb = XKBManager(root)
        layouts = xkb.list_all(mask) if all else xkb.list(mask)
        for locale, variants in sorted(layouts.items()):
            for name, desc in sorted(variants.items()):
                filtered[f"{locale}/{name}"] = desc

        if mask == "*" and root == XKB_ROOT and xkb.has_custom_symbols(root):
            filtered['custom'] = ''

        if bool(filtered):
            home_path = os.environ.get('HOME')
            if root.startswith(home_path):
                root = '~' + root[len(home_path):]
            print(root)
            for id, desc in filtered.items():
                print(f"    {id:<24} {desc}")

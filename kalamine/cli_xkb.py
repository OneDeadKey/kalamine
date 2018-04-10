#!/usr/bin/env python3
import click
import os
import platform
import shutil
import sys
import tempfile

from lxml import etree
from lxml.builder import E

from kalamine import Layout, Template


XKB = '/usr/share/X11/xkb/'

"""
On GNU/Linux, keyboard layouts must be installed in /usr/share/X11/xkb.
To be able to revert a layout installation, Kalamine marks layouts like this:

    - XKB/symbols/[locale]: layout definitions
        // KALAMINE::[NAME]::BEGIN
        xkb_symbols "[name]" { ... }
        // KALAMINE::[NAME]::END

    - XKB/rules/{base,evdev}.xml: layout references
        <variant type="kalamine">
            <configItem>
                <name>lafayette42</name>
                <description>French (Lafayette42)</description>
            </configItem>
        </variant>
"""


def open_symbols(path, name):
    """ Open an xkb/symbols file, dropping existing Kalamnine layouts. """

    MARK_BEGIN = 'KALAMINE::' + name.upper() + '::BEGIN\n'
    MARK_END = 'KALAMINE::' + name.upper() + '::END\n'

    LEGACY_MARK_BEGIN = 'LAFAYETTE::BEGIN\n'
    LEGACY_MARK_END = 'LAFAYETTE::END\n'

    between_marks = False
    modified_text = False
    text = ''

    # with open(path, 'r+') as symbols:
    symbols = open(path, 'r+')
    for line in symbols:
        if line.endswith(MARK_BEGIN) or line.endswith(LEGACY_MARK_BEGIN):
            between_marks = True
            modified_text = True
        elif line.endswith(MARK_END) or line.endswith(LEGACY_MARK_END):
            between_marks = False
        elif not between_marks:
            text += line
    if modified_text:  # clear previous Kalamine layouts
        print('... ' + path)
        symbols.seek(0)
        symbols.write(text)
        symbols.truncate()

    return symbols


def get_rules_locale(tree, locale):
    query = '//layout/configItem/name[text()="{}"]/../..'.format(locale)
    return tree.xpath(query)[0]


def open_rules(path, locale, name, update_if_cleaned=False):
    """ Open an xkb/rules/*.xml file, dropping the named Kalamine layout. """

    tree = etree.parse(path, etree.XMLParser(remove_blank_text=True))
    modified_tree = False

    layout = get_rules_locale(tree, locale)
    for signature in ['lafayette', 'kalamine']:
        query = '//variant[@type="{}"]/configItem/name[text()="{}"]/../..'.\
                format(signature, name)
        for variant in layout.xpath(query):
            variant.getparent().remove(variant)
            modified_tree = True

    if modified_tree and update_if_cleaned:
        update_rules(path, tree)
        print('... ' + path)

    return tree


def update_rules(path, tree):
    tree.write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')


HELP_EXTENDS = 'Optional, keyboard layout to extend.'


@click.group()
def cli():
    if platform.system() != 'Linux':
        print('This command is only compatible with GNU/Linux, sorry.')
        sys.exit()


@cli.command()
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--extends', default='', type=click.Path(), help=HELP_EXTENDS)
def apply(input, extends):
    """ Apply a Kalamine layout. """

    layout = Layout(input, extends)
    tpl = Template(layout)

    f = tempfile.NamedTemporaryFile(mode='w+', suffix='.xkb')
    try:
        f.write(tpl.xkb)
        os.system('xkbcomp -w9 {} $DISPLAY'.format(f.name))
    finally:
        f.close()


@cli.command()
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--extends', default='', type=click.Path(), help=HELP_EXTENDS)
def install(input, extends):
    """ Install a new Kalamine layout. """

    layout = Layout(input, extends)
    locale = layout.meta['locale']
    name = layout.meta['variant']
    desc = layout.meta['description']
    tpl = Template(layout)

    # add layouts in XKB/symbols
    path = os.path.join(XKB, 'symbols', locale)
    if not os.path.isfile(path + '.orig'):  # backup, just in case :-)
        shutil.copy(path, path + '.orig')
        print('backup: ' + path + '.orig')
    symbols = open_symbols(path, name)
    symbols.write('// KALAMINE::' + name.upper() + '::BEGIN\n')  # MARK_BEGIN
    symbols.write(tpl.xkb_patch + '\n')
    symbols.write('// KALAMINE::' + name.upper() + '::END\n')    # MARK_END
    symbols.close()
    print('... ' + path)

    # add references in XKB/rules
    for filename in ['base.xml', 'evdev.xml']:
        path = os.path.join(XKB, 'rules', filename)
        tree = open_rules(path, locale, name)
        variantList = get_rules_locale(tree, locale).xpath('variantList')[0]
        variantList.append(
            E.variant(
                E.configItem(
                    E.name(name),
                    E.description(desc)
                ), type='kalamine'))
        update_rules(path, tree)
        print('... ' + path)

    print('Successfully installed. You can try the layout with:')
    print('    setxkbmap {} -variant {}'.format(locale, name))


@cli.command()
def list():
    """ List all installed Kalamine layouts. """

    layouts = []
    for filename in ['base.xml', 'evdev.xml']:
        tree = etree.parse(os.path.join(XKB, 'rules', filename))
        for variant in tree.xpath('//variant[@type]'):
            locale = variant.xpath('../../configItem/name')[0].text
            name = variant.xpath('configItem/name')[0].text
            desc = variant.xpath('configItem/description')[0].text
            id = locale + '/' + name
            if id not in layouts:
                layouts.append(id)
                print('{:<24}   {}'.format(id, desc))


@cli.command()
@click.argument('layout_id')  # [locale]/[name]
def remove(layout_id):
    """ Remove an existing Kalamine layout. """

    info = layout_id.split('/')
    locale = info[0]
    name = info[1]

    # remove layouts in XKB/symbols
    open_symbols(os.path.join(XKB, 'symbols', locale), name)

    # remove references in XKB/rules
    for filename in ['base.xml', 'evdev.xml']:
        path = os.path.join(XKB, 'rules', filename)
        open_rules(path, locale, name, True)

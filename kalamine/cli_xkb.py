#!/usr/bin/env python3
import click
import os
import platform
import shutil
import sys
import tempfile
import traceback

from lxml import etree
from lxml.builder import E

from kalamine import Layout, Template

XKB = '/usr/share/X11/xkb/'


###############################################################################
# Helpers: XKB/symbols
#

""" On GNU/Linux, keyboard layouts must be installed in /usr/share/X11/xkb. To
    be able to revert a layout installation, Kalamine marks layouts like this:

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

    Unfortunately, the Lafayette project has released a first installer before
    the XKalamine installer was developed, so we have to handle this situation
    too:

    - XKB/symbols/[locale]: layout definitions
        // LAFAYETTE::BEGIN
        xkb_symbols "lafayette"   { ... }
        xkb_symbols "lafayette42" { ... }
        // LAFAYETTE::END

    - XKB/rules/{base,evdev}.xml: layout references
        <variant type="lafayette">
            <configItem>
                <name>lafayette</name>
                <description>French (Lafayette)</description>
            </configItem>
        </variant>
        <variant type="lafayette">
            <configItem>
                <name>lafayette42</name>
                <description>French (Lafayette42)</description>
            </configItem>
        </variant>

    Consequence: these two Lafayette layouts must be uninstalled together.
    Because of the way they are grouped in symbols/fr, it is impossible to
    remove one without removing the other.
"""

LEGACY_MARK = {
    'begin': '// LAFAYETTE::BEGIN\n',
    'end': '// LAFAYETTE::END\n'
}


def get_symbol_mark(name):
    return {
        'begin': '// KALAMINE::' + name.upper() + '::BEGIN\n',
        'end': '// KALAMINE::' + name.upper() + '::END\n'
    }


def open_symbols(path, name):
    """ Open an xkb/symbols file, dropping existing Kalamnine layouts. """

    between_marks = False
    modified_text = False
    text = ''

    marks = [get_symbol_mark(name)]
    if name.lower().startswith('lafayette'):
        marks.append(LEGACY_MARK)

    # with open(path, 'r+') as symbols:
    symbols = open(path, 'r+')
    for mark in marks:
        for line in symbols:
            if line.endswith(mark['begin']):
                between_marks = True
                text = text.rstrip()
                modified_text = True
            elif line.endswith(mark['end']):
                between_marks = False
            elif not between_marks:
                text += line

    # clear previous Kalamine layouts if needed
    if modified_text:
        print('... ' + path)
        symbols.seek(0)
        symbols.write(text.rstrip() + '\n')
        symbols.truncate()

    return symbols


###############################################################################
# Helpers: XKB/rules
#

def get_rules_locale(tree, locale):
    query = '//layout/configItem/name[text()="%s"]/../..' % locale
    result = tree.xpath(query)
    if len(result) != 1:
        exit_LocaleNotSupported(locale)
    return tree.xpath(query)[0]


def open_rules(path, locale, name, update_if_cleaned=False):
    """ Open an xkb/rules/*.xml file, dropping the named Kalamine layout. """

    tree = etree.parse(path, etree.XMLParser(remove_blank_text=True))
    modified_tree = False

    signatures = ['kalamine']
    if name.lower().startswith('lafayette'):
        signatures.append('lafayette')

    layout = get_rules_locale(tree, locale)
    for signature in signatures:
        query = '//variant[@type="{}"]/configItem/name[text()="{}"]/../..'.\
                format(signature, name)
        for variant in layout.xpath(query):
            variant.getparent().remove(variant)
            modified_tree = True

    if modified_tree and update_if_cleaned:
        update_rules(path, tree)
        print('... ' + path)

    return tree


def list_rules(mask='*'):
    """ List all installed Kalamine layouts. """

    layouts = {}

    for filename in ['base.xml', 'evdev.xml']:
        tree = etree.parse(os.path.join(XKB, 'rules', filename))
        for variant in tree.xpath('//variant[@type]'):
            locale = variant.xpath('../../configItem/name')[0].text
            name = variant.xpath('configItem/name')[0].text
            desc = variant.xpath('configItem/description')[0].text
            id = locale + '/' + name
            if id not in layouts:
                layouts[id] = desc

    return layouts


def update_rules(path, tree):
    tree.write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')


###############################################################################
# Exception Handling (there must be a better way...)
#

def exit(message):
    print('')
    print(message)
    sys.exit(1)


def exit_LocaleNotSupported(locale):
    exit('Error: the `%s` locale is not supported.' % locale)


def exit_FileNotWritable(exception, path):
    if isinstance(exception, PermissionError):  # noqa: F821
        exit('Permission denied. Are you root?')
    elif isinstance(exception, IOError):
        exit('Error: could not write to file %s.' % path)
    else:  # exit('Unexpected error: ' + sys.exc_info()[0])
        exit('Error: {}.\n{}'.format(exception, traceback.format_exc()))


###############################################################################
# Command-Line Handlers
#

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

    layout = Layout(input, extends)
    tpl = Template(layout)

    f = tempfile.NamedTemporaryFile(mode='w+', suffix='.xkb')
    try:
        f.write(tpl.xkb)
        os.system('xkbcomp -w9 %s $DISPLAY' % f.name)
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
    print('Installing {}/{}...'.format(locale, name))

    try:
        """ add layouts in XKB/symbols """
        path = os.path.join(XKB, 'symbols', locale)
        if not os.path.exists(path):
            exit_LocaleNotSupported(locale)

        if not os.path.isfile(path + '.orig'):  # backup, just in case :-)
            shutil.copy(path, path + '.orig')
            print('backup: ' + path + '.orig')

        MARK = get_symbol_mark(name)
        symbols = open_symbols(path, name)
        symbols.write('\n')
        symbols.write(MARK['begin'])
        symbols.write(tpl.xkb_patch.rstrip() + '\n')
        symbols.write(MARK['end'])
        symbols.close()
        print('... ' + path)

        """ add references in XKB/rules """
        for filename in ['base.xml', 'evdev.xml']:
            path = os.path.join(XKB, 'rules', filename)
            tree = open_rules(path, locale, name)
            variants = get_rules_locale(tree, locale).xpath('variantList')
            if len(variants) != 1:
                exit('Error: unexpected xml format in %s.' % path)
            variants[0].append(
                E.variant(
                    E.configItem(
                        E.name(name),
                        E.description(desc)
                    ), type='kalamine'))
            update_rules(path, tree)
            print('... ' + path)

    except Exception as e:
        exit_FileNotWritable(e, path)

    print('Successfully installed. You can try the layout with:')
    print('    setxkbmap {} -variant {}'.format(locale, name))


@cli.command()
def list():
    """ List all installed Kalamine layouts. """

    for id, desc in list_rules().items():
        print('{:<24}   {}'.format(id, desc))


@cli.command()
@click.argument('layout_id')  # [locale]/[name]
def remove(layout_id):
    """ Remove an existing Kalamine layout. """

    if layout_id not in list_rules():
        print('Error: %s is not installed.' % layout_id)
        print('Use `xkalamine list` to list all installed layouts.')
        sys.exit(1)

    info = layout_id.split('/')
    locale = info[0]
    name = info[1]

    path = os.path.join(XKB, 'symbols', locale)
    if not os.path.exists(path):  # should be caught by the `layout_id` check
        exit_LocaleNotSupported(locale)

    # remove layout from XKB/symbols and XKB/rules
    try:
        open_symbols(path, name)
        for filename in ['base.xml', 'evdev.xml']:
            path = os.path.join(XKB, 'rules', filename)
            open_rules(path, locale, name, True)

    except Exception as e:
        exit_FileNotWritable(e, path)

#!/usr/bin/env python3
import os
import shutil
import sys
import traceback

from lxml import etree
from lxml.builder import E


class XKBManager:
    """ Wrapper to list/add/remove keyboard drivers to XKB. """

    def __init__(self, xkb_root='/usr/share/X11/xkb/'):
        self._rootdir = xkb_root
        self._index = {}

    @property
    def index(self):
        return self._index.items()

    def add(self, layout):
        locale = layout.meta['locale']
        variant = layout.meta['variant']
        if locale not in self._index:
            self._index[locale] = {}
        self._index[locale][variant] = layout

    def remove(self, layout_id):
        locale, variant = layout_id.split('/')
        if locale not in self._index:
            self._index[locale] = {}
        self._index[locale][variant] = None

    def update(self):
        update_symbols(self._rootdir, self._index)  # XKB/symbols/{locales}
        update_rules(self._rootdir, self._index)  # XKB/rules/{base,evdev}.xml
        self._index = {}

    def list(self, mask=''):
        return list_rules(self._rootdir, mask)

    def list_all(self, mask=''):
        return list_rules(self._rootdir, mask, True)


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


def update_symbols_locale(path, named_layouts):
    """ Update Kalamine layouts in an xkb/symbols file. """

    text = ''
    modified_text = False
    names = list(map(lambda n: n.upper(), named_layouts.keys()))

    def is_marked_for_deletion(line):
        if line.startswith('// KALAMINE::'):
            name = line[13:-8]
        elif line.startswith('// LAFAYETTE::'):
            name = 'LAFAYETTE'
        else:
            return False
        return name in names

    with open(path, 'r+', encoding='utf-8') as symbols:

        # look for Kalamine layouts to be updated or removed
        between_marks = False
        closing_mark = ''
        for line in symbols:
            if line.endswith('::BEGIN\n'):
                if is_marked_for_deletion(line):
                    closing_mark = line[:-6] + 'END\n'
                    modified_text = True
                    between_marks = True
                    text = text.rstrip()
                else:
                    text += line
            elif line.endswith('::END\n'):
                if between_marks and line.startswith(closing_mark):
                    between_marks = False
                    closing_mark = ''
                else:
                    text += line
            elif not between_marks:
                text += line

        # clear previous Kalamine layouts if needed
        if modified_text:
            symbols.seek(0)
            symbols.write(text.rstrip() + '\n')
            symbols.truncate()

        # add new Kalamine layouts
        for name, layout in named_layouts.items():
            if layout is None:
                print('      - ' + name)
            else:
                print('      + ' + name)
                mark = get_symbol_mark(name)
                symbols.write('\n')
                symbols.write(mark['begin'])
                symbols.write(layout.xkb_patch.rstrip() + '\n')
                symbols.write(mark['end'])

        symbols.close()


def update_symbols(xkb_root, kbindex):
    """ Update Kalamine layouts in all xkb/symbols files. """

    for locale, named_layouts in kbindex.items():
        path = os.path.join(xkb_root, 'symbols', locale)
        if not os.path.exists(path):
            exit_LocaleNotSupported(locale)

        try:
            if not os.path.isfile(path + '.orig'):
                # backup, just in case :-)
                shutil.copy(path, path + '.orig')
                print('... ' + path + '.orig (backup)')

            print('... ' + path)
            update_symbols_locale(path, named_layouts)

        except Exception as exc:
            exit_FileNotWritable(exc, path)


###############################################################################
# Helpers: XKB/rules
#

def get_rules_locale(tree, locale):
    query = f"//layout/configItem/name[text()=\"{locale}\"]/../.."
    result = tree.xpath(query)
    if len(result) != 1:
        exit_LocaleNotSupported(locale)
    return tree.xpath(query)[0]


def remove_rules_variant(variant_list, name):
    signatures = ['kalamine']
    if name.lower().startswith('lafayette'):
        signatures.append('lafayette')

    for signature in signatures:
        query = "variant[@type=\"{format}\"]/configItem/name[text()=\"{name}\"]/../.."
        for variant in variant_list.xpath(query):
            variant.getparent().remove(variant)


def add_rules_variant(variant_list, name, description):
    variant_list.append(
        E.variant(
            E.configItem(
                E.name(name),
                E.description(description)
            ), type='kalamine'))


def update_rules(xkb_root, kbindex):
    """ Update references in XKB/rules/{base,evdev}.xml. """

    for filename in ['base.xml', 'evdev.xml']:
        try:
            path = os.path.join(xkb_root, 'rules', filename)
            tree = etree.parse(path, etree.XMLParser(remove_blank_text=True))

            for locale, named_layouts in kbindex.items():
                vlist = get_rules_locale(tree, locale).xpath('variantList')
                if len(vlist) != 1:
                    exit(f"Error: unexpected xml format in {path}.")
                for name, layout in named_layouts.items():
                    remove_rules_variant(vlist[0], name)
                    if layout is not None:
                        description = layout.meta['description']
                        add_rules_variant(vlist[0], name, description)

            tree.write(path, pretty_print=True, xml_declaration=True,
                       encoding='utf-8')
            print('... ' + path)

        except Exception as exc:
            exit_FileNotWritable(exc, path)


def list_rules(xkb_root, mask='', include_non_kalamine_variants=False):
    """ List all installed Kalamine layouts. """

    if mask in ('', '*'):
        locale_mask = '*'
        variant_mask = '*'
    else:
        m = mask.split('/')
        if len(m) != 2:
            exit('Error: expecting a [locale]/[variant] mask.')
        locale_mask, variant_mask = m

    query = '//variant'
    if not include_non_kalamine_variants:
        query += '[@type]'

    layouts = {}
    for filename in ['base.xml', 'evdev.xml']:
        tree = etree.parse(os.path.join(xkb_root, 'rules', filename))
        for variant in tree.xpath(query):
            locale = variant.xpath('../../configItem/name')[0].text
            name = variant.xpath('configItem/name')[0].text
            desc = variant.xpath('configItem/description')[0].text
            layout_id = locale + '/' + name
            if layout_id not in layouts \
               and locale_mask in ('*', locale) \
               and variant_mask in ('*', name):
                layouts[layout_id] = desc

    return layouts


###############################################################################
# Exception Handling (there must be a better way...)
#

def exit(message):
    print('')
    print(message)
    sys.exit(1)


def exit_LocaleNotSupported(locale):
    exit(f"Error: the `{locale}` locale is not supported.")


def exit_FileNotWritable(exception, path):
    if isinstance(exception, PermissionError):  # noqa: F821
        exit('Permission denied. Are you root?')
    elif isinstance(exception, IOError):
        exit(f"Error: could not write to file {path}.")
    else:  # exit('Unexpected error: ' + sys.exc_info()[0])
        exit(f"Error: {exception}.\n{traceback.format_exc()}")

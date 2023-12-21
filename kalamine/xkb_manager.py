#!/usr/bin/env python3
import os
import sys
import traceback

from lxml import etree
from lxml.builder import E

CFG_HOME = os.environ.get('XDG_CONFIG_HOME') or \
    os.path.join(os.environ.get('HOME'), '.config')
XKB_HOME = os.path.join(CFG_HOME, 'xkb')
XKB_ROOT = '/usr/share/X11/xkb/'


class XKBManager:
    """ Wrapper to list/add/remove keyboard drivers to XKB. """

    def __init__(self, xkb_root=XKB_ROOT):
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

    def remove(self, locale, variant):
        if locale not in self._index:
            self._index[locale] = {}
        self._index[locale][variant] = None

    def update(self):
        update_symbols(self._rootdir, self._index)  # XKB/symbols/{locales}
        update_rules(self._rootdir, self._index)  # XKB/rules/{base,evdev}.xml
        self._index = {}

    def clean(self):
        """ Drop the obsolete 'type' attributes Kalamine used to add. """
        for filename in ['base.xml', 'evdev.xml']:
            filepath = os.path.join(self._rootdir, 'rules', filename)
            if not os.path.exists(filepath):
                continue
            tree = etree.parse(filepath, etree.XMLParser(remove_blank_text=True))
            for variant in tree.xpath('//variant[@type]'):
                variant.attrib.pop('type')

    def list(self, mask=''):
        layouts = list_rules(self._rootdir, mask)
        return list_symbols(self._rootdir, layouts)

    def list_all(self, mask=''):
        return list_rules(self._rootdir, mask)

    def has_custom_symbols(self):
        """ Check if there is a usable xkb/symbols/custom file. """

        custom_path = os.path.join(self._rootdir, 'symbols', 'custom')
        if not os.path.exists(custom_path):
            return False

        for filename in ['base.xml', 'evdev.xml']:
            filepath = os.path.join(self._rootdir, 'rules', filename)
            if not os.path.exists(filepath):
                continue
            tree = etree.parse(filepath)
            if bool(tree.xpath(f"//layout/configItem/name[text()=\"custom\"]")):
                return True

        return False


""" On GNU/Linux, keyboard layouts must be installed in /usr/share/X11/xkb. To
    be able to revert a layout installation, Kalamine marks layouts like this:

    - XKB/symbols/[locale]: layout definitions
        // KALAMINE::[NAME]::BEGIN
        xkb_symbols "[name]" { ... }
        // KALAMINE::[NAME]::END

    Earlier versions of XKalamine used to mark index files as well but recent
    versions of Gnome do not support the custom `type` attribute any more, which
    must be removed:

    - XKB/rules/{base,evdev}.xml: layout references
        <variant type="kalamine">
            <configItem>
                <name>lafayette42</name>
                <description>French (Lafayette42)</description>
            </configItem>
        </variant>

    Even worse, the Lafayette project has released a first installer before
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

def clean_legacy_lafayette():
    return


###############################################################################
# Helpers: XKB/symbols
#


LEGACY_MARK = {
    'begin': '// LAFAYETTE::BEGIN\n',
    'end': '// LAFAYETTE::END\n'
}


def get_symbol_mark(name):
    return {
        'begin': '// KALAMINE::' + name.upper() + '::BEGIN\n',
        'end': '// KALAMINE::' + name.upper() + '::END\n'
    }


def is_new_symbol_mark(line):
    if line.endswith('::BEGIN\n'):
        if line.startswith('// KALAMINE::'):
            return line[13:-8].lower()  # XXX Kalamine expects lowercase names
        elif line.startswith('// LAFAYETTE::'):  # obsolete marker
            return 'lafayette'
    return None


def update_symbols_locale(path, named_layouts):
    """ Update Kalamine layouts in an xkb/symbols file. """

    text = ''
    modified_text = False
    with open(path, 'r+', encoding='utf-8') as symbols:

        # look for Kalamine layouts to be updated or removed
        between_marks = False
        closing_mark = ''
        for line in symbols:
            name = is_new_symbol_mark(line)
            if name:
                if name in named_layouts.keys():
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


def update_symbols(xkb_root, kb_index):
    """ Update Kalamine layouts in all xkb/symbols files. """

    for locale, named_layouts in kb_index.items():
        path = os.path.join(xkb_root, 'symbols', locale)
        with open(path, 'w') as file:
            file.write('// Generated by Kalamine')
            file.close()

        try:
            print('... ' + path)
            update_symbols_locale(path, named_layouts)

        except Exception as exc:
            exit_FileNotWritable(exc, path)


def list_symbols(xkb_root, kb_index):
    """ Filter input layouts: only keep the ones defined with Kalamine. """

    filtered_index = {}
    for locale, variants in sorted(kb_index.items()):
        path = os.path.join(xkb_root, 'symbols', locale)
        if not os.path.exists(path):
            continue

        with open(path, 'r', encoding='utf-8') as symbols:
            for line in symbols:
                name = is_new_symbol_mark(line)
                if name in variants.keys():
                    if locale not in filtered_index:
                        filtered_index[locale] = {}
                    filtered_index[locale][name] = variants[name]

    return filtered_index


###############################################################################
# Helpers: XKB/rules
#

def get_rules_locale(tree, locale):
    query = f'//layout/configItem/name[text()="{locale}"]/../..'
    result = tree.xpath(query)
    if len(result) != 1:
        tree.xpath('//layoutList')[0].append(
            E.layout(
                E.configItem(E.name(locale)),
                E.variantList()))
    return tree.xpath(query)[0]


def remove_rules_variant(variant_list, name):
    query = f'variant/configItem/name[text()="{name}"]/../..'
    for variant in variant_list.xpath(query):
        variant.getparent().remove(variant)


def add_rules_variant(variant_list, name, description):
    variant_list.append(
        E.variant(
            E.configItem(
                E.name(name),
                E.description(description))))


def update_rules(xkb_root, kb_index):
    """ Update references in XKB/rules/{base,evdev}.xml. """

    for filename in ['base.xml', 'evdev.xml']:
        filepath = os.path.join(xkb_root, 'rules', filename)
        if not os.path.exists(filepath):
            continue

        try:
            tree = etree.parse(filepath, etree.XMLParser(remove_blank_text=True))

            for locale, named_layouts in kb_index.items():
                vlist = get_rules_locale(tree, locale).xpath('variantList')
                if len(vlist) != 1:
                    exit(f"Error: unexpected xml format in {filepath}.")
                for name, layout in named_layouts.items():
                    remove_rules_variant(vlist[0], name)
                    if layout is not None:
                        description = layout.meta['description']
                        add_rules_variant(vlist[0], name, description)

            tree.write(filepath, pretty_print=True, xml_declaration=True,
                       encoding='utf-8')
            print('... ' + filepath)

        except Exception as exc:
            exit_FileNotWritable(exc, filepath)


def list_rules(xkb_root, mask='*'):
    """ List all matching XKB layouts. """

    if mask in ('', '*'):
        locale_mask = '*'
        variant_mask = '*'
    else:
        m = mask.split('/')
        if len(m) == 2:
            locale_mask, variant_mask = m
        else:
            locale_mask = mask
            variant_mask = "*"

    kb_index = {}
    for filename in ['base.xml', 'evdev.xml']:
        filepath = os.path.join(xkb_root, 'rules', filename)
        if not os.path.exists(filepath):
            continue

        tree = etree.parse(filepath)
        for variant in tree.xpath('//variant'):
            locale = variant.xpath('../../configItem/name')[0].text
            name = variant.xpath('configItem/name')[0].text
            desc = variant.xpath('configItem/description')[0].text

            if locale_mask in ('*', locale) and variant_mask in ('*', name):
                if locale not in kb_index:
                    kb_index[locale] = {}
                kb_index[locale][name] = desc

    return kb_index


###############################################################################
# Exception Handling (there must be a better way...)
#

def sys_exit(message):
    print('')
    print(message)
    sys.exit(1)


def exit_LocaleNotSupported(locale):
    sys_exit(f"Error: the `{locale}` locale is not supported.")


def exit_FileNotWritable(exception, path):
    if isinstance(exception, PermissionError):  # noqa: F821
        raise exception
        # sys_exit('Permission denied. Are you root?')
    elif isinstance(exception, IOError):
        sys_exit(f"Error: could not write to file {path}.")
    else:
        sys_exit(f"Error: {exception}.\n{traceback.format_exc()}")

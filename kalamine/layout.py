#!/usr/bin/env python3
import datetime
import os
import re
import sys
import yaml

import tomli

from .template import xkb_keymap, \
    osx_keymap, osx_actions, osx_terminators, \
    klc_keymap, klc_deadkeys, klc_dk_index, \
    web_keymap, web_deadkeys

from .utils import open_local_file, load_data, text_to_lines, lines_to_text, \
    DEAD_KEYS, ODK_ID


###
# Helpers
#


def upper_key(letter):
    if len(letter) != 1:  # dead key?
        return ' '
    custom_alpha = {
        '\u00df': '\u1e9e',  # ß ẞ
        '\u007c': '\u00a6',  # | ¦
        '\u003c': '\u2264',  # < ≤
        '\u003e': '\u2265',  # > ≥
        '\u2020': '\u2021',  # † ‡
        '\u2190': '\u21d0',  # ← ⇐
        '\u2191': '\u21d1',  # ↑ ⇑
        '\u2192': '\u21d2',  # → ⇒
        '\u2193': '\u21d3',  # ↓ ⇓
        '\u00b5': ' ',       # µ (to avoid getting `Μ` as uppercase)
    }
    if letter in custom_alpha:
        return custom_alpha[letter]
    if letter.upper() != letter.lower():
        return letter.upper()
    return ' '


def substitute_lines(text, variable, lines):
    prefix = 'KALAMINE::'
    exp = re.compile('.*' + prefix + variable + '.*')

    indent = ''
    for line in text.split('\n'):
        m = exp.match(line)
        if m:
            indent = m.group().split(prefix)[0]
            break

    return exp.sub(lines_to_text(lines, indent), text)


def substitute_token(text, token, value):
    exp = re.compile('\\$\\{' + token + '(=[^\\}]*){0,1}\\}')
    return exp.sub(value, text)


def load_tpl(layout, ext):
    tpl = 'base'
    if layout.has_altgr:
        tpl = 'full'
        if layout.has_1dk and ext.startswith('.xkb'):
            tpl = 'full_1dk'
    out = open_local_file(os.path.join('tpl', tpl + ext)).read()
    out = substitute_lines(out, 'GEOMETRY_base', layout.base)
    out = substitute_lines(out, 'GEOMETRY_full', layout.full)
    out = substitute_lines(out, 'GEOMETRY_altgr', layout.altgr)
    for key, value in layout.meta.items():
        out = substitute_token(out, key, value)
    return out


def load_descriptor(file_path):
    if file_path.endswith('.yaml') or file_path.endswith('.yml'):
        with open(file_path, encoding='utf-8') as file:
            return yaml.load(file, Loader=yaml.SafeLoader)
    with open(file_path, mode='rb') as file:
        return tomli.load(file)


###
# Constants
#


CONFIG = {
    'author': 'Fabien Cazenave',
    'license': 'WTFPL - Do What The Fuck You Want Public License',
    'geometry': 'ISO'
}

SPACEBAR = {
    'shift':       " ",  # U+0020 SPACE
    'altgr':       " ",  # U+0020 SPACE
    'altgr_shift': " ",  # U+0020 SPACE
    '1dk':         "'",  # U+0027 APOSTROPHE
    '1dk_shift':   "'"   # U+0027 APOSTROPHE
}

GEOMETRY = load_data('geometry.yaml')


###
# Main
#


class KeyboardLayout:
    """ Lafayette-style keyboard layout: base + 1dk + altgr layers. """

    def __init__(self, filepath):
        """ Import a keyboard layout to instanciate the object. """

        # initialize a blank layout
        self.layers = [{}, {}, {}, {}, {}, {}]
        self.dead_keys = {}        # dictionary subset of DEAD_KEYS
        self.dk_index = []         # ordered keys of the above dictionary
        self.meta = CONFIG.copy()  # default parameters, hardcoded
        self.has_altgr = False
        self.has_1dk = False

        # load the YAML data (and its ancessor, if any)
        try:
            cfg = load_descriptor(filepath)
            if 'extends' in cfg:
                path = os.path.join(os.path.dirname(filepath), cfg['extends'])
                ext = load_descriptor(path)
                ext.update(cfg)
                cfg = ext
        except Exception as exc:
            print('File could not be parsed.')
            print(f"Error: {exc}.")
            sys.exit(1)

        # metadata: self.meta
        for k in cfg:
            if k != 'base' and k != 'full' and k != 'altgr' \
                    and not isinstance(cfg[k], dict):
                self.meta[k] = cfg[k]
        filename = os.path.splitext(os.path.basename(filepath))[0]
        self.meta['name'] = cfg['name'] if 'name' in cfg else filename
        self.meta['name8'] = cfg['name8'] if 'name8' in cfg \
            else self.meta['name'][0:8]
        self.meta['fileName'] = self.meta['name8'].lower()
        self.meta['lastChange'] = datetime.date.today().isoformat()

        # keyboard layers: self.layers & self.dead_keys
        rows = GEOMETRY[self.meta['geometry']]['rows']
        if 'full' in cfg:
            full = text_to_lines(cfg['full'])
            self._parse_template(full, rows, 0)
            self._parse_template(full, rows, 4)
            self.has_altgr = True
        else:
            base = text_to_lines(cfg['base'])
            self._parse_template(base, rows, 0)
            self._parse_template(base, rows, 2)
            if 'altgr' in cfg:
                self.has_altgr = True
                self._parse_template(text_to_lines(cfg['altgr']), rows, 4)

        # space bar
        spc = SPACEBAR.copy()
        if 'spacebar' in cfg:
            for k in cfg['spacebar']:
                spc[k] = cfg['spacebar'][k]
        self.layers[0]['spce'] = ' '
        self.layers[1]['spce'] = spc['shift']
        self.layers[2]['spce'] = spc['1dk']
        self.layers[3]['spce'] = spc['shift_1dk'] if 'shift_1dk' in spc \
            else spc['1dk']
        if self.has_altgr:
            self.layers[4]['spce'] = spc['altgr']
            self.layers[5]['spce'] = spc['altgr_shift']

        # active dead keys: self.dk_index
        for dk in DEAD_KEYS:
            if dk['char'] in self.dead_keys:
                self.dk_index.append(dk['char'])

        # remove unused characters in self.dead_keys[].{base,alt}
        def layer_has_char(char, layer_index):
            for id in self.layers[layer_index]:
                if self.layers[layer_index][id] == char:
                    return True
            return False

        for dk_id in self.dead_keys:
            base = self.dead_keys[dk_id]['base']
            alt = self.dead_keys[dk_id]['alt']
            used_base = ''
            used_alt = ''
            for i in range(len(base)):
                if layer_has_char(base[i], 0) or layer_has_char(base[i], 1):
                    used_base += base[i]
                    used_alt += alt[i]
            self.dead_keys[dk_id]['base'] = used_base
            self.dead_keys[dk_id]['alt'] = used_alt

        # 1dk behavior
        if ODK_ID in self.dead_keys:
            self.has_1dk = True
            odk = self.dead_keys[ODK_ID]
            # alt_self (double-press), alt_space (1dk+space)
            odk['alt_space'] = spc['1dk']
            for key in self.layers[0]:
                if self.layers[0][key] == ODK_ID:
                    odk['alt_self'] = self.layers[2][key]
                    break
            # copy the 2nd and 3rd layers to the dead key
            for i in [0, 1]:
                for (name, alt_char) in self.layers[i + 2].items():
                    base_char = self.layers[i][name]
                    if name != 'spce' and base_char != ODK_ID:
                        odk['base'] += base_char
                        odk['alt'] += alt_char

    def _parse_template(self, template, rows, layer_number):
        """ Extract a keyboard layer from a template. """

        if layer_number == 0:  # base layer
            col_offset = 0
        else:  # AltGr or 1dk
            col_offset = 2

        j = 0
        for row in rows:
            i = row['offset'] + col_offset
            keys = row['keys']

            base = list(template[2 + j * 3])
            shift = list(template[1 + j * 3])

            for key in keys:
                base_key = ('*' if base[i - 1] == '*' else '') + base[i]
                shift_key = ('*' if shift[i - 1] == '*' else '') + shift[i]

                if layer_number == 0 and base_key == ' ':  # 'shift' prevails
                    base_key = shift_key.lower()
                if layer_number != 0 and shift_key == ' ':
                    shift_key = upper_key(base_key)

                if base_key != ' ':
                    self.layers[layer_number + 0][key] = base_key
                if shift_key != ' ':
                    self.layers[layer_number + 1][key] = shift_key

                for dk in DEAD_KEYS:
                    if base_key == dk['char']:
                        self.dead_keys[base_key] = dk.copy()
                    if shift_key == dk['char']:
                        self.dead_keys[shift_key] = dk.copy()

                i += 6

            j += 1

    ###
    # Geometry: base, full, altgr
    #

    def _fill_template(self, template, rows, layer_number):
        """ Fill a template with a keyboard layer. """

        if layer_number == 0:  # base layer
            col_offset = 0
            shift_prevails = True
        else:  # AltGr or 1dk
            col_offset = 2
            shift_prevails = False

        j = 0
        for row in rows:
            i = row['offset'] + col_offset
            keys = row['keys']

            base = list(template[2 + j * 3])
            shift = list(template[1 + j * 3])

            for key in keys:
                base_key = ' '
                if key in self.layers[layer_number]:
                    base_key = self.layers[layer_number][key]

                shift_key = ' '
                if key in self.layers[layer_number + 1]:
                    shift_key = self.layers[layer_number + 1][key]

                dead_base = len(base_key) == 2 and base_key[0] == '*'
                dead_shift = len(shift_key) == 2 and shift_key[0] == '*'

                if shift_prevails:
                    shift[i] = shift_key[-1]
                    if dead_shift:
                        shift[i-1] = '*'
                    if upper_key(base_key) != shift_key:
                        base[i] = base_key[-1]
                        if dead_base:
                            base[i-1] = '*'
                else:
                    base[i] = base_key[-1]
                    if dead_base:
                        base[i-1] = '*'
                    if upper_key(base_key) != shift_key:
                        shift[i] = shift_key[-1]
                        if dead_shift:
                            shift[i-1] = '*'

                i += 6

            template[2 + j * 3] = ''.join(base)
            template[1 + j * 3] = ''.join(shift)
            j += 1

        return template

    def _get_geometry(self, layers=[0], name='ISO'):
        """ `geometry` view of the requested layers. """

        rows = GEOMETRY[name]['rows']
        template = GEOMETRY[name]['template'].split('\n')[:-1]
        for i in layers:
            template = self._fill_template(template, rows, i)
        return template

    @property
    def base(self):
        """ Base + 1dk layers. """
        return self._get_geometry([0, 2])

    @property
    def full(self):
        """ Base + AltGr layers. """
        return self._get_geometry([0, 4])

    @property
    def altgr(self):
        """ AltGr layer only. """
        return self._get_geometry([4])

    ###
    # OS-specific drivers: keylayout, klc, xkb, xkb_patch
    #

    @property
    def keylayout(self):
        """ macOS driver """
        out = load_tpl(self, '.keylayout')
        for i, layer in enumerate(osx_keymap(self)):
            out = substitute_lines(out, 'LAYER_' + str(i), layer)
        out = substitute_lines(out, 'ACTIONS', osx_actions(self))
        out = substitute_lines(out, 'TERMINATORS', osx_terminators(self))
        return out

    @property
    def klc(self):
        """ Windows driver (warning: requires CR/LF + UTF16LE encoding) """
        out = load_tpl(self, '.klc')
        out = substitute_lines(out, 'LAYOUT', klc_keymap(self))
        out = substitute_lines(out, 'DEAD_KEYS', klc_deadkeys(self))
        out = substitute_lines(out, 'DEAD_KEY_INDEX', klc_dk_index(self))
        out = substitute_token(out, 'encoding', 'utf-16le')
        return out

    @property
    def xkb(self):  # will not work with Wayland
        """ GNU/Linux driver (standalone / user-space) """
        out = load_tpl(self, '.xkb')
        out = substitute_lines(out, 'LAYOUT', xkb_keymap(self, False))
        return out

    @property
    def xkb_patch(self):
        """ GNU/Linux driver (system patch) """
        out = load_tpl(self, '.xkb_patch')
        out = substitute_lines(out, 'LAYOUT', xkb_keymap(self, True))
        return out

    ###
    # JSON output: keymap (base+altgr layers) and dead keys
    #

    @property
    def json(self):
        """ JSON layout descriptor """
        return {
            'name': self.meta['name'],
            'description': self.meta['description'],
            'geometry': self.meta['geometry'].lower(),
            'keymap': web_keymap(self),
            'deadkeys': web_deadkeys(self),
            'altgr': self.has_altgr
        }

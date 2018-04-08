#!/usr/bin/env python3
import datetime
import os
import yaml

from .utils import open_local_file, text_to_lines


##
# Helpers
#


def upper_key(letter):
    customAlpha = {
        '\u00df': '\u1e9e',  # ß ẞ
        '\u007c': '\u00a6',  # | ¦
        '\u003c': '\u2264',  # < ≤
        '\u003e': '\u2265',  # > ≥
        '\u2020': '\u2021',  # † ‡
        '\u2190': '\u21d0',  # ← ⇐
        '\u2191': '\u21d1',  # ↑ ⇑
        '\u2192': '\u21d2',  # → ⇒
        '\u2193': '\u21d3',  # ↓ ⇓
    }
    if letter in customAlpha:
        return customAlpha[letter]
    elif letter.upper() != letter.lower():
        return letter.upper()
    else:
        return ' '


def hex_ord(char):
    return hex(ord(char))[2:].zfill(4)


def xml_proof(char):
    if char not in '<&"\u00a0>':
        return char
    else:
        return '&#x{0};'.format(hex_ord(char))


def load_data(filename):
    return yaml.load(open_local_file(os.path.join('data', filename)))


##
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
DEAD_KEYS = load_data('dead_keys.yaml')
KEY_CODES = load_data('key_codes.yaml')
XKB_KEY_SYM = load_data('key_sym.yaml')

LAFAYETTE_KEY = '\u20e1'  # must match the value in dead_keys.yaml

LAYER_KEYS = [
    '- Digits',
    'ae01', 'ae02', 'ae03', 'ae04', 'ae05',
    'ae06', 'ae07', 'ae08', 'ae09', 'ae10',

    '- Letters, first row',
    'ad01', 'ad02', 'ad03', 'ad04', 'ad05',
    'ad06', 'ad07', 'ad08', 'ad09', 'ad10',

    '- Letters, second row',
    'ac01', 'ac02', 'ac03', 'ac04', 'ac05',
    'ac06', 'ac07', 'ac08', 'ac09', 'ac10',

    '- Letters, third row',
    'ab01', 'ab02', 'ab03', 'ab04', 'ab05',
    'ab06', 'ab07', 'ab08', 'ab09', 'ab10',

    '- Pinky keys',
    'ae11', 'ae12', 'ad11', 'ad12', 'ac11',
    'tlde', 'bksl', 'lsgt',

    '- Space bar',
    'spce'
]


##
# Main
#


class Layout:
    """ Lafayette-style keyboard layout: base + dead key + altgr layers. """

    def __init__(self, filepath, extends=''):
        """ Import a keyboard layout to instanciate the object. """

        # initialize a blank layout
        self.layers = [{}, {}, {}, {}, {}, {}]
        self.dead_keys = {}  # dictionary subset of DEAD_KEYS
        self.dk_index = []   # ordered keys of the above dictionary
        self.meta = CONFIG   # default parameters, hardcoded
        self.has_altgr = False
        self.has_1dk = False
        spc = SPACEBAR

        for file in ([filepath] if extends == '' else [extends, filepath]):
            """ Append data from YAML layout(s). """

            # metadata: self.meta
            cfg = yaml.load(open(file))
            for k in cfg:
                if k != 'base' and k != 'altgr' and k != 'spacebar':
                    self.meta[k] = cfg[k]
            fileName = os.path.splitext(os.path.basename(file))[0]
            self.meta['name'] = cfg['name'] if 'name' in cfg else fileName
            self.meta['name8'] = cfg['name8'] if 'name8' in cfg \
                else self.meta['name'][0:8]
            self.meta['fileName'] = self.meta['name8'].lower()
            self.meta['lastChange'] = datetime.date.today().isoformat()

            # keyboard layers: self.layers & self.dead_keys
            rows = GEOMETRY[self.meta['geometry']]['rows']
            base = text_to_lines(cfg['base'])
            self._parse_template(base, rows, 0)
            self._parse_template(base, rows, 2)
            self._parse_lafayette_keys()

            # optional AltGr layer
            if 'altgr' in cfg:
                self.has_altgr = True
                self._parse_template(text_to_lines(cfg['altgr']), rows, 4)

            # space bar
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

            # 1dk behavior: alt_self (double-press), alt_space (1dk+space)
            if LAFAYETTE_KEY in self.dead_keys:
                self.has_1dk = True
                odk = self.dead_keys[LAFAYETTE_KEY]
                odk['alt_space'] = spc['1dk']
                odk['alt_self'] = "'"
                for key in self.layers[0]:
                    if self.layers[0][key] == LAFAYETTE_KEY:
                        odk['alt_self'] = self.layers[2][key]
                        break

    def _parse_lafayette_keys(self):
        """ populates the `base` and `alt` props for the Lafayette dead key """

        if LAFAYETTE_KEY not in self.dead_keys:
            return

        base0 = list('')
        base1 = list('')
        alt0 = list('')
        alt1 = list('')

        for keyName in LAYER_KEYS:
            if keyName.startswith('-'):
                continue

            if keyName in self.layers[2]:
                base0.append(self.layers[0][keyName])
                alt0.append(self.layers[2][keyName])

            if keyName in self.layers[3]:
                base1.append(self.layers[1][keyName])
                alt1.append(self.layers[3][keyName])

        lafayette = self.dead_keys[LAFAYETTE_KEY]
        lafayette['base'] = ''.join(base0) + ''.join(base1)
        lafayette['alt'] = ''.join(alt0) + ''.join(alt1)

    def _parse_template(self, template, rows, layerNumber):
        """ Extract a keyboard layer from a template. """

        if layerNumber == 0:  # base layer
            colOffset = 0
        else:  # AltGr or dead key (lafayette)
            colOffset = 2

        j = 0
        for row in rows:
            i = row['offset'] + colOffset
            keys = row['keys']

            base = list(template[2 + j * 3])
            shift = list(template[1 + j * 3])

            for key in keys:
                baseKey = base[i]
                shiftKey = shift[i]

                if layerNumber == 0 and baseKey == ' ':  # 'shift' prevails
                    baseKey = shiftKey.lower()
                if layerNumber != 0 and shiftKey == ' ':
                    shiftKey = upper_key(baseKey)

                if (baseKey != ' '):
                    self.layers[layerNumber + 0][key] = baseKey
                if (shiftKey != ' '):
                    self.layers[layerNumber + 1][key] = shiftKey

                for dk in DEAD_KEYS:
                    if baseKey == dk['char']:
                        self.dead_keys[baseKey] = dk
                    if shiftKey == dk['char']:
                        self.dead_keys[shiftKey] = dk

                i += 6

            j += 1

    def _fill_template(self, template, rows, layerNumber):
        """ Fill a template with a keyboard layer. """

        if layerNumber == 0:  # base layer
            colOffset = 0
            shiftPrevails = True
        else:  # AltGr or dead key (lafayette)
            colOffset = 2
            shiftPrevails = False

        j = 0
        for row in rows:
            i = row['offset'] + colOffset
            keys = row['keys']

            base = list(template[2 + j * 3])
            shift = list(template[1 + j * 3])

            for key in keys:
                baseKey = ' '
                if key in self.layers[layerNumber]:
                    baseKey = self.layers[layerNumber][key]

                shiftKey = ' '
                if key in self.layers[layerNumber + 1]:
                    shiftKey = self.layers[layerNumber + 1][key]

                if shiftPrevails:
                    shift[i] = shiftKey
                    if upper_key(baseKey) != shiftKey:
                        base[i] = baseKey
                else:
                    base[i] = baseKey
                    if upper_key(baseKey) != shiftKey:
                        shift[i] = shiftKey

                i += 6

            template[2 + j * 3] = ''.join(base)
            template[1 + j * 3] = ''.join(shift)
            j += 1

        return template

    def get_geometry(self, layers=[0], name='ISO'):
        """ `geometry` view of the requested layers. """

        rows = GEOMETRY[name]['rows']
        template = GEOMETRY[name]['template'].split('\n')[:-1]
        for i in layers:
            template = self._fill_template(template, rows, i)
        return template

    """
    GNU/Linux: XKB
    - standalone xkb file to be used by `setxkbcomp` (Xorg only)
    - system-wide installer script for Xorg & Wayland
    """

    def get_xkb_keymap(self, eight_levels):
        """ Linux layout. """

        showDescription = True
        maxLength = 16  # `ISO_Level3_Latch` should be the longest symbol name

        output = []
        for keyName in LAYER_KEYS:
            if keyName.startswith('-'):  # separator
                if len(output):
                    output.append('')
                output.append('//' + keyName[1:])
                continue

            symbols = []
            description = ' //'
            for layer in self.layers:
                if keyName in layer:
                    symbol = layer[keyName]
                    desc = symbol
                    if symbol in self.dead_keys:
                        dk = self.dead_keys[symbol]
                        desc = dk['alt_self']
                        if dk['char'] == LAFAYETTE_KEY:
                            symbol = 'ISO_Level3_Latch'
                        else:
                            symbol = 'dead_' + dk['name']
                    elif symbol in XKB_KEY_SYM \
                            and len(XKB_KEY_SYM[symbol]) <= maxLength:
                        symbol = XKB_KEY_SYM[symbol]
                    else:
                        symbol = 'U' + hex_ord(symbol).upper()
                else:
                    desc = ' '
                    symbol = 'VoidSymbol'

                description += ' ' + desc
                symbols.append(symbol.ljust(maxLength))

            s = 'key <{}> {{[ {}, {}, {}, {}]}};'  # 4-level layout by default
            if self.has_altgr and self.has_1dk:
                """ 6 layers are needed: they won't fit on the 4-level format.
                System XKB files require a Neo-like eight-level solution.
                Standalone XKB files work best with a dual-group solution:
                one 4-level group for base+1dk, one two-level group for AltGr.
                """
                if eight_levels:  # system XKB file (patch)
                    s = 'key <{}> {{[ {}, {}, {}, {}, {}, {}, {}, {}]}};'
                    symbols.append('VoidSymbol'.ljust(maxLength))
                    symbols.append('VoidSymbol'.ljust(maxLength))
                else:  # user-space XKB file (standalone)
                    s = 'key <{}> {{[ {}, {}, {}, {}],[ {}, {}]}};'
            elif self.has_altgr:
                del symbols[3]
                del symbols[2]

            line = s.format(* [keyName.upper()] + symbols)
            if showDescription:
                line += description.rstrip()
                if line.endswith('\\'):
                    line += ' '  # escape trailing backslash
            output.append(line)

        return output

    @property
    def xkb_keymap(self):  # will not work with Wayland
        """ Linux layout, user-space file (standalone). """
        return self.get_xkb_keymap(False)

    @property
    def xkb_patch(self):
        """ Linux layout, system file (patch). """
        return self.get_xkb_keymap(True)

    """
    Windows: KLC
    To be used by the MS Keyboard Layout Creator to generate an installer.
    https://www.microsoft.com/en-us/download/details.aspx?id=22339
    https://levicki.net/articles/2006/09/29/HOWTO_Build_keyboard_layouts_for_Windows_x64.php
    Also supported by KbdEdit: http://www.kbdedit.com/ (non-free).
    """

    @property
    def klc_keymap(self):
        """ Windows layout, main part. """

        supportedSymbols = \
            '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

        output = []
        for keyName in LAYER_KEYS:
            if keyName.startswith('-'):
                if len(output):
                    output.append('')
                output.append('//' + keyName[1:])
                continue

            symbols = []
            description = '//'
            alpha = False

            for i in [0, 1, 4, 5]:
                layer = self.layers[i]

                if keyName in layer:
                    symbol = layer[keyName]
                    desc = symbol
                    if symbol in self.dead_keys:
                        desc = self.dead_keys[symbol]['alt_space']
                        symbol = hex_ord(desc) + '@'
                    else:
                        if i == 0:
                            alpha = symbol.upper() != symbol
                        if symbol not in supportedSymbols:
                            symbol = hex_ord(symbol)
                    symbols.append(symbol)
                else:
                    desc = ' '
                    symbols.append('-1')
                description += ' ' + desc

            if (self.has_altgr):
                output.append('\t'.join([
                    KEY_CODES['klc'][keyName],     # scan code & virtual key
                    '1' if alpha else '0',         # affected by CapsLock?
                    symbols[0], symbols[1], '-1',  # base layer
                    symbols[2], symbols[3],        # altgr layer
                    description.strip()
                ]))
            else:
                output.append('\t'.join([
                    KEY_CODES['klc'][keyName],     # scan code & virtual key
                    '1' if alpha else '0',         # affected by CapsLock?
                    symbols[0], symbols[1], '-1',  # base layer
                    description.strip()
                ]))

        return output

    @property
    def klc_deadkeys(self):
        """ Windows layout, dead keys. """

        output = []

        def appendLine(base, alt):
            s = '{0}\t{1}\t// {2} -> {3}'
            output.append(s.format(hex_ord(base), hex_ord(alt), base, alt))

        for k in self.dk_index:
            dk = self.dead_keys[k]

            output.append('// DEADKEY: ' + dk['name'].upper() + ' //{{{')
            output.append('DEADKEY\t' + hex_ord(dk['alt_space']))
            output.append('')

            if k == LAFAYETTE_KEY:
                output.extend(self.klc_dk_lafayette)
            else:
                for i in range(len(dk['base'])):
                    appendLine(dk['base'][i], dk['alt'][i])

            output.append('')
            output.append('// Space bar')
            appendLine('\u00a0', dk['alt_space'])
            appendLine('\u0020', dk['alt_space'])

            output.append('//}}}')
            output.append('')

        return output[:-1]

    @property
    def klc_dk_index(self):
        """ Windows layout, dead key index. """

        output = []
        for k in self.dk_index:
            dk = self.dead_keys[k]
            output.append('{0}\t"{1}"'.format(hex_ord(dk['alt_space']),
                                              dk['name'].upper()))
        return output

    @property
    def klc_dk_lafayette(self):
        """ Windows layout, Lafayette key. """

        output = []
        for i in [0, 1]:
            baseLayer = self.layers[i]
            extLayer = self.layers[i + 2]

            for keyName in LAYER_KEYS:
                if keyName.startswith('- Space') or keyName == 'spce':
                    continue
                if keyName.startswith('-'):
                    if len(output):
                        output.append('')
                    output.append('//' + keyName[1:])
                    continue
                elif keyName in extLayer:
                    base = baseLayer[keyName]
                    if base in self.dead_keys:
                        base = self.dead_keys[base]['alt_space']
                    ext = extLayer[keyName]
                    if (ext in self.dead_keys):
                        ext = self.dead_keys[ext]['alt_space']
                        lafayette = hex_ord(ext) + '@'
                    else:
                        lafayette = hex_ord(ext)

                    output.append('\t'.join([
                        hex_ord(base), lafayette, '// ' + base + ' -> ' + ext
                    ]))

        return output

    """
    MacOS X: keylayout
    https://developer.apple.com/library/content/technotes/tn2056/_index.html
    """

    @property
    def osx_keymap(self):
        """ Mac OSX layout, main part. """

        str = []
        for index in range(5):
            layer = self.layers[[0, 1, 0, 4, 5][index]]
            caps = index == 2

            def has_dead_keys(letter):
                for k in self.dead_keys:
                    if letter in self.dead_keys[k]['base']:
                        return True
                return False

            output = []
            for keyName in LAYER_KEYS:
                if keyName.startswith('-'):
                    if len(output):
                        output.append('')
                    output.append('<!--' + keyName[1:] + ' -->')
                    continue

                symbol = '&#x0010;'
                finalKey = True

                if keyName in layer:
                    key = layer[keyName]
                    if key in self.dead_keys:
                        symbol = 'dead_' + self.dead_keys[key]['name']
                        finalKey = False
                    else:
                        symbol = xml_proof(key.upper() if caps else key)
                        finalKey = not has_dead_keys(key)

                c = 'code="{0}"'.format(KEY_CODES['osx'][keyName]).ljust(10)
                a = '{0}="{1}"'.format('output' if finalKey
                                       else 'action', symbol)
                output.append('<key {0} {1} />'.format(c, a))

            str.append(output)
        return str

    @property
    def osx_actions(self):
        """ Mac OSX layout, dead key actions. """

        output = []
        deadKeys = []
        dkIndex = []

        def when(state, action):
            s = 'state="{0}"'.format(state).ljust(18)
            if action in self.dead_keys:
                a = 'next="{0}"'.format(self.dead_keys[action]['name'])
            elif action.startswith('dead_'):
                a = 'next="{0}"'.format(action[5:])
            else:
                a = 'output="{0}"'.format(xml_proof(action))
            return '  <when {0} {1} />'.format(s, a)

        # spacebar actions
        output.append('<!-- Spacebar -->')
        output.append('<action id="space">')
        output.append(when('none', ' '))
        for k in self.dk_index:
            dk = self.dead_keys[k]
            output.append(when(dk['name'], dk['alt_space']))
        output.append('</action>')
        output.append('<action id="nbsp">')
        output.append(when('none', '&#x00a0;'))
        for k in self.dk_index:
            dk = self.dead_keys[k]
            output.append(when(dk['name'], dk['alt_space']))
        output.append('</action>')

        # all other actions
        for keyName in LAYER_KEYS:
            if keyName.startswith('-'):
                output.append('')
                output.append('<!--' + keyName[1:] + ' -->')
                continue

            for i in [0, 1]:
                if keyName not in self.layers[i]:
                    continue

                key = self.layers[i][keyName]
                if i and key == self.layers[0][keyName]:
                    continue
                if key in self.dead_keys:
                    symbol = 'dead_' + self.dead_keys[key]['name']
                else:
                    symbol = xml_proof(key)

                action = []
                for k in self.dk_index:
                    dk = self.dead_keys[k]
                    if key in dk['base']:
                        idx = dk['base'].index(key)
                        action.append(when(dk['name'], dk['alt'][idx]))

                if key in self.dead_keys:
                    deadKeys.append('<action id="{0}">'.format(symbol))
                    deadKeys.append(when('none', symbol))
                    deadKeys.extend(action)
                    deadKeys.append('</action>')
                    dkIndex.append(symbol)
                elif len(action):
                    output.append('<action id="{0}">'.format(symbol))
                    output.append(when('none', symbol))
                    output.extend(action)
                    output.append('</action>')

            for i in [2, 3, 4, 5]:
                if keyName not in self.layers[i]:
                    continue
                key = self.layers[i][keyName]
                if key not in self.dead_keys:
                    continue
                symbol = 'dead_' + self.dead_keys[key]['name']
                if symbol in dkIndex:
                    continue
                deadKeys.append('<action id="{0}">'.format(symbol))
                deadKeys.append(when('none', symbol))
                deadKeys.extend(action)
                deadKeys.append('</action>')
                dkIndex.append(symbol)

        return deadKeys + [''] + output

    @property
    def osx_terminators(self):
        """ Mac OSX layout, dead key terminators. """

        output = []
        for k in self.dk_index:
            dk = self.dead_keys[k]
            s = 'state="{0}"'.format(dk['name']).ljust(18)
            o = 'output="{0}"'.format(xml_proof(dk['alt_self']))
            output.append(' <when {0} {1} />'.format(s, o))
        return output

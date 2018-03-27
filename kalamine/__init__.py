#!/usr/bin/env python3

import datetime
import os
import re
import unicodedata
import yaml


##
# Helpers and constants used by the `Layout` class
#


def add_spaces_before_combining_chars(text):
    out = ''
    for char in text:
        if unicodedata.combining(char):
            out += ' ' + char
        else:
            out += char
    return out


def remove_spaces_before_combining_chars(text):
    out = list('')
    for char in text:
        if unicodedata.combining(char):
            out[-1] = char
        else:
            out.append(char)
    return ''.join(out)


def lines_to_text(lines, indent=''):
    out = ''
    for line in lines:
        if len(line):
            out += indent + add_spaces_before_combining_chars(line)
        out += '\n'
    return out[:-1]


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


def openLocalFile(fileName):
    return open(os.path.join(os.path.dirname(__file__), fileName))


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

GEOMETRY = yaml.load(openLocalFile('data/geometry.yaml'))
DEAD_KEYS = yaml.load(openLocalFile('data/dead_keys.yaml'))
KEY_CODES = yaml.load(openLocalFile('data/key_codes.yaml'))
XKB_KEY_SYM = yaml.load(openLocalFile('data/key_sym.yaml'))

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
    'tlde', 'ae11', 'ae12', 'ad11', 'ad12', 'ac11', 'bksl', 'lsgt',

    '- Space bar',
    'spce'
]


class Layout:
    """ Lafayette-style keyboard layout: base + dead key + altgr layers. """

    def __init__(self, filePath):
        """ Import a keyboard layout to instanciate the object. """

        self.layers = [{}, {}, {}, {}, {}, {}]
        self.dead_keys = {}  # dictionary subset of DEAD_KEYS
        self.dk_index = []   # ordered keys of the above dictionary
        self.meta = CONFIG   # default parameters, hardcoded
        self.has_altgr = False

        # metadata: self.meta
        cfg = yaml.load(open(filePath))
        for k in cfg:
            if k != 'base' and k != 'altgr' and k != 'spacebar':
                self.meta[k] = cfg[k]
        fileName = os.path.splitext(os.path.basename(filePath))[0]
        self.meta['name'] = cfg['name'] if 'name' in cfg else fileName
        self.meta['name8'] = cfg['name8'] if 'name8' in cfg \
            else self.meta['name'][0:8]
        self.meta['fileName'] = self.meta['name8'].lower()
        self.meta['lastChange'] = datetime.date.today().isoformat()

        # keyboard layers: self.layers & self.dead_keys
        rows = GEOMETRY[self.meta['geometry']]['rows']
        base = remove_spaces_before_combining_chars(cfg['base']).split('\n')
        self._parse_template(base, rows, 0)
        self._parse_template(base, rows, 2)
        self._parse_lafayette_keys()

        # optional AltGr layer
        if 'altgr' in cfg:
            tmp = remove_spaces_before_combining_chars(cfg['altgr'])
            self._parse_template(tmp.split('\n'), rows, 4)
            self.has_altgr = True

        # space bar
        spc = SPACEBAR
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

    @property
    def xkb(self):
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

            s = 'key <{}> {{[ {}, {}, {}, {}],[ {}, {}]}};' if self.has_altgr \
                else 'key <{}> {{[ {}, {}, {}, {}]}};'
            line = s.format(* [keyName.upper()] + symbols)
            if showDescription:
                line += description.rstrip()
            output.append(line)

        return output

    @property
    def klc(self):
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
                output.extend(self.klc_dkLafayette)
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
    def klc_dkIndex(self):
        """ Windows layout, dead key index. """

        output = []
        for k in self.dk_index:
            dk = self.dead_keys[k]
            output.append('{0}\t"{1}"'.format(hex_ord(dk['alt_space']),
                                              dk['name'].upper()))
        return output

    @property
    def klc_dkLafayette(self):
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

    def get_osx_keyMap(self, index):
        """ Mac OSX layout, main part. """

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
            a = '{0}="{1}"'.format('output' if finalKey else 'action', symbol)
            output.append('<key {0} {1} />'.format(c, a))

        return output

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


##
# Main script and related helpers
#


def substitute_lines(template, variable, lines):
    prefix = 'LAFAYETTE::'
    exp = re.compile('.*' + prefix + variable + '.*')

    indent = ''
    for line in template.split('\n'):
        m = exp.match(line)
        if m:
            indent = m.group().split(prefix)[0]
            break

    return exp.sub(lines_to_text(lines, indent), template)


def substitute_token(template, token, value):
    exp = re.compile('\$\{' + token + '(=[^\}]*){0,1}\}')
    return exp.sub(value, template)


def substitute_meta(template, meta):
    for k in meta:
        template = substitute_token(template, k, meta[k])
    return template


def make_layout(filePath):
    layout = Layout(filePath)
    layout_qwerty = layout.get_geometry([0, 2])  # base + dead key
    layout_altgr = layout.get_geometry([4])      # altgr

    if not os.path.exists('dist'):
        os.makedirs('dist')

    # Windows driver (the utf-8 template is converted to a utf-16le file)
    klc_path = 'dist/' + layout.meta['fileName'] + '.klc'
    klc_tpl = 'tpl/full.klc' if layout.has_altgr else 'tpl/base.klc'
    klc_out = openLocalFile(klc_tpl).read()
    klc_out = substitute_lines(klc_out, 'GEOMETRY_qwerty', layout_qwerty)
    klc_out = substitute_lines(klc_out, 'GEOMETRY_altgr', layout_altgr)
    klc_out = substitute_lines(klc_out, 'LAYOUT', layout.klc)
    klc_out = substitute_lines(klc_out, 'DEAD_KEYS', layout.klc_deadkeys)
    klc_out = substitute_lines(klc_out, 'DEAD_KEY_INDEX', layout.klc_dkIndex)
    klc_out = substitute_token(klc_out, 'encoding', 'utf-16le')
    klc_out = substitute_meta(klc_out, layout.meta)
    klc_out = klc_out.replace('\n', '\r\n')
    open(klc_path, 'w', encoding='utf-16le').write(klc_out)
    print('... ' + klc_path)

    # an utf-8 version can't hurt (easier to diff)
    klc_path = 'dist/' + layout.meta['fileName'] + '_utf8.klc'
    open(klc_path, 'w').write(klc_out)
    print('... ' + klc_path)

    # Mac OSX driver
    osx_path = 'dist/' + layout.meta['fileName'] + '.keylayout'
    osx_out = openLocalFile('tpl/full.keylayout').read()
    osx_out = substitute_lines(osx_out, 'GEOMETRY_qwerty', layout_qwerty)
    osx_out = substitute_lines(osx_out, 'GEOMETRY_altgr', layout_altgr)
    osx_out = substitute_lines(osx_out, 'LAYOUT_0', layout.get_osx_keyMap(0))
    osx_out = substitute_lines(osx_out, 'LAYOUT_1', layout.get_osx_keyMap(1))
    osx_out = substitute_lines(osx_out, 'LAYOUT_2', layout.get_osx_keyMap(2))
    osx_out = substitute_lines(osx_out, 'LAYOUT_3', layout.get_osx_keyMap(3))
    osx_out = substitute_lines(osx_out, 'LAYOUT_4', layout.get_osx_keyMap(4))
    osx_out = substitute_lines(osx_out, 'ACTIONS', layout.osx_actions)
    osx_out = substitute_lines(osx_out, 'TERMINATORS', layout.osx_terminators)
    osx_out = substitute_meta(osx_out, layout.meta)
    open(osx_path, 'w').write(osx_out)
    print('... ' + osx_path)

    # Linux driver
    xkb_path = 'dist/' + layout.meta['fileName'] + '.xkb'
    xkb_tpl = 'tpl/full.xkb' if layout.has_altgr else 'tpl/base.xkb'
    xkb_out = openLocalFile(xkb_tpl).read()
    xkb_out = substitute_lines(xkb_out, 'GEOMETRY_qwerty', layout_qwerty)
    xkb_out = substitute_lines(xkb_out, 'GEOMETRY_altgr', layout_altgr)
    xkb_out = substitute_lines(xkb_out, 'LAYOUT', layout.xkb)
    xkb_out = substitute_meta(xkb_out, layout.meta)
    open(xkb_path, 'w').write(xkb_out)
    print('... ' + xkb_path)

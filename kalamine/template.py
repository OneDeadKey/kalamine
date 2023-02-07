#!/usr/bin/env python3
from .utils import load_data, LAYER_KEYS, ODK_ID


###
# Helpers
#

KEY_CODES = load_data('key_codes.yaml')
XKB_KEY_SYM = load_data('key_sym.yaml')


def hex_ord(char):
    return hex(ord(char))[2:].zfill(4)


def xml_proof(char):
    if char not in '<&"\u0020\u00a0\u202f>':
        return char
    return f"&#x{hex_ord(char)};"


def xml_proof_id(symbol):
    return symbol[2:-1] if symbol.startswith('&#x') else symbol


###
# GNU/Linux: XKB
# - standalone xkb file to be used by `setxkbcomp` (Xorg only)
# - system-wide installer script for Xorg & Wayland
#

def xkb_keymap(layout, eight_levels):
    """ Linux layout. """

    show_description = True
    max_length = 16  # `ISO_Level3_Latch` should be the longest symbol name

    output = []
    for key_name in LAYER_KEYS:
        if key_name.startswith('-'):  # separator
            if output:
                output.append('')
            output.append('//' + key_name[1:])
            continue

        symbols = []
        description = ' //'
        for layer in layout.layers:
            if key_name in layer:
                symbol = layer[key_name]
                desc = symbol
                if symbol in layout.dead_keys:
                    dk = layout.dead_keys[symbol]
                    desc = dk['alt_self']
                    if dk['char'] == ODK_ID:
                        symbol = 'ISO_Level3_Latch'
                    else:
                        symbol = 'dead_' + dk['name']
                elif symbol in XKB_KEY_SYM \
                        and len(XKB_KEY_SYM[symbol]) <= max_length:
                    symbol = XKB_KEY_SYM[symbol]
                else:
                    symbol = 'U' + hex_ord(symbol).upper()
            else:
                desc = ' '
                symbol = 'VoidSymbol'

            description += ' ' + desc
            symbols.append(symbol.ljust(max_length))

        key = 'key <{}> {{[ {}, {}, {}, {}]}};'  # 4-level layout by default
        if layout.has_altgr and layout.has_1dk:
            # 6 layers are needed: they won't fit on the 4-level format.
            # System XKB files require a Neo-like eight-level solution.
            # Standalone XKB files work best with a dual-group solution:
            # one 4-level group for base+1dk, one two-level group for AltGr.
            if eight_levels:  # system XKB file (patch)
                key = 'key <{}> {{[ {}, {}, {}, {}, {}, {}, {}, {}]}};'
                symbols.append('VoidSymbol'.ljust(max_length))
                symbols.append('VoidSymbol'.ljust(max_length))
            else:  # user-space XKB file (standalone)
                key = 'key <{}> {{[ {}, {}, {}, {}],[ {}, {}]}};'
        elif layout.has_altgr:
            del symbols[3]
            del symbols[2]

        line = key.format(* [key_name.upper()] + symbols)
        if show_description:
            line += description.rstrip()
            if line.endswith('\\'):
                line += ' '  # escape trailing backslash
        output.append(line)

    return output


###
# Windows: KLC
# To be used by the MS Keyboard Layout Creator to generate an installer.
# https://www.microsoft.com/en-us/download/details.aspx?id=102134
# https://levicki.net/articles/2006/09/29/HOWTO_Build_keyboard_layouts_for_Windows_x64.php
# Also supported by KbdEdit: http://www.kbdedit.com/ (non-free).
# Note: blank lines and comments in KLC sections are removed from the output
# file because they are not recognized by KBDEdit (as of v19.8.0).
#

def klc_keymap(layout):
    """ Windows layout, main part. """

    supported_symbols = \
        '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    output = []
    for key_name in LAYER_KEYS:
        if key_name.startswith('-'):
            continue

        symbols = []
        description = '//'
        alpha = False

        for i in [0, 1, 4, 5]:
            layer = layout.layers[i]

            if key_name in layer:
                symbol = layer[key_name]
                desc = symbol
                if symbol in layout.dead_keys:
                    desc = layout.dead_keys[symbol]['alt_space']
                    symbol = hex_ord(desc) + '@'
                else:
                    if i == 0:
                        alpha = symbol.upper() != symbol
                    if symbol not in supported_symbols:
                        symbol = hex_ord(symbol)
                symbols.append(symbol)
            else:
                desc = ' '
                symbols.append('-1')
            description += ' ' + desc

        if layout.has_altgr:
            output.append('\t'.join([
                KEY_CODES['klc'][key_name],    # scan code & virtual key
                '1' if alpha else '0',         # affected by CapsLock?
                symbols[0], symbols[1], '-1',  # base layer
                symbols[2], symbols[3],        # altgr layer
                description.strip()
            ]))
        else:
            output.append('\t'.join([
                KEY_CODES['klc'][key_name],    # scan code & virtual key
                '1' if alpha else '0',         # affected by CapsLock?
                symbols[0], symbols[1], '-1',  # base layer
                description.strip()
            ]))

    return output


def klc_deadkeys(layout):
    """ Windows layout, dead keys. """

    output = []

    def append_line(base, alt):
        output.append(f"{hex_ord(base)}\t{hex_ord(alt)}\t// {base} -> {alt}")

    for k in layout.dk_index:
        dk = layout.dead_keys[k]

        output.append('// DEADKEY: ' + dk['name'].upper() + ' //{{{')
        output.append('DEADKEY\t' + hex_ord(dk['alt_space']))

        if k == ODK_ID:
            output.extend(klc_1dk(layout))
        else:
            for i in range(len(dk['base'])):
                append_line(dk['base'][i], dk['alt'][i])

        append_line('\u00a0', dk['alt_space'])
        append_line('\u0020', dk['alt_space'])

        output.append('//}}}')
        output.append('')

    return output[:-1]


def klc_dk_index(layout):
    """ Windows layout, dead key index. """

    output = []
    for k in layout.dk_index:
        dk = layout.dead_keys[k]
        output.append(f"{hex_ord(dk['alt_space'])}\t\"{dk['name'].upper()}\"")
    return output


def klc_1dk(layout):
    """ Windows layout, 1dk. """

    output = []
    for i in [0, 1]:
        base_layer = layout.layers[i]
        ext_layer = layout.layers[i + 2]

        for key_name in LAYER_KEYS:
            if key_name.startswith('- Space') or key_name == 'spce':
                continue

            if key_name.startswith('-'):
                if output:
                    output.append('')
                output.append('//' + key_name[1:])
                continue

            if key_name in ext_layer:
                base = base_layer[key_name]
                if base in layout.dead_keys:
                    base = layout.dead_keys[base]['alt_space']
                ext = ext_layer[key_name]
                if ext in layout.dead_keys:
                    ext = layout.dead_keys[ext]['alt_space']
                    odk = hex_ord(ext) + '@'
                else:
                    odk = hex_ord(ext)

                output.append('\t'.join([
                    hex_ord(base), odk, '// ' + base + ' -> ' + ext
                ]))

    return output


###
# macOS: keylayout
# https://developer.apple.com/library/content/technotes/tn2056/
#

def osx_keymap(layout):
    """ macOS layout, main part. """

    ret_str = []
    for index in range(5):
        layer = layout.layers[[0, 1, 0, 4, 5][index]]
        caps = index == 2

        def has_dead_keys(letter):
            if letter in '\u0020\u00a0\u202f':  # space
                return True
            for k in layout.dead_keys:
                if letter in layout.dead_keys[k]['base']:
                    return True
            return False

        output = []
        for key_name in LAYER_KEYS:
            if key_name in ['ae13', 'ab11']:  # ABNT / JIS keys
                continue  # these two keys are not supported yet

            if key_name.startswith('-'):
                if output:
                    output.append('')
                output.append('<!--' + key_name[1:] + ' -->')
                continue

            symbol = '&#x0010;'
            final_key = True

            if key_name in layer:
                key = layer[key_name]
                if key in layout.dead_keys:
                    symbol = 'dead_' + layout.dead_keys[key]['name']
                    final_key = False
                else:
                    symbol = xml_proof(key.upper() if caps else key)
                    final_key = not has_dead_keys(key.upper())

            char = f"code=\"{KEY_CODES['osx'][key_name]}\"".ljust(10)
            if final_key:
                action = f"output=\"{symbol}\""
            else:
                action = f"action=\"{xml_proof_id(symbol)}\""
            output.append(f"<key {char} {action} />")

        ret_str.append(output)
    return ret_str


def osx_actions(layout):
    """ macOS layout, dead key actions. """

    ret_actions = []

    def when(state, action):
        state_attr = f"state=\"{state}\"".ljust(18)
        if action in layout.dead_keys:
            action_attr = f"next=\"{layout.dead_keys[action]['name']}\""
        elif action.startswith('dead_'):
            action_attr = f"next=\"{action[5:]}\""
        else:
            action_attr = f"output=\"{xml_proof(action)}\""
        return f"  <when {state_attr} {action_attr} />"

    def append_actions(symbol, actions):
        ret_actions.append(f"<action id=\"{xml_proof_id(symbol)}\">")
        ret_actions.append(when('none', symbol))
        for (state, out) in actions:
            ret_actions.append(when(state, out))
        ret_actions.append('</action>')

    # dead key definitions
    for key in layout.dead_keys:
        symbol = layout.dead_keys[key]['name']
        ret_actions.append(f"<action id=\"dead_{symbol}\">")
        ret_actions.append(f"  <when state=\"none\" next=\"{symbol}\" />")
        ret_actions.append('</action>')
        continue

    # normal key actions
    for key_name in LAYER_KEYS:
        if key_name.startswith('-'):
            ret_actions.append('')
            ret_actions.append('<!--' + key_name[1:] + ' -->')
            continue

        for i in [0, 1]:
            if key_name not in layout.layers[i]:
                continue

            key = layout.layers[i][key_name]
            if i and key == layout.layers[0][key_name]:
                continue
            if key in layout.dead_keys:
                continue

            actions = []
            for k in layout.dk_index:
                dk = layout.dead_keys[k]
                if key in dk['base']:
                    idx = dk['base'].index(key)
                    actions.append((dk['name'], dk['alt'][idx]))
            if actions:
                append_actions(xml_proof(key), actions)

    # spacebar actions
    actions = []
    for k in layout.dk_index:
        dk = layout.dead_keys[k]
        actions.append((dk['name'], dk['alt_space']))
    append_actions('&#x0020;', actions)
    append_actions('&#x00a0;', actions)
    append_actions('&#x202f;', actions)

    return ret_actions


def osx_terminators(layout):
    """ macOS layout, dead key terminators. """

    ret_terminators = []
    for k in layout.dk_index:
        dk = layout.dead_keys[k]
        state = f"state=\"{dk['name']}\"".ljust(18)
        output = f"output=\"{xml_proof(dk['alt_self'])}\""
        ret_terminators.append(f"<when {state} {output} />")
    return ret_terminators


###
# Web: JSON
# To be used with the <x-keyboard> web component.
# https://github.com/fabi1cazenave/x-keyboard
#

def web_keymap(layout):
    """ Web layout, main part. """

    keymap = {}
    for key_name in LAYER_KEYS:
        if key_name.startswith('-'):
            continue
        chars = list('')
        for i in [0, 1, 4, 5]:
            if key_name in layout.layers[i]:
                chars.append(layout.layers[i][key_name])
        if chars:
            keymap[KEY_CODES['web'][key_name]] = chars

    return keymap


def web_deadkeys(layout):
    """ Web layout, dead keys. """

    deadkeys = {}
    if layout.has_1dk:  # ensure 1dk is first in the dead key dictionary
        deadkeys[ODK_ID] = {}
    for (id, dk) in layout.dead_keys.items():
        deadkeys[id] = {}
        deadkeys[id][id] = dk['alt_self']
        deadkeys[id]['\u0020'] = dk['alt_space']
        deadkeys[id]['\u00a0'] = dk['alt_space']
        deadkeys[id]['\u202f'] = dk['alt_space']
        if id == ODK_ID:
            for key_name in LAYER_KEYS:
                if key_name.startswith('-'):
                    continue
                for i in [3, 2]:
                    if key_name in layout.layers[i]:
                        deadkeys[id][layout.layers[i - 2][key_name]] = \
                            layout.layers[i][key_name]
        else:
            base = dk['base']
            alt = dk['alt']
            for i in range(len(base)):
                deadkeys[id][base[i]] = alt[i]

    return deadkeys

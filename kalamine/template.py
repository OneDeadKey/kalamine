#!/usr/bin/env python3
import os
import re

from .utils import open_local_file, lines_to_text


##
# Helpers
#


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
    exp = re.compile('\$\{' + token + '(=[^\}]*){0,1}\}')
    return exp.sub(value, text)


##
# Main
#


class Template:
    """ System-specific layout template. """

    def __init__(self, layout):
        self.tpl = 'full' if layout.has_altgr else 'base'
        self.base = layout.get_geometry([0, 2])  # base + 1dk
        self.altgr = layout.get_geometry([4])    # altgr only
        self.layout = layout

    def load_tpl(self, ext):
        out = open_local_file(os.path.join('tpl', self.tpl + ext)).read()
        out = substitute_lines(out, 'GEOMETRY_base', self.base)
        out = substitute_lines(out, 'GEOMETRY_altgr', self.altgr)
        for key, value in self.layout.meta.items():
            out = substitute_token(out, key, value)
        return out

    @property
    def xkb(self):
        """ GNU/Linux driver (standalone / user-space) """
        out = self.load_tpl('.xkb')
        out = substitute_lines(out, 'LAYOUT', self.layout.xkb_keymap)
        return out

    @property
    def xkb_patch(self):
        """ GNU/Linux driver (system patch) """
        out = self.load_tpl('.xkb_patch')
        out = substitute_lines(out, 'LAYOUT', self.layout.xkb_keymap)
        return out

    @property
    def klc(self):
        """ Windows driver (warning: must be encoded in utf-16le) """
        out = self.load_tpl('.klc')
        out = substitute_lines(out, 'LAYOUT', self.layout.klc_keymap)
        out = substitute_lines(out, 'DEAD_KEYS', self.layout.klc_deadkeys)
        out = substitute_lines(out, 'DEAD_KEY_INDEX', self.layout.klc_dk_index)
        # the utf-8 template is converted into a utf-16le file
        out = substitute_token(out, 'encoding', 'utf-16le')
        return out

    @property
    def keylayout(self):
        """ Mac OSX driver """
        out = self.load_tpl('.keylayout')
        for i, layer in enumerate(self.layout.osx_keymap):
            out = substitute_lines(out, 'LAYER_' + str(i), layer)
        out = substitute_lines(out, 'ACTIONS', self.layout.osx_actions)
        out = substitute_lines(out, 'TERMINATORS', self.layout.osx_terminators)
        return out

    def make_all(self, subdir):
        def out_path(ext=''):
            return os.path.join(subdir, self.layout.meta['fileName'] + ext)

        if not os.path.exists(subdir):
            os.makedirs(subdir)

        # Windows driver (the utf-8 template is converted to a utf-16le file)
        klc_path = out_path('.klc')
        open(klc_path, 'w', encoding='utf-16le').write(self.klc)
        print('... ' + klc_path)

        # a utf-8 version can't hurt (easier to diff)
        klc_path = out_path('.klc_utf8')
        open(klc_path, 'w').write(self.klc)
        print('... ' + klc_path)

        # Mac OSX driver
        osx_path = out_path('.keylayout')
        open(osx_path, 'w').write(self.keylayout)
        print('... ' + osx_path)

        # Linux driver, user space
        xkb_path = out_path('.xkb')
        open(xkb_path, 'w').write(self.xkb)
        print('... ' + xkb_path)

        # Linux driver, XKB patch
        if 'variant' in self.layout.meta and 'locale' in self.layout.meta:
            dir_path = os.path.join(subdir, 'xkb', self.layout.meta['locale'])
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            xkb_path = os.path.join(dir_path, self.layout.meta['variant'])
            open(xkb_path, 'w').write(self.xkb_patch)
            print('... ' + xkb_path)

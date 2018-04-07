#!/usr/bin/env python3
import os
import re

from .utils import lines_to_text, open_local_file


##
# Helpers
#


def substitute_lines(template, variable, lines):
    prefix = 'KALAMINE::'
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


##
# Main
#


class Template:
    """ System-specific layout template. """

    def __init__(self, layout):
        self.tpl = 'tpl/full' if layout.has_altgr else 'tpl/base'
        self.base = layout.get_geometry([0, 2])  # base + 1dk
        self.altgr = layout.get_geometry([4])    # altgr only
        self.layout = layout

    @property
    def xkb(self):
        """ GNU/Linux driver (standalone / user-space) """
        out = open_local_file(self.tpl + '.xkb').read()
        out = substitute_lines(out, 'GEOMETRY_base', self.base)
        out = substitute_lines(out, 'GEOMETRY_altgr', self.altgr)
        out = substitute_lines(out, 'LAYOUT', self.layout.xkb)
        out = substitute_meta(out, self.layout.meta)
        return out

    @property
    def xkb_patch(self):
        """ GNU/Linux driver (system patch) """
        out = open_local_file(self.tpl + '.xkb_patch').read()
        out = substitute_lines(out, 'GEOMETRY_base', self.base)
        out = substitute_lines(out, 'GEOMETRY_altgr', self.altgr)
        out = substitute_lines(out, 'LAYOUT', self.layout.xkb)
        out = substitute_meta(out, self.layout.meta)
        return out

    @property
    def klc(self):
        """ Windows driver """
        out = open_local_file(self.tpl + '.klc').read()
        out = substitute_lines(out, 'GEOMETRY_base', self.base)
        out = substitute_lines(out, 'GEOMETRY_altgr', self.altgr)
        out = substitute_lines(out, 'LAYOUT', self.layout.klc)
        out = substitute_lines(out, 'DEAD_KEYS', self.layout.klc_deadkeys)
        out = substitute_lines(out, 'DEAD_KEY_INDEX', self.layout.klc_dk_index)
        # the utf-8 template is converted into a utf-16le file
        out = substitute_token(out, 'encoding', 'utf-16le')
        out = substitute_meta(out, self.layout.meta)
        return out

    @property
    def keylayout(self):
        """ Mac OSX driver """
        out = open_local_file('tpl/full.keylayout').read()
        out = substitute_lines(out, 'GEOMETRY_base', self.base)
        out = substitute_lines(out, 'GEOMETRY_altgr', self.altgr)
        out = substitute_lines(out, 'LAYOUT_0', self.layout.get_osx_keymap(0))
        out = substitute_lines(out, 'LAYOUT_1', self.layout.get_osx_keymap(1))
        out = substitute_lines(out, 'LAYOUT_2', self.layout.get_osx_keymap(2))
        out = substitute_lines(out, 'LAYOUT_3', self.layout.get_osx_keymap(3))
        out = substitute_lines(out, 'LAYOUT_4', self.layout.get_osx_keymap(4))
        out = substitute_lines(out, 'ACTIONS', self.layout.osx_actions)
        out = substitute_lines(out, 'TERMINATORS', self.layout.osx_terminators)
        out = substitute_meta(out, self.layout.meta)
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

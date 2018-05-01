#!/usr/bin/env python3
import click
import os

from .layout import KeyboardLayout


def make_all(layout, subdir):
    def out_path(ext=''):
        return os.path.join(subdir, layout.meta['fileName'] + ext)

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    # Windows driver
    klc_path = out_path('.klc')
    open(klc_path, 'w', encoding='utf-16le').write(layout.klc)
    print('... ' + klc_path)

    # Mac OSX driver
    osx_path = out_path('.keylayout')
    open(osx_path, 'w').write(layout.keylayout)
    print('... ' + osx_path)

    # Linux driver, user-space
    xkb_path = out_path('.xkb')
    open(xkb_path, 'w').write(layout.xkb)
    print('... ' + xkb_path)


@click.command()
@click.argument('input', nargs=-1, type=click.Path(exists=True))
@click.option('--out',
              default='all',
              type=click.Path(),
              help='Keyboard driver(s) to generate.')
def make(input, out):
    """ Convert yaml layout descriptions into OS-specific keyboard layouts. """

    for input_file in input:
        layout = KeyboardLayout(input_file)

        # default: build all in the `dist` subdirectory
        if out == 'all':
            make_all(layout, 'dist')
            continue

        # quick output: reuse the input name and change the file extension
        if out in ['keylayout', 'klc', 'xkb']:
            output_file = os.path.splitext(input_file)[0] + '.' + out
        else:
            output_file = out

        # detailed output
        if output_file.endswith('.klc'):
            open(output_file, 'w', encoding='utf-16le').write(layout.klc)
        elif output_file.endswith('.keylayout'):
            open(output_file, 'w').write(layout.keylayout)
        elif output_file.endswith('.xkb'):
            open(output_file, 'w').write(layout.xkb)
        else:
            print('Unsupported output format.')
            return

        # successfully converted, display file name
        print('... ' + output_file)

if __name__ == '__main__':
    make()

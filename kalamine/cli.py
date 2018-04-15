#!/usr/bin/env python3
import click
import os

from kalamine import Layout, Template


@click.command()
@click.argument('input', nargs=-1, type=click.Path(exists=True))
@click.option('--extends',
              default='',
              type=click.Path(),
              help='Optional, keyboard layout to extend.')
@click.option('--out',
              default='all',
              type=click.Path(),
              help='Keyboard driver(s) to generate.')
def make(input, extends, out):
    """ Convert yaml layout descriptions into OS-specific keyboard layouts. """

    for input_file in input:
        layout = Layout(input_file, extends)
        tpl = Template(layout)

        # default: build all in the `dist` subdirectory
        if out == 'all':
            tpl.make_all('dist')
            continue

        # quick output: reuse the input name and change the file extension
        if out in ['keylayout', 'klc', 'xkb']:
            output_file = os.path.splitext(input_file)[0] + '.' + out
        else:
            output_file = out

        # detailed output
        if output_file.endswith('.klc'):
            open(output_file, 'w', encoding='utf-16le').write(tpl.klc)
        elif output_file.endswith('.keylayout'):
            open(output_file, 'w').write(tpl.keylayout)
        elif output_file.endswith('.xkb'):
            open(output_file, 'w').write(tpl.xkb)
        else:
            print('Unsupported output format.')
            return

        # successfully converted, display file name
        print('... ' + output_file)

if __name__ == '__main__':
    make()

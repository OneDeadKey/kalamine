#!/usr/bin/env python3
import os
import yaml


def lines_to_text(lines, indent=''):
    out = ''
    for line in lines:
        if len(line):
            out += indent + line
        out += '\n'
    return out[:-1]


def text_to_lines(text):
    return text.split('\n')


def open_local_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name))


def load_data(filename):
    return yaml.load(open_local_file(os.path.join('data', filename)),
                     Loader=yaml.SafeLoader)


DEAD_KEYS = load_data('dead_keys.yaml')
ODK_ID = '**'  # must match the value in dead_keys.yaml
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
    'ae11', 'ae12', 'ae13', 'ad11', 'ad12',
    'ac11', 'ab11', 'tlde', 'bksl', 'lsgt',

    '- Space bar',
    'spce'
]

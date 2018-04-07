#!/usr/bin/env python3
import os
import unicodedata


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


def open_local_file(fileName):
    return open(os.path.join(os.path.dirname(__file__), fileName))

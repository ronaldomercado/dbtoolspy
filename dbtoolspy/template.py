from __future__ import print_function
#from __future__ import unicode_literals

from .tokenizer import tokenizer

def parse_filename(next):
    filename = None

    token = next()
    while True:
        if token == '{':
            break
        filename = token

        token = next()

    return filename


def parse_pattern_macros(next):
    macros = []

    token = next()
    while True:
        if token == '}':
            break

        if token != ',':
            macros.append(token)

        token = next()

    return macros


def parse_pattern_values(next):
    values = []

    token = next()
    while True:
        if token == '}':
            break

        if token != ',':
            values.append(token)

        token = next()

    return values


def parse_macro_value(next):
    macros = []
    values = []
    
    equal = False
    token = next()
    while True:
        if token == '}':
            break

        if token == '=':
            equal = True
        elif token == ',':
            equal = False
        else:
            if equal:
                values.append(token)
                equal = False
            else:
                macros.append(token)

        token = next()

    return macros, values

NEUTRAL = 0
GLOBAL = 1
FILE = 2
PATTERN = 3
SUBS = 4

def parse_template(source):
    """
    :param str source: EPICS substitutes
    :return: list of (filename, macros, values)
    """
    files = []

    next = iter(tokenizer(source)).next

    global_macros = {}
    saved_state = state = NEUTRAL
    macros = values = None
    while True:
        try:
            token = next()
        except StopIteration:
            break
        if state == NEUTRAL:
            if token == 'file':
                filename = parse_filename(next)
                macros = values = None
                local_global_macros = {}
                saved_state = state
                state = FILE
            elif token == 'global':
                saved_state = state
                state = GLOBAL
        elif state == FILE:
            if token == 'global':
                saved_state = state
                state = GLOBAL
            elif token == 'pattern':
                saved_state = state
                state = PATTERN
            elif token == '{':
                if macros is None:
                    macros, values = parse_macro_value(next)
                    d = dict(zip(macros, values))
                    d.update(local_global_macros)
                    files.append((filename, d))
                    macros = values = None
                else:
                    values = parse_pattern_values(next)
                    d = dict(zip(macros, values))
                    d.update(local_global_macros)
                    files.append((filename, d))
            elif token == '}':
                saved_state = state
                state = NEUTRAL
        elif state == PATTERN:
            if token == '{':
                macros = parse_pattern_macros(next)
                state = saved_state
        elif state == GLOBAL:
            if token == '{':
                macros, values = parse_macro_value(next)
                if saved_state == FILE:
                    local_global_macros.update(zip(macros, values)) 
                else:
                    global_macros.update(zip(macros, values))
                macros = values = None
                state = saved_state

    return files


def load_template_file(file):
    return parse_template(open(file))


if __name__ == '__main__':
    import argparse
    from .database import load_database_file, Database
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument(
            dest = 'substitution_files',
            nargs = '+',
            help='substitution files')
    args = parser.parse_args()


    db = Database()
    for subs_file in args.substitution_files:
        if os.path.exists(subs_file):
            for db_file, macros in load_template_file(subs_file):
                db.update(load_database_file(db_file, macros, includes=[os.path.dirname(subs_file)]))
    print(db)

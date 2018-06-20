#!/usr/bin/env python
from __future__ import print_function
#from __future__ import unicode_literals

import os
import io
import collections
import warnings

from .tokenizer import tokenizer
from .macro import macExpand, macSplit


class DatabaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    
class Record(object):
    def __init__(self):
        self.name = None
        self.rtyp = None
        self.infos = collections.OrderedDict()
        self.fields = collections.OrderedDict()
        self.aliases = []

    def __bool__(self):
        return self.name != None and self.rtype != None

    def __repr__(self):
        repr = 'record ({0}, "{1}")\n'.format(self.rtyp, self.name)
        repr += '{\n'
        for field, value in self.fields.items():
            repr += '    field({0:4}, "{1}")\n'.format(field, value)
        for field, value in self.infos.items():
            repr += '    info({0}, "{1}")\n'.format(field, value)
        for alias in self.aliases:
            repr += '    alias({0})\n'.format(alias)
        repr += '}'
        return repr

    def is_valid(self):
        """
        Valid record has defined name and type.
        """
        return self.name and self.rtyp

    def merge(self, another):
        """
        Merge fields, infos, aliases from another record instance.
        """
        self.fields.update(another.fields)
        self.infos.update(another.infos)
        self.aliases.extend(another.aliases)


class Database(collections.OrderedDict):
    def __init__(self):
        super(Database, self).__init__()

    def __repr__(self):
        msg = []
        for record in self.values():
            msg.append(repr(record))
        return '\n'.join(msg)

    def add_record(self, record):
        if not record.is_valid():
            return

        record_existed = self.get(record.name)
        if record_existed:
            if record_existed.rtyp != record.rtyp:
                raise DatabaseException('Reappearing record "%s" with conflicting record type "%s"'
                        %(record.name, record.rtyp))
            else:
                warnings.warn('Merging record "%s"' % (record.name), stacklevel=2)
                record_existed.merge(record)
        else:
            self[record.name] = record

    def update(self, database):
        for record in database.values():
            self.add_record(record)
 

def parse_pair(next):
    """
    parse '(field, "value")' definition to tuple (field, value)
    """
    token = next()
    if token != '(':
        return None, None
    token = next()
    field = token
    token = next()
    if token == ')':
        return field, None
    elif token != ',':
        return None, None
    token = next()
    value = token
    token = next()
    if token != ')':
        return None, None
    return field, value


def parse_record(next):
    """
    :param func next: token generator function
    """
    record = Record()

    record.rtyp, record.name = parse_pair(next)

    token = next()
    while True:
        if token == '}':
            break

        elif token == 'field':
            field, value = parse_pair(next)
            record.fields[field] = value
        elif token == 'info':
            field, value = parse_pair(next)
            record.infos[field] = value
        elif token == 'alias':
            record.aliases.append(parse_pair(next))

        token = next()

    return record


def find_database_file(filename, includes):
    if not os.path.isabs(filename):
        for include in includes:
            path = os.path.join(include, filename)
            if os.path.exists(path):
                filename = path
                break
    return filename


def load_database_file(filename, macros=None, includes=[]):
    """
    :param str filename: EPICS database filename
    :return: list of record dict
    :rtype: list of dicts
    """
    # search filename through include directories
    filename = find_database_file(filename, includes)

    database = Database()

    # read line by line and expand macros
    lineno = 1
    lines = []
    failed = False
    for line in open(filename):
        if macros is not None:
            expanded, unmatched = macExpand(line, macros)
            if unmatched:
                failed = True
                print('{0}:{1}: macro "{2}" is undefined ({3})'.format(
                    os.path.basename(filename), 
                    lineno, 
                    '" "'.join(unmatched), 
                    line.strip()))
            else:
                lines.append(expanded)
        else:
            lines.append(line)
        lineno += 1
    
    if failed:
        return database
    
    # parse record instances
    next = iter(tokenizer(io.StringIO(''.join(lines)), filename)).next
    while True:
        try:
            token = next()
        except StopIteration:
            break

        if token == 'record':
            database.add_record(parse_record(next))
        elif token == 'alias':
            record_name, alias_name = parse_pair(next)
            records[alias_name] = records[record_name]
        elif token == 'include':
            inclusion = next()
            extended_includes = set(includes)
            extended_includes.add(os.path.dirname(filename))
            for record in load_database_file(inclusion, macros, extended_includes).values():
                database.add_record(record)

    return database


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--macro',
            help='macro substitution')
    parser.add_argument(
            dest = 'database_files',
            nargs = '+',
            help='database files')
    args = parser.parse_args()

    macros = None
    if args.macro:
        macros = macSplit(args.macro)

    for file in args.database_files:
        if os.path.exists(file):
            database = load_database_file(file, macros)
            print(database) 

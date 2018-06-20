from __future__ import print_function
#from __future__ import unicode_literals

import io
import re

from .tokenizer import tokenizer

Macros = re.compile('\$\(([^)=]+)(=([^)]*))?\)')

def macExpand(source, macros):
    """
    >>> macExpand('$(A) $(B) $(C=3)', {'A': '1'})
    ('1 $(B) 3', ['B'])
    """
    unmatched = set()

    def replace(matchobj):
        name = matchobj.group(1)
        default = matchobj.group(3)
        value =  macros.get(name)
        if value is None:
            if default is None:
                unmatched.add(name)
                return '$(%s)' % name 
            else:
                return default
        else:
            return value

    while True:
        expanded = Macros.sub(replace, source)
        if expanded == source:
            break
        source = expanded

    return expanded, list(unmatched)


def macSplit(macro_string):
    """
    >>> print(macSplit('a=1,b="2",c,d=\\'hello\\''))
    {'a': '1', 'b': '2', 'd': 'hello'}
    """
    src = tokenizer(io.StringIO(macro_string))
    
    macros = {}
    name = value = None
    for token in src:
        if token == '=':
            pass 
        elif token == ',':
            name = value = None
        else:
            if name:
                macros[name] = token
            else:
                name = token
       
    return macros


if __name__ == '__main__':
    import doctest
    doctest.testmod()

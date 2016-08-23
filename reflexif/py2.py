# -*- coding: utf-8 -*-
'''
.. created on 22.08.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals

import sys
import warnings
import codecs

if sys.version_info[0] > 2:
    warnings.warn('You should not use the module reflexif.py2 with Python >2.')

open = codecs.open


def bytes(obj):
    if isinstance(obj, str):
        return obj
    try:
        return obj.__bytes__()
    except AttributeError:
        return str(bytearray(obj))

# When this module is imported with Python >2, for example by sphinx,
# no exception should be raised.
try:
    range = xrange
except NameError:
    pass

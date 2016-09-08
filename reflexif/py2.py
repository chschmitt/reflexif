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

orig_bytes = bytes


class monkey_bytes(object):
    def __new__(cls, obj):
        if isinstance(obj, str):
            return obj
        try:
            return obj.__bytes__()
        except AttributeError:
            return str(bytearray(obj))


class ipy_bytes(object):
    def __new__(cls, obj):
        try:
            return obj.__bytes__()
        except AttributeError:
            try:
                return orig_bytes(obj)
            except TypeError:
                return orig_bytes(bytearray(obj))


if orig_bytes is str:
    bytes = monkey_bytes
else:
    bytes = ipy_bytes


# When this module is imported with Python >2, for example by sphinx,
# no exception should be raised.
try:
    range = xrange
except NameError:
    pass

open = codecs.open

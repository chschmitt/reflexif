# -*- coding: utf-8 -*-
'''
.. created on 22.08.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals

import sys

if sys.version_info[0] == 2:
    PY2 = True
    from reflexif.py2 import range, bytes, open
    __all__ = ['range', 'bytes', 'open']

else:
    PY2 = False
    unicode = str
    __all__ = ['unicode']

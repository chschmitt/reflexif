# -*- coding: utf-8 -*-
'''
.. created on 05.02.2015
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals


class MetaDataError(Exception):
    pass


class JPEGError(MetaDataError):
    pass


class TIFFError(MetaDataError):
    pass


class NikonError(TIFFError):
    pass


class RangeError(MetaDataError):
    pass

# -*- coding: utf-8 -*-
'''
.. created on 08.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *


from reflexif.framework.model_base import FrameObject, child, value, Structs
from reflexif import types
from reflexif.types import Types


class TagValues(FrameObject):
    values = value(desc='decoded values')
    header = value()

    def bytes(self):
        return self.values

    def string(self, encoding='ascii'):
        return self.strings(encoding)[0]

    def strings(self, encoding='ascii'):
        data = self.values.rstrip(b'\x00')
        raw = data.split(b'\x00')
        if not raw:
            raw = [b'']
        if encoding is None:
            return raw
        else:
            return [s.decode(encoding) for s in raw]

    def rational(self):
        return self.rationals()[0]

    def rationals(self):
        return [(n/d) for n, d in self.values]

    def all(self):
        t = self.header.tag_type
        if t == Types.ASCII:
            return self.strings()
        elif t == Types.UNDEFINED:
            return [self.bytes()]
        elif t in (Types.RATIONAL, Types.SRATIONAL):
            return self.rationals()
        else:
            return self.values

    def first(self):
        if self.header.tag_type == Types.UNDEFINED:
            return self.bytes()
        return self.all()[0]


class TagHeader(FrameObject):
    tag_code = value(0, Structs.SHORT, leaf=True)
    type_code = value(2, Structs.SHORT, leaf=True)
    value_count = value(4, Structs.LONG, leaf=True)
    value_offset = value(8, Structs.LONG)

    type = child(types.Type)
    values = child(TagValues)

    @property
    def is_valid_pointer(self):
        header_ok = self.type == types.Types.LONG and self.value_count == 1
        values_ok = len(self.values.values) == 1
        return header_ok and values_ok

    @property
    def firstvalue(self):
        values = self.values.values

        if self.type == types.Types.UNDEFINED:
            return values

        if self.type == types.Types.ASCII:
            data = values.decode('ascii').strip('\x00')
            values = data.split('\x00')

        if values:
            return values[0]

        raise ValueError


class IFD(FrameObject):
    tag_count = value(0, Structs.SHORT, desc='tag count')
    tags = child(TagHeader, desc='tags')
    ifd_pointer = value(struct_spec=Structs.LONG, desc='pointer to next IFD')

    def search_tag(self, code):
        for tag in self.tags:
            if tag.tag_code == code:
                return tag

    def __getitem__(self, code):
        tag = self.search_tag(code)
        if tag is None:
            raise KeyError
        return tag


class TiffHeader(FrameObject):
    endianess = value(0, 2, desc='endianess marker')
    magic = value(2, Structs.SHORT, desc='magic value (42)')
    ifd_pointer = value(4, Structs.LONG, desc='0th IFD pointer')
    ifds = child()

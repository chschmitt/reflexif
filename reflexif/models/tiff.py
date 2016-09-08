# -*- coding: utf-8 -*-
'''
.. created on 08.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *


from reflexif.framework.model_base import FrameObject, child, value, Structs
from reflexif import types

class TagValues(FrameObject):
    values = value(desc='foo')

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

class IFD(FrameObject):
    tag_count = value(0, Structs.SHORT, desc='tag count')
    tags = child(TagHeader, desc='tags')
    ifd_pointer = value(struct_spec=Structs.LONG, desc='pointer to next IFD')
    
    def search_tag(self, code):
        for tag in self.tags:
            if tag.tag_code == code:
                return tag

class TiffHeader(FrameObject):
    endianess = value(0, 2, desc='endianess marker')
    magic = value(2, Structs.SHORT, desc='magic value (42)')
    ifd_pointer = value(4, Structs.LONG, desc='0th IFD pointer')
    ifds = child()


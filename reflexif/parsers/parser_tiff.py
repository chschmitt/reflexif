# -*- coding: utf-8 -*-
'''
.. created on 08.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *


from reflexif import errors, types
from reflexif.types import Types

from reflexif.framework.declarative import parses
from reflexif.framework.parser_base import parse, Parser, parentalias

from reflexif.framework.model_base import structs
from reflexif.models.tiff import (
     TiffHeader, IFD, TagHeader, TagValues 
    )

class IFDChainParser(Parser):
    def parse_ifd_chain(self, ifd0_pointer):
        # self.conseen_pointers = set()
        self.pending_pointers = [ifd0_pointer]
        ifds = []
        while self.pending_pointers:
            pointer = self.pending_pointers.pop()
            if pointer == 0:
                continue
            if pointer in self.state.seen_ifd_pointers:
                print('circular pointers!')
                continue
            #print(pointer)
            ifd, _ = self.parse_class(IFD, self.frame[pointer:])
            ifds.append(ifd)
            self.state.seen_ifd_pointers.add(pointer)
        return ifds

@parses(TiffHeader)
class TiffHeaderParser(IFDChainParser):
    @parse(TiffHeader.endianess)
    def parse_endianess(self):
        value, frame = self.unpack_value(TiffHeader.endianess)
        if not value in (b'II', b'MM'):
            raise errors.TIFFError
        self.state.little_endian = value == b'II'
        return value, frame
    
    #@parse(TiffHeader.ifd0)
    #def parse_ifd(self):
    #    offset = self.target.ifd_pointer
    #    return self.parse_child_field(TiffHeader.ifd0, self.frame[offset:])
    
    @parse(TiffHeader.ifds)
    def parse_ifds(self):
        return self.parse_ifd_chain(self.target.ifd_pointer), None
    
    


@parses(IFD)
class IFDParser(Parser):
    header_parser = parentalias(TiffHeaderParser)
    
    def on_create(self):
        self.truncated = False
    
    def get_tag_header_frame_resilient(self):
        c = self.target.tag_count-1
        while c >= 0:
            try:
                return self.frame.slice(2, 12*c)
            except IndexError:
                c -= 1
    
    @parse(IFD.tags)
    def parse_tags(self):
        try:
            tag_header_frame = self.frame.slice(2, 12*self.target.tag_count)
        except IndexError:
            if not self.state.resilient:
                raise
            self.truncated = True
            tag_header_frame = self.get_tag_header_frame_resilient()
        
        tags = []
        for offset in range(0, len(tag_header_frame), 12):
            th, _ = self.parse_child_field(IFD.tags, tag_header_frame.slice(offset, 12))
            tags.append(th)
        
        return tags, tag_header_frame
    
    @parse(IFD.ifd_pointer)
    def parse_ifd_pointer(self):
        if self.truncated:
            return 0, None
        offset = 2 + self.target.tag_count * 12
        sub_frame = self.frame.slice(offset, 4)
        t =  self.unpack_value(IFD.ifd_pointer, sub_frame)
        self.parent.pending_pointers.append(t[0])
        return t
    
@parses(TagHeader)
class TagHeaderParser(Parser):
    
    @parse(TagHeader.type)
    def parse_type(self):
        t = types.BY_CODE[self.target.type_code]
        return t, self.target.frames['type_code'] 

    @parse(TagHeader.values)
    def parse_values(self):
        t = self.target.type
        frame_size = self.target.value_count * t.multiplicator
        if frame_size <= 4:
            value_frame = self.frame[8:12]
            self.target.value_offset = None
        else:
            header = self.parent.parent.target
            value_frame = header.frame.slice(self.target.value_offset, frame_size)
        
        return self.parse_child_field(TagHeader.values, value_frame)
            
@parses(TagValues)
class TagValuesParser(Parser):
    
    @parse(TagValues.values)
    def parse_values(self):
        tag_header = self.parent.target
        count = tag_header.value_count
        type_ = tag_header.type
        if hasattr(type_, 'size'):
            if self.state.little_endian:
                struct_ = structs.le[type_.struct_def]
            else:
                struct_ = structs.be[type_.struct_def]
                
            values = []
            for i in range(count):
                val_frame = self.frame.slice(i*type_.size, type_.size)
                val = struct_.unpack(val_frame.data)
                if len(val) == 1:
                    val = val[0]
                values.append(val)
            # print(values)
            return values, None
        elif tag_header.type in (Types.ASCII, Types.UNDEFINED):
            return self.frame.data, None
        return None, None

   
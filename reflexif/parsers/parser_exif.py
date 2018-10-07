# -*- coding: utf-8 -*-
'''
.. created on 08.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *

from reflexif.models.exif import ExifExtension, MakernoteExentsion, JPEGExifSegment, ExifHeader
from reflexif.parsers.parser_tiff import IFDChainParser
from reflexif.framework.declarative import parses
from reflexif.framework.parser_base import parse, Parser
from reflexif.parsers.parser_jpeg import JPEGStreamParser
from reflexif.models.jpeg import Segments
import reflexif.io
from reflexif import errors

@parses(JPEGExifSegment)
class JPEGExifSegmentParser(Parser):
    def on_create(self):
        self.fd = self.frame
        self.frame = None

    @parse(JPEGExifSegment.exif_segment_raw)
    def parse_exif_app_segment(self):
        parser = JPEGStreamParser(self.fd)
        for segdata in parser.parse_segments():
            seg = segdata.segment
            if seg == Segments.SOS:
                break
            if seg.is_app and segdata.payload and segdata.payload[0:4] == b'Exif':
                frame = reflexif.io.Frame(memoryview(segdata.payload))
                self.frame = frame
                return segdata, frame

        raise errors.MetaDataError('no exif header found')


@parses(ExifHeader)
class ExifHeaderParser(Parser):
    pass


@parses(ExifExtension)
class ExifExtensionParser(IFDChainParser):

    @parse(ExifExtension.exif_ifd)
    def parse_exif_ifd(self):
        return self.parse_sub_ifd(0x8769)

    @parse(ExifExtension.gps_ifd)
    def parse_gps_ifd(self):
        return self.parse_sub_ifd(0x8825)

    @parse(ExifExtension.interop_ifd)
    def parse_interop_ifd(self):
        if self.target.exif_ifd is None:
            return None, None

        return self.parse_sub_ifd(0xA005, parent_ifd=self.target.exif_ifd)

    def parse_sub_ifd(self, tag, parent_ifd=None):
        if parent_ifd is None:
            parent_ifd = self.target.ifds[0]
        exif_tag = parent_ifd.search_tag(tag)
        if exif_tag is None or not exif_tag.is_valid_pointer:
            return None, None

        pointer = exif_tag.values.values[0]
        ifds = self.parse_ifd_chain(pointer)
        if not ifds:
            return None, None
        return ifds[0], None


@parses(MakernoteExentsion)
class MakernoteExtensionParser(Parser):
    @parse(MakernoteExentsion.makernote)
    def parse_makernote(self):
        return 'Foo', None

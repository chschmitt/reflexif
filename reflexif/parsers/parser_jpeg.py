# -*- coding: utf-8 -*-
'''
Created on 09.09.2016

@author: gongy
'''

import io
import struct

from reflexif.models.jpeg import SZ_VARIABLE, SZ_ZERO, SEGMENTS
from reflexif import errors, compat
from reflexif.models import jpeg
from reflexif.io import readexactly

class SegmentData(object):
    def __init__(self, segment, offset, size, payload, incomplete=False):
        self.segment = segment
        self.offset = offset
        self.size = size
        self.payload = payload
        self.incomplete = incomplete
        
    def __repr__(self):
        return '<SegmentData: %s offset=%d, size=%d>' % (
            self.segment.name, self.offset, self.size)

    @property
    def payload_offeset(self):
        if self.size == 0:
            raise ValueError
        return self.offset + 4

class NoMarkerError(Exception):
    pass

class JPEGStreamParser(object):
    segment_by_marker = {s.marker: s for s in SEGMENTS}
    uint16 = struct.Struct('>H')

    def __init__(self, fd, search_markers=False, read_trailer=False):
        self.fd = fd
        self.read_trailer = read_trailer
        self.search_markers = search_markers
        self.trailer = None
        self.segments = []

    def read_checked(self, n):
        return readexactly(self.fd, n) 

    def parse_marker(self):
        data = self.read_checked(2)
        if data[0:1] != b'\xff':
            self.fd.seek(-2, io.SEEK_CUR)
            raise NoMarkerError

        while data[1:2] == b'\xff':
            data = data[1:2] + self.read_checked(1)

        return self.uint16.unpack(data)[0]

    def parse_uint16(self):
        return self.uint16.unpack(self.read_checked(2))[0]

    def check_marker(self, buffer, length):
        offset = 0
        while offset < length:
            try:
                index = buffer.index(b'\xff', offset)
            except ValueError:
                return None

            index += 1
            if index == length:
                return -1

            marker = buffer[index]
            if marker == 0:
                offset = index + 1
            else:
                return index - 1


    def skip_scan(self):
        buf = bytearray(4096)
        while True:
            r = self.fd.readinto(buf)
            if r == 0:
                raise EOFError
            marker_offset = self.check_marker(buf, r)
            if marker_offset is None:
                continue

            if marker_offset == -1:
                self.fd.seek(-1, io.SEEK_CUR)
            else:
                self.fd.seek(marker_offset - r, io.SEEK_CUR)
                break

        # self.state = ST_SEG

    #def parse_scan(self):
    #    while True:
    #        b = self.read_checked(1)
    #        if b == b'\xff':
    #            b2 = self.read_checked(1)
    #            if b2 == b'\x00':
    #                continue
    #
    #            offset = self.fd.tell() - 2
    #            self.fd.seek(offset)
    #            break

    def search_marker(self):
        while True:
            b = self.read_checked(1)
            if b != b'\xff':
                continue
            data = b + self.read_checked(1)
            return self.uint16.unpack(data)[0]


        #if self.state == ST_SCAN and not segment.is_rst and not segment is jpeg.Segments.EOI:
        #    raise errors.JPEGError('unexpected segment in ST_SCAN: %r' % segment)

        #if segment.is_rst or segment is jpeg.Segments.SOS:
        #    self.state = ST_SCAN
        #    self.skip_scan()
        #else:
        #    self.state = ST_SEG
    
    def parse_segments(self):
        for seg in self._parse_segments():
            self.segments.append(seg)
            yield seg
    
    def parse_segments2(self):
        for seg in self._parse_segments():
            self.segments.append(seg)
    
    def _parse_segments(self):
        scan = False
        while True:
            seg = self.parse_segment()
            if not seg.segment.is_rst:
                yield seg

            if seg.segment == jpeg.Segments.EOI:
                break
            elif seg.segment == jpeg.Segments.SOS:
                scan = True
            elif scan and seg.segment.is_rst:
                pass
            else:
                scan = False

            if scan:
                self.skip_scan()
        
        if self.read_trailer:
            self.parse_trailer()
            #trailer_data = self.fd.read()
            #self.trailer = TrailerData(trailer_data)
    
    def parse_trailer(self):
        trailer_data = self.fd.read()
        self.trailer = TrailerData(trailer_data)
        return self.trailer


    def parse_segment(self):
        offset = self.fd.tell()

        try:
            marker = self.parse_marker()
        except NoMarkerError:
            if not self.search_markers:
                raise
            marker = self.search_marker()

        segment = self.segment_by_marker.get(marker)
        if segment is None:
            raise errors.JPEGError('unknown marker %04X' % marker)

        if segment.sizing == SZ_ZERO:
            return SegmentData(segment, offset, 0, None)
        else:
            size = self.parse_uint16()
            if size in (0, 1):
                raise errors.JPEGError('illegal segment size %d, segement=%r' % (size, segment))
            try:
                incomplete = False
                payload = self.read_checked(size-2)
            except EOFError as e:
                incomplete = True
                payload = e.args[0]

            return SegmentData(segment, offset, size, payload, incomplete)

TR_ALL_ZEROS = 1
TR_ALL_FF = 2
TR_JPEG = 3
TR_UNKNOWN = 4

class TrailerData(object):
    def __init__(self, data):
        self.data = data
        self.type = self._analyze()
    
    def get_jpeg_data(self):
        if self.type != TR_JPEG:
            raise ValueError
        return self.data.lstrip(b'\x00')
    
    def parse_trailer_segments(self, read_trailer=True):
        with io.BytesIO(self.get_jpeg_data()) as fd:
            p = JPEGStreamParser(fd)
            p.parse_segments2()
            return p
        
    def _analyze(self):
        d = self.data
        if not d.strip(b'\x00'):
            return TR_ALL_ZEROS
        elif not d.strip(b'\xff'):
            return TR_ALL_FF
        elif d.lstrip(b'\00').startswith(b'\xff\xd8'):
            return TR_JPEG
        
    def __bool__(self):
        return self.type not in (TR_ALL_FF, TR_ALL_ZEROS)
    
    if compat.PY2:
        __nonzero__ = __bool__

# -*- coding: utf-8 -*-
'''
.. created on 08.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *

from reflexif.models.tiff import TiffHeader
from reflexif.framework.model_base import FrameObject, child, value, Structs
from reflexif.framework.declarative import extend


class ExifHeader(FrameObject):
    exif_start = value(0, 6, desc='Exif marker')
    tiff_header = child(TiffHeader, 6, desc='TIFF header')


class JPEGExifSegment(FrameObject):
    exif_segment_raw = child()
    exif_segment = child(ExifHeader)

    @property
    def tiff_header(self):
        return self.exif_segment.tiff_header


@extend(TiffHeader)
class ExifExtension(FrameObject):
    exif_ifd = child()
    gps_ifd = child()
    interop_ifd = child()

    def search_tag(self, ifdname, tag):
        ifd = None
        if ifdname == "Image":
            if self.ifds:
                ifd = self.ifds[0]
        elif ifdname == "Exif":
            ifd = self.exif_ifd

        if not ifd:
            return

        return ifd.search_tag(tag)

@extend(TiffHeader, depends_on=[ExifExtension])
class MakernoteExentsion(FrameObject):
    makernote = child()

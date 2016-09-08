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


class ExifSegment(FrameObject):
    exif_start = value(0, 6, desc='Exif marker')
    tiff_header = child(TiffHeader, 6, desc='TIFF header')
    
@extend(TiffHeader)
class ExifExtension(FrameObject):
    exif_ifd = child()
    gps_ifd = child()
    interop_ifd = child()

@extend(TiffHeader, depends_on=[ExifExtension])
class MakernoteExentsion(FrameObject):
    makernote = child()


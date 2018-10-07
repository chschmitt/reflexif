'''
Created on 09.09.2016

@author: gongy
'''
import functools

SZ_ZERO = 1
SZ_VARIABLE = 2


class JPEGMarker(object):
    def __init__(self, marker, desc=None, name=None, is_rst=False, is_app=False, is_jpg=False):
        self.marker = marker
        self.identifier = marker & 0xff
        self.name = name
        self.desc = desc

        self.is_app = is_app
        self.is_jpg = is_jpg
        self.is_rst = is_rst

    def __repr__(self):
        return '<%s: %s %04X (%s)>' % (type(self).__name__, self.name, self.marker, self.desc)


class SegmentMarker(JPEGMarker):
    sizing = SZ_VARIABLE


class StandaloneMarker(JPEGMarker):
    sizing = SZ_ZERO


segment = SegmentMarker
marker = StandaloneMarker
rstmarker = functools.partial(marker, is_rst=True)


class Segments(object):
    # Start Of Frame markers, non-differential, Huffman coding
    SOF0 = segment(0xFFC0, "Start of Frame, Baseline DCT")
    SOF1 = segment(0xFFC1, "Start of Frame, Extended sequential DCT")
    SOF2 = segment(0xFFC2, "Start of Frame, Progressive DCT")
    SOF3 = segment(0xFFC3, "Start of Frame, Lossless (sequential)")

    # Start Of Frame markers, differential, Huffman coding
    SOF5 = segment(0xFFC5, "Start of Frame, Differential sequential DCT")
    SOF6 = segment(0xFFC6, "Start of Frame, Differential progressive DCT")
    SOF7 = segment(0xFFC7, "Start of Frame, Differential lossless (sequential)")

    # Start Of Frame markers, non-differential, arithmetic coding
    JPG = segment(0xFFC8, "Reserved for JPEG extensions")
    SOF9 = segment(0xFFC9, "Extended sequential DCT")
    SOF10 = segment(0xFFCA, "Progressive DCT")
    SOF11 = segment(0xFFCB, "Lossless (sequential)")

    # Start Of Frame markers, differential, arithmetic coding
    SOF13 = segment(0xFFCD, "Differential sequential DCT")
    SOF14 = segment(0xFFCE, "Differential progressive DCT")
    SOF15 = segment(0xFFCF, "Differential lossless (sequential)")

    # Huffman table specification
    DHT = segment(0xFFC4, "Define Huffman table(s)")

    # Arithmetic coding conditioning specification
    DAC = segment(0xFFCC, "Define arithmetic coding conditioning(s)")

    # Restart interval termination
    RST0 = rstmarker(0xFFD0, "Restart with modulo 8 count 0")
    RST1 = rstmarker(0xFFD1, "Restart with modulo 8 count 1")
    RST2 = rstmarker(0xFFD2, "Restart with modulo 8 count 2")
    RST3 = rstmarker(0xFFD3, "Restart with modulo 8 count 3")
    RST4 = rstmarker(0xFFD4, "Restart with modulo 8 count 4")
    RST5 = rstmarker(0xFFD5, "Restart with modulo 8 count 5")
    RST6 = rstmarker(0xFFD6, "Restart with modulo 8 count 6")
    RST7 = rstmarker(0xFFD7, "Restart with modulo 8 count 7")

    # Other markers
    SOI = marker(0xFFD8, "Start of image")
    EOI = marker(0xFFD9, "End of image")
    SOS = segment(0xFFDA, "Start of scan")
    DQT = segment(0xFFDB, "Define quantization table(s)")
    DNL = segment(0xFFDC, "Define number of lines")
    DRI = segment(0xFFDD, "Define restart interval")
    DHP = segment(0xFFDE, "Define hierarchical progression")
    EXP = segment(0xFFDF, "Expand reference component(s)")
    COM = segment(0xFFFE, "Comment")


def add_app_segements():
    app_segements = []
    for i in range(16):
        name ='APP%d' % i
        seg = segment(0xFFE0 + i, "Application Segment %d" % i, is_app=True)
        app_segements.append(seg)
        setattr(Segments, name, seg)

    Segments.app_segements = app_segements



def add_jpg_segements():
    for i in range(14):
        name ='JPG%d' % i
        seg = segment(0xFFF0 + i, "JPEG extension segment %d" % i, is_jpg=True)
        setattr(Segments, name, seg)

SEGMENTS = []

def apply_names_and_collect():
    for name, value in vars(Segments).items():
        if isinstance(value, JPEGMarker):
            value.name = name
            SEGMENTS.append(value)


add_app_segements()
add_jpg_segements()
apply_names_and_collect()

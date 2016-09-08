# -*- coding: utf-8 -*-
'''
.. created on 30.08.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division
from reflexif.compat import *

import fractions
from reflexif.errors import TIFFError
import struct


class Type(object):
    # def for_endianess(self, endianess):
    #     return self

    def byte_count(self, count):
        raise NotImplementedError

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, Type):
            return False
        else:
            return self.code == other.code

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.code


class UnsizedType(Type):
    multiplicator = 1

    def __init__(self, name, code):
        self.name = name
        self.code = code

    # def byte_count(self, count):
    #     return count


class AsciiType(UnsizedType):
    def parse_values(self, count, data):
        if data.endswith(b'\x00'):
            data = data[:-1]
        parts = data.split(b'\x00')
        # return parts
        try:
            return [p.decode('ascii') for p in parts]
        except UnicodeDecodeError:
            return [p.decode('latin1') for p in parts]


class BytesType(UnsizedType):
    def parse_values(self, count, data):
        return data


class SizedType(Type):
    def __init__(self, name, code, struct_def):
        self.name = name
        self.code = code
        self.struct_def = struct_def
        self.size = struct.calcsize('>' + struct_def)
        self.multiplicator = self.size
        # self.struct = None
        # self.struct = struct.Struct(struct_fmt)

    # @property
    # def size(self):
    #     return self.struct.size

    # def for_endianess(self, endianess):
    #     copy = SizedType(self.name, self.code, self.struct_def)
    #     copy.struct = struct.Struct(endianess + copy.struct_def)
    #     return copy

    # def byte_count(self, count):
    #     return self.size * count

    # def parse_value(self, data):
    #     return self.struct.unpack(data)[0]

    def parse_values(self, count, data):
        if len(data) != self.byte_count(count):
            raise TIFFError

        values = []

        o1 = 0
        o2 = self.size
        for _ in range(count):
            value = self.parse_value(data[o1:o2])
            values.append(value)
            o1 = o2
            o2 = o1 + self.size

        return values

    def pack_values(self, values):
        count = len(values)
        data = b''
        for v in values:
            data += self.pack_value(v)
        return count, data

    def pack_value(self, value):
        return self.struct.pack(value)


class RationalType(SizedType):
    def parse_value(self, data):
        num, den = self.struct.unpack(data)
        return num, den
        # return fractions.Fraction(num, den)

    def pack_value(self, value):
        return self.struct.pack(value.numerator, value.denominator)


class Types(object):
    BYTE = SizedType('BYTE', 1, 'B')
    ASCII = AsciiType('ASCII', 2)
    SHORT = SizedType('SHORT', 3, 'H')
    LONG = SizedType('LONG', 4, 'L')
    RATIONAL = RationalType('RATIONAL', 5, 'LL')
    SBYTE = SizedType('SBYTE', 6, 'b')
    UNDEFINED = BytesType('UNDEFINED', 7)
    SSHORT = SizedType('SSHORT', 8, 'h')
    SLONG = SizedType('SLONG', 9, 'l')
    SRATIONAL = RationalType('SRATIONAL', 10, 'll')
    FLOAT = SizedType('FLOAT', 11, 'f')
    DOUBLE = SizedType('DOUBLE', 12, 'd')

    numeric = [BYTE, SHORT, LONG, RATIONAL, SBYTE, SSHORT, SLONG, SRATIONAL, FLOAT, DOUBLE]
    integer = [BYTE, SHORT, LONG, SBYTE, SSHORT, SLONG]
    unsigned_integer = [BYTE, SHORT, LONG]


TYPES = {t for t in Types.__dict__.values() if isinstance(t, Type)}
BY_CODE = {t.code: t for t in TYPES}

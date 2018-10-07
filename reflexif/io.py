# -*- coding: utf-8 -*-
'''
.. created on 22.08.2016
.. by Christoph Schmitt
'''

# do not use unicode literals in this module, otherwise the Struct
# constructor will complain
from __future__ import print_function, absolute_import, division

from reflexif.compat import *
import struct


class SourceWrapper(object):
    delegates = set('__bytes__')

    def __init__(self, source):
        self.source = source

    def __getattr__(self, attr):
        if attr not in self.delegates:
            raise AttributeError
        return getattr(self.source, attr)

    def __len__(self):
        return len(self.source)

    def __getitem__(self, key):
        return self.source[key]


class FileSource(object):
    def __init__(self, fd, offset, length):
        if offset < 0:
            raise IndexError('offset < 0')
        if length < 0:
            raise IndexError('negative length')

        self.fd = fd
        self.offset = offset
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step is not None:
                raise IndexError('illegal slicing %r' % index)

            if index.start is None:
                start = 0
            else:
                start = index.start

            if index.stop is None:
                stop = self.length
            else:
                stop = index.stop

            if start < 0 or stop < start:
                raise IndexError('illegal slicing %r' % index)

            return self.read_at(start, stop-start)
        else:

            return self.read_at(index, 1)[0]

    def detach(self):
        self.fd = None

    def read_at(self, offset, length):
        if offset < 0 or length < 0:
            raise ValueError
        if offset + length > self.length:
            raise EOFError
        abs_offset = self.offset + offset
        self.fd.seek(abs_offset)
        if self.fd.tell() != abs_offset:
            raise IOError('seek resulted in wrong offset')
        data = readexactly(self.fd, length)
        return data

def readexactly(fd, n):
    buffer = bytearray(n)
    m = memoryview(buffer)
    read = 0
    while read < n:
        r = fd.readinto(m)
        if not r:
            raise EOFError(bytes(m[:read]))
        read += r
        m = m[r:]
    return bytes(buffer)

class Frame(object):
    def __init__(self, source, offset=0, length=None):
        if offset < 0:
            raise IndexError('offset < 0')

        if length is None:
            if source is None:
                raise ValueError('length or source must not be None')
            length = len(source) - offset

        if length < 0:
            raise IndexError('negative length')
        elif offset + length > len(source):
            raise IndexError('length of source exceeded')

        self.source = source
        self.offset = offset
        self.length = length

        self.on_create()

    def on_create(self):
        pass

    def on_sliced_from(self, parent):
        pass
        # print(self, bytes(self))

    def slice(self, offset, length):
        if offset is None or length is None:
            raise ValueError
        if offset < 0 or length < 0:
            raise IndexError('illegal slicing offset or length')
        new_offset = self.offset + offset
        stop = new_offset + length
        if stop > self.stop:
            raise IndexError('slicing exceeds boundary', self, offset, length)
        cls = type(self)
        child = cls(self.source, new_offset, length)
        child.on_sliced_from(self)
        return child

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.start is None:
                start = 0
            else:
                start = index.start

            if index.stop is None:
                stop = self.length
            else:
                stop = index.stop

            if index.step is not None:
                raise IndexError('illegal slicing %r' % index)
            if start < 0 or stop < start:
                raise IndexError('illegal slicing %r' % index)
            return self.slice(start, stop - start)
        else:
            return self.data[index]

    @property
    def data(self):
        data = self.source[self.offset:self.offset + self.length]
        if len(data) < self.length:
            raise EOFError('got %d bytes at source offset %d, %d expected'
                           % (len(data), self.offset, self.length))

        return data

    def __bytes__(self):
        return bytes(self.data)

    @property
    def start(self):
        return self.offset

    @property
    def stop(self):
        return self.offset + self.length

    def __len__(self):
        return self.length

    def __repr__(self):
        return '<%s: [%d:%d], len=%d>' % (type(self).__name__,
                                          self.start,
                                          self.stop,
                                          len(self))


class StructSpec(object):
    def __init__(self, spec):
        self.spec = spec
        self.le = struct.Struct('>'+spec)
        self.be = struct.Struct('<'+spec)


uint8 = StructSpec('B')
uint16 = StructSpec('H')
uint32 = StructSpec('I')
uint64 = StructSpec('Q')

int8 = StructSpec('b')
int16 = StructSpec('h')
int32 = StructSpec('i')
int64 = StructSpec('q')

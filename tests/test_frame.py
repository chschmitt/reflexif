# -*- coding: utf-8 -*-
'''
.. created on 21.08.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *

import io
import os
import unittest

from reflexif.io import Frame, SourceWrapper, FileSource


class TestFrame(unittest.TestCase):
    data = bytes(range(256))

    def testConstructorFail(self):
        with self.assertRaises(IndexError):
            Frame(self.data, -1)
        with self.assertRaises(IndexError):
            Frame(self.data, 0, len(self.data)+1)
        with self.assertRaises(IndexError):
            Frame(self.data, len(self.data), 1)
        with self.assertRaises(IndexError):
            Frame(self.data, len(self.data), -1)

    def testConstructor(self):
        Frame(self.data, 0)
        Frame(self.data, 1)

        f = Frame(self.data, len(self.data))
        self.assertEqual(0, len(f))

        f = Frame(self.data, len(self.data), 0)
        self.assertEqual(0, len(f))

    def testSliceLength(self):
        f = Frame(self.data, 20, 10)
        self.assertEqual(len(f[5:6]), 1)
        self.assertEqual(len(f[0:10]), 10)

    def testSliceContent(self):
        f = Frame(self.data, 20, 10)
        self.assertEqual(f[0:10].data, f.data)
        self.assertEqual(f[5:6].data, self.data[25:26])
        f2 = f[2:8]
        f3 = f2[2:4]
        self.assertEqual(f3.data, self.data[24:26])

    def testSliceMethodFail(self):
        f = Frame(self.data, 20, 10)
        with self.assertRaises(ValueError):
            f.slice(None, None)
        with self.assertRaises(ValueError):
            f.slice(None, 1)
        with self.assertRaises(ValueError):
            f.slice(1, None)

    def testSliceSpecialCases(self):
        f = Frame(self.data, 20, 10)
        s1 = f[:]
        s2 = f[1:]
        s3 = f[:1]

        self.assertEqual(s1.length, f.length)
        self.assertEqual(s2.length, f.length-1)
        self.assertEqual(s3.length, 1)

        self.assertEqual(s1.offset, f.offset)
        self.assertEqual(s2.offset, f.offset+1)
        self.assertEqual(s3.offset, f.offset)

    def testSliceFail(self):
        f = Frame(self.data, 20, 10)
        with self.assertRaises(IndexError):
            f[:-1]
        with self.assertRaises(IndexError):
            f[-1:]
        with self.assertRaises(IndexError):
            f[::1]
        with self.assertRaises(IndexError):
            f[1:2:3]
        with self.assertRaises(IndexError):
            f[0:11]
        with self.assertRaises(IndexError):
            f[5:0]
        with self.assertRaises(IndexError):
            f[10:12]

    def testDataFail(self):
        f = Frame(self.data, 10, 20)

        # make frame too long
        f.length = len(self.data)-9

        with self.assertRaises(EOFError):
            data_slice = f.data

            # debugging output
            # used to identify https://github.com/IronLanguages/main/issues/1387
            b = bytes(data_slice)
            print('lengths: data_slice: %d, f: %d, f.source: %d, bytes(data_slice): %d' % (len(data_slice), len(f), len(f.source), len(b)))
            print('f.source:              ', type(f.source), '%r' % f.source, '%r' % bytes(f.source))
            print('wrongly returned slice:', type(data_slice), '%r' % data_slice, '%r' % b)

    def testBytes(self):
        f = Frame(self.data, 10, 20)
        actual = bytes(self.data[10:30])
        expected = bytes(f)
        self.assertEqual(actual[0], 10)
        self.assertEqual(expected, actual)

    def testData(self):
        l = 100

        def testoffset(o):
            f = Frame(self.data, o, l)
            self.assertEqual(self.data[o:o+l], f.data)
            for i in range(len(f)):
                self.assertEqual(f[i], self.data[o+i])

        testoffset(0)
        testoffset(10)
        testoffset(30)
        testoffset(156)


class TestFrameWithWrapperSource(TestFrame):
    data = SourceWrapper(bytes(range(256)))


class TestFrameWithMemoryView(TestFrame):
    data = memoryview(bytes(range(80)))


class TestFrameWithFileSource(TestFrame):
    data = FileSource(io.BytesIO(bytes(range(256))), 0, 256)


class TestFrameWithFileSourceWithOffset(TestFrame):
    raw = bytearray(os.urandom(1024))
    raw[200:456] = bytes(range(256))
    data = FileSource(io.BytesIO(raw), 200, 256)


class TestFrameWithWrappedMemoryView(TestFrame):
    data = SourceWrapper(memoryview(bytes(range(256))))


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
'''
.. created on 25.08.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *

import functools
import itertools
import struct
import re

from reflexif import types

EXIF_START = b'Exif\x00\x00'
    

class Field(object):
    _order_counter = iter(itertools.count()) 
    
    def __init__(self, cls=None, start=None, stop=None, struct_spec=None, name=None, desc=None, leaf=False):
        if stop is not None and not isinstance(stop, int):
            size = struct.calcsize('>' + stop)
            struct_spec = stop
            stop = start + size
            
        self.cls = cls
        self.start = start
        self.stop = stop
        self.struct_spec = struct_spec
        self.name = name
        self.desc = desc
        self.leaf = leaf
        self._order = next(self._order_counter)
        
    def start(self, start):
        self.start = start
        return self
    
    def length(self, length):
        if self.start is None:
            raise ValueError
        self.end = self.start + length
        return self
    
    def stop(self, stop):
        self.stop = stop
    
    @property
    def is_value(self):
        return self.cls is None
        
    @property
    def slice(self):
        return slice(self.start, self.stop)
    
    def __repr__(self):
        return '<%s: %s (%s)>' % (type(self).__name__, self.name, self.desc)

child = Field
value = functools.partial(Field, None)
        

#class Context(object):
#    def __init__(self, little_endian=False, resilient=True, extensions=None):
#        if extensions is None:
#            extensions = [ExifExtension, MakernoteExentsion]
#        self.extensions = map_extensions(extensions)
#        self.little_endian = little_endian
#        self.resilient = resilient
#        self.seen_ifd_pointers = set()


def get_fields(cls):
    fields = []
    names = {}

    for name, value in vars(cls).items():
        if not isinstance(value, Field):
            continue
        if value.name is None:
            value.name = name

        fields.append(value)
        names[name] = cls

    
    for mro_cls in cls.__mro__:
        if mro_cls is cls or not issubclass(mro_cls, FrameObject):
            continue
        
        for field in mro_cls.fields:
            if field.name not in names:
                fields.append(field)
                names[name] = mro_cls
            else:
                print('field %r: already defined in %r, ignoring definition in %s' % (value, names[name], mro_cls))
        
                
    fields.sort(key=lambda f : f._order)
    print(cls, fields)
    return fields


class FieldsDescriptor(object):
    def __get__(self, obj, cls):
        #if obj is not None:
        #    raise AttributeError('fields accessed through instance')
        if not issubclass(cls, FrameObject):
            raise TypeError('WTF?')
        value = vars(cls).get('_fields_')
        if value is None:
            value = get_fields(cls)
            cls._fields_ = value
        return value        

#def fieldnames(cls):
#    return cls
#    
#    fields = []
#    for mro_class in cls.__mro__:
#        for name, value in vars(mro_class).items():
#            if not isinstance(value, Field):
#                continue
#            value.name = name
#            fields.append(value)
#
#    fields.sort(key=lambda f : f._order)
#    cls._fields = fields
#    cls._extension_fields = []
#    return cls

class FrameObject(object):
    fields = FieldsDescriptor()
    
    def __init__(self, frame):
        self.frame = frame
        self.frames = {f.name: None for f in self.fields}
        self.on_create()
        
    def on_create(self):
        pass
    
    #@classmethod
    #def _all_fields(cls):
    #    return cls._fields + cls._extension_fields
        
    def __repr__(self):
        def fields():
            for field in self.fields:
                if not field.is_value:
                    continue
                yield '%s=%r' % (field.name, getattr(self, field.name))
                
        return '<%s: %s>' % (type(self).__name__, ', '.join(fields()))
    
    def dump(self, with_frame=False, with_data=False, indent=None):
        if indent is None:
            indent = ''
            
        def islistof_fo(value):
            if isinstance(value, (list, tuple)) and len(value) > 0:
                return isinstance(value[0], FrameObject)
            return False
        
        if not indent:        
            print('%s%s:' % (indent, type(self).__name__))
        
        for field in self.fields:
            value = getattr(self, field.name)
            if isinstance(value, FrameObject):
                print('%s  %s=%s:' % (indent, field.name, type(value).__name__))
                value.dump(with_frame, with_data, indent + '  ')
            elif islistof_fo(value):
                for i, item in enumerate(value):
                    print('%s  %s=%s:' % (indent, '%s[%d]' % (field.name, i), type(item).__name__))
                    item.dump(with_frame, with_data, indent + '  ')
            else:
                if isinstance(value, (str, bytes, unicode)):
                    value = value[:100]
                    
                msg = '%s  %s=%r' % (indent, field.name, value)
                frame = self.frames[field.name]
                if with_frame:
                    if frame is None:
                        msg += ', [no frame]'
                    else:
                        msg = ('%s, offset=%d, length=%d' % (msg, frame.offset, frame.length))
                if with_data:
                    if frame is None:
                        data = None
                    else:
                        data = frame.data
                    msg = ('%s, data=%r' % (msg, data))
                print(msg)

def add_type_structs(cls):
    for t in types.TYPES:
        try:
            setattr(cls, t.name, t.struct_def)
        except AttributeError:
            pass
    return cls

@add_type_structs
class Structs(object):
    SHORT = 'H'
    LONG = 'L'

    def __init__(self):
        self.le = {}
        self.be = {}
        for name, value in vars(type(self)).items():
            if not re.match('^[A-Z]+$', name):
                continue
            self.be[value] = struct.Struct('>' + value)
            self.le[value] = struct.Struct('<' + value)
            
structs = Structs()




    
    
# class ContainerDict(dict):
#     container = list
#     
#     def append(self, key, element):
#         try:
#             self[key].append(element)
#         except KeyError:
#             self[key] = self.container()
#             self[key].append(element)
#     
#     def __getitem__(self, key):
#         try:
#             return super(ContainerDict, self).__getitem__(key)
#         except KeyError:
#             return self.container()


    


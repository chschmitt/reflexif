# -*- coding: utf-8 -*-
'''
.. created on 08.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *

from reflexif.framework import model_base, declarative
from reflexif.framework.model_base import structs


def parentalias(cls=None):
    def parent(self):
        if cls is not None and not isinstance(self.parent, cls):
            raise TypeError('parent of %r is not an instance of %r' % (self, cls))
        return self.parent
    return property(parent)


def parse(field, returns_frame=False):
    if not isinstance(field, model_base.Field):
        raise ValueError

    def decorator(f):
        f.parsed_field = field
        f.returns_frame = returns_frame
        return f

    return decorator


class State(object):
    def __init__(self, little_endian=False, resilient=True, active_extensions=None):
        self.little_endian = little_endian
        self.resilient = resilient
        self.seen_ifd_pointers = set()
        self.active_extensions = active_extensions or {}


class Parser(object):
    def __init__(self, frame, state=None,
                 context=declarative.default_parser_context,
                 extension_context=declarative.default_extension_context):

        self.context = context
        self.extension_context = extension_context

        if state is None:
            ext_classes = frozenset(extension_context.all_extension_classes)
            ext_lookup = extension_context.map_extensions(ext_classes)
            state = State(active_extensions=ext_lookup)

        self.frame = frame
        self.state = state
        self.target = None

        self.on_create()

    @property
    def annotation(self):
        return self.context[type(self)]

    def on_create(self):
        pass

    def get_taget_class(self):
        parsed_class = self.annotation.parsed_class
        if not self.extensions:
            return parsed_class
        else:
            ext_classes = [e.extension_class for e in self.extensions]
            # use str to be compatible with Python 2
            # see http://stackoverflow.com/questions/19618031
            name = str('Extended' + parsed_class.__name__)
            bases = (parsed_class,) + tuple(ext_classes)
            return type(name, bases, {})

    def __call__(self):
        # print(type(self))
        if self.target is None:
            target_cls = self.get_taget_class()
            self.target = target_cls(self.frame)

        for field in self.annotation.parsed_class.fields:
            try:
                self.parse_field(field)
            except:
                print('error: %s: %s' % (type(self), field))
                raise

        self.parse_extensions()
        return self.target

    def parse_field(self, field):
        parse_func = self.annotation.field_parsers.get(field)
        if parse_func is None:
            if field.is_value:
                fallback = lambda: self.unpack_value(field)
            else:
                fallback = lambda: self.parse_child_field(field)

            value, sub_frame = fallback()
        else:
            value, sub_frame = parse_func(self)

        setattr(self.target, field.name, value)
        self.target.frames[field.name] = sub_frame

    def unpack_value(self, field, sub_frame=None):
        if sub_frame is None:
            sub_frame = self.frame[field.slice]
        if field.struct_spec is None:
            value = bytes(sub_frame.data)
        else:
            if self.state.little_endian:
                s = structs.le[field.struct_spec]
            else:
                s = structs.be[field.struct_spec]
            # print(self, field.name, s.format, sub_frame, sub_frame.data, field.slice)
            value = s.unpack(sub_frame.data)[0]
        return value, sub_frame

    def parse_child_field(self, field, sub_frame=None):
        if sub_frame is None:
            sub_frame = self.frame[field.slice]
        return self.parse_class(field.cls, sub_frame)

    def parse_class(self, cls, sub_frame, state=None):
        if state is None:
            state = self.state
        try:
            sub_parser_cls = self.context.resolve_parser(cls)
        except AttributeError:
            sub_parser_cls = self.default_parser(cls)
        sub_parser = sub_parser_cls(sub_frame, self.state)
        sub_parser.parent = self
        return sub_parser(), sub_frame

    def default_parser(self, cls):
        parser_cls = type(cls.__name__ + 'Parser', (Parser,), {})
        deco = self.context.parses(cls)
        return deco(parser_cls)

    @property
    def extensions(self):
        return self.state.active_extensions.get(self.annotation.parsed_class)

    def parse_extensions(self):
        if not self.extensions:
            return

        for extension in self.extensions:
            # print('parsing extension %s, parent parser: %s, target: %s' % (extension, self, self.target))
            parser_cls = self.context.resolve_parser(extension.extension_class)
            parser = parser_cls(self.frame)
            parser.target = self.target
            parser()

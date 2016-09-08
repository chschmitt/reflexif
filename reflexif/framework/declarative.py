# -*- coding: utf-8 -*-
'''
.. created on 08.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *

import collections

from reflexif.framework import depresolver


class SimpleCache(object):
    def __init__(self, f):
        self.f = f
        self.cache = {}
        self.hits = 0
        self.misses = 0

    def __call__(self, arg):
        try:
            value = self.cache[arg]
            self.hits += 1
        except KeyError:
            value = self.f(arg)
            self.cache[arg] = value
            self.misses += 1

        return value

    def invalidate(self):
        self.cache.clear()


class ModelContext(object):
    pass


class ParserAnnotation(object):
    def __init__(self, parser, parsed_class):
        self.parser = parser
        self.parsed_class = parsed_class
        self.field_parsers = {}


class FieldAnnotation(object):
    pass


class ParserContext(object):
    def __init__(self):
        self.annotations = {}
        self.resolve_parser = SimpleCache(self._resolve_parser)

    def __getitem__(self, key):
        return self.annotations[key]

    def _resolve_parser(self, cls):
        for annotation in self.annotations.values():
            if annotation.parsed_class == cls:
                return annotation.parser

    def parses(self, cls):
        def decorator(parser_cls):
            pa = ParserAnnotation(parser_cls, cls)
            # cls.parsed_by = parser_cls
            # parser_cls.parses = cls

            for name, value in vars(parser_cls).items():
                try:
                    field = value.parsed_field
                except AttributeError:
                    continue
                pa.field_parsers[field] = value

            self.resolve_parser.invalidate()
            self.annotations[parser_cls] = pa
            return parser_cls
        return decorator

Extension = collections.namedtuple('Extension', ['extension_class', 'extended_class', 'dependencies'])


class ExtensionContext(object):
    def __init__(self):
        self.extensions = {}
        self.map_extensions = SimpleCache(self._map_extensions)

    @property
    def all_extension_classes(self):
        return list(e.extension_class for e in self.extensions.values())

    def extend(self, extended_cls, depends_on=None):
        if depends_on is None:
            depends_on = tuple()

        def decorator(cls):
            ext = Extension(cls, extended_cls, tuple(depends_on))
            self.extensions[cls] = ext
            return cls
        return decorator

    def _map_extensions(self, active_extension_classes):
        if not isinstance(active_extension_classes, frozenset):
            raise TypeError

        result = collections.defaultdict(list)
        for ext_cls in active_extension_classes:
            extension = self.extensions[ext_cls]
            result[extension.extended_class].append(extension)

        expand = lambda e: [self.extensions[cls] for cls in e.dependencies]

        def depsort(extensions):
            return depresolver.depsort(extensions, expand)

        return {cls: depsort(exts) for cls, exts in result.items()}


default_parser_context = ParserContext()
parses = default_parser_context.parses

default_extension_context = ExtensionContext()
extend = default_extension_context.extend

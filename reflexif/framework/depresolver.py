# -*- coding: utf-8 -*-
'''
.. created on 06.09.2016
.. by Christoph Schmitt
'''

from __future__ import print_function, absolute_import, division, unicode_literals
from reflexif.compat import *


class Resolver(object):
    def __init__(self, nodes, expand):
        self.nodes = nodes
        self.expand = expand
        self.depth_cache = {}
        self.misses = 0
        self.hits = 0

    def depth(self, node):
        return self._depth(node)

    def _depth(self, node, startnode=None):
        if node in self.depth_cache:
            self.hits += 1
            return self.depth_cache[node]
        else:
            self.misses += 1

        if startnode is None:
            startnode = node
        elif node is startnode:
            raise ValueError('%r has circular dependency' % node)

        children = self.expand(node)
        if children:
            res = 1 + max(self._depth(c, startnode) for c in children)
        else:
            res = 0

        self.depth_cache[node] = res
        return res

    def dependecy_sorted(self):
        return sorted(self.nodes, key=self.depth)


def depsort(nodes, expand):
    return Resolver(nodes, expand).dependecy_sorted()

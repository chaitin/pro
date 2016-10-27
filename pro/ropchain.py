from collections import defaultdict

from .parse import Address

class RopChainError(Exception):
    pass

class Marker(object):
    pass

class RopChain(list):
    def __init__(self, *args):
        super(RopChain, self).__init__(*args)

        self.define = set()
        self.reserve = set()

    def __add__(self, other):
        return RopChunk([self, other])

    def fix(self):
        ''' try to resolve Marker '''
        for i in xrange(len(self)):
            if isinstance(self[i], Marker):
                for j in xrange(len(self)):
                    if self[j] == id(self[i]):
                        # find match
                        self[i] = Address('self', j * 8)
                        break

    def final(self):
        ''' rebase `self` to `code` '''
        self.fix()
        for g in self:
            if isinstance(g, Marker):
                raise RopChainError('unresolved marker')
            elif isinstance(g, Address) and g.base == 'self':
                g.base = '_CODE'
        return self

    def extends(self, other):
        ''' concat with another RopChain and rebase it'''
        offset = len(self) * 8
        other.fix()
        for i in xrange(len(other)):
            o = other[i]
            if isinstance(o, Address) and o.base == 'self':
                o.offset += offset
            self.append(o)

        if 'all' in other.define:
            self.define = {'all'}
        else:
            self.define |= other.define

        if 'all' in other.reserve:
            self.reserve = {'all'}
        else:
            self.reserve |= other.reserve

        return self

    @property
    def size(self):
        return len(self) * 8

class RopChunk(list):
    def compact(self):
        n = len(self)
        D = [0] * n
        M = defaultdict(set)
        for i in xrange(n):
            u = self[i]
            for j in xrange(n):
                if i == j:
                    continue
                v = self[j]
                if (u.define & v.reserve) or ('all' in v.reserve):
                    # u should be in front of v
                    M[i].add(j)
                    D[j] += 1

        compacted = RopChain()

        for i in xrange(n):
            try:
                u = D.index(0)
                D[u] = -1
            except ValueError:
                raise RopChainError('failed to build ropchain')

            compacted.extends(self[u])

            for v in M[u]:
                D[v] -= 1

        compacted.fix()
        compacted.define = set()
        compacted.reserve = set()

        return compacted

    @property
    def size():
        return sum((x.size for x in self))

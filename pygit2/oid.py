# -*- coding: utf-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# Import from the Standard Library
import binascii
from sys import version_info
from functools import total_ordering

# Import from pygit2
from _pygit2 import Repository as _Repository
from _pygit2 import GIT_BRANCH_LOCAL, GIT_BRANCH_REMOTE
from _pygit2 import Oid, GIT_OID_HEXSZ, GIT_OID_MINPREFIXLEN
from _pygit2 import GIT_CHECKOUT_SAFE_CREATE, GIT_DIFF_NORMAL
from _pygit2 import Reference, Tree, Commit, Blob

# ffi version
from .ffi import ffi, C, to_str
from .errors import check_error

def expand_id(repo, short_id):
    if len(short_id) == GIT_OID_HEXSZ:
        return Oid(hex=short_id)

    codb = ffi.new("git_odb **")
    err = C.git_repository_odb(codb, repo)
    check_error(err)

    # get the short id inot a git_oid
    l = len(short_id)
    if l % 2 == 1:
        l -= 1

    coid = ffi.new("git_oid *")
    err = C.git_oid_fromstrn(coid, to_str(short_id), len(short_id))
    check_error(err)

    cobj = ffi.new("git_odb_object **")
    err = C.git_odb_read_prefix(cobj, codb[0], coid, l)
    C.git_odb_free(codb[0])
    check_error(err)

    oid = Oid.from_c(C.git_odb_object_id(cobj[0]))
    C.git_odb_object_free(cobj[0])

    return oid

@total_ordering
class Oid(object):

    __slots__ = ['_buf', '_oid', '_len']

    def __init__(self, hex=None, raw=None):

        if not hex and not raw:
            raise ValueError("Expected raw or hex.")
        if hex and raw:
            raise ValueError("Expected raw or hex, not both.")

        oid = ffi.new("git_oid *")
        buf = ffi.buffer(oid)
        if raw:
            if len(raw) > 40:
                raise ValueError(raw)

            buf[:] = raw[:]
            l = C.GIT_OID_RAWSZ
        else:
            if len(hex) > 40:
                raise ValueError("too long")
            if version_info.major == 3 and type(hex) != str:
                    raise TypeError(hex)

            l = int(len(hex)/2)
            buf[:l] = binascii.unhexlify(hex)

        self._oid = oid
        self._buf = buf
        self._len = l

    @classmethod
    def from_c(cls, oid):
        o = cls.__new__(cls)
        o._oid = ffi.new('git_oid *')
        C.git_oid_cpy(o._oid, oid)
        o._buf = ffi.buffer(o._oid)
        o._len = C.GIT_OID_HEXSZ
        return o

    @property
    def raw(self):
        return bytes(self._buf)

    @property
    def hex(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, str(self))

    def __str__(self):
        return binascii.hexlify(self._buf).decode()

    def _cmp(self, b):
        return C.git_oid_cmp(self._oid, b._oid)

    def __eq__(self, b):
        return self._cmp(b) == 0

    def __lt__(self, b):
        return self._cmp(b) < 0

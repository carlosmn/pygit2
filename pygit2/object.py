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
from string import hexdigits

# Import from pygit2
from _pygit2 import Oid, GIT_OID_HEXSZ, GIT_OID_MINPREFIXLEN
from _pygit2 import GIT_CHECKOUT_SAFE_CREATE, GIT_DIFF_NORMAL

# ffi
from .ffi import ffi, C, to_str

from .reference import Reference as Reference2
from .oid import Oid, expand_id
from .errors import check_error

def wrap_object(repo, cobj):
    obj = cobj[0]

    objtype = C.git_object_type(obj)
    if objtype == C.GIT_OBJ_COMMIT:
        return Commit(repo, cobj)
    elif objtype == C.GIT_OBJ_BLOB:
        return Blob(repo, cobj)
    elif objtype == C.GIT_OBJ_TREE:
        return Tree(repo, cobj)
    elif objtype == C.GIT_OBJ_Tag:
        return Tag(repo, cobj)

class Object(object):

    def __init__(self, repo, cobj):
        self._repo = repo
        self._cobj = cobj
        self._obj = cobj[0]

    @property
    def id(self):
        return Oid(raw=ffi.buffer(C.git_object_id(self._obj)))

    @property
    def hex(self):
        return self.id.hex

class Commit(Object):
    pass

class Blob(Object):
    pass

class Tree(Object):
    pass

class Tag(Object):
    pass

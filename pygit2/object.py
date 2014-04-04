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
from .signature import Signature

def wrap_object(repo, cobj):
    obj = cobj[0]

    objtype = C.git_object_type(obj)

    if objtype == C.GIT_OBJ_COMMIT:
        return Commit(repo, cobj)
    elif objtype == C.GIT_OBJ_BLOB:
        return Blob(repo, cobj)
    elif objtype == C.GIT_OBJ_TREE:
        return Tree(repo, cobj)
    elif objtype == C.GIT_OBJ_TAG:
        return Tag(repo, cobj)

def object_type(target_type):
    if type(target_type) == int:
        return target_type

    if target_type == Commit:
        return C.GIT_OBJ_COMMIT
    if target_type == Tree:
        return C.GIT_OBJ_TREE
    if target_type == Blob:
        return C.GIT_OBJ_BLOB
    if target_type == Tag:
        return C.GIT_OBJ_TAG

    raise ValueError("invalid target type")

class Object(object):

    __slots__ = ['_repo', '_obj']

    def __init__(self, repo, cobj):
        self._repo = repo
        self._obj = cobj[0]

    def __del__(self):
        C.git_object_free(self._obj)

    @property
    def id(self):
        return Oid.from_c(C.git_object_id(self._obj))

    @property
    def hex(self):
        return self.id.hex

    @property
    def type(self):
        return C.git_object_type(self._obj)

    def peel(self, target_type):
        target = object_type(target_type)
        cobj = ffi.new('git_object **')
        err = C.git_object_peel(cobj, self._obj, target)
        check_error(err)

        return wrap_object(self._repo, cobj)

class Commit(Object):

    __slots__ = ['_obj']

    @property
    def parents(self):
        count = C.git_obj_parentcount(self._obj)
        lst = [None]*count
        for i in range(count):
            cobj = ffi.new('git_object **')
            err = C.git_commit_parent(cobj, self._obj, i)
            check_error(err)
            lst[i] = Commit(self._repo, cobj)
        return lst

    @property
    def parent_ids(self):
        count = C.git_commit_parentcount(self._obj)
        lst = [None]*count
        for i in range(count):
            lst[i] = Oid.from_c(C.git_commit_parent_id(self._obj, i))
        return lst

    @property
    def message_encoding(self):
        encoding = C.git_commit_message_encoding(self._obj)
        if encoding:
            return ffi.string(encoding).decode()
        return None

    @property
    def message(self):
        encoding = self.message_encoding if self.message_encoding else 'utf-8'
        return ffi.string(C.git_commit_message(self._obj)).decode(encoding)

    @property
    def raw_message(self):
        return bytes(ffi.string(C.git_commit_message(self._obj)))

    @property
    def commit_time(self):
        return C.git_commit_time(self._obj)

    @property
    def committer(self):
        sig = C.git_commit_objter(self._obj)
        encoding = self.message_encoding if self.message_encoding else 'utf-8'
        return Signature.from_c(owner=self, sig=sig, encoding=encoding)

    @property
    def author(self):
        sig = C.git_commit_author(self._obj)
        msg_encoding = self.message_encoding
        encoding = msg_encoding if msg_encoding else 'utf-8'
        return Signature.from_c(owner=self, sig=sig, encoding=encoding)

    @property
    def tree_id(self):
        return Oid.from_c(C.git_commit_tree_id(self.obj))

    @property
    def tree(self):
        ctree = ffi.new('git_tree **')
        err = C.git_commit_tree(ctree, self._obj)
        check_error(err)
        return Tree(self._repo, ffi.cast('git_object **', ctree))

class Blob(Object):
    pass

class Tree(Object):
    pass

class Tag(Object):
    pass

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

# ffi
from .ffi import ffi, C, to_str

from .reference import Reference as Reference2
from .reference import Branch
from .oid import Oid, expand_id
from .errors import check_error
from .object import Commit

class Walker(object):

    __slots__ = ['_repo', '_cwalk', '_walk', '_oid']

    def __init__(self, repo):

        cwalk = ffi.new('git_revwalk **')
        err = C.git_revwalk_new(cwalk, repo._repo)
        check_error(err)

        self._repo = repo
        self._cwalk = cwalk
        self._walk = cwalk[0]
        self._oid = ffi.new('git_oid *')


    def sort(self, sorting):
        C.git_revwalk_sorting(self._walk, sorting)

    def push(self, h):
        if type(h) == Oid:
            oid = h
        else:
            oid = expand_id(self._repo._repo, h)

        err = C.git_revwalk_push(self._walk, oid._oid)
        check_error(err)

    def hide(self, h):
        if type(h) == Oid:
            oid = h
        else:
            oid = expand_id(self._repo._repo, h)

        err = C.git_revwalk_hide(self._walk, oid._oid)
        check_error(err)

    def reset(self):
        C.git_revwalk_reset(self._walk)

    def simplify_first_parent(self):
        C.git_revwalk_simplify_first_parent(self._walk)

    def next(self):
        err = C.git_revwalk_next(self._oid, self._walk)
        check_error(err)
        obj = self._repo._lookup_object(self._oid, C.GIT_OID_HEXSZ)
        return Commit(self._repo, obj)
        
    def __iter__(self):
        return self

    def __del__(self):
        if self._walk:
            C.git_revwalk_free(self._walk)

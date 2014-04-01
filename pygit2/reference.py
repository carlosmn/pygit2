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
from .oid import Oid, expand_id
from .errors import check_error

from _pygit2 import GitError

def guess_oid(repo, id):
    if type(id) == bytes:
        return Oid(raw=id)
    else:
        return expand_id(repo, id)

class Reference(object):

    def __init__(self, repo, cref):
        """This constructor is internal"""
        self._repo = repo
        self._cref = cref
        self._ref = cref[0]

    @property
    def name(self):
        self._assert_valid()
        return ffi.string(C.git_reference_name(self._ref)).decode()

    @property
    def type(self):
        self._assert_valid()
        return C.git_reference_type(self._ref)

    @property
    def target(self):
        self._assert_valid()
        if C.git_reference_type(self._ref) == C.GIT_REF_OID:
            return self._target_direct()
        else:
            return self._target_symbolic()

    @target.setter
    def target(self, target):
        self._assert_valid()
        if self.type == C.GIT_REF_OID:
            self._target_direct_set(target)
        else:
            self._target_symbolic_set(target)

    def get_object(self):
        return self._repo[self.target]

    @property
    def shorthand(self):
        self._assert_valid()
        return ffi.string(C.git_reference_shorthand(self._ref)).decode()

    def resolve(self):
        self._assert_valid()
        if self.type == C.GIT_REF_OID:
            return self

        cref = ffi.new('git_reference **')
        err = C.git_reference_resolve(cref, self._ref)
        check_error(err)

        return Reference(self._repo, cref)

    def rename(self, new_name, force=False):
        self._assert_valid()
        cref = ffi.new('git_reference **')
        err = C.git_reference_rename(cref, self._ref, to_str(new_name), force)
        check_error(err)

        self._swap(cref)

    def delete(self):
        self._assert_valid()
        err = C.git_reference_delete(self._ref)
        check_error(err)

        C.git_reference_free(self._ref)
        self._ref = None
        del self._cref

    def __del__(self):
        if self._ref:
            C.git_reference_free(self._ref)

    def _assert_valid(self):
        if not self._ref:
            raise GitError("deleted reference")

    def _swap(self, cref):
        C.git_reference_free(self._ref)
        self._cref = cref
        self._ref = cref[0]

    def _target_direct(self):
        return Oid.from_c(C.git_reference_target(self._ref))

    def _target_direct_set(self, target):
        cref = ffi.new("git_reference **")
        err = C.git_reference_set_target(cref, self._ref, guess_oid(self._repo._repo, target)._oid)
        check_error(err)

        self._swap(cref)
        
    def _target_symbolic(self):
        return ffi.string(C.git_reference_symbolic_target(self._ref)).decode()

    def _target_symbolic_set(self, target):
        cref = ffi.new("git_reference **")
        err = C.git_reference_symbolic_set_target(cref, self._ref, to_str(target))
        check_error(err)

        self._swap(cref)

class Branch(Reference):

    def is_head(self):
        return bool(C.git_branch_is_head(self._ref))

    @property
    def branch_name(self):
        cbuf = ffi.new('char **')
        err = C.git_branch_name(cbuf, self._ref)
        check_error(err)

        return ffi.string(cbuf[0]).decode()

    def rename(self, new_name, force=False):
        cref = ffi.new('git_reference **')
        err = C.git_branch_move(cref, self._ref, to_str(new_name), force)
        check_error(err)
        return Branch(self._repo, cref)

    def delete(self):
        err = C.git_branch_delete(self._ref)
        check_error(err)
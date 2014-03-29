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
from _pygit2 import Repository as _Repository
from _pygit2 import GIT_BRANCH_LOCAL, GIT_BRANCH_REMOTE
from _pygit2 import Oid, GIT_OID_HEXSZ, GIT_OID_MINPREFIXLEN
from _pygit2 import GIT_CHECKOUT_SAFE_CREATE, GIT_DIFF_NORMAL
from _pygit2 import Reference, Tree, Commit, Blob

# ffi
from .ffi import ffi, C, to_str

from .reference import Reference as Reference2
from .oid import Oid, expand_id
from .errors import check_error
from .object import wrap_object

class Repository2(object):

    _repo = None

    def __init__(self, path):
        crepo = ffi.new("git_repository **")
        if C.git_repository_open(crepo, to_str(path)):
            raise "oops"
        self._crepo = crepo
        self._repo = crepo[0] # to get the pointer itself

    @property
    def path(self):
        """The normalized path to the git repository"""
        return ffi.string(C.git_repository_path(self._repo))

    @property
    def is_empty(self):
        return bool(C.git_repository_is_empty(self._repo))

    @property
    def is_shallow(self):
        return bool(C.git_repository_is_shallow(self._repo))

    @property
    def workdir(self):
        """The normalized path to the working directory of the repository.

        If the repository is bare, None will be returned.
        """
        cstr = C.git_repository_workdir(self._repo)
        if cstr == ffi.NULL:
            return None
        else:
            return ffi.string(cstr)

    @property
    def head(self):
        cref = ffi.new('git_reference **')
        err = C.git_repository_head(cref, self._repo)
        check_error(err)

        return Reference2(self, cref)

    def lookup_reference(self, name):
        cref = ffi.new("git_reference **")
        err = C.git_reference_lookup(cref, self._repo, to_str(name))
        if err == C.GIT_ENOTFOUND:
            raise KeyError(name)
        elif err < 0:
            raise Exception("dunno")

        return Reference2(self, cref)

    def listall_references(self):
        strarray = ffi.new('git_strarray *')
        err = C.git_reference_list(strarray, self._repo)
        if err < 0:
            raise Exception(err)

        for i in range(strarray.count):
            yield ffi.string(strarray.strings[i]).decode()

        C.git_strarray_free(strarray)

    def create_reference(self, name, target, force=False):
        """
        Create a new reference "name" which points to an object or to another
        reference.

        Based on the type and value of the target parameter, this method tries
        to guess whether it is a direct or a symbolic reference.

        Keyword arguments:

        force
            If True references will be overridden, otherwise (the default) an
            exception is raised.

        Examples::

            repo.create_reference('refs/heads/foo', repo.head.hex)
            repo.create_reference('refs/tags/foo', 'refs/heads/master')
            repo.create_reference('refs/tags/foo', 'bbb78a9cec580')
        """
        direct = (
            type(target) is Oid
            or (
                all(c in hexdigits for c in target)
                and GIT_OID_MINPREFIXLEN <= len(target) <= GIT_OID_HEXSZ))

        cref = ffi.new('git_reference **')
        if direct:
            err = C.git_reference_create(cref, self._repo, to_str(name), Oid(hex=expand_id(self._repo, target))._oid, force)
        else:
            err = C.git_reference_symbolic_create(cref, self._repo, to_str(name), to_str(target), force)

        check_error(err)
        return Reference2(self, cref)

    def __getitem__(self, key):
        if type(key) == str:
            key = Oid(hex=key)

        cobj = ffi.new('git_object **')
        err = C.git_object_lookup_prefix(cobj, self._repo, key._oid, key._len, C.GIT_OBJ_ANY)
        check_error(err)
        return wrap_object(self, cobj)

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, self.path)

    def __del__(self):
        if self._repo:
            C.git_repository_free(self._repo)

class Repository(_Repository):

    #
    # Mapping interface
    #
    def get(self, key, default=None):
        value = self.git_object_lookup_prefix(key)
        return value if (value is not None) else default


    def __getitem__(self, key):
        value = self.git_object_lookup_prefix(key)
        if value is None:
            raise KeyError(key)
        return value


    def __contains__(self, key):
        return self.git_object_lookup_prefix(key) is not None

    def __repr__(self):
        return "pygit2.Repository(%r)" % self.path

    #
    # References
    #
    def create_reference(self, name, target, force=False):
        """
        Create a new reference "name" which points to an object or to another
        reference.

        Based on the type and value of the target parameter, this method tries
        to guess whether it is a direct or a symbolic reference.

        Keyword arguments:

        force
            If True references will be overridden, otherwise (the default) an
            exception is raised.

        Examples::

            repo.create_reference('refs/heads/foo', repo.head.hex)
            repo.create_reference('refs/tags/foo', 'refs/heads/master')
            repo.create_reference('refs/tags/foo', 'bbb78a9cec580')
        """
        direct = (
            type(target) is Oid
            or (
                all(c in hexdigits for c in target)
                and GIT_OID_MINPREFIXLEN <= len(target) <= GIT_OID_HEXSZ))

        if direct:
            return self.create_reference_direct(name, target, force)

        return self.create_reference_symbolic(name, target, force)


    #
    # Checkout
    #
    def checkout(self, refname=None, strategy=GIT_CHECKOUT_SAFE_CREATE):
        """
        Checkout the given reference using the given strategy, and update
        the HEAD.
        The reference may be a reference name or a Reference object.
        The default strategy is GIT_CHECKOUT_SAFE_CREATE.

        To checkout from the HEAD, just pass 'HEAD'::

          >>> checkout('HEAD')

        If no reference is given, checkout from the index.

        """
        # Case 1: Checkout index
        if refname is None:
            return self.checkout_index(strategy)

        # Case 2: Checkout head
        if refname == 'HEAD':
            return self.checkout_head(strategy)

        # Case 3: Reference
        if type(refname) is Reference:
            reference = refname
            refname = refname.name
        else:
            reference = self.lookup_reference(refname)

        oid = reference.resolve().target
        treeish = self[oid]
        self.checkout_tree(treeish, strategy)
        self.head = refname


    #
    # Diff
    #
    def diff(self, a=None, b=None, cached=False, flags=GIT_DIFF_NORMAL,
             context_lines=3, interhunk_lines=0):
        """
        Show changes between the working tree and the index or a tree,
        changes between the index and a tree, changes between two trees, or
        changes between two blobs.

        Keyword arguments:

        cached
            use staged changes instead of workdir

        flag
            a GIT_DIFF_* constant

        context_lines
            the number of unchanged lines that define the boundary
            of a hunk (and to display before and after)

        interhunk_lines
            the maximum number of unchanged lines between hunk
            boundaries before the hunks will be merged into a one

        Examples::

          # Changes in the working tree not yet staged for the next commit
          >>> diff()

          # Changes between the index and your last commit
          >>> diff(cached=True)

          # Changes in the working tree since your last commit
          >>> diff('HEAD')

          # Changes between commits
          >>> t0 = revparse_single('HEAD')
          >>> t1 = revparse_single('HEAD^')
          >>> diff(t0, t1)
          >>> diff('HEAD', 'HEAD^') # equivalent

        If you want to diff a tree against an empty tree, use the low level
        API (Tree.diff_to_tree()) directly.
        """

        def treeish_to_tree(obj):
            try:
                obj = self.revparse_single(obj)
            except:
                pass

            if isinstance(obj, Commit):
                return obj.tree
            elif isinstance(obj, Reference):
                oid = obj.resolve().target
                return self[oid]

        a = treeish_to_tree(a) or a
        b = treeish_to_tree(b) or b

        opt_keys = ['flags', 'context_lines', 'interhunk_lines']
        opt_values = [flags, context_lines, interhunk_lines]

        # Case 1: Diff tree to tree
        if isinstance(a, Tree) and isinstance(b, Tree):
            return a.diff_to_tree(b, **dict(zip(opt_keys, opt_values)))

        # Case 2: Index to workdir
        elif a is None and b is None:
            return self.index.diff_to_workdir(*opt_values)

        # Case 3: Diff tree to index or workdir
        elif isinstance(a, Tree) and b is None:
            if cached:
                return a.diff_to_index(self.index, *opt_values)
            else:
                return a.diff_to_workdir(*opt_values)

        # Case 4: Diff blob to blob
        if isinstance(a, Blob) and isinstance(b, Blob):
            raise NotImplementedError('git_diff_blob_to_blob()')

        raise ValueError("Only blobs and treeish can be diffed")

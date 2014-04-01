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
from __future__ import unicode_literals
from string import hexdigits

# ffi
from .ffi import ffi, C, to_str

from .reference import Reference as Reference2
from .oid import Oid, expand_id
from .errors import check_error

class Signature(object):

    _owner = None
    _sig = None

    def __init__(self, name, email, time=None, offset=0, encoding='ascii'):
        csig = ffi.new('git_signature **')

        name = to_str(name, encoding)
        email = to_str(email, encoding)
        if time:
            err = C.git_signature_new(csig, name, email, time, offset)
        else:
            err = C.git_signature_now(csig, name, email)

        check_error(err)
        self._encoding = encoding
        self._csig = csig
        self._sig = csig[0]

    def __del__(self):
        # Not having an owner means we're reponsible for freeing this signature
        if not self._owner and self._sig:
            C.git_signature_free(self._sig)

    @classmethod
    def from_c(cls, csig=None, sig=None, owner=None, encoding='utf-8'):
        c = cls.__new__(cls)
        c._csig = csig
        c._sig = sig
        c._owner = owner
        c._encoding = encoding
        return c

    @property
    def raw_name(self):
        return bytes(ffi.string(self._sig.name))
    
    @property
    def name(self):
        return ffi.string(self._sig.name).decode(self._encoding)

    @property
    def raw_email(self):
        return bytes(ffi.string(self._sig.email))

    @property
    def email(self):
        return ffi.string(self._sig.email).decode(self._encoding)

    @property
    def time(self):
        return self._sig.when.time

    @property
    def offset(self):
        return self._sig.when.offset

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

# Import from the future
from __future__ import absolute_import

from enum import Enum

# Import from pygit2
from .errors import check_error, GitError
from .ffi import ffi, C
from .utils import to_bytes

class DescribeStrategy(Enum):
    Default = C.GIT_DESCRIBE_DEFAULT
    Tags    = C.GIT_DESCRIBE_TAGS
    All     = C.GIT_DESCRIBE_ALL

class DescribeResult(object):
    def __init__(self, ptr):
        self._describe_result = ptr

    def format(self, abbreviated_size=7, always_use_long_format=False, dirty_suffix=None):

        copts = ffi.new('git_describe_format_options *')
        check_error(C.git_describe_format_init_options(copts, C.GIT_DESCRIBE_FORMAT_OPTIONS_VERSION))
        copts.abbreviated_size = abbreviated_size
        copts.always_use_long_format = int(always_use_long_format)
        ctops.dirty_suffix = to_bytes(dirty_suffix)

        cbuf = ffi.new('git_buf *', (ffi.NULL, 0))

        err = C.git_describe_format(cbuf, self._describe_result, copts)
        check_error(err)

        try:
            return ffi.string(cbuf.ptr).decode()
        finally:
            C.git_buf_free(cbuf)


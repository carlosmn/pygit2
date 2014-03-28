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

from cffi import FFI
import sys

if sys.version_info.major < 2:
    def to_str(s):
        return s
else:
    def to_str(s):
        return bytes(s, 'utf-8')

ffi = FFI()

ffi.cdef("""
void git_libgit2_version(int *, int *, int *);

#define GIT_OID_RAWSZ ...

typedef struct git_oid {
	unsigned char id[20];
} git_oid;

int git_oid_fromstr(git_oid *out, const char *str);
void git_oid_fmt(char *out, const git_oid *id);
int git_oid_cmp(const git_oid *a, const git_oid *b);

typedef struct git_repository git_repository;

int git_repository_open(git_repository **, const char *);
const char *git_repository_path(git_repository *);
const char *git_repository_workdir(git_repository *);
int git_repository_is_bare(git_repository *repo);
int git_repository_is_empty(git_repository *repo);
int git_repository_is_shallow(git_repository *repo);
void git_repository_free(git_repository *);
""")

C = ffi.verify("#include <git2.h>", libraries=["git2"])

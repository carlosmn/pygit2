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

if sys.version_info.major < 3:
    def to_str(s):
        return str(s)
else:
    def to_str(s):
        if type(s) == bytes:
            return s
        else:
            print(type(s))

ffi = FFI()

ffi.cdef("""
void git_libgit2_version(int *, int *, int *);

typedef enum {
	GIT_OK = 0,
	GIT_ERROR = -1,
	GIT_ENOTFOUND = -3,
	GIT_EEXISTS = -4,
	GIT_EAMBIGUOUS = -5,
	GIT_EBUFS = -6,
	GIT_EUSER = -7,
	GIT_EBAREREPO = -8,
	GIT_EUNBORNBRANCH = -9,
	GIT_EUNMERGED = -10,
	GIT_ENONFASTFORWARD = -11,
	GIT_EINVALIDSPEC = -12,
	GIT_EMERGECONFLICT = -13,
	GIT_ELOCKED = -14,

	GIT_PASSTHROUGH = -30,
	GIT_ITEROVER = -31,
} git_error_code;

typedef struct {
	char *message;
	int klass;
} git_error;

typedef struct {
	char **strings;
	size_t count;
} git_strarray;

const git_error *giterr_last(void);

typedef enum {
	GIT_OBJ_ANY = -2,
	GIT_OBJ_BAD = -1,
	GIT_OBJ__EXT1 = 0,
	GIT_OBJ_COMMIT = 1,
	GIT_OBJ_TREE = 2,
	GIT_OBJ_BLOB = 3,
	GIT_OBJ_TAG = 4,
	GIT_OBJ__EXT2 = 5,
	GIT_OBJ_OFS_DELTA = 6,
	GIT_OBJ_REF_DELTA = 7,
} git_otype;

#define GIT_OID_RAWSZ ...

typedef struct git_oid {
	unsigned char id[20];
} git_oid;

int git_oid_fromstr(git_oid *out, const char *str);
void git_oid_fmt(char *out, const git_oid *id);
int git_oid_cmp(const git_oid *a, const git_oid *b);

typedef struct git_reference git_reference;
typedef struct git_repository git_repository;
typedef struct git_object git_object;
typedef struct git_odb git_odb;

int git_repository_open(git_repository **, const char *);
const char *git_repository_path(git_repository *);
const char *git_repository_workdir(git_repository *);
int git_repository_is_bare(git_repository *repo);
int git_repository_is_empty(git_repository *repo);
int git_repository_is_shallow(git_repository *repo);
int git_repository_odb(git_odb **out, git_repository *repo);
int git_repository_head(git_reference **, git_repository *repo);
void git_repository_free(git_repository *);

typedef enum {
	GIT_REF_INVALID = 0,
	GIT_REF_OID = 1,
	GIT_REF_SYMBOLIC = 2,
} git_ref_t;

int git_reference_lookup(git_reference **out, git_repository *repo, const char *name);
const char * git_reference_name(const git_reference *ref);
git_ref_t git_reference_type(const git_reference *ref);
const git_oid * git_reference_target(const git_reference *ref);
const char * git_reference_symbolic_target(const git_reference *ref);
int git_reference_set_target(git_reference **out,
	git_reference *ref,
	const git_oid *id);
int git_reference_symbolic_set_target(git_reference **out,
	git_reference *ref,
	const char *target);

int git_reference_create(git_reference **out, git_repository *repo, const char *name, const git_oid *id, int force);
int git_reference_symbolic_create(git_reference **out, git_repository *repo, const char *name, const char *target, int force);
const char * git_reference_shorthand(git_reference *ref);
int git_reference_dwim(git_reference **out, git_repository *repo, const char *shorthand);
int git_reference_resolve(git_reference **out, const git_reference *ref);
int git_reference_rename(git_reference **out, git_reference *ref, const char *new_name, int force);
int git_reference_list(git_strarray *, git_repository *);

int git_reference_delete(git_reference *ref);
void git_reference_free(git_reference *ref);

void git_strarray_free(git_strarray *);

int git_object_lookup(git_object **, git_repository *, git_oid *, git_otype type);
int git_object_lookup_prefix(git_object **, git_repository *, git_oid *, size_t len, git_otype type);
git_otype git_object_type(git_object *);
git_oid *git_object_id(git_object *);

typedef struct git_odb_object git_odb_object;
int git_odb_read_prefix(git_odb_object **out, git_odb *db, const git_oid *short_id, size_t len);
void git_odb_free(git_odb *db);
void git_odb_object_free(git_odb_object *object);
const git_oid * git_odb_object_id(git_odb_object *object);
""")

C = ffi.verify("#include <git2.h>", libraries=["git2"])

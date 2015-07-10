# -*- coding: utf-8 -*-
# Utilities to read and inspect the ``versions`` folder

import os
import os.path
import re

from . import utils
from .migrations import Migration

file_re = re.compile("\d+\_[a-zA-Z0-9_]+\_([0-9a-f]+)\.py")


def _topological_sort(revisions):
    unsorted_objs = {}
    for obj in revisions:
        unsorted_objs[obj.revision_id] = obj

    sorted_objs = []
    while unsorted_objs:
        acyclic = False
        for obj_id, obj in unsorted_objs.items():
            depends = obj.depends
            for dep_id in depends:
                if dep_id in unsorted_objs:
                    break
            else:
                acyclic = True
                sorted_objs.append(obj)
                del unsorted_objs[obj_id]
        # There is a cycle if we can't resolve at least 1 object per
        # `while` loop
        if not acyclic:
            raise ValueError(
                "Cannot sort revisions. There's a cycle in dependencies.")
    return sorted_objs


class Revisions(object):

    def __init__(self, revisions):
        self.revisions = revisions

    def __iter__(self):
        return iter(self.revisions)

    @classmethod
    def from_folder(cls, folder):
        revisions = []
        if not os.path.isdir(folder):
            raise ValueError("{} should be a folder path".format(folder))
        for path in os.listdir(folder):
            revisions.append(Revision.from_file(path))

        # Find multiple heads
        head_revisions = filter(lambda x: x.revision_id, revisions)
        if len(head_revisions) > 1:
            raise ValueError("We have multiple heads: {}".format(
                [x.revision_id for x in head_revisions]))
        # Find multiple dependencies
        by_down = {}
        for revision in revisions:
            if revision.down_revision_id in by_down:
                raise ValueError(
                    "Both {} and {} depends on same revision {}".format(
                        revision.revision_id,
                        by_down[revision.down_revision_id].revision_id,
                        revision.down_revision_id))
            by_down[revision.down_revision_id] = revision
        # Order by dependencies
        sorted_revisions = [head_revisions[0]]
        next_down = head_revisions[0].revision_id
        while next_down:
            try:
                rev = by_down[next_down]
            except KeyError:
                if len(sorted_revisions) != len(by_down):
                    raise ValueError(
                        "Could not find revision, that depend on {}"
                        .format(next_down))
            sorted_revisions.append(rev)
            next_down = rev.revision_id

        return cls(revisions)


class Revision(object):

    def __init__(self, revision_id, down_revision_id, migrations):
        self.migrations = migrations
        self.revision_id = revision_id
        self.down_revision_id = down_revision_id

    def __iter__(self):
        return iter(self.migrations)

    @classmethod
    def from_file(cls, filepath):
        dirname, filename = os.path.split(filepath)
        file_match = file_re.match(filename)
        if not file_match:
            raise ValueError("{} does not match pattern {}".format(
                filename, file_re))

        file_rev_id = file_match.group(0)

        revision_module = utils.import_file_as_py(filepath)
        if file_rev_id != revision_module.revision:
            raise ValueError(
                "Revision in filename {} does not match revision in module {}"
                .format(file_rev_id, revision_module.revision))

        # Extract all classes, that extend
        migrations = []
        for vname in dir(revision_module):
            veriable = getattr(revision_module, vname)
            if issubclass(veriable, Migration):
                if veriable.order is None:
                    raise ValueError("Migration.__init__ not called in {} {}"
                                     .format(filepath, vname))
                migrations.append(veriable)
        migrations.sort(key=lambda x: x.order)

        return cls(
            revision_id=revision_module.revision_id,
            down_revision_id=revision_module.down_revision_id,
            migrations=migrations)

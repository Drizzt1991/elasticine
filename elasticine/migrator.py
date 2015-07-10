# -*- coding: utf-8 -*-

import logging


DEFAULT_NAME_TEMPLATES = {
    "read_alias": "{index_name}_read",
    "write_alias": "{index_name}_write",
    "index_name": "{index_name}_{revision_id}"
}


class MigrationError(Exception):
    pass


class ElasticMigrator(object):

    log = logging.getLogger(__name__)

    def __init__(self, revisions, adapter, name_templates=None):
        self.revisions = revisions
        self.adapter = adapter
        self.name_templates = name_templates or DEFAULT_NAME_TEMPLATES

    def get_revision(self, revision_id):
        for revision in self.revisions:
            if revision.revision_id == revision_id:
                return revision

    def do_upgrade(self, to_revision_id):
        current_revision_id = self.get_current_revision()
        if current_revision_id == to_revision_id:
            return

        current_revision = self.get_revision(current_revision_id)
        to_revision = self.get_revision(to_revision_id)

        if current_revision is None:
            raise MigrationError(
                "Could not find current revision `{}`".format(
                    current_revision_id))
        if to_revision is None:
            raise MigrationError(
                "Could not find revision `{}` to upgrate".format(
                    to_revision_id))

        # Get [current_revision:to_revision] slice
        revisions = []
        start = False
        for revision in self.revisions:
            if revision is current_revision:
                start = True
            elif revision is to_revision:
                if not start:
                    raise MigrationError(
                        "Current revision `{}` is higher than requested `{}`."
                        .format(current_revision_id, to_revision_id))
                revisions.append(revision)
                break
            elif start:
                revisions.append(revision)

        # Now we can execute migrations
        for revision in revisions:
            # List of migrations, that done most work and are only waiting to
            # finalize.
            pending = []
            for Migration in revision:
                migration = Migration(
                    adapter=self.adapter,
                    name_templates=self.name_templates)
                try:
                    migration.do_upgrade()
                except Exception as exc:
                    # Revert all pending migrations
                    for m in pending:
                        try:
                            m.revert(was_done=True)
                        except Exception:
                            # We did all we could to revert all done changes.
                            # Just log it.
                            self.log.error(
                                "Could not revert migration {}".format(m),
                                exc_info=True)
                    # Revert the broken migration
                    try:
                        migration.revert(was_done=False)
                    except Exception:
                        # We did all we could to revert all done changes.
                        # Just log it.
                        self.log.error(
                            "Could not revert migration {}".format(m),
                            exc_info=True)
                    # We raise this one from original
                    raise MigrationError("Failed to migrate data") from exc
                else:
                    pending.append(migration)
            # Now just finalize the changes
            for migration in pending:
                try:
                    migration.commit()
                except Exception:
                    # Commits should try not to raise error as thay will not
                    # be reverted in any cases. Just log...
                    self.log.error(
                        "Could not commit migration {}".format(m),
                        exc_info=True)

    def do_downgrade(self, to_revision):
        current_revision = self.get_current_revision()
        if current_revision == to_revision:
            return
        if current_revision < to_revision:
            raise MigrationError(
                "Current revision `{}` is lower than requested `{}`.".format(
                    current_revision, to_revision))
        for migration in self.get_migrations(
                current_revision, to_revision, reverse=True):
            migration.do_downgrade()

# -*- coding: utf-8 -*-


class MigrationError(Exception):
    pass


class ElasticMigrator(object):

    def __init__(self):
        pass

    def get_migrations(self):
        

    def do_upgrade(self, to_revision):
        current_revision = self.get_current_revision()
        if current_revision == to_revision:
            return
        if current_revision > to_revision:
            raise MigrationError(
                "Current revision `{}` is higher than requested `{}`.".format(
                    current_revision, to_revision))
        for migration in self.get_migrations(current_revision, to_revision):
            migration.do_upgrade()

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

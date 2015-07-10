# -*- coding: utf-8 -*-

import abc

elastic_default = object()


class Migration(metaclass=abc.ABCMeta):
    """ Base class for all migrations
    """

    def __init__(self, adapter, name_templates, revision_id):
        self.adapter = adapter
        self.name_templates = name_templates
        self.revision_id = revision_id

    def do_upgrade(self):
        return self.upgrade()

    @property
    def read_alias(self):
        return self.name_templates['read_alias'].format(self.index_name)

    @property
    def write_alias(self):
        return self.name_templates['write_alias'].format(self.index_name)

    @property
    def index_revision_name(self):
        return self.name_templates['index_name'].format(
            self.index_name, self.revision_id)

    @abc.abstractpropery
    def index_name(self):
        """ Actualy this is not an index name. More like it's the base name for
            aliases. By default migrator will use those formats:

                Read Alias: {index_name}_read
                Write Alias: {index_name}_write
                Real index name: {index_name}_{revision_id}

        """
        return None

    @abc.abstractmethod
    def upgrade(self):
        pass

    @abc.abstractmethod
    def revert(self):
        pass

    @abc.abstractmethod
    def commit(self):
        pass


class MappingMigration(Migration):

    @abc.abstractmethod
    def upgrade(self):
        pass

    @abc.abstractmethod
    def revert(self):
        pass

    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def change_mapping(self, old_mapping):
        pass


class SettingsMigration(Migration):

    @abc.abstractmethod
    def change_settings(self, old_settings):
        pass


class CreateIndex(Migration):

    @abc.abstractpropery
    def mappings(self):
        return None

    @abc.abstractpropery
    def settings(self):
        return None

    @abc.abstractpropery
    def warmers(self):
        return None

    def upgrade(self):
        body = {}
        if self.settings:
            body['settings'] = self.settings
        if self.mapping:
            body['mappings'] = self.mappings
        if self.warmers:
            body['warmers'] = self.warmers

        index_name = self.index_revision_name
        # FIXME: set timeout and master_timeout
        self.adapter.index_create(
            index_name, body=body)

    def revert(self, was_done):
        index_name = self.index_revision_name
        if self.adapter.index_exists(index_name):
            self.adapter.index_remove(index_name)

    def commit(self):
        index_name = self.index_revision_name
        # Add aliases to newly created index so we can receive requests
        self.adapter.update_aliases([
            {'add': {"index": index_name, "alias": self.read_alias}},
            {'add': {"index": index_name, "alias": self.write_alias}},
            ])


class DropIndex(Migration):

    @abc.abstractpropery
    def mappings(self):
        return None

    @abc.abstractpropery
    def settings(self):
        return None

    @abc.abstractpropery
    def warmers(self):
        return None

    def upgrade(self):
        index_name = self.index_revision_name
        self.adapter.update_aliases([
            {'add': {"index": index_name, "alias": self.read_alias}},
            {'add': {"index": index_name, "alias": self.write_alias}},
            ])

    def revert(self):
        pass

    def commit(self):
        pass

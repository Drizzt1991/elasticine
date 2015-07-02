# -*- coding: utf-8 -*-


elastic_default = object()


class MappingMigration(object):

    def __init__(self, index_name, mapping_change):
        self._index_name = index_name
        if not mapping_change:
            raise ValueError("`mapping_change` can not be empty")
        self._mapping_change = mapping_change


class SettingsMigration(object):

    def __init__(self, index_name, settings_change):
        self._index_name = index_name
        if not settings_change:
            raise ValueError("`settings_change` can not be empty")
        self._settings_change = settings_change

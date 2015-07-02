# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch


class ElasticAdapter(object):
    """ Abstraction in case we will need to add another or change elastic
        driver.
    """

    def __init__(self, hosts, **es_params):
        self.es = Elasticsearch(hosts, **es_params)

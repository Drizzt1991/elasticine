# -*- coding: utf-8 -*-

import uuid


def rev_id():
    # Took from Alembic...
    val = int(uuid.uuid4()) % 100000000000000
    return hex(val)[2:-1]


def import_file_as_py(filename):
    pass

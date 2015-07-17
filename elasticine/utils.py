# -*- coding: utf-8 -*-

import uuid
import os.path
import re
from importlib import machinery


def rev_id():
    # Took from Alembic...
    val = int(uuid.uuid4()) % 100000000000000
    return hex(val)[2:-1]


def import_file_as_py(filepath, module_id=None):
    """Load a file from the given path as a Python module."""
    dirname, name = os.path.split(filepath)
    name, ext = os.path.splitext(name)
    if module_id is None:
        module_id = re.sub(r'\W', "_", name)
    if ext == ".py":
        if os.path.exists(filepath):
            module = machinery.SourceFileLoader(module_id, filepath)\
                .load_module(module_id)
        else:
            raise ImportError("Can't find file %s" % filepath)
    else:
        raise ValueError("Wrong file extension {}".format(ext))
    return module

elasticine
==========

Elastic migration tool



Contribute
----------

Installation
~~~~~~~~~~~~

To install ``elasticine`` for local development follow those steps (all examples
are for python3):

1. Install system dependencies
   
   * Elastic

2. Create and activate a virtual environment. For python3 use ``pyvenv``, 
   for python2.7 use ``virtualenv``. You can also use ``virtualenvwrapper``.
   
.. code-block:: bash

    pyvenv .env
    source .env/bin/activate

3. Install application and dev requirements
   
.. code-block:: bash
    
    pip install -Ur requirements-dev.txt
    pip install -Ue .

4. Run tests
   
.. code-block:: bash

    nosetests tests/


Pull request
~~~~~~~~~~~~

If you want to contribute code changes follow the basic ``Pull request``
procedure of GitHub. After code review one of the maintainers will merge or
close the ``Pull request``.

NOTE: All changes to files, that are used for release's (CHANGES.rst, 
CONTRIBUTORS and others), are managed by maintainers, so pls don't modify those.



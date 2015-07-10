.. _glossarry:

Glossary
========

.. glossary::
   :sorted:

   environment

      The folder layout containing :term:`revision` files, configuration and
      revision template.

   revision

      Each migration file is called a ``revision``. They contain ID's, that
      will be saved to database. They are atomic parts of the migration
      procedure, in other words you can not migrate part of a revision.

   migration

      :term:`revision` consists of migrations. You can define only 1 migration
      per index per :term:`revision`.

   lazy migration

      type of :term:`migration`, that can be defined using declerative API.
      This can allow ``elasticine`` to optimize some operations and minimize
      reindexing steps during migrations of several revisions.

   manual migration

      type of :term:`migration`, that is written as separate downgrade and
      upgrade functions, which can run arbitrary code. ``elasticine`` will not
      optimize anything. You can not mix term:`lazy migration` with manual
      ones.

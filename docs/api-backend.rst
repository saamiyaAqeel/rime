RIME backend API
================

If you're interested on fixing bugs in RIME, extending existing Providers, or adding new ones, you should be familiar
with the backend API.

.. figure:: rime\ architecture.png

   RIME architecture

RIME is designed to be accessed via GraphQL queries, but it is kept separate from the web server frontend. This approach
allows for more flexibility with usage. For example, it allows RIME to be used as a library as part of other projects.

The above Figure describes the basic architecture:

* Server: Provides the HTTP interface to the GraphQL backend. It uses the Flask framework.
* Rime state: The main ``Rime`` object retains information about known devices, and provides a list of ``Provider`` objects
  for each device. 
* GraphQL: This provides the GraphQL query interface, using the ``ariadne`` library. All graphql-specific code is
  contained in the ``graphql`` module.
* Providers: These provide access to information from specific applications on the device dump.
* Filesystems: Provides access to the device dump filesystem. Device filesystems are kept abstracted so that providers
  don't need to know the details of the dump format. For example, the files in iOS device dumps are named as a hash
  of their contents, and the true filename is kept in an SQLite database at the root of the filesystem; the
  IosDeviceFilesystem class handles the translation transparently.

State
-----

.. automodule:: rime.rime
   :members:
   :undoc-members:
   :show-inheritance:

GraphQL
-------

Providers
---------

.. automodule:: rime.providers.provider
   :members:
   :undoc-members:
   :show-inheritance:

Filesystem access
-----------------

.. automodule:: rime.filesystem
   :members:
   :undoc-members:
   :show-inheritance:

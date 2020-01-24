=======================================
Pathlab makes it easy to extend Pathlib
=======================================

*Pathlib* is a built-in Python module that provides object-oriented access to
filesystem paths.

*Pathlab* is a small Python module that helps you extend pathlib for other
kinds of path, such as:

- Archives and disk images. The ``examples/`` directory contains an
  implementation for ``.zip`` archives.
- Network filesystem protocols like FTP, NFS and WebDAV.
- Any other place where the ``pathlib.Path`` interface makes sense.

Installation
------------

Requires Python 3.6+

Use pip::

    pip install --user pathlab

Usage
-----

Subclass ``pathlab.Path`` and ``pathlab.Accessor``. A skeleton implementation
might look like this::

    import pathlab

    class ZipPath(pathlab.Path):
        pass

    class ZipAccessor(pathlab.Accessor):
        path_base = ZipPath

To implement basic support for zip files, first add a ``ZipAccessor``
initializer that records or creates a ``zipfile.ZipFile`` object. Next,
implement accessor methods like ``listdir()`` and ``stat()``. See the
``pathlab.py`` source code for a full list of methods and the ``examples/``
directory for samples. All of these methods are optional, so you can implement
support for your chosen format/protocol piecemeal.

To use the ``ZipPath`` class (defined above), access it as an attribute of an
``ZipAccessor`` instance. For example::

    documents = ZipAccessor("/home/me/project.zip")

    readme = documents.ZipPath("/README.txt")
    print(readme.read_text())

The is similar to how you might work with files on disk::

    import pathlib

    readme = pathlib.Path("/home/me/project/README.txt")
    print(readme.read_text())

To extend the pathlib API, add new methods in your ``ZipPath`` equivalent.
These should call appropriate methods on the accessor.


Implementation Notes
--------------------

The only "magic" part of this library is that each accessor *object* creates a
path *type* with the accessor object as a class attribute. It's worth noting
the multiple levels of inheritance of the ``readme`` object in the above
example:

1. ``pathlib.PurePath`` provides methods that do not require filesystem access
2. ``pathlib.Path`` provides methods that use an accessor object to access the
   filesystem.
3. ``pathlab.Path`` fixes instances where ``pathlib.Path`` doesn't use its
   accessor. This class cannot be instantiated directly.
4. ``pathlab.examples.zippath.ZipPath`` does nothing, but could provide
   additional methods. This class cannot be instantiated directly.
5. ``documents.ZipPath`` is a type which binds a specific accessor instance -
   ``documents`` in this case. This class *can* be instantiated directly.

The standard library's ``pathlib`` mostly delegates to an accessor object -
``pathlib._normal_accessor`` - but uses OS functionality directly in a few
cases; these include use of the ``pwd``, ``grp`` and ``os`` modules. Pathlab
re-implements problematic methods in a ``Path`` subclass, and adds methods to
the ``Accessor`` subclass where needed.

Pathlab does not attempt to bridge between different kinds of ``Path`` object.
Mixed types may result in headaches.

API Reference
=============

.. module:: pathlab

Tar Accessor
------------

.. autoclass:: TarAccessor

Zip Accessor
------------

.. autoclass:: ZipAccessor

ISO Accessor
------------

.. autoclass:: IsoAccessor

Artifactory Accessor
--------------------

.. autoclass:: RtAccessor

Accessor
--------

This table shows all abstract methods that you may wish to implement in your
own :class:`Accessor` subclass, along with their stdlib equivalents.

.. table::

    ============================  ====================  =======================================================
    Abstract Method               Equivalent            Description
    ============================  ====================  =======================================================
    :meth:`~Accessor.open`        :func:`io.open`       Open path and return a file object.
    :meth:`~Accessor.stat`        :func:`os.stat`       Return the a :class:`Stat` object for the path.
    :meth:`~Accessor.listdir`     :func:`os.listdir`    Return a list of names of directory children
    :meth:`~Accessor.readlink`    :func:`os.readlink`   Return the target of the this symbolic link
    :meth:`~Accessor.touch`                             Create the file, if it doesn't exist
    :meth:`~Accessor.mkdir`       :func:`os.mkdir`      Create the directory, if it doesn't exist
    :meth:`~Accessor.symlink`     :func:`os.symlink`    Create a symbolic link
    :meth:`~Accessor.link`        :func:`os.link`       Create a hard link
    :meth:`~Accessor.unlink`      :func:`os.unlink`     Delete the file or link
    :meth:`~Accessor.rmdir`       :func:`os.rmdir`      Delete the directory (must be empty)
    :meth:`~Accessor.rename`      :func:`os.rename`     Move/rename path
    :meth:`~Accessor.replace`     :func:`os.replace`    Move/rename path, clobbering existing files
    :meth:`~Accessor.chmod`       :func:`os.chmod`      Change permissions
    :meth:`~Accessor.fsencode`    :func:`os.fsencode`   Encode filename to filesystem encoding
    :meth:`~Accessor.fspath`                            Return a *local* path for this path
    :meth:`~Accessor.download`                          Download to the *local* filesystem
    :meth:`~Accessor.upload`                            Upload from the *local* filesystem
    :meth:`~Accessor.getcwd`      :func:`os.getcwd`     Return the working directory.
    :meth:`~Accessor.gethomedir`                        Return the user's home directory.
    ============================  ====================  =======================================================

.. autoclass:: Accessor
    :members:
    :exclude-members: lstat, lchmod, scandir

Path
----

This table shows all methods and attributes available from :class:`Path`
instances. You should not need to re-implement any of these methods.
Methods marked as pure will work even without an accessor; other methods will
call at least one method of the accessor.

.. seealso::

    See the :mod:`pathlib` documentation for more detail!


.. table::
    :widths: 10 50 40 10

    ====  =====================================  =========================================  ==========================
    Pure  Method                                 Description                                Returns
    ====  =====================================  =========================================  ==========================
    ✓     :data:`~pathlib.PurePath.parts`        Path components                            ``str`` sequence
    ✓     :data:`~pathlib.PurePath.drive`        Drive letter, if any                       ``str``
    ✓     :data:`~pathlib.PurePath.root`         Root, e.g. ``/``                           ``str``
    ✓     :data:`~pathlib.PurePath.anchor`       Drive letter and root                      ``str``
    ✓     :data:`~pathlib.PurePath.name`         Final path component                       ``str``
    ✓     :data:`~pathlib.PurePath.stem`         Final path component without its suffix    ``str``
    ✓     :data:`~pathlib.PurePath.suffix`       File extension of final path component     ``str``
    ✓     :data:`~pathlib.PurePath.suffixes`     File extensions of final path component    ``str`` sequence
    ✓     :meth:`~pathlib.PurePath.as_posix`     With forward slashes                       ``str``
    ✓     :meth:`~pathlib.PurePath.as_uri`       With ``file://`` prefix                    ``str``
    ..    :meth:`~pathlib.Path.owner`            Name of file owner                         ``str``
    ..    :meth:`~pathlib.Path.group`            Name of file group                         ``str``
    ..    :meth:`~pathlib.Path.stat`             Status of file (follow symlinks)           :class:`~Stat`
    ..    :meth:`~pathlib.Path.lstat`            Status of symlink                          :class:`~Stat`
    ..    :meth:`~pathlib.Path.samefile`         Paths are equivalent                       ``bool``
    ..    :meth:`~pathlab.Path.sameaccessor`     Paths use the same accessor                ``bool``
    ..    :meth:`~pathlib.Path.exists`           Path exists                                ``bool``
    ..    :meth:`~pathlib.Path.is_dir`           Path is a directory                        ``bool``
    ..    :meth:`~pathlib.Path.is_file`          Path is a regular file                     ``bool``
    ..    :meth:`~pathlib.Path.is_mount`         Path is a mount point                      ``bool``
    ..    :meth:`~pathlib.Path.is_symlink`       Path is a symlink                          ``bool``
    ..    :meth:`~pathlib.Path.is_block_device`  Path is a block device                     ``bool``
    ..    :meth:`~pathlib.Path.is_char_device`   Path is a character device                 ``bool``
    ..    :meth:`~pathlib.Path.is_fifo`          Path is a FIFO                             ``bool``
    ..    :meth:`~pathlib.Path.is_socket`        Path is a socket                           ``bool``
    ✓     :meth:`~pathlib.PurePath.is_absolute`  Path is absolute                           ``bool``
    ✓     :meth:`~pathlib.PurePath.is_reserved`  Path is reserved                           ``bool``
    ✓     :meth:`~pathlib.PurePath.match`        Path matches a glob pattern                ``bool``
    ✓     :meth:`~pathlib.PurePath.joinpath`     Append path components                     :class:`~Path`
    ✓     :data:`~pathlib.PurePath.parent`       Immediate ancestor                         :class:`~Path`
    ✓     :data:`~pathlib.PurePath.parents`      Ancestors                                  :class:`~Path` sequence
    ..    :meth:`~pathlib.Path.iterdir`          Files in directory                         :class:`~Path` sequence
    ..    :meth:`~pathlib.Path.glob`             Files in subtree matching pattern          :class:`~Path` sequence
    ..    :meth:`~pathlib.Path.rglob`            As above, but includes directories         :class:`~Path` sequence
    ✓     :meth:`~pathlib.PurePath.relative_to`  Make relative                              :class:`~Path`
    ✓     :meth:`~pathlib.PurePath.with_name`    Change name                                :class:`~Path`
    ✓     :meth:`~pathlib.PurePath.with_suffix`  Change suffix                              :class:`~Path`
    ..    :meth:`~pathlib.Path.resolve`          Resolve symlinks and make absolute         :class:`~Path`
    ..    :meth:`~pathlib.Path.expanduser`       Expand ``~`` and ``~user``                 :class:`~Path`
    ..    :meth:`~pathlib.Path.touch`            Create file
    ..    :meth:`~pathlib.Path.mkdir`            Create directory
    ..    :meth:`~pathlib.Path.symlink_to`       Create symlink
    ..    :meth:`~pathlib.Path.unlink`           Delete file or link
    ..    :meth:`~pathlib.Path.rmdir`            Delete directory
    ..    :meth:`~pathlib.Path.rename`           Move without clobbering
    ..    :meth:`~pathlib.Path.replace`          Move
    ..    :meth:`~pathlib.Path.chmod`            Change perms of file (follow symlinks)
    ..    :meth:`~pathlib.Path.lchmod`           Change perms of symlink0
    ..    :meth:`~pathlib.Path.open`             Open file and return file object           ``fileobj``
    ..    :meth:`~pathlib.Path.read_bytes`       Read file content as bytes                 ``bytes``
    ..    :meth:`~pathlib.Path.read_text`        Read file content as text                  ``str``
    ..    :meth:`~pathlib.Path.write_bytes`      Write file content as bytes
    ..    :meth:`~pathlib.Path.write_text`       Write file content as text
    ..    :meth:`~pathlab.Path.upload_from`      Upload from *local* filesystem
    ..    :meth:`~pathlab.Path.download_to`      Download to *local* filesystem
    ====  =====================================  =========================================  ==========================

.. autoclass:: Path
    :show-inheritance:
    :members: sameaccessor, upload_from, download_to, absolute

    Only *additional* methods are documented here; see the :mod:`pathlib`
    documentation for other methods.


Stat
----

.. autoclass:: Stat
    :members:


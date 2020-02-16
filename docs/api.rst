API Reference
=============

.. module:: pathlab

Concrete Accessors
------------------

.. autoclass:: TarAccessor
.. autoclass:: ZipAccessor
.. autoclass:: IsoAccessor
.. autoclass:: RtAccessor

Abstract Accessor
-----------------

.. autoclass:: Accessor
    :members:

    This table shows all abstract methods that should be implemented
    in your own :class:`Accessor` subclass.

    .. table::

        ============================  ==============================================
        Abstract Method               Description
        ============================  ==============================================
        :meth:`~Accessor.open`        Open path and return a file object
        :meth:`~Accessor.stat`        Return the a :class:`Stat` object for the path
        :meth:`~Accessor.listdir`     Yield names of directory children
        :meth:`~Accessor.readlink`    Return the target of the this symbolic link
        :meth:`~Accessor.create`      Create the file, if it doesn't exist
        :meth:`~Accessor.chmod`       Change file permissions
        :meth:`~Accessor.move`        Move/rename the file
        :meth:`~Accessor.delete`      Delete the file
        :meth:`~Accessor.download`    Download to the *local* filesystem
        :meth:`~Accessor.upload`      Upload from the *local* filesystem
        :meth:`~Accessor.fspath`      Return a *local* path for this path
        :meth:`~Accessor.getcwd`      Return the working directory
        :meth:`~Accessor.gethomedir`  Return the user's home directory
        :meth:`~Accessor.close`       Close this accessor object
        ============================  ==============================================

    This table shows utility methods you may call from your methods to raise
    an exception:

    .. table::

        ===================================  =========================  ======================
        Method                               Raises                     Errno
        ===================================  =========================  ======================
        :meth:`~Accessor.not_found`          :exc:`FileNotFoundError`   :data:`~errno.ENOENT`
        :meth:`~Accessor.already_exists`     :exc:`FileExistsError`     :data:`~errno.EEXIST`
        :meth:`~Accessor.not_a_directory`    :exc:`NotADirectoryError`  :data:`~errno.ENOTDIR`
        :meth:`~Accessor.is_a_directory`     :exc:`IsADirectoryError`   :data:`~errno.EISDIR`
        :meth:`~Accessor.not_a_symlink`      :exc:`OSError`             :data:`~errno.EINVAL`
        :meth:`~Accessor.permission_denied`  :exc:`PermissionError`     :data:`~errno.EACCES`
        ===================================  =========================  ======================

    This table shows all methods with default implementations that you may
    wish to re-implement:

    .. table::

        ======================================  ==========================  ========================
        Method                                  Uses                        Like
        ======================================  ==========================  ========================
        :meth:`~Accessor.splitroot`
        :meth:`~Accessor.casefold`
        :meth:`~Accessor.casefold_parts`
        :meth:`~Accessor.is_reserved`
        :meth:`~Accessor.make_uri`
        :meth:`~Accessor.resolve`               :meth:`~Accessor.readlink`  :func:`os.path.abspath`
        :meth:`~Accessor.scandir`               :meth:`~Accessor.listdir`   :func:`os.scandir`
        :meth:`~Accessor.touch`                 :meth:`~Accessor.create`
        :meth:`~Accessor.mkdir`                 :meth:`~Accessor.create`    :func:`os.mkdir`
        :meth:`~Accessor.symlink`               :meth:`~Accessor.create`    :func:`os.symlink`
        :meth:`~Accessor.unlink`                :meth:`~Accessor.delete`    :func:`os.unlink`
        :meth:`~Accessor.rmdir`                 :meth:`~Accessor.delete`    :func:`os.rmdir`
        :meth:`~Accessor.rename`                :meth:`~Accessor.move`      :func:`os.rename`
        :meth:`~Accessor.replace`               :meth:`~Accessor.move`      :func:`os.replace`
        :meth:`~Accessor.lstat`                 :meth:`~Accessor.stat`      :func:`os.lstat`
        :meth:`~Accessor.lchmod`                :meth:`~Accessor.chmod`     :func:`os.lchmod`
        :meth:`~Accessor.__enter__`
        :meth:`~Accessor.__exit__`              :meth:`~Accessor.close`
        ======================================  ==========================  ========================

Path
----

.. autoclass:: Path
    :show-inheritance:
    :members: sameaccessor, upload_from, download_to

    This table shows all methods and attributes available from :class:`Path`
    instances. You should not need to re-implement any of these methods.
    Methods marked as pure will work even without an accessor; other methods
    will call at least one method of the accessor.

    .. table::
        :widths: 10 50 40 10

        ====  =====================================  =========================================  =======================
        Pure  Method                                 Description                                Returns
        ====  =====================================  =========================================  =======================
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
        ====  =====================================  =========================================  =======================

    Only *additional* methods are documented here; see the :mod:`pathlib`
    documentation for other methods.


Stat
----

.. autoclass:: Stat
    :members:

Creator
-------

.. autoclass:: Creator

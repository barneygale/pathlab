import errno
import pathlib


class Path(pathlib.Path):
    """
    This class provides bugfixes for places where ``pathlib.Pathlib()`` hits
    the (file)system directly without using the accessor.
    """

    _flavour = pathlib._posix_flavour

    def sameaccessor(self, other_path):
        """
        Returns whether this path uses the same accessor as *other_path*.
        """
        return self._accessor is getattr(other_path, '_accessor', None)

    def upload(self, source):
        """
        Upload/add to this path from the given *local* filesystem path.
        """
        self._accessor.upload(source, self)

    def download(self, target):
        """
        Download/extract this path to the given *local* filesystem path.
        """
        self._accessor.download(self, target)

    # Avoid ``str(self)``; delegate to accessor.
    def __fspath__(self):
        return self._accessor.fspath(self)

    # Add compatibility with ``os.DirEntry()``
    @property
    def path(self):
        return str(self)

    # Avoid Windows/Linux magic and direct instantiation
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._accessor, Accessor):
            raise TypeError("pathlab.Path cannot be instantiated directly")
        return cls._from_parts(args)

    # Avoid accessor changes
    def _init(self, template=None):
        self._closed = False

    # Avoid ``import pwd`` etc
    def owner(self):
        return self._accessor.owner(self)

    # Avoid ``import grp`` etc
    def group(self):
        return self._accessor.group(self)

    # Avoid file descriptors
    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        if self._closed:
            self._raise_closed()
        return self._accessor.open(
            self, mode, buffering, encoding, errors, newline)

    # Avoid file descriptors
    def touch(self, mode=0o666, exist_ok=True):
        if self._closed:
            self._raise_closed()
        self._accessor.touch(self, mode, exist_ok)

    # Avoid ``os.getcwd()``
    @classmethod
    def cwd(cls):
        return cls(cls._accessor.getcwd())

    # Avoid ``os.getcwd()``
    def absolute(self):
        if self._closed:
            self._raise_closed()
        if self.is_absolute():
            return self
        parts = [self._accessor.getcwd()] + self._parts
        obj = self._from_parts(parts, init=False)
        obj._init(template=self)
        return obj

    # Avoid ``os.getcwd()``; shift responsibility from flavour to accessor.
    def resolve(self):
        if self._closed:
            self._raise_closed()
        s = self._accessor.resolve(self)
        s = self._flavour.pathmod.normpath(s)
        obj = self._from_parts((s,), init=False)
        obj._init(template=self)
        return obj

    # Avoid ``os.fsencode()``
    def __bytes__(self):
        return self._accessor.fsencode(self)


class Accessor(pathlib._Accessor):
    """
    An accessor object provides means for instances of an associated ``Path``
    type to access some kind of filesystem. Most accessor methods have
    equivalent functions in the ``os`` module.

    Subclasses are free to define an initializer and store state, such as a
    socket object or file descriptor. Methods such as ``listdir()`` may then
    reference that state.

    To create a path object, access it as an attribute of an accessor::

        arc = ZipAccessor(zipfile.ZipFile("/foo/bar/project.zip"))
        root = arc.ZipPath("/")
        readme = root / "README.txt"
        print(readme.read_text())
    """

    # Path type factory -------------------------------------------------------

    #: The base type of the instance-specific path type
    path_base = Path

    def __new__(cls, *args, **kwargs):
        """
        Instantiate an accessor object and assign a ``pathlab.Path`` subclass
        as an attribute.
        """
        if not issubclass(cls.path_base, Path):
            raise TypeError("path_base must subclass pathlab.Path")
        self = super(Accessor, cls).__new__(cls)
        name = cls.path_base.__name__
        setattr(self, name, type(name, (cls.path_base,), {'_accessor': self}))
        return self

    # Utilities ---------------------------------------------------------------

    def not_found(self, path):
        """
        Return a ``FileNotFoundError`` for the given path. Utility method.
        """
        return FileNotFoundError(
            errno.ENOENT, "No such file or directory: %r.%r" % (self, path))

    def not_a_dir(self, path):
        """
        Return a ``NotADirectoryError`` for the given path. Utility method.
        """
        return NotADirectoryError(
            errno.ENOTDIR, "Not a directory: %r.%r" % (self, path))

    # Basics ------------------------------------------------------------------

    def open(self, path, mode='r', buffering=-1, encoding=None, errors=None,
             newline=None):
        """
        Open the path and return a file object, as the built-in ``open()``
        function does.

        Note: the signature of this method differs from the pathlib accessor
        method of the same name.
        """
        raise NotImplementedError

    def stat(self, path):
        """
        Return the result of the ``stat()`` system call on the path, like
        ``os.stat()`` does.
        """
        raise NotImplementedError

    def listdir(self, path):
        """
        Return a list containing the names of the files in the directory. The
        list is in arbitrary order.  It does not include the special entries
        '.' and '..'.
        """
        raise NotImplementedError

    def scandir(self, path):
        """
        A generator that yields the ``Path`` objects for files in the
        directory. The results are in arbitrary order. They do not include the
        special entries '.' and '..'.
        """
        raise NotImplementedError

    # Ownership and permissions -----------------------------------------------

    def owner(self, path):
        """
        Return the login name of the file owner.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    def group(self, path):
        """
        Return the group name of the file gid.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    def chmod(self, path, mode):
        """
        Change the permissions of the path, like os.chmod().
        """
        raise NotImplementedError

    # Create, move and delete -------------------------------------------------

    def touch(self, path, mode=0o666, exist_ok=True):
        """
        Create the file with the given access mode, if it doesn't exist.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    def mkdir(self, path, mode=0o777):
        """
        Create the directory with the given access mode, if it doesn't exist.
        Like ``os.mkdir()``
        """
        raise NotImplementedError

    def unlink(self, path):
        """
        Remove the file or link, like ``os.unlink()``.
        """
        raise NotImplementedError

    def rmdir(self, path):
        """
        Remove the directory, like ``os.rmdir()``. The directory must be empty.
        """
        raise NotImplementedError

    def rename(self, src, dst):
        """
        Rename *src* to *dst*, like ``os.rename()``.
        """
        raise NotImplementedError

    def replace(self, src, dst):
        """
        Rename *src* to *dst*, clobbering the existing destination if it
        exists. Like ``os.replace()``
        """
        raise NotImplementedError

    # Pathlab specialities ----------------------------------------------------

    def upload(self, src, dst):
        """
        Upload from *src* to *dst*. Only the destination is guaranteed to be
        an instance of your path class.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    def download(self, src, dst):
        """
        Download from *src* to *dst*. Only the source is guaranteed to be an
        instance of your path class.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    def fspath(self, path):
        """
        Return a string/bytes object representing the given path as a *local*
        filesystem path.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    # Links -------------------------------------------------------------------

    def link(self, src, dst):
        """
        Create a hard link pointing to *src* named *dst*, like ``os.link()``.
        """
        raise NotImplementedError

    def symlink(self, src, dst, target_is_directory=False):
        """
        Create a symbolic link pointing to *src* named *dst*, like
        ``os.symlink()``.
        """
        raise NotImplementedError

    def resolve(self, path):
        """
        Make the path absolute, resolving all symlinks on the way and also
        normalizing it (for example turning slashes into backslashes under
        Windows).

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    def lstat(self, path):
        """
        Like ``stat()``, except if the path points to a symlink, the symlink's
        status information is returned, rather than its target's.
        """
        raise NotImplementedError

    def lchmod(self, path, mode):
        """
        Like ``chmod()``, except if the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.
        """
        raise NotImplementedError

    # Misc --------------------------------------------------------------------

    def utime(self, path, times=None):
        """
        Set the access and modified time of path, like ``os.utime()``.
        """
        raise NotImplementedError

    def getcwd(self):
        """
        Return the current working directory like ``os.getcwd()``.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError

    def fsencode(self, path):
        """
        Encode filename to the filesystem encoding, like ``os.fsencode()``.

        Note: this method is an addition to the pathlib accessor class.
        """
        raise NotImplementedError


class StatResult(object):
    """
    An alternative to ``os.stat_result``. Objects of this type may be returned
    from ``Accessor.stat()``.
    """

    #: File mode (type + permissions).
    st_mode = 0

    #: Uniquely identifies the file for the given value of ``st_dev``.
    st_ino = 0

    #: Identifier for the device on which this file resides.
    st_dev = 0

    #: Number of hard links.
    st_nlink = 0

    #: User ID of the file owner
    st_uid = 0

    #: Group ID of the file owner
    st_gid = 0

    #: File size in bytes
    st_size = 0

    #: Timestamp of most recent access
    st_atime = 0

    #: Timestamp of most recent content modification
    st_mtime = 0

    #: Timestamp of file creation or most recent metadata modification,
    st_ctime = 0

    def __repr__(self):
        name = self.__class__.__name__
        fields = ", ".join("%s=%r" % pair for pair in vars(self).items())
        return "%s(%s)" % (name, fields)

import errno
import pathlib


class Accessor(pathlib._Accessor):
    """
    An accessor object provides means for instances of an associated
    :class:`Path` type to access some kind of filesystem. Most accessor methods
    have equivalent functions in the :mod:`os` module.

    Subclasses are free to define an initializer and store state, such as a
    socket object or file descriptor. Methods such as :meth:`listdir` may then
    reference that state.

    To create a path object, access its type as an attribute of an accessor
    object.
    """

    # Path type factory -------------------------------------------------------

    #: Must be set to a subclass of :class:`pathlab.Path`
    factory = None

    def __new__(cls, *args, **kwargs):
        """
        Instantiate an accessor object and assign a :class:`pathlab.Path`
        subclass as an attribute.
        """

        if not cls.factory:
            raise TypeError("factory must subclass pathlab.Path")
        self = super(Accessor, cls).__new__(cls)
        name = cls.factory.__name__
        self.factory = type(name, (cls.factory,), {"_accessor": self})
        setattr(self, name, self.factory)
        return self

    # Utilities ---------------------------------------------------------------

    @staticmethod
    def not_found(path):
        """
        Raise a :exc:`FileNotFoundError`
        """
        raise FileNotFoundError(errno.ENOENT, "Not found", path)

    @staticmethod
    def already_exists(path):
        """
        Raise a :exc:`FileExistsError`
        """
        raise FileExistsError(errno.EEXIST, "Already exists", path)

    @staticmethod
    def not_a_directory(path):
        """
        Raise a :exc:`NotADirectoryError`
        """
        raise NotADirectoryError(errno.ENOTDIR, "Not a directory", path)

    @staticmethod
    def is_a_directory(path):
        """
        Raise an :exc:`IsADirectoryError`
        """
        raise IsADirectoryError(errno.EISDIR, "Is a directory", path)

    @staticmethod
    def permission_denied(path):
        """
        Raise a :exc:`PermissionError`
        """
        raise PermissionError(errno.EACCES, "Permission denied", path)

    # Open method -------------------------------------------------------------

    def open(self, path, mode="r", buffering=-1):
        """
        Open the path and return a file object, like :func:`io.open`.

        The underlying stream *must* be opened in binary mode (not text mode).
        The file mode is as in :func:`io.open`, except that it will not contain
        any of 'b', 't' or 'U'.
        """
        raise NotImplementedError

    # Read methods ------------------------------------------------------------

    def stat(self, path, *, follow_symlinks=True):
        """
        Return a :class:`Stat` object for the path, like :func:`os.stat`.
        """
        raise NotImplementedError

    def listdir(self, path):
        """
        Return a list containing the names of the files in the directory, like
        :func:`os.listdir`.
        """
        raise NotImplementedError

    def readlink(self, path):
        """
        Return a string representing the path to which the symbolic link
        points, like :func:`os.readlink`
        """
        raise NotImplementedError

    # Create methods ----------------------------------------------------------

    def touch(self, path, mode=0o666, exist_ok=True):
        """
        Create the file with the given access mode, if it doesn't exist.
        """
        raise NotImplementedError

    def mkdir(self, path, mode=0o777):
        """
        Create the directory with the given access mode, if it doesn't exist.
        Like :func:`os.mkdir`
        """
        raise NotImplementedError

    def symlink(self, src, dst, target_is_directory=False):
        """
        Create a symbolic link pointing to *src* named *dst*, like
        :func:`os.symlink`.
        """
        raise NotImplementedError

    def link(self, src, dst):
        """
        Create a hard link pointing to *src* named *dst*, like :func:`os.link`.
        """
        raise NotImplementedError

    # Delete methods ----------------------------------------------------------

    def unlink(self, path):
        """
        Remove the file or link, like :func:`os.unlink`.
        """
        raise NotImplementedError

    def rmdir(self, path):
        """
        Remove the directory, like :func:`os.rmdir`. The directory must be empty.
        """
        raise NotImplementedError

    # Move/copy/rename methods ------------------------------------------------

    def rename(self, src, dst):
        """
        Rename *src* to *dst*, like :func:`os.rename`.
        """
        raise NotImplementedError

    def replace(self, src, dst):
        """
        Rename *src* to *dst*, clobbering the existing destination if it
        exists. Like :func:`os.replace`
        """
        raise NotImplementedError

    # Permission methods ------------------------------------------------------

    def chmod(self, path, mode, *, follow_symlinks=True):
        """
        Change the permissions of the path, like :func:`os.chmod`.
        """
        raise NotImplementedError

    # Miscellaneous methods ---------------------------------------------------

    def fsencode(self, path):
        """
        Encode filename to the filesystem encoding, like :func:`os.fsencode`.
        """
        raise NotImplementedError

    def fspath(self, path):
        """
        Return an string representing the given path as a *local* filesystem
        path. The path need not exist.
        """
        raise NotImplementedError

    # Interaction with the *local* filesystem ---------------------------------

    def download(self, src, dst):
        """
        Download from *src* to *dst*. Only the source is guaranteed to be an
        instance of your path class.
        """
        raise NotImplementedError

    def upload(self, src, dst):
        """
        Upload from *src* to *dst*. Only the destination is guaranteed to be
        an instance of your path class.
        """
        raise NotImplementedError

    # Context -----------------------------------------------------------------

    def getcwd(self):
        """
        Return the current working directory, like :func:`os.getcwd`.
        """
        raise NotImplementedError


    def gethomedir(self, username=None):
        """
        Return the user's home directory.
        """
        raise NotImplementedError

    # Redirects ---------------------------------------------------------------

    def scandir(self, path):
        for name in self.listdir(path):
            yield self.factory(path, name)

    def lstat(self, path):
        return self.stat(path, follow_symlinks=False)

    def lchmod(self, path, mode):
        return self.chmod(path, mode, follow_symlinks=False)


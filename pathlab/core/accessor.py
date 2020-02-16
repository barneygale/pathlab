import errno
import pathlib

from pathlab.core.stat import Stat


class Accessor(pathlib._Accessor, pathlib._PosixFlavour):
    """
    An accessor object allows instances of an associated :class:`Path` type
    to access some kind of filesystem.

    Subclasses are free to define an initializer and store state, such as a
    socket object or file descriptor. Methods such as :meth:`listdir` may then
    reference that state.

    To create a path object, access its type as an attribute of an accessor
    object.
    """

    # Path factory ------------------------------------------------------------

    #: Must be set to a subclass of :class:`pathlab.Path`
    factory = None

    def __new__(cls, *args, **kwargs):
        if not cls.factory:
            raise TypeError("factory must subclass pathlab.Path")
        self = super(Accessor, cls).__new__(cls)
        name = cls.factory.__name__
        self.factory = type(name, (cls.factory,), {
            "_accessor": self,
            "_flavour": self})
        setattr(self, name, self.factory)
        return self

    # Open method -------------------------------------------------------------

    def open(self, path, mode="r", buffering=-1):
        """
        Open the path and return a file object, like :func:`io.open`.

        The underlying stream *must* be opened in binary mode (not text mode).
        The file mode is as in :func:`io.open`, except that it will not contain
        any of ``b``, ``t`` or ``U``.

        In ``w`` mode, you may wish to return a :class:`Creator` object.
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
        Yield names of the files in the directory, a bit like
        :func:`os.listdir`.
        """
        raise NotImplementedError

    def readlink(self, path):
        """
        Return a string representing the path to which the symbolic link
        points, like :func:`os.readlink`
        """
        raise NotImplementedError

    # Create/edit/delete methods ----------------------------------------------

    def create(self, path, stat, fileobj=None):
        """
        Create the file. The given :class:`Stat` object provides file metadata,
        and the *fileobj*, where given, provides a readable stream of the new
        file's content.
        """
        raise NotImplementedError

    def chmod(self, path, mode, *, follow_symlinks=True):
        """
        Change the permissions of the path.
        """
        raise NotImplementedError

    def move(self, path, dest):
        """
        Move/rename the file.
        """
        raise NotImplementedError

    def delete(self, path):
        """
        Remove the file.
        """
        raise NotImplementedError

    # Interaction with the *local* filesystem ---------------------------------

    def fspath(self, path):
        """
        Return an string representing the given path as a *local* filesystem
        path. The path need not exist.
        """
        raise NotImplementedError

    def download(self, src, dst):
        """
        Download from *src* to *dst*. *src* is an instance of your path class.
        """
        raise NotImplementedError

    def upload(self, src, dst):
        """
        Upload from *src* to *dst*. *dst* is an instance of your path class.
        """
        raise NotImplementedError

    # Context methods ---------------------------------------------------------

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

    # Close method ------------------------------------------------------------

    def close(self):
        """
        Close this accessor object.
        """
        pass  # FIXME: or NotImplementedError?

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
        Raise a :exc:`FileExistsError` with :data:`~errno.EEXIST`
        """
        raise FileExistsError(errno.EEXIST, "Already exists", path)

    @staticmethod
    def not_a_directory(path):
        """
        Raise a :exc:`NotADirectoryError` with :data:`~errno.ENOTDIR`
        """
        raise NotADirectoryError(errno.ENOTDIR, "Not a directory", path)

    @staticmethod
    def is_a_directory(path):
        """
        Raise an :exc:`IsADirectoryError` with :data:`~errno.EISDIR`
        """
        raise IsADirectoryError(errno.EISDIR, "Is a directory", path)

    @staticmethod
    def not_a_symlink(path):
        """
        Raise an :exc:`OSError` with :data:`~errno.EINVAL`
        """
        raise OSError(errno.EINVAL, "Invalid argument", path)

    @staticmethod
    def permission_denied(path):
        """
        Raise a :exc:`PermissionError` with :data:`~errno.EACCES`
        """
        raise PermissionError(errno.EACCES, "Permission denied", path)

    # Accessor redirects ------------------------------------------------------

    encoding = 'utf-8'

    def scandir(self, path):
        for name in self.listdir(path):
            yield self.factory(path, name)

    def touch(self, path, mode=0o666, exist_ok=True):
        if path.exists():
            if exist_ok:
                return
            return self.already_exists(path)
        elif not path.parent.exists():
            return self.not_found(path.parent)
        return self.create(path, Stat(permissions=mode))

    def mkdir(self, path, mode=0o777):
        if path.exists():
            return self.already_exists(path)
        elif not path.parent.exists():
            return self.not_found(path.parent)
        return self.create(path, Stat(type='dir', permissions=mode))

    def symlink(self, target, path, target_is_directory=False):
        if path.exists():
            return self.already_exists(path)
        elif not path.parent.exists():
            return self.not_found(path.parent)
        target = self.factory(target)
        return self.create(path, Stat(type='symlink', target=target))

    def unlink(self, path):
        return self.delete(path)

    def rmdir(self, path):
        return self.delete(path)

    def rename(self, path, dest):
        dest = self.factory(dest)
        if dest.exists():
            return self.already_exists(dest)
        return self.move(path, dest)

    def replace(self, path, dest):
        return self.move(path, self.factory(dest))

    def lstat(self, path):
        return self.stat(path, follow_symlinks=False)

    def lchmod(self, path, mode):
        return self.chmod(path, mode, follow_symlinks=False)

    # Flavour redirects -------------------------------------------------------

    is_supported = True

    def resolve(self, path, strict=False):
        return super(Accessor, self).resolve(path.absolute(), strict)

    def join(self, parts):
        return self.sep.join(parts)

    # Context manager redirects -----------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
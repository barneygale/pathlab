import contextlib
import io
import pathlib



class Path(pathlib.Path):
    """
    Path-like object.
    """

    __slots__ = ()
    _flavour = pathlib._posix_flavour
    _accessor = None

    # Additional methods ------------------------------------------------------

    def sameaccessor(self, other_path):
        """
        Returns whether this path uses the same accessor as *other_path*.
        """
        return self._accessor == getattr(other_path, "_accessor", None)

    def upload_from(self, source):
        """
        Upload/add to this path from the given *local* filesystem path.
        """
        return self._accessor.upload(source, self)

    def download_to(self, target):
        """
        Download/extract this path to the given *local* filesystem path.
        """
        return self._accessor.download(self, target)

    @property
    def path(self):
        """
        The path as a string, like ``str(path)``. Principally exists for
        compatibility with :class:`os.DirEntry`.
        """
        return str(self)

    # Bugfixes and hacks ------------------------------------------------------

    # Avoid ``os.getcwd()``
    @classmethod
    def cwd(cls):
        return cls(cls._accessor.getcwd())

    # Avoid ``os.environ`` etc.
    @classmethod
    def home(cls):
        return cls(cls._accessor.gethomedir(None))

    # Avoid Windows/Linux magic and direct instantiation
    def __new__(cls, *args, **kwargs):
        from pathlab.core.accessor import Accessor
        if not isinstance(cls._accessor, Accessor):
            raise TypeError("pathlab.Path cannot be instantiated directly")
        return cls._from_parts(args)

    # Avoid accessor changes
    def _init(self, template=None):
        self._closed = False

    # Avoid ``str(self)``; delegate to accessor.
    def __fspath__(self):
        target = pathlib.Path(self._accessor.fspath(self))
        if not target.exists():
            self._accessor.download(self, target)
        return str(target)

    def __repr__(self):
        return "%r.%s" % (self._accessor, super(Path, self).__repr__())

    # Avoid file descriptors
    @contextlib.contextmanager
    def open(self, mode="r", buffering=-1, encoding=None,
             errors=None, newline=None):
        if self._closed:
            self._raise_closed()
        text = 'b' not in mode
        mode = ''.join(c for c in mode if c not in 'btU')
        with self._accessor.open(self, mode, buffering) as fileobj:
            if text:
                with io.TextIOWrapper(fileobj, encoding, errors, newline) as wrapper:
                    yield wrapper
            else:
                yield fileobj

    # Avoid file descriptors
    def touch(self, mode=0o666, exist_ok=True):
        if self._closed:
            self._raise_closed()
        self._accessor.touch(self, mode, exist_ok)

    # Avoid ``os.fsencode()``
    def __bytes__(self):
        return self._accessor.fsencode(self)

    # Avoid ``import pwd`` etc
    def owner(self):
        return self._accessor.stat(self).user

    # Avoid ``import grp`` etc
    def group(self):
        return self._accessor.stat(self).group

    # Avoid ``os.environ`` etc.
    def expanduser(self):
        if (not (self._drv or self._root) and
            self._parts and self._parts[0][:1] == '~'):
            homedir = self._accessor.gethomedir(self._parts[0][1:])
            return self._from_parts([homedir] + self._parts[1:])

        return self

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

    # Avoid ``os.getcwd()``
    def resolve(self, strict=False):
        if self._closed:
            self._raise_closed()
        return super(Path, self.absolute()).resolve(strict=strict)

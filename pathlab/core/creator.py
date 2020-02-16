import io

from pathlab.core.stat import Stat


class Creator(io.BytesIO):
    """
    A creator object is a :class:`~io.BytesIO` object that writes its contents
    to a path when closed. It calls :meth:`Accessor.create` to achieve this.

    A creator object may be returned from :meth:`Accessor.open` in ``w`` mode.

    :param path: The path to be created
    :param initial: Initial data to add to the buffer
    :param unlink: Whether to call :meth:`Accessor.unlink` in advance if the
        path already exists.
    """

    def __init__(self, path, initial=None, unlink=True):
        super(Creator, self).__init__(initial)
        self.path = path
        self.parent = path.parent
        self.accessor = path._accessor
        self.unlink = unlink

    def close(self):
        if not self.parent.exists():
            return self.accessor.not_found(self.parent)
        if self.unlink and self.path.exists():
            self.path.unlink()
        size = self.tell()
        self.seek(0)
        self.accessor.create(self.path, Stat(size=size), self)

import io

from pathlab.core.stat import Stat


class Creator(io.BytesIO):
    """
    A creator object is a :class:`~io.BytesIO` object that writes its contents
    to a path when closed. It calls :meth:`Accessor.create` to achieve this.

    A creator object may be returned from :meth:`Accessor.open` in ``w`` mode.

    :param path: The path to be created
    :param path_mode: Action to take when path exists. One of ``ignore``,
        ``raise``, or ``delete`` (the default).
    :param parent_mode: Action to take when parent doesn't exist. One of
        ``ignore``, ``raise`` (the default), or ``create``.
    :param initial: Initial data to add to the buffer
    :param stat: The initial :class:`Stat` object, which will have its ``size``
        attribute overwritten.
    """

    def __init__(self, path, path_mode="delete", parent_mode="raise",
                 initial=None, stat=None, ):
        assert path_mode in ("ignore", "raise", "delete")
        assert parent_mode in ("ignore", "raise", "create")
        self.path = path
        self.path_mode = path_mode
        self.parent = path.parent
        self.parent_mode = parent_mode
        self.check()
        super(Creator, self).__init__(initial)
        self.stat = stat or Stat()

    def close(self):
        self.check()
        self.stat.size = self.tell()
        self.seek(0)
        self.path._accessor.create(self.path, self.stat, self)

    def check(self):
        accessor = self.path._accessor
        if self.parent_mode != "ignore":
            if not self.parent.exists():
                if self.parent_mode == "create":
                   self.parent.mkdir(parents=True)
                else:
                   accessor.not_found(parent)
        if self.path_mode != "ignore":
            if self.path.exists():
                if self.path_mode == "delete":
                    self.path.unlink()
                else:
                    accessor.already_exists(self.path)

import io

from pathlab.core.stat import Stat


class Creator(io.BytesIO):
    """
    A creator object is a :class:`~io.BytesIO` object that writes its contents
    to a path when closed. It calls :meth:`Accessor.create` to achieve this.

    A creator object may be returned from :meth:`Accessor.open` in ``w`` mode.

    :param target: The path to be created
    :param target_mode: Action to take when path exists. One of ``ignore``,
        ``raise``, or ``delete`` (the default).
    :param parent_mode: Action to take when parent doesn't exist. One of
        ``ignore``, ``raise`` (the default), or ``create``.
    :param stat: The initial :class:`Stat` object, which will have its ``size``
        attribute changed.
    """

    def __init__(self, target, target_mode="delete", parent_mode="raise",
                 stat=None):
        assert target_mode in ("ignore", "raise", "delete")
        assert parent_mode in ("ignore", "raise", "create")
        self.target = target
        self.parent = target.parent
        self.target_mode = target_mode
        self.parent_mode = parent_mode
        self.accessor = target._accessor
        self.check()
        self.stat = stat or Stat()
        super(Creator, self).__init__()

    def close(self):
        self.check()
        self.stat.size = self.tell()
        self.seek(0)
        self.accessor.create(self.target, self.stat, self)

    def check(self):
        if self.parent_mode != "ignore":
            if not self.parent.exists():
                if self.parent_mode == "create":
                   self.parent.mkdir(parents=True)
                else:
                   self.accessor.not_found(self.parent)
        if self.target_mode != "ignore":
            if self.target.exists():
                if self.target_mode == "delete":
                    self.target.unlink()
                else:
                    self.accessor.already_exists(self.target)

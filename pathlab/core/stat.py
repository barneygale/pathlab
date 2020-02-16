import collections.abc
import functools
import datetime
import stat


default_time = datetime.datetime.fromtimestamp(0)
types = {
    'file':         stat.S_IFREG,
    'dir':          stat.S_IFDIR,
    'char_device':  stat.S_IFCHR,
    'block_device': stat.S_IFBLK,
    'fifo':         stat.S_IFIFO,
    'symlink':      stat.S_IFLNK,
    'socket':       stat.S_IFSOCK,
}
types_inv = {mode: name for name, mode in types.items()}
st_fields = [
    'st_mode',
    'st_ino',
    'st_dev',
    'st_nlink',
    'st_uid',
    'st_gid',
    'st_size',
    'st_atime',
    'st_mtime',
    'st_ctime',
]

@functools.total_ordering
class Stat(collections.abc.Sequence):
    """
    Mutable version of :class:`os.stat_result`. The usual ``st_`` attributes
    are available as read-only properties. Other attributes may be passed to
    the initializer or set directly.

    Objects of this type (or a subclass) may be returned from
    :meth:`Accessor.stat()`.
    """

    #: File type, for example ``file``, ``dir``, ``symlink``, ``socket``,
    #: ``fifo``,  ``char_device`` or ``block_device``. Other values may be
    #: used, but will result in a ``stat.st_mode`` that indicates a regular
    #: file.
    type = "file"

    #: File size in bytes
    size = 0

    #: Permission bits
    permissions = 0

    #: Name of file owner
    user = None

    #: Name of file group
    group = None

    #: ID of file owner
    user_id = 0

    #: ID of file group
    group_id = 0

    #: ID of containing device
    device_id = 0

    #: ID that uniquely identifies the file on the device
    file_id = 0

    #: Number of hard links to this file
    hard_link_count = 0

    #: Time of creation
    create_time = default_time

    #: Time of last access
    access_time = default_time

    #: Time of last modification
    modify_time = default_time

    #: Time of last status modification
    status_time = default_time

    #: Link target
    target = None

    def __init__(self, **params):
        self.update(params)

    def update(self, params):
        for name, value in params.items():
            setattr(self, name, value)

    def __repr__(self):
        name = self.__class__.__name__
        fields = sorted(vars(self).items())
        fields = ", ".join("%s=%r" % pair for pair in fields)
        return "%s(%s)" % (name, fields)

    # Sequence methods --------------------------------------------------------

    def __getitem__(self, item):
        return getattr(self, st_fields[item])

    def __len__(self):
        return len(st_fields)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __lt__(self, other):
        return tuple(self) < tuple(other)

    # File mode utilities -----------------------------------------------------

    @staticmethod
    def pack_mode(type, permissions):
        return types.get(type, stat.S_IFREG) | permissions

    @staticmethod
    def unpack_mode(mode):
        return types_inv.get(stat.S_IFMT(mode), 'file'), stat.S_IMODE(mode)

    # Compatibility with ``os.stat_result`` -----------------------------------

    st_mode  = property(lambda self: self.pack_mode(self.type, self.permissions))
    st_ino   = property(lambda self: self.file_id)
    st_dev   = property(lambda self: self.device_id)
    st_nlink = property(lambda self: self.hard_link_count)
    st_uid   = property(lambda self: self.user_id)
    st_gid   = property(lambda self: self.group_id)
    st_size  = property(lambda self: self.size)
    st_atime = property(lambda self: self.access_time.timestamp())
    st_mtime = property(lambda self: self.modify_time.timestamp())
    st_ctime = property(lambda self: self.status_time.timestamp())

import collections.abc
import datetime
import stat


default_time = datetime.datetime.fromtimestamp(0)
default_type = stat.S_IFREG
types = {
    'dir':          stat.S_IFDIR,
    'char_device':  stat.S_IFCHR,
    'block_device': stat.S_IFBLK,
    'fifo':         stat.S_IFIFO,
    'symlink':      stat.S_IFLNK,
    'socket':       stat.S_IFSOCK,
}
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

    #: Time of last access
    access_time = default_time

    #: Time of last modification
    modify_time = default_time

    #: Time of creation
    create_time = default_time

    def __init__(self, **params):
        for name, value in params.items():
            setattr(self, name, value)

    def __repr__(self):
        name = self.__class__.__name__
        fields = sorted(vars(self).items())
        fields = ", ".join("%s=%r" % pair for pair in fields)
        return "%s(%s)" % (name, fields)

    def __getitem__(self, item):
        return getattr(self, st_fields[item])

    def __len__(self):
        return len(st_fields)

    # Compatibility with ``os.stat_result`` -----------------------------------

    @property
    def st_mode(self):
        return types.get(self.type, default_type) | self.permissions

    @property
    def st_ino(self):
        return self.file_id

    @property
    def st_dev(self):
        return self.device_id

    @property
    def st_nlinks(self):
        return self.hard_link_count

    @property
    def st_uid(self):
        return self.user_id

    @property
    def st_gid(self):
        return self.group_id

    @property
    def st_size(self):
        return self.size

    @property
    def st_atime(self):
        return self.access_time.timestamp()

    @property
    def st_mtime(self):
        return self.modify_time.timestamp()

    @property
    def st_ctime(self):
        return self.create_time.timestamp()

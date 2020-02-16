import datetime
import pathlab
import tarfile


file_types = {
    tarfile.REGTYPE:  'file',
    tarfile.DIRTYPE:  'dir',
    tarfile.SYMTYPE:  'symlink',
    tarfile.LNKTYPE:  'link',
    tarfile.CHRTYPE:  'char_device',
    tarfile.BLKTYPE:  'block_device',
    tarfile.FIFOTYPE: 'fifo',
}
file_types_inv = {v: k for k, v in file_types.items()}


class TarPath(pathlab.Path):
    __slots__ = ()


class TarAccessor(pathlab.Accessor):
    """
    Accessor for ``.tar`` archives. Supports writing of files, but not other
    forms of modification.

    :param file: Path to ``.tar`` file, or file object.
    """

    factory = TarPath
    reader = None
    writer = None

    def __init__(self, file):
        self.file = file
        self._reload()

    def __repr__(self):
        return "TarAccessor(%r)" % self.file

    def _reload(self):
        if self.writer:
            self.writer.close()
        self.reader = tarfile.open(self.file, "r")
        self.writer = tarfile.open(self.file, "a")

    def _encode(self, path):
        return str(path.absolute())[1:]

    def _decode(self, string):
        return self.factory("/%s" % string)

    def create(self, path, stat, fileobj=None):
        info = tarfile.TarInfo()
        info.name = self._encode(path)
        info.type = file_types_inv[stat.type]
        info.size = stat.size
        info.mode = stat.permissions
        info.linkname = self._encode(stat.target) if stat.target else ""
        self.writer.addfile(info, fileobj)
        self._reload()

    def open(self, path, mode="r", buffering=-1):
        if buffering != -1:
            raise NotImplementedError
        elif mode == "r":
            return self.reader.extractfile(self._encode(path))
        elif mode == "w":
            return pathlab.Creator(path, target_mode="ignore")
        else:
            raise NotImplementedError

    def stat(self, path, *, follow_symlinks=True):
        # Resolve symlinks
        if not follow_symlinks:
            path = path.parent.resolve() / path.name
        else:
            path = path.resolve()

        # Handle the root directory
        if str(path) == "/":
            return pathlab.Stat(
                type='dir',
                device_id=id(self),
                file_id=1,
                path=self._decode(''))

        # Retrieve the member info
        try:
            info = self.reader.getmember(self._encode(path))
        except KeyError:
            return self.not_found(path)

        # Build our stat object
        return pathlab.Stat(
            type=file_types.get(info.type, 'file'),
            size=info.size,
            permissions=info.mode,
            device_id=id(self),
            file_id=info.offset + 2,
            user_id=info.uid,
            group_id=info.gid,
            modify_time=datetime.datetime.fromtimestamp(info.mtime),
            path=self._decode(info.name),
            target=self._decode(info.linkname),
            user=info.uname,
            group=info.gname)

    def listdir(self, path):
        # Check directory exists
        stat = self.stat(path)
        if stat.type != 'dir':
            return self.not_a_directory(path)

        # Resolve symlinks
        path = stat.path

        # Find members with a matching parent
        for info in self.reader.getmembers():
            p = self._decode(info.name)
            if p.parent == path:
                yield p.name

    def readlink(self, path):
        # Handle the root directory
        if str(path) == "/":
            return "/"

        # Retrieve the member info
        path = self.factory(path)
        try:
            info = self.reader.getmember(self._encode(path))
        except KeyError:
            return self.not_found(path)

        # Check this is a symlink
        if not info.linkname:
            return self.not_a_symlink(path)

        # Return the symlink target
        return str(self._decode(info.linkname))

"""
    # TODO: test!
    def upload(self, src, dst):
        self.writer.write(src, str(dst.absolute()))
        self._reload()

    # TODO: test!
    def download(self, src, dst):
        with open(dst, "wb") as fdst:
            with self.reader.open(self._encode(src), "rb") as fsrc:
                fdst.write(fsrc.read())
"""

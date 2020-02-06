import datetime
import posixpath
import pathlab
import tarfile


file_types = {
    tarfile.DIRTYPE:  'dir',
    tarfile.SYMTYPE:  'symlink',
    tarfile.LNKTYPE:  'link',
    tarfile.CHRTYPE:  'char_device',
    tarfile.BLKTYPE:  'block_device',
    tarfile.FIFOTYPE: 'fifo',
}


def normalize(path):
    return posixpath.normpath("/" + path)


class TarPath(pathlab.Path):
    pass


class TarAccessor(pathlab.Accessor):
    """
    Accessor for ``.tar`` archives. The initializer accepts the same arguments
    as :func:`tarfile.open`.
    """

    factory = TarPath

    def __init__(self, file, *args, **kwargs):
        if isinstance(file, tarfile.TarFile):
            self.file = file
        else:
            self.file = tarfile.open(file, *args, **kwargs)
        self.stats = {}
        for member in self.file.getmembers():
            stat = pathlab.Stat(
                type=file_types.get(member.type, 'file'),
                size=member.size,
                permissions=member.mode,
                file_id=member.offset_data + 1,
                user_id=member.uid,
                group_id=member.gid,
                modify_time=datetime.datetime(*member.mtime),
                raw_path=member.name,
                path=normalize(member.name),
                target_path=normalize(member.linkname),
                user=member.uname,
                group=member.gname)
            self.stats[stat.path] = stat

    def __repr__(self):
        return "TarAccessor(%r)" % (
            self.file.name if self.file.name else self.file.fileobj)

    def open(self, path, mode="r", buffering=-1):
        if mode == "r":
            return self.file.extractfile(self.stat(path).raw_path)
        # TODO: is writing possible?
        # seems we need to know the stream length ahead of time?
        raise NotImplementedError

    def stat(self, path, *, follow_symlinks=True):
        seen = set()
        target = str(path.absolute())
        while True:
            seen.add(target)
            try:
                stat = self.stats[target]
            except KeyError:
                return self.not_found(target)
            if not follow_symlinks:
                return stat
            target = stat.target_path
            if not target or target in seen:
                return stat

    def listdir(self, path):
        stat = self.stat(path)
        if stat.type != 'dir':
            return self.not_a_directory(path)
        path = stat.path
        for stat in self.stats.values():
            head, tail = posixpath.split(stat.path)
            if head == path:
                yield tail

    def readlink(self, path):
        stat = self.stat(path)
        if stat.target_path:
            return stat.target_path
        return path

    def upload(self, src, dst):
        self.file.write(src, str(dst.absolute()))

    def download(self, src, dst):
        with open(dst, "wb") as fdst:
            with self.file.open(self.stat(src).raw_path, "rb") as fsrc:
                fdst.write(fsrc.read())

    def fspath(self, path):
        return self.file.extract(self.stat(path).raw_path)

    def owner(self, path):
        return self.stat(path).user

    def group(self, path):
        return self.stat(path).group
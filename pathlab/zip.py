import datetime
import posixpath
import pathlab
import zipfile


class ZipPath(pathlab.Path):
    __slots__ = ()


class ZipAccessor(pathlab.Accessor):
    """
    Accessor for ``.zip`` archives. The initializer accepts the same arguments
    as :class:`zipfile.ZipFile`.
    """

    factory = ZipPath

    def __init__(self, file, *args, **kwargs):
        if isinstance(file, zipfile.ZipFile):
            self.file = file
        else:
            self.file = zipfile.ZipFile(file, *args, **kwargs)

        # Load members
        self.stats = {
            "/": pathlab.Stat(type='dir', file_id=1, path='/', raw_path='/')}
        for info in self.file.infolist():
            stat = pathlab.Stat(
                type='dir' if info.filename[-1] == '/' else 'file',
                size=info.file_size,
                file_id=info.header_offset + 2,
                modify_time=datetime.datetime(*info.date_time),
                path=posixpath.normpath("/" + info.filename),
                raw_path=info.filename)
            self.stats[stat.path] = stat

    def __repr__(self):
        return "ZipAccessor(%r)" % (
            self.file.fp if self.file._filePassed else self.file.filename)

    def open(self, path, mode="r", buffering=-1):
        return self.file.open(self.stat(path).raw_path, mode)

    def stat(self, path, *, follow_symlinks=True):
        try:
            return self.stats[str(path.absolute())]
        except KeyError:
            return self.not_found(path)

    def listdir(self, path):
        stat = self.stat(path)
        if stat.type != 'dir':
            return self.not_a_directory(path)
        path = stat.path
        for stat in self.stats.values():
            head, tail = posixpath.split(stat.path)
            if head == path:
                yield tail

    def upload(self, src, dst):
        self.file.write(src, str(dst.absolute()))

    def download(self, src, dst):
        with open(dst, "wb") as fdst:
            with self.file.open(self.stat(src).raw_path, "rb") as fsrc:
                fdst.write(fsrc.read())

    def fspath(self, path):
        return self.file.extract(self.stat(path).raw_path)

import datetime
import io
import posixpath
import pathlab
import zipfile


class ZipPath(pathlab.Path):
    @property
    def zipfile(self):
        return self._accessor.zipfile


class ZipAccessor(pathlab.Accessor):
    path_base = ZipPath

    def __init__(self, file, *args, **kwargs):
        if isinstance(file, zipfile.ZipFile):
            self.zipfile = file
        else:
            self.zipfile = zipfile.ZipFile(file, *args, **kwargs)

        # Enumerate members
        self.infodict = {}
        for info in self.zipfile.infolist():
            filename = posixpath.normpath('/' + info.filename)
            self.infodict[filename] = info

    def __repr__(self):
        return 'ZipAccessor(%r)' % self.zipfile.filename

    def getinfo(self, path):
        path = str(path.absolute())
        info = self.infodict.get(path)
        if info is None and path != '/':
            raise self.not_found(path)
        return info

    # Re-implement ``open()``
    def open(self, path, mode='r', buffering=-1, encoding=None, errors=None,
             newline=None):
        obj = self.zipfile.open(self.getinfo(path), mode.replace('b', ''))
        if 'b' not in mode:
            obj = io.TextIOWrapper(obj, encoding, errors, newline)
        return obj

    # Re-implement ``os.scandir()``
    def scandir(self, path):
        # Check the directory exists
        self.getinfo(path)

        # Find children
        path1 = str(path.absolute())
        for path2, info in self.infodict.items():
            parent, name = posixpath.split(path2)
            if path1 == parent:
                yield self.ZipPath(path2)

    # Re-implement ``os.listdir()``
    def listdir(self, path):
        return [p.name for p in self.scandir(path)]

    # Re-implement ``os.stat()``
    def stat(self, path, follow_link=True):
        result = pathlab.StatResult()
        result.st_dev = id(self.zipfile)
        info = self.getinfo(path)

        # Root directory
        if info is None:
            result.st_type = 'dir'

        # Other path
        else:
            result.st_type = 'dir' if info.is_dir() else 'file'
            result.st_ino = info.header_offset + 1
            result.st_size = info.file_size
            result.st_mtime = int(datetime.datetime(*info.date_time).timestamp())
        return result

    # Re-implement ``os.lstat()``
    lstat = stat

    def upload(self, src, dst):
        self.zipfile.write(src, str(dst.absolute()))

    def download(self, src, dst):
        with open(dst, 'wb') as fdst:
            with self.zipfile.open(self.getinfo(src), 'rb') as fsrc:
                fdst.write(fsrc.read())

    def fspath(self, path):
        return self.zipfile.extract(self.getinfo(path))
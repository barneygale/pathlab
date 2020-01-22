import datetime
import io
import posixpath
import stat
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
        self.infodict = {}
        for info in self.zipfile.infolist():
            filename = posixpath.normpath('/' + info.filename)
            self.infodict[filename] = info

    def __repr__(self):
        return "ZipAccessor(%r)" % self.zipfile.filename

    # Re-implement ``open()``
    def open(self, path, mode='r', buffering=-1, encoding=None, errors=None,
             newline=None):
        path1 = str(path.absolute())
        info = self.infodict.get(path1)
        if info is None:
            raise self.not_found(path)
        obj = self.zipfile.open(info, mode.replace('b', ''))
        if 'b' not in mode:
            obj = io.TextIOWrapper(obj, encoding, errors, newline)
        return obj

    # Re-implement ``os.listdir()``
    def listdir(self, path):
        path1 = str(path.absolute())
        found = path1 == '/'
        children = []

        for path2, info in self.infodict.items():
            # Look for the requested path
            is_dir = info.filename[-1] == '/'
            if path1 == path2:
                if not is_dir:
                    raise self.not_a_dir(path)
                found = True

            # Look for children of the requested path
            parent, name = posixpath.split(path2)
            if path1 == parent:
                children.append(name)

        if not found:
            raise self.not_found(path)

        return children

    # Re-implement ``os.stat()``
    def stat(self, path, follow_link=True):
        path1 = str(path.absolute())

        if path1 == '/':
            result = pathlab.StatResult()
            result.st_mode = stat.S_IFDIR
            return result

        info = self.infodict.get(path1)
        if info is None:
            raise self.not_found(path)

        is_dir = info.filename[-1] == '/'
        result = pathlab.StatResult()
        result.st_mode = stat.S_IFDIR if is_dir else stat.S_IFREG
        result.st_ino = info.header_offset
        result.st_dev = id(self.zipfile)
        result.st_size = info.file_size
        result.st_mtime = int(datetime.datetime(*info.date_time).timestamp())

        return result

    # Re-implement ``os.lstat()``
    lstat = stat

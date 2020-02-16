import datetime
import pathlab
import zipfile


class ZipPath(pathlab.Path):
    __slots__ = ()


class ZipAccessor(pathlab.Accessor):
    """
    Accessor for ``.zip`` archives. Supports writing of files, but not other
    forms of modification.

    :param file: Path to ``.zip`` file, or file object.
    """

    factory = ZipPath
    zipobj = None

    def __init__(self, file):
        self.file = file
        self.zipobj = zipfile.ZipFile(file, 'a')

    def __repr__(self):
        return "ZipAccessor(%r)" % self.file

    def _encode(self, path, is_dir=False):
        string = str(path.absolute())[1:]
        if is_dir:
            string += "/"
        return string

    def _decode(self, string):
        return self.factory("/%s" % string)

    def create(self, path, stat, fileobj=None):
        info = zipfile.ZipInfo(self._encode(path, stat.type == 'dir'))
        data = fileobj.read() if fileobj else b""
        self.zipobj.writestr(info, data)

    def open(self, path, mode="r", buffering=-1):
        if buffering != -1:
            raise NotImplementedError
        return self.zipobj.open(self._encode(path), mode)

    def stat(self, path, *, follow_symlinks=True):
        # Handle the root directory
        if str(path) == "/":
            return pathlab.Stat(
                type='dir',
                device_id=id(self),
                file_id=1,
                path=self._decode(''))

        # Retrieve the member info
        info = (self.zipobj.NameToInfo.get(self._encode(path, True)) or
                self.zipobj.NameToInfo.get(self._encode(path, False)))
        if info is None:
            return self.not_found(path)

        # Build our stat object
        return pathlab.Stat(
            type='dir' if info.filename[-1] == '/' else 'file',
            size=info.file_size,
            device_id=id(self),
            file_id=info.header_offset + 2,
            modify_time=datetime.datetime(*info.date_time),
            path=self._decode(info.filename))

    def listdir(self, path):
        # Check directory exists
        stat = self.stat(path)
        if stat.type != 'dir':
            return self.not_a_directory(path)

        # Find members with a matching parent
        for info in self.zipobj.infolist():
            p = self._decode(info.filename)
            if p.parent == path:
                yield p.name

"""
    # TODO: test!
    def upload(self, src, dst):
        self.zf.write(src, str(dst.absolute()))

    # TODO: test!
    def download(self, src, dst):
        with open(dst, "wb") as fdst:
            with self.zf.open(unnormalize(src), "rb") as fsrc:
                fdst.write(fsrc.read())
"""
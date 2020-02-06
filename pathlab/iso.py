import contextlib
import pathlab
import posixpath

from pycdlib import PyCdlib
from pycdlib.pycdlibexception import PyCdlibInvalidInput

class IsoPath(pathlab.Path):
    __slots__ = ()


class IsoAccessor(pathlab.Accessor):
    """
    Accessor for ``.iso`` disc images, using ``pycdlib``.

    :param path: specifies the filesystem path to the ISO file
    :param kind: specifies the ISO variant. This should be one of ``iso9660``,
        ``joliet``, ``rock_ridge`` or ``udf`` (the default).
    """

    factory = IsoPath

    def __init__(self, path, kind="udf"):
        self.iso = PyCdlib()
        self.iso.open(path)
        self.facade = getattr(self.iso, "get_%s_facade" % kind)()

    @contextlib.contextmanager
    def handle_exc(self, path):
        try:
            yield
        except PyCdlibInvalidInput as exc:
            msg = exc.args[0].lower()
            if 'could not find' in msg:
                self.not_found(path)
            if 'not a directory' in msg:
                self.not_a_directory(path)
            raise

    @contextlib.contextmanager
    def open(self, path, mode="r", buffering=-1):
        if mode == "r":
            with self.facade.open_file_from_iso(str(path.absolute())) as fileobj:
                yield fileobj
        else:
            raise NotImplementedError

    def stat(self, path, *, follow_symlinks=True):
        stat = pathlab.Stat()
        with self.handle_exc(path):
            record = self.facade.get_record(str(path.absolute()))
            stat.file_id = record.extent_location()
            if record.is_dir():
                stat.type = 'dir'
            else:
                stat.size = record.get_data_length()
        return stat

    def listdir(self, path):
        self.stat(path)
        children = []
        with self.handle_exc(path):
            for child in self.facade.list_children(str(path.absolute())):
                if child:
                    children.append(posixpath.basename(
                        self.iso.full_path_from_dirrecord(child)))
        return children

    # TODO: various other methods

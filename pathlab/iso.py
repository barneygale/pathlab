import datetime
import io
import functools
import struct

import pathlab


SECTOR = 2048
ISO_IDENT = b"CD001"
PVD_TYPE = 1
END_TYPE = 255
PX_FIELDS = ('mode', 'hard_link_count', 'user_id', 'group_id', 'file_id')
TF_FIELDS = ('create_time', 'modify_time', 'access_time', 'status_time',
             'backup_time', 'expiration_time', 'effective_time')


class IsoPath(pathlab.Path):
    __slots__ = ()


class IsoAccessor(pathlab.Accessor):
    """
    Accessor for ``.iso`` image. Supports plain ISOs and those with
    SUSP/Rock Ridge data. Does not support Joliet or UDF (yet). Does not
    support modification.

    :param file: Path to ``.iso`` file, or file object.
    :param ignore_susp: Whether to ignore SUSP/Rock Ridge data
    :param cache_size: specifies the size of the LRU cache to use for
        ``_load_record()`` results. Set to ``0`` to disable caching.
    """

    fileobj = None
    managed = False
    root = None
    factory = IsoPath

    def __init__(self, file, ignore_susp=False, cache_size=1024):
        self.file = file
        self.ignore_susp = ignore_susp
        if cache_size:
            self._load_record = functools.lru_cache(cache_size)(self._load_record)

        if hasattr(file, "close"):
            self.fileobj = file
            self.managed = False
        else:
            self.fileobj = open(file, 'rb', buffering=SECTOR)
            self.managed = True

        # Load volume descriptors
        sector = 16
        while True:
            self.fileobj.seek(SECTOR * sector)
            type = self._unpack_byte()
            ident = self._unpack_bytes(5)
            if ident == ISO_IDENT:
                if type == PVD_TYPE:
                    self.fileobj.seek(SECTOR * sector + 156)
                    self.root = self._unpack_record()
                elif type == END_TYPE:
                    break
            sector += 1
        if not self.root:
            raise ValueError("No valid volume descriptors")

    def __repr__(self):
        return "IsoAccessor(%r)" % self.file

    # Unpacking methods -------------------------------------------------------

    def _unpack_byte(self):
        return self.fileobj.read(1)[0]

    def _unpack_bytes(self, count):
        return self.fileobj.read(count)

    def _unpack_to(self, end):
        start = self.fileobj.tell()
        if start == end:
            return b""
        assert start < end
        return self.fileobj.read(end - start)

    def _unpack_to_boundary(self):
        return self.fileobj.read(SECTOR - self.fileobj.tell() % SECTOR)

    # ISO 9660:7.3.3
    def _unpack_both(self, fmt):
        l = struct.calcsize(fmt)
        a = struct.unpack('<' + fmt, self.fileobj.read(l))[0]
        b = struct.unpack('>' + fmt, self.fileobj.read(l))[0]
        assert a == b
        return a

    # 17 bytes (long)  - ISO 9660:8.4.26.1
    #  7 bytes (short) - ISO 9660:9.1.5
    def _unpack_time(self, long=False):
        if long:
            s = self.fileobj.read(16).decode('ascii')
            t = datetime.datetime.strptime(s, '%Y%m%d%H%M%S%f')
        else:
            y, m, d, H, M, S = self.fileobj.read(6)
            t = datetime.datetime(1900 + y, m, d, H, M, S)
        offset = self.fileobj.read(1)[0]
        return t + datetime.timedelta(minutes=15*offset)

    # ISO 9660:9.1
    def _unpack_record(self):
        # Some notation:
        #   i:  ISO 9660
        #   s:  SUSP
        #   b:  SUSP block
        #   r:  SUSP record
        #   c:  SUSP record element

        # Load ISO 9660 data
        i_start       = self.fileobj.tell()
        i_end         = self._unpack_byte() + i_start
        _             = self._unpack_byte()
        i_sector      = self._unpack_both('I')
        i_size        = self._unpack_both('I')
        i_create_time = self._unpack_time()
        i_flags       = self._unpack_byte()
        _             = self._unpack_bytes(6)
        i_name        = self._unpack_bytes(self._unpack_byte())
        _             = self._unpack_byte() if len(i_name) % 2 == 0 else 0

        # Decode name
        if i_name == b'\x00':
            i_name = '.'
        elif i_name == b'\x01':
            i_name = '..'
        else:
            i_name = i_name.decode('ascii').split(";")[0]

        # Create record
        record = {
            'name': i_name,
            'size': i_size,
            'sector': i_sector,
            'file_id': i_sector,
            'device_id': id(self),
            'create_time': i_create_time,
            'type': 'dir' if i_flags & 2 else 'file'}

        # No SUSP entries?
        if self.fileobj.tell() == i_end:
            return record

        # Ignore SUSP entries?
        if self.ignore_susp:
            self._unpack_to(i_end)
            return record

        # Set up SUSP state
        s_name        = []     # SUSP filename parts
        s_target      = []     # SUSP symlink target parts
        s_target_tail = []     # SUSP symlink target tail parts
        b_start       = 0      # SUSP block start offset
        b_end         = i_end  # SUSP block end offset
        b_next        = None   # SUSP block continuation info

        # Load SUSP entries
        while True:
            r_start = self.fileobj.tell()
            r_kind  = self._unpack_bytes(2)
            r_end   = self._unpack_byte() + r_start
            _       = self._unpack_byte()

            # Continuation area
            if r_kind == b'CE':
                b_next = (
                    self._unpack_both('I'),
                    self._unpack_both('I'),
                    self._unpack_both('I'))

            # File attributes
            elif r_kind == b'PX':
                for c_field in PX_FIELDS:
                    c_value =  self._unpack_both('I')
                    if c_field == 'mode':
                        c_value = pathlab.Stat.unpack_mode(c_value)
                        record['type'], record['permissions'] = c_value
                    else:
                        record[c_field] = c_value
                    if self.fileobj.tell() >= r_end:
                        break

            # Symbolic link target
            elif r_kind == b'SL':
                _ = self._unpack_byte()
                while self.fileobj.tell() < r_end:
                    c_flags = self._unpack_byte()
                    c_flag_partial = c_flags & 0x01  # more to come
                    c_flag_current = c_flags & 0x02
                    c_flag_parent = c_flags & 0x04
                    c_flag_root = c_flags & 0x08
                    c_name_len = self._unpack_byte()
                    c_name = self._unpack_bytes(c_name_len)
                    c_name = c_name.decode(self.encoding)

                    if c_flag_root:
                        s_target.clear()
                        s_target.append("")
                    elif c_flag_current:
                        s_target.append(".")
                    elif c_flag_parent:
                        s_target.append("..")
                    else:
                        s_target_tail.append(c_name)
                        if not c_flag_partial:
                            s_target.append("".join(s_target_tail))
                            s_target_tail.clear()

            # Filename
            elif r_kind == b'NM':
                c_flags = self._unpack_byte()
                c_flag_current = c_flags & 0x02
                c_flag_parent  = c_flags & 0x04
                c_name = self._unpack_to(r_end)
                c_name = c_name.decode(self.encoding)

                if c_flag_current:
                    s_name.append(".")
                elif c_flag_parent:
                    s_name.append("..")
                else:
                    s_name.append(c_name)

            # Timestamps
            elif r_kind == b'TF':
                c_flags = self._unpack_byte()
                c_flag_long = c_flags & 0x80
                for i, c_field in enumerate(TF_FIELDS):
                    if c_flags & (1 << i):
                        record[c_field] = self._unpack_time(c_flag_long)

            # Some other record
            else:
                self._unpack_to(r_end)

            # Ensure we read the entire SUSP record
            assert self.fileobj.tell() == r_end

            # Discard padding byte
            if self.fileobj.tell() == (b_end - 1):
                self._unpack_byte()

            # End of current block
            if self.fileobj.tell() == b_end:
                # No further block
                if not b_next:
                    break

                # Jump to next block
                b_start = SECTOR * b_next[0] + b_next[1]
                b_end = b_start + b_next[2]
                b_next = None
                self.fileobj.seek(b_start)

        # Seek back to the end of the ISO record
        if b_start:
            self.fileobj.seek(i_end)

        # Finalize SUSP data
        if s_name:
            record['name'] = ''.join(s_name)
        if s_target:
            record['target'] = '/'.join(s_target)
        assert len(s_target_tail) == 0

        # Return our record!
        return record

    def _load_children(self, record):
        assert record['type'] == 'dir'
        start = SECTOR * record['sector']
        end = start + record['size']
        self.fileobj.seek(start)
        while self.fileobj.tell() < end:
            if not self.fileobj.peek(1)[0]:
                self._unpack_to_boundary()
                continue
            yield self._unpack_record()

    def _load_record(self, path):
        record = self.root
        paths = [path] + list(path.parents)
        for part in paths[::-1][1:]:
            if record['type'] != 'dir':
                return self.not_found(path)
            for child in self._load_children(record):
                if child['name'] == part.name:
                    record = child
                    break
            else:
                self.not_found(path)
        return record

    # Main accessor methods ---------------------------------------------------

    def stat(self, path, *, follow_symlinks=True):
        if not follow_symlinks:
            path = path.parent.resolve() / path.name
        else:
            path = path.resolve()
        return pathlab.Stat(**self._load_record(path))

    def readlink(self, path):
        path = self.factory(path)
        record = self._load_record(path)
        if record['type'] != 'symlink':
            return self.not_a_symlink(path)
        target = self.factory(record['target'])
        if not target.is_absolute():
            target = path.parent / record['target']
        return str(target)

    def listdir(self, path):
        record = self._load_record(path.resolve())
        if record['type'] != 'dir':
            return self.not_a_directory(path)
        for child in self._load_children(record):
            if child['name'] not in ('.', '..'):
                yield child['name']

    def open(self, path, mode="r", buffering=-1):
        if buffering != -1:
            raise NotImplementedError
        if mode == "r":
            record = self._load_record(path)
            self.fileobj.seek(SECTOR * record['sector'])
            return io.BytesIO(self.fileobj.read(record['size']))
        raise NotImplementedError

    def close(self):
        if self.managed:
            self.fileobj.close()
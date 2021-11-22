import os
import io
import mmap

class FileInFile(io.IOBase):
    def __init__(self, parent, offset, length):
        if isinstance(parent, FileInFile):
            # in this case, data is already mapped, so we just adapt the offsets
            self.data = parent.data
            self.offset = parent.offset + offset
            self.length = length
            assert parent.length >= offset + length
        else:
            self.data = mmap.mmap(parent.fileno(), 0, prot=mmap.PROT_READ)
            self.offset = offset
            self.length = length
        self.pos = 0

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self.pos = offset
        elif whence == os.SEEK_END:
            self.pos = self.length - offset
        elif whence == os.SEEK_CUR:
            self.pos += offset

    def peek(self, size):
        return self.read(size, peek=True)

    def read(self, size=None, peek=False):
        if self.pos >= self.length:
            return b''

        if size is None or self.pos + size > self.length:
            size = self.length - self.pos

        o = self.pos + self.offset
        data = self.data[o:o + size]
        if not peek:
            self.pos += size
        return data

    def tell(self):
        return self.pos

    def writable(self) -> bool:
        return False

    def readable(self) -> bool:
        return True

    def as_buffer(self):
        return memoryview(self.data)[self.offset: self.offset + self.length]
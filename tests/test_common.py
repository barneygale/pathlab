import io
import os
import stat
import subprocess

import pathlib
import pathlab

import pytest

support = {
    'open_unbuffered': ('local'),
    'create': ('local', 'tar', 'zip'),
    'symlink': ('local', 'tar', 'iso'),
    'chmod': ('local',),
    'delete': ('local',),
    'rename': ('local',)
}


@pytest.fixture(params=("local", "zip", "tar", "iso"))
def root(request, tmp_path):
    fs_path = tmp_path / 'fs'
    os.mkdir(fs_path)
    os.mkdir(fs_path / 'dirA')
    os.mkdir(fs_path / 'dirB')
    os.mkdir(fs_path / 'dirC')
    os.mkdir(fs_path / 'dirC' / 'dirD')
    with open(fs_path / 'fileA', 'wb') as f:
        f.write(b"this is file A\n")
    with open(fs_path / 'dirB' / 'fileB', 'wb') as f:
        f.write(b"this is file B\n")
    with open(fs_path / 'dirC' / 'fileC', 'wb') as f:
        f.write(b"this is file C\n")
    with open(fs_path / 'dirC' / 'dirD' / 'fileD', 'wb') as f:
        f.write(b"this is file D\n")
    if has_support(request.param, "symlink"):
        os.symlink('fileA',          fs_path / 'linkA')
        os.symlink('non-existing',   fs_path / 'brokenLink')
        os.symlink('dirB',           fs_path / 'linkB')
        os.symlink('../dirB',        fs_path / 'dirA' / 'linkC')
        os.symlink('../dirB',        fs_path / 'dirB' / 'linkD')
        os.symlink('brokenLinkLoop', fs_path / 'brokenLinkLoop')
    if request.param == 'local':
        yield fs_path
    elif request.param == 'zip':
        zip_path = tmp_path / 'fs.zip'
        subprocess.check_call('zip --symlinks -r %s .' % zip_path, cwd=fs_path, shell=True)
        yield pathlab.ZipAccessor(zip_path).ZipPath('/')
    elif request.param == 'tar':
        tar_path = tmp_path / 'fs.tar'
        subprocess.check_call('tar cf %s *' % tar_path, cwd=fs_path, shell=True)
        yield pathlab.TarAccessor(tar_path).TarPath('/')
    elif request.param == 'iso':
        iso_path = tmp_path / 'fs.iso'
        subprocess.check_call(
            ['genisoimage', '-r', '-o', iso_path, '.'],
            cwd=fs_path)
        yield pathlab.IsoAccessor(iso_path).IsoPath('/')


def has_support(name_or_path, kind):
    if isinstance(name_or_path, str):
        name = name_or_path
    else:
        name = {
            pathlib._NormalAccessor: "local",
            pathlab.ZipAccessor: "zip",
            pathlab.TarAccessor: "tar",
            pathlab.IsoAccessor: "iso",
        }[type(name_or_path._accessor)]

    return name in support[kind]

def test_samefile(root):
    p  = root / 'fileA'
    pp = root / 'fileA'
    q  = root / 'dirB' / 'fileB'
    r  = root / 'foo'
    assert p.samefile(pp)
    assert not p.samefile(q)
    with pytest.raises(FileNotFoundError):
        p.samefile(r)
    with pytest.raises(FileNotFoundError):
        r.samefile(p)
    with pytest.raises(FileNotFoundError):
        r.samefile(r)


def test_exists(root):
    assert root.exists()
    assert (root / 'dirA').exists()
    assert (root / 'fileA').exists()
    assert not (root / 'fileA' / 'bah').exists()
    if has_support(root, "symlink"):
        assert (root / 'linkA').exists()
        assert (root / 'linkB').exists()
        assert (root / 'linkB' / 'fileB').exists()
    assert not (root / 'linkA' / 'bah').exists()
    assert not (root / 'foo').exists()

def test_open(root):
    with (root / 'fileA').open('r') as f:
        assert isinstance(f, io.TextIOBase)
        assert f.read() == "this is file A\n"

def test_open_binary(root):
    with (root / 'fileA').open('rb') as f:
        assert isinstance(f, io.BufferedIOBase)
        assert f.read().strip() == b"this is file A"

def test_open_unbuffered(root):
    if not has_support(root, "open_unbuffered"):
        pytest.skip("No support for unbuffered open")
    with (root / 'fileA').open('rb', buffering=0) as f:
        assert isinstance(f, io.RawIOBase)
        assert f.read().strip() == b"this is file A"


def test_read_write_bytes(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    (root / 'fileA').write_bytes(b'abcdefg')
    assert (root / 'fileA').read_bytes() == b'abcdefg'
    with pytest.raises(TypeError):
        (root / 'fileA').write_bytes('somestr')
    assert (root / 'fileA').read_bytes() == b'abcdefg'

def test_read_write_text(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    (root / 'fileA').write_text('äbcdefg', encoding='latin-1')
    assert (root / 'fileA').read_text(encoding='utf-8', errors='ignore') == 'bcdefg'
    with pytest.raises(TypeError):
        (root / 'fileA').write_text(b'somebytes')
    assert (root / 'fileA').read_text(encoding='latin-1') == 'äbcdefg'

def test_iterdir(root):
    it = root.iterdir()
    paths = set(it)
    expected = ['dirA', 'dirB', 'dirC', 'fileA']
    if has_support(root, "symlink"):
        expected += ['linkA', 'linkB', 'brokenLink', 'brokenLinkLoop']
    assert paths == { root / q for q in expected }

def test_iterdir_symlink(root):
    if not has_support(root, "symlink"):
        pytest.skip("No symlink support")
    path = root / 'linkB'
    paths = set(path.iterdir())
    expected = { path / q for q in ['fileB', 'linkD'] }
    assert paths == expected

def test_iterdir_nodir(root):
    path = root / 'fileA'
    with pytest.raises(OSError):
        next(path.iterdir())

"""
def test_glob_common(root):
    def _check(glob, expected):
        assert set(glob) == { root / q for q in expected }

    it = root.glob("fileA")
    assert isinstance(it, collections.abc.Iterator)
    _check(it, ["fileA"])

    _check(root.glob("fileB"), [])
    _check(root.glob("dir*/file*"), ["dirB/fileB", "dirC/fileC"])
    _check(root.glob("*A"), ['dirA', 'fileA'])
    _check(root.glob("*B/*"), ['dirB/fileB'])
    _check(root.glob("*/fileB"), ['dirB/fileB'])


def test_rglob_common(root):
    def _check(glob, expected):
        assert set(glob) == {root / q for q in expected}
    path = root / "dirC"

    it = root.rglob("fileA")
    assert isinstance(it, collections.abc.Iterator)
    _check(it, ["fileA"])

    _check(root.rglob("fileB"),   ["dirB/fileB"])
    _check(root.rglob("*/fileA"), [])
    _check(root.rglob("*/fileB"), ["dirB/fileB", "dirB/linkD/fileB", "linkB/fileB", "dirA/linkC/fileB"])
    _check(root.rglob("file*"),   ["fileA", "dirB/fileB", "dirC/fileC", "dirC/dirD/fileD"])
    _check(path.rglob("file*"),   ["dirC/fileC", "dirC/dirD/fileD"])
    _check(path.rglob("*/*"),     ["dirC/dirD/fileD"])


def test_rglob_symlink_loop(root):
    if has_support(root, "symlink"):
        given = set(root.rglob('*'))
        expect = {'brokenLink',
                  'dirA', 'dirA/linkC',
                  'dirB', 'dirB/fileB', 'dirB/linkD',
                  'dirC', 'dirC/dirD', 'dirC/dirD/fileD', 'dirC/fileC',
                  'fileA',
                  'linkA',
                  'linkB',
                  'brokenLinkLoop',
                  }
        assert given == {root / x for x in expect}


def test_glob_dotdot(root):
    assert set(root.glob("..")) == {root / ".."}
    assert set(root.glob("dirA/../file*")) == {root / "dirA" / ".." / "fileA"}
    assert set(root.glob("../xyzzy")) == set()
"""

def test_resolve_common(root):
    if not has_support(root, "symlink"):
        pytest.skip("No symlink support")
    p = root / 'foo'
    with pytest.raises(OSError):
        p.resolve(strict=True)
    assert p.resolve(strict=False) == p
    p = root / 'foo' /  'in' / 'spam'
    assert p.resolve(strict=False) == p

    p = root /  'dirB' / 'fileB'
    assert p.resolve() == p

    p = root / 'linkA'
    q = root / 'fileA'
    assert p.resolve() == q

    p = root / 'dirA' / 'linkC' / 'fileB'
    q = root / 'dirB' / 'fileB'
    assert p.resolve() == q

    p = root / 'dirB' / 'linkD' / 'fileB'
    q = root / 'dirB' / 'fileB'
    assert p.resolve() == q

    p = root / 'dirA' / 'linkC' / 'fileB' / 'foo' / 'in' / 'spam'
    q = root / 'dirB' / 'fileB' / 'foo' / 'in' / 'spam'
    assert p.resolve(False) == q

    p = root / 'dirA' / 'linkC' /  '..' /  'foo' /  'in' / 'spam'
    q = root / 'foo' / 'in' / 'spam'
    assert p.resolve(False) == q

def test_with(root):
    it = root.iterdir()
    it2 = root.iterdir()
    next(it2)
    with root:
        pass
    # I/O operation on closed path.
    with pytest.raises(ValueError):
        next(it)
    with pytest.raises(ValueError):
        next(it2)
    with pytest.raises(ValueError):
        print(root.open())
    with pytest.raises(ValueError):
        root.resolve()
    with pytest.raises(ValueError):
        root.absolute()
    with pytest.raises(ValueError):
        root.__enter__()


def test_chmod(root):
    if not has_support(root, "chmod"):
        pytest.skip("No chmod support")
    p = root / 'fileA'
    mode = p.stat().st_mode
    # Clear writable bit.
    new_mode = mode & ~0o222
    p.chmod(new_mode)
    assert p.stat().st_mode == new_mode
    # Set writable bit.
    new_mode = mode | 0o222
    p.chmod(new_mode)
    assert p.stat().st_mode == new_mode


def test_stat(root):
    p = root / 'fileA'
    st = p.stat()
    assert p.stat() == st

    if has_support(root, "chmod"):
        # Change file mode by flipping write bit.
        p.chmod(st.st_mode ^ 0o222)
        assert p.stat() != st


def test_lstat(root):
    if not has_support(root, "symlink"):
        pytest.skip("No symlink support")
    p = root / 'linkA'
    st = p.stat()
    assert st != p.lstat()

def test_lstat_nosymlink(root):
    p = root / 'fileA'
    st = p.stat()
    assert st == p.lstat()

def test_unlink(root):
    if not has_support(root, "delete"):
        pytest.skip("No delete support")
    p = root / 'fileA'
    p.unlink()
    with pytest.raises(FileNotFoundError):
        p.stat()
    with pytest.raises(FileNotFoundError):
        p.unlink()

def test_rmdir(root):
    if not has_support(root, "delete"):
        pytest.skip("No delete support")
    p = root / 'dirA'
    for q in p.iterdir():
        q.unlink()
    p.rmdir()
    with pytest.raises(FileNotFoundError):
        p.stat()
    with pytest.raises(FileNotFoundError):
        p.unlink()
"""
def test_link_to(root):
    if not has_support(root, "symlink"):
        pytest.skip("No symlink support")
    p = root / 'fileA'
    size = p.stat().st_size
    q = root / 'dirA' / 'fileAA'
    p.link_to(q)
    assert q.stat().st_size == size
    assert os.path.samefile(p, q)
    assert p.stat()
"""

def test_rename(root):
    if not has_support(root, "rename"):
        pytest.skip("No rename support")
    p = root / 'fileA'
    size = p.stat().st_size
    q = root / 'dirA' / 'fileAA'
    p.rename(q)
    assert q.stat().st_size == size
    with pytest.raises(FileNotFoundError):
        p.stat()

def test_replace(root):
    p = root / 'fileA'
    if not has_support(root, "rename"):
        pytest.skip("No rename support")
    size = p.stat().st_size
    q = root / 'dirA' / 'fileAA'
    p.replace(q)
    assert q.stat().st_size == size
    with pytest.raises(FileNotFoundError):
        p.stat()

"""
def test_readlink(root):
    if not has_support(root, "symlink"):
        pytest.skip("No symlink support")
    assert (root / 'linkA').readlink() == (root / 'fileA')
    assert (root / 'brokenLink').readlink() == (root / 'non-existing')
    assert (root / 'linkB').readlink() == (root / 'dirB')
    with pytest.raises(OSError):
        (root / 'fileA').readlink()
"""

def test_touch_common(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'newfileA'
    assert not p.exists()
    p.touch()
    assert p.exists()
    p = root / 'newfileB'
    assert not p.exists()
    p.touch(mode=0o700, exist_ok=False)
    assert p.exists()
    with pytest.raises(OSError):
        p.touch(exist_ok=False)

def test_touch_nochange(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'fileA'
    p.touch()
    with p.open('rb') as f:
        assert f.read().strip() == b"this is file A"

def test_mkdir(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'newdirA'
    assert not p.exists()
    p.mkdir()
    assert p.exists()
    assert p.is_dir()
    with pytest.raises(OSError):
        p.mkdir()

def test_mkdir_parents(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'newdirB' / 'newdirC'
    assert not p.exists()
    with pytest.raises(FileNotFoundError):
        p.mkdir()
    p.mkdir(parents=True)
    assert p.exists()
    assert p.is_dir()
    with pytest.raises(FileExistsError):
        p.mkdir(parents=True)
    mode = stat.S_IMODE(p.stat().st_mode)  # Default mode.
    p = root / 'newdirD' / 'newdirE'
    p.mkdir(0o555, parents=True)
    assert p.exists()
    assert p.is_dir()
    assert stat.S_IMODE(p.stat().st_mode) == 0o7555 & mode
    assert stat.S_IMODE(p.parent.stat().st_mode) == mode

def test_mkdir_exist_ok(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'dirB'
    st_ctime_first = p.stat().st_ctime
    assert p.exists()
    assert p.is_dir()
    with pytest.raises(FileExistsError):
        p.mkdir()
    p.mkdir(exist_ok=True)
    assert p.exists()
    assert p.stat().st_ctime == st_ctime_first

def test_mkdir_exist_ok_with_parent(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'dirC'
    assert p.exists()
    with pytest.raises(FileExistsError):
        p.mkdir()
    p = p / 'newdirC'
    p.mkdir(parents=True)
    st_ctime_first = p.stat().st_ctime
    assert p.exists()
    with pytest.raises(FileExistsError):
        p.mkdir(parents=True)
    p.mkdir(parents=True, exist_ok=True)
    assert p.exists()
    assert p.stat().st_ctime == st_ctime_first


def test_mkdir_with_child_file(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'dirB' / 'fileB'
    assert p.exists()
    with pytest.raises(FileExistsError):
        p.mkdir(parents=True)
    with pytest.raises(FileExistsError):
        p.mkdir(parents=True, exist_ok=True)


def test_mkdir_no_parents_file(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    p = root / 'fileA'
    assert p.exists()
    with pytest.raises(FileExistsError):
        p.mkdir()
    with pytest.raises(FileExistsError):
        p.mkdir(exist_ok=True)


def test_symlink_to(root):
    if not has_support(root, "create"):
        pytest.skip("No create support")
    if not has_support(root, "symlink"):
        pytest.skip("No symlink support")
    target = root / 'fileA'
    # Symlinking a path target.
    link = root / 'dirA' / 'linkAA'
    link.symlink_to(target)
    assert link.stat() == target.stat()
    assert link.lstat() != target.stat()
    # Symlinking a str target.
    link = root / 'dirA' / 'linkAAA'
    link.symlink_to(str(target))
    assert link.stat() == target.stat()
    assert link.lstat() != target.stat()
    assert not link.is_dir()
    # Symlinking to a directory.
    target = root / 'dirB'
    link = root / 'dirA' / 'linkAAAA'
    link.symlink_to(target, target_is_directory=True)
    assert link.stat() == target.stat()
    assert link.lstat() != target.stat()
    assert link.is_dir()
    assert list(link.iterdir())


def test_is_dir(root):
    assert (root / 'dirA').is_dir()
    assert not (root / 'fileA').is_dir()
    assert not (root / 'non-existing').is_dir()
    assert not (root / 'fileA' / 'bah').is_dir()
    if has_support(root, "symlink"):
        assert not (root / 'linkA').is_dir()
        assert (root / 'linkB').is_dir()
        assert not (root / 'brokenLink').is_dir()


def test_is_file(root):
    assert (root / 'fileA').is_file()
    assert not (root / 'dirA').is_file()
    assert not (root / 'non-existing').is_file()
    assert not (root / 'fileA' / 'bah').is_file()
    if has_support(root, "symlink"):
        assert (root / 'linkA').is_file()
        assert not (root / 'linkB').is_file()
        assert not (root / 'brokenLink').is_file()


def test_is_mount(root):
    assert not (root / 'fileA').is_mount()
    assert not (root / 'dirA').is_mount()
    assert not (root / 'non-existing').is_mount()
    assert not (root / 'fileA' / 'bah').is_mount()
    if has_support(root, "symlink"):
        assert not (root / 'linkA').is_mount()


def test_is_symlink(root):
    assert not (root / 'fileA').is_symlink()
    assert not (root / 'dirA').is_symlink()
    assert not (root / 'non-existing').is_symlink()
    assert not (root / 'fileA' / 'bah').is_symlink()
    if has_support(root, "symlink"):
        assert (root / 'linkA').is_symlink()
        assert (root / 'linkB').is_symlink()
        assert (root / 'brokenLink').is_symlink()


def test_is_fifo_false(root):
    assert not (root / 'fileA').is_fifo()
    assert not (root / 'dirA').is_fifo()
    assert not (root / 'non-existing').is_fifo()
    assert not (root / 'fileA' / 'bah').is_fifo()


def test_is_socket_false(root):
    assert not (root / 'fileA').is_socket()
    assert not (root / 'dirA').is_socket()
    assert not (root / 'non-existing').is_socket()
    assert not (root / 'fileA' / 'bah').is_socket()


def test_is_block_device_false(root):
    assert not (root / 'fileA').is_block_device()
    assert not (root / 'dirA').is_block_device()
    assert not (root / 'non-existing').is_block_device()
    assert not (root / 'fileA' / 'bah').is_block_device()


def test_is_char_device_false(root):
    assert not (root / 'fileA').is_char_device()
    assert not (root / 'dirA').is_char_device()
    assert not (root / 'non-existing').is_char_device()
    assert not (root / 'fileA' / 'bah').is_char_device()

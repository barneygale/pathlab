import contextlib
import datetime
import functools
import pathlab
import requests


def parse_time(string):
    return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f%z')


class RtPath(pathlab.Path):
    __slots__ = ()


class RtAccessor(pathlab.Accessor):
    """
    Accessor for JFrog Artifactory.

    :param url: specifies the Artifactory base URL (excluding the repo name)
    :param cache_size: specifies the size of the LRU cache to use for
        ``stat()`` results. Set to ``0`` to disable caching.
    """

    factory = RtPath

    def __init__(self, url, cache_size=1024):
        self.url = url.rstrip("/")
        self.sess = requests.Session()
        if cache_size:
            self.stat = functools.lru_cache(cache_size)(self.stat)

    def __repr__(self):
        return "RtAccessor(%r)" % self.url

    @contextlib.contextmanager
    def open(self, path, mode="r", buffering=-1):
        if mode == "r":
            url = self.url +  str(path.absolute())
            response = self.sess.get(url, stream=True)
            if response.status_code == 404:
                return self.not_found(path)
            response.raise_for_status()
            yield response.raw  # FIXME: this isn't seekable
        else:
            raise NotImplementedError

    def stat(self, path, *, follow_symlinks=True):
        path = path.absolute()
        if path.anchor == str(path):
            return self.stat_root()

        url = self.url + "/api/storage" + str(path)
        response = self.sess.get(url)
        if response.status_code == 404:
            return self.not_found(path)
        response.raise_for_status()
        data = response.json()
        return pathlab.Stat(
            type='file' if 'size' in data else 'dir',
            size=int(data.get('size', 0)),
            create_time=parse_time(data['created']),
            modify_time=parse_time(data['lastModified']),
            create_user=data.get('createdBy'),
            modify_user=data.get('modifiedBy'),
            children=[child['uri'][1:] for child in data.get('children', [])])

    def stat_root(self):
        url = self.url + "/api/repositories"
        response = self.sess.get(url)
        response.raise_for_status()
        data = response.json()
        return pathlab.Stat(
            type='dir',
            children=[child['key'] for child in data])

    def listdir(self, path):
        stat = self.stat(path)
        if stat.type != 'dir':
            return self.not_a_directory(path)
        return stat.children

    # TODO: open(..., "w")
    # TODO: mkdir()
    # TODO: rmdir() / unlink()
    # TODO: rename()
    # TODO: upload()
    # TODO: download()
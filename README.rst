=======
Pathlab
=======

|pypi| |docs|

Pathlab provides an object-oriented path interface to archives, images, remote
filesystems, etc. It is built upon pathlib_ and includes built-in support for:

- ``tar`` archives
- ``zip`` archives
- ``iso`` disc images (via ``pycdlib``)
- JFrog Artifactory (via ``requests``)

You can also define your own ``Path`` subclass with its own accessor.

Installation
------------

Requires Python 3.6+. Use pip::

    pip install --user pathlab

Usage
-----

These usage examples are adapted from the pathlib_ documentation.

Getting a path type:

    >>> from pathlab import TarAccessor
    >>> TarPath = TarAccessor('project.tgz').TarPath

Listing subdirectories:

    >>> root = TarPath('/')
    >>> [x for x in root.iterdir() if x.is_dir()]
    [TarAccessor('project.tgz').TarPath('/docs')
     TarAccessor('project.tgz').TarPath('/etc'),
     TarAccessor('project.tgz').TarPath('/project')]

Listing Python source files in this directory tree:

    >>> list(root.glob('**/*.py'))
    [TarAccessor('project.tgz').TarPath('/setup.py'),
     TarAccessor('project.tgz').TarPath('/docs/conf.py'),
     TarAccessor('project.tgz').TarPath('/project/__init__.py')]

Navigating inside a directory tree:

    >>> p = TarPath('/etc')
    >>> q = p / 'init.d' / 'reboot'
    >>> q
    TarAccessor('project.tgz').TarPath('/etc/init.d/reboot')
    >>> q.resolve()
    TarAccessor('project.tgz').TarPath('/etc/rc.d/init.d/halt')

Querying path properties:

    >>> q.exists()
    True
    >>> q.is_dir()
    False

Opening a file:

    >>> with q.open() as f: f.readline()
    ...
    '#!/bin/bash\n'


.. _pathlib: https://docs.python.org/3/library/pathlib.html

.. |pypi| image:: https://img.shields.io/pypi/v/pathlab.svg
    :target: https://pypi.python.org/pypi/pathlab
    :alt: Latest version released on PyPi

.. |docs| image:: https://readthedocs.org/projects/pathlab/badge/?version=latest
    :target: http://pathlab.readthedocs.io/en/latest
    :alt: Documentation

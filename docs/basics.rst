Using Pathlab
=============

Use the Python standard library's :mod:`pathlib` module to interact with the
local filesystem::

    >>> import pathlib
    >>> etc = pathlib.Path('/etc')
    >>> etc.exists()
    True

Tar Archives
~~~~~~~~~~~~

Use a :class:`pathlab.TarAccessor` object to interact with a ``tar`` file::

    >>> import pathlab
    >>> archive = pathlab.TarAccessor('myproject.tar.gz')
    >>> root = archive.TarPath('/')
    >>> readme = root / 'readme.txt'
    >>> readme.exists()
    True

Zip Archives
~~~~~~~~~~~~

Use a :class:`pathlab.ZipAccessor` object to interact with a ``zip`` file::

    >>> import pathlab
    >>> archive = pathlab.ZipAccessor('myproject.zip')
    >>> root = archive.ZipPath('/')
    >>> readme = root / 'readme.txt'
    >>> readme.exists()
    True


Iso Images
~~~~~~~~~~

Use an :class:`pathlab.IsoAccessor` object to interact with an ``iso`` file::

    >>> import pathlab
    >>> disk = pathlab.IsoAccessor('myproject.iso')
    >>> root = disc.IsoPath('/')
    >>> readme = root / 'readme.txt'
    >>> readme.exists()
    True

Artifactory Instances
~~~~~~~~~~~~~~~~~~~~~


Use an :class:`pathlab.RtAccessor` object to interact with a JFrog Artifactory
instance::

    >>> import pathlab
    >>> rt = pathlab.RtAccessor('http://artifactory/')
    >>> repo = rt.RtPath('/myproject/latest')
    >>> readme = repo / 'readme.txt'
    >>> readme.exists()
    True

.. seealso::

    See the :doc:`api` and :mod:`pathlib` documentation for more detail!

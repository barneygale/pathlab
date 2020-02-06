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

    >>> from pathlab.tar import TarAccessor
    >>> archive = TarAccessor('thing.tar')
    >>> readme = archive.TarPath('/readme.txt')
    >>> readme.exists()
    True

Zip Archives
~~~~~~~~~~~~

Use a :class:`pathlab.ZipAccessor` object to interact with a ``zip`` file::

    >>> from pathlab.zip import ZipAccessor
    >>> archive = ZipAccessor('thing.zip')
    >>> readme = archive.ZipPath('/readme.txt')
    >>> readme.exists()
    True


Iso Images
~~~~~~~~~~

Use an :class:`pathlab.IsoAccessor` object to interact with an ``iso`` file::

    >>> from pathlab.iso import IsoAccessor
    >>> disc = IsoAccessor('thing.iso')
    >>> readme = disc.IsoPath('/readme.txt')
    >>> readme.exists()
    True

Artifactory Instances
~~~~~~~~~~~~~~~~~~~~~


Use an :class:`pathlab.RtAccessor` object to interact with a JFrog Artifactory
instance::

    >>> from pathlab.rt import RtAccessor
    >>> rt = RtAccessor('http://artifactory/')
    >>> readme = rt.RtPath('/myrepo/latest/readme.txt')
    >>> readme.exists()
    True

.. seealso::

    See the :doc:`api` and :mod:`pathlib` documentation for more detail!

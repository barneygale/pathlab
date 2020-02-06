Extending Pathlab
=================

.. currentmodule:: pathlab

Here's how you can create your own path-like class by subclassing :class:`Path`
and :class:`Accessor`::

    import pathlab

    class MyPath(pathlab.Path):
        pass

    class MyAccessor(pathlab.Accessor):
        factory = MyPath

        def __repr__(self):
            return "MyAccessor()"

At this point we can instantiate our accessor, which acts like a module with a
``MyPath`` class::

    >>> accessor = MyAccessor()
    >>> accessor
    MyAccessor()
    >>> root = accessor.MyPath("/")
    >>> root
    MyAccessor().MyPath('/')

Pure methods work as we'd expect, whereas impure methods raise
:exc:`NotImplementedError`::

    >>> docs = root / 'docs'
    >>> docs
    MyAccessor().MyPath('/docs')
    >>> docs.exists()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".../pathlib.py", line 1339, in exists
        self.stat()
      File ".../pathlib.py", line 1161, in stat
        return self._accessor.stat(self)
      File ".../pathlab/core/accessor.py", line 76, in stat
        raise NotImplementedError
    NotImplementedError

Add methods like :meth:`~Accessor.stat` and :meth:`~Accessor.listdir` to your
accessor to implement impure functionality. You can use the
:meth:`~Accessor.not_found`, :meth:`~Accessor.already_exists`,
:meth:`~Accessor.not_a_directory`, :meth:`~Accessor.is_a_directory` and
:meth:`~Accessor.permission_denied` methods to raise appropriate exceptions.
You'll also probably want to add an ``__init__()`` method that records some
state (e.g. an open file or a socket) for later use.

Refer to the pathlab source code for example accessor implementations.

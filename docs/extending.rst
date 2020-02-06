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

Now we can begin adding methods to our accessor::

    class MyAccessor(pathlab.Accessor):
        factory = MyPath

        def __repr__(self):
            return "MyAccessor(%r)" % self.children

        def __init__(self, children):
            self.children = children

        def stat(self, path):
            return pathlab.Stat(type='dir')

        def listdir(self, path):
            return self.children

Refer to the :class:`Accessor` API documentation for a full list of abstract
methods you may wish to implement. Refer to the pathlab source code for
example accessor implementations.
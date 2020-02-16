Implementation Notes
====================

Using the Accessor
------------------

The standard library's :mod:`pathlib` module already includes the notion of an
*accessor*, but it is bypassed in certain cases, such as:

- ``str(self)`` called to get a local filesystem path
- :func:`os.close` called to close file descriptors
- :func:`os.getcwd` called to get the working directory
- :func:`os.fsencode` called to get a ``bytes`` representation of a path
- :data:`os.environ` accessed to expand ``~``
- :mod:`pwd` and :mod:`grp` used to retrieve user and group names

Pathlab fixes these instances by subclassing :class:`pathlib.Path` as
:class:`pathlab.Path` and re-implementing the problematic methods. This
includes a few additions and changes to the accessor interface.

Flavouring the Accessor
-----------------------

The standard library's :mod:`pathlib` module uses a *flavour* object to handle
pure path semantics. As before, this abstraction is leaky. Pathlab makes no
distinction between the path accessor and flavour, and so allows methods like
:meth:`~Accessor.casefold()` to be re-implemented.

Binding the Accessor
--------------------

The standard library's :mod:`pathlib` module provides limited means of storing
state. A path instance may have its ``_accessor`` attribute customized, and
in *some* cases derived path instances are initialized with
``path._init(template=self)`` to make the new path use the same accessor.
However, this mechanism is used inconsistently.

Pathlab solves this by creating a new path *type* per accessor *instance*. The
accessor instance is bound to the new type as a class attribute. Therefore the
inheritance chain of an accessor's path type is as follows:

.. table:: Path inheritance chain
    :align: center
    :widths: 10 10 30

    ========  ====  ================================
    Abstract  Pure  Class
    ========  ====  ================================
    ..        ✓     :class:`pathlib.PurePath`
    ..              :class:`pathlib.Path`
    ✓         ✓     :class:`pathlab.Path`
    ✓         ✓     ``mylib.MyPath``
    ..              ``mylib.MyAccessor(...).MyPath``
    ========  ====  ================================


"""
This module contains some utility methods to make interacting with .NET easier.
"""
from contextlib import contextmanager as _contextmanager
from typing import Any as _Any, Iterator as _Iterator, TypeVar as _TypeVar

from System import IDisposable as _IDisposable

_T = _TypeVar('_T')
_DisposableT = _TypeVar('_DisposableT', bound=_IDisposable)


def clr_to_implementation(obj: object) -> _Any:
    """Return the implementation class object of a .NET object.

    If you get an interface object returned from Python.NET, it won't be the
    actual object, but an interface wrapper instead. This function will return
    you the actual object.
    """
    if hasattr(obj, '__implementation__'):
        return obj.__implementation__
    return obj


def clr_isinstance(obj: object, class_or_tuple: type | tuple[_Any, ...]) -> bool:
    """Return whether a .NET object is an instance of a class or of a subclass thereof.

    This function is more robust for .NET types compared to regular
    ``isinstance``. This is related to the fact that if a method returns an
    interface object in Python.NET, it will `actually` return an interface
    wrapper, which this function accounts for.
    """
    return isinstance(clr_to_implementation(obj), class_or_tuple)


def clr_try_cast(obj: object, typ: type[_T]) -> _T | None:
    """Cast object to the specified type, if possible. Return None otherwise.

    If a .NET function returns an interface in Python.NET, you will be able to
    only call methods of that interface. This means, that usual duck typing
    won't work. Using this function you can downcast the object to the expected
    type.
    """
    obj = clr_to_implementation(obj)
    return obj if isinstance(obj, typ) else None


def clr_cast(obj: object, typ: type[_T]) -> _T:
    """Cast object to the specified type, if possible. Raise TypeError otherwise.

    If a .NET function returns an interface in Python.NET, you will be able to
    only call methods of that interface. This means, that usual duck typing
    won't work. Using this function you can downcast the object to the expected
    type.
    """
    obj = clr_try_cast(obj, typ)
    if obj is None:
        raise TypeError('unable to cast object')
    return obj


@_contextmanager
def disposing(obj: _DisposableT) -> _Iterator[_DisposableT]:
    """Context to automatically dispose of a .NET object at the end of a block."""
    try:
        yield obj
    finally:
        _IDisposable.Dispose(obj)

"""Adapter mixin for exposing an in-memory view of a HoneyNode.

Provides LoadableMixin which lets a node present a materialised or view
representation of its children (for example: a NumPy array, pandas object,
or any heavy container) and persist changes automatically when used as a
context manager.

Usage
    with node.data() as data:
        # mutate/use data
        ...
    # on exit, changes are persisted via load_from
"""

from abc import ABC, abstractmethod
from typing import Generic, Iterator, Optional, TypeVar

P_co = TypeVar("P_co", covariant=True)
E = TypeVar("E")


class _LoadableContextManager(Generic[E, P_co]):
    """
    Context manager used by LoadableMixin.data().

    Usage:
        with node.data() as data:
            # mutate/use data
            ...

    Behaviour:
    - On __enter__: calls parent.get_data() and yields the result.
    - On normal __exit__ (no exception): calls parent.load_from(data) to persist
      changes.
    - On exceptional __exit__: if parent defines on_context_error, it will be called
      with (data, exc_type, exc_value, traceback). Exceptions are not suppressed.
    """

    _parent: "LoadableMixin[E, P_co]"
    _data: E

    def __init__(self, parent: "LoadableMixin[E, P_co]") -> None:
        self._parent = parent
        self._data = parent.get_external_data()

    def __enter__(self) -> E:
        """Enter the context and return the loaded in-memory data object."""
        base_iter = iter(self._parent)
        self._data = self._parent._get_data(base_iter)
        return self._data

    def __exit__(self, exc_type, exc_value, traceback):
        """On exit, persist data on success or notify on error.

        Return False so exceptions (if any) propagate.
        """
        if exc_type is None:
            self._parent._external_data = self._data  # type: ignore
            return False

        hook = getattr(self._parent, "on_context_error", None)
        if callable(hook):
            try:
                hook(self._data, exc_type, exc_value, traceback)
            except Exception:
                # Do not swallow the original exception
                pass

        return False


class LoadableMixin(ABC, Generic[E, P_co]):
    """
    Mixin to expose an in-memory container view for a HoneyNode subclass.

    Public API:
      - data() -> _DataContext[T]: context manager yielding the in-memory object and
        persisting it on normal exit via load_from.
    """

    _external_data: Optional[E] = None

    def data(self) -> "_LoadableContextManager[E, P_co]":
        """Return a context manager that yields the in-memory data and saves on exit."""
        return _LoadableContextManager[E, P_co](self)

    def get_external_data(self) -> E:
        """
        Return an in-memory object constructed from the node's children.

        This calls the subclass-provided _get_data with the current children
        iterator. The returned object may be a view or a materialised container.
        """
        return self._get_data(iter(self))  # type: ignore

    def __iter__(self) -> Iterator[P_co]:
        data = self._external_data
        if data is not None:
            return self.load_from(data)

        return super().__iter__()  # type: ignore

    @staticmethod
    @abstractmethod
    def _get_data(children: Iterator[P_co]) -> E:
        """
        Build and return the in-memory representation from the node's children.

        Implementations should return a container/view of type T.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def load_from(data: E) -> Iterator[P_co]:
        """
        Convert an in-memory data object back into an iterator of child items.

        The returned iterator will be passed to the base `load` method to replace
        the node's children.
        """
        raise NotImplementedError

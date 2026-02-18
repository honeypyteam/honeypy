"""Adapter mixin for exposing an in-memory view of a HoneyNode.

Provides LoadableMixin which lets a node present a materialised or view
representation of its children (for example: a NumPy array, pandas object,
or any heavy container) and persist changes automatically when used as a
context manager.

Public API
- LoadableMixin.data() -> context manager that yields the in-memory object and
  calls load_from(...) on normal exit.
- LoadableMixin.get_data() and LoadableMixin.load_from(...) bridge between the
  node's children and the in-memory container; subclasses implement the static
  helpers _get_data and _load_from.

Usage
    with node.data() as data:
        # mutate/use data
        ...
    # on exit, changes are persisted via load_from

Notes
-----
- Designed for optional adapter implementations; keep heavy dependencies out of
  the core package. Implementations should prefer provider factories / context
  managers for resource safety when streaming from files.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class _LoadableContextManager(Generic[U]):
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

    _parent: "LoadableMixin"
    _data: U

    def __init__(self, parent: "LoadableMixin[U]") -> None:
        self._parent = parent
        self._data = parent.get_data()

    def __enter__(self) -> U:
        """Enter the context and return the loaded in-memory data object."""
        return self._data

    def __exit__(self, exc_type, exc_value, traceback):
        """On exit, persist data on success or notify on error.

        Return False so exceptions (if any) propagate.
        """
        if exc_type is None:
            self._parent.load_from(self._data)
            return False

        hook = getattr(self._parent, "on_context_error", None)
        if callable(hook):
            try:
                hook(self._data, exc_type, exc_value, traceback)
            except Exception:
                # Do not swallow the original exception
                pass

        return False


class LoadableMixin(ABC, Generic[T]):
    """
    Mixin to expose an in-memory container view for a HoneyNode subclass.

    Subclasses must implement:
      - _get_data(children) -> T: build an in-memory representation from children.
      - _load_from(data) -> Iterable[Any]: convert in-memory data back into children.

    Public API:
      - data() -> _DataContext[T]: context manager yielding the in-memory object and
        persisting it on normal exit via load_from.

    Notes
    -----
    - The context manager returns a fresh in-memory object produced by get_data().
    - load_from delegates to the HoneyNode.load mechanism; implementations should
      return an iterable of child items suitable for the base class loader.
    """

    def data(self) -> "_LoadableContextManager[T]":
        """Return a context manager that yields the in-memory data and saves on exit."""
        return _LoadableContextManager[T](self)

    def load_from(self, data: T) -> None:
        """
        Persist an in-memory data object by delegating to the base loader.

        This converts `data` to an iterable of child items via _load_from and then
        calls the base class `load` to replace the node's children.
        """
        # Pragmatic decision. Types must be ignored here because parent is `HoneyNode`,
        # which is a template class. This means type info is lost, or else you'll have
        # to write the formal type parameters (metadata, tuples) each time you use a
        # LoadableMixin
        super().load(self._load_from(data))  # type: ignore

    def get_data(self) -> T:
        """
        Return an in-memory object constructed from the node's children.

        This calls the subclass-provided _get_data with the current children
        iterable. The returned object may be a view or a materialised container.
        """
        # See note in `load_from` for type ignores
        return self._get_data(self.children)  # type: ignore

    @staticmethod
    @abstractmethod
    def _get_data(children: Iterable[Any]) -> T:
        """
        Build and return the in-memory representation from the node's children.

        Implementations should return a container/view of type T.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _load_from(data: T) -> Iterable[Any]:
        """
        Convert an in-memory data object back into an iterable of child items.

        The returned iterable will be passed to the base `load` method to replace
        the node's children.
        """
        raise NotImplementedError

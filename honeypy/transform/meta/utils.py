"""Utilities for transformations and other IR helpers."""

import inspect
from typing import Any, Callable, Tuple, TypeGuard


def get_single_argument_predicate(predicate: Callable) -> Tuple[Callable, int]:
    """Normalise a predicate to a single-tuple argument form and return its arity.

    If ``predicate`` already takes exactly one positional argument, it is returned
    unchanged. Otherwise a wrapper ``wrapped(t)`` is built that calls
    ``predicate(*t)`` and the number of positional parameters is returned
    alongside the wrapped callable.
    """
    sig = inspect.signature(predicate)

    params = list(sig.parameters.values())
    if any(p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD) for p in params):
        raise TypeError("Predicate with *args/**kwargs is not supported")

    positional = [
        p for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    n_args = len(positional)

    if n_args == 1:
        return predicate, n_args

    def wrapped(t: Tuple[Any, ...]):
        return predicate(*t)

    return wrapped, n_args


def is_tuple(x: Any) -> TypeGuard[Tuple[Any, ...]]:
    """Type-guard helper to check whether ``x`` is a tuple value."""
    return isinstance(x, tuple)


def as_tuple(x: Any) -> Tuple[Any, ...]:
    """Return ``x`` as a tuple, wrapping non-tuples in a 1-length tuple."""
    match x:
        case tuple():
            return x
        case _:
            return (x,)


def expand_on_arity(val: Any, arity: int) -> tuple[Any, ...]:
    """Expand a value into a tuple according to an IR node's arity.

    For 1D sources (``arity == 1``) the value is treated as atomic and wrapped in
    a single-element tuple. For higher-arity sources the value is assumed to be an
    iterable of modalities and is converted to ``tuple(val)``.
    """
    if arity == 1:
        return (val,)
    return tuple(val)

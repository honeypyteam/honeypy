"""Data graph utilities."""

from collections.abc import Mapping
from typing import Any


def nested_intersection(
    a: Mapping[Any, Any], b: Mapping[Any, Any]
) -> Mapping[Any, Any] | None:
    """Return the deep intersection of two nested mappings.

    The intersection contains all key paths where ``a`` and ``b`` have equal
    values. Non-mapping leaves must compare equal to be kept; unequal leaves are
    dropped. If no common structure exists at a position, ``None`` is returned
    from that branch.
    """
    if not (isinstance(a, Mapping) and isinstance(b, Mapping)):
        return a if a == b else None

    result: dict[Any, Any] = {}
    for k in a.keys() & b.keys():
        v = nested_intersection(a[k], b[k])
        if v is not None:
            result[k] = v

    return result

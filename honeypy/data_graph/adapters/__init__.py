"""Adapter helpers for optional, external integrations.

This small package contains lightweight adapter primitives that let HoneyNode
subclasses expose in-memory container views (for example: numpy arrays,
pandas objects, or other optimized representations) without forcing those
heavy dependencies into the core package.

Notes
-----
Prefer adapters in separate, optional packages so your plugin remains dependency
free. The same goes for the core package itself. Adapter code should register any
additional transforms or helper factories separately.
"""

from .loadable_mixin import LoadableMixin

__all__ = ["LoadableMixin"]

__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"

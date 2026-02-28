"""
Package containing the bootstrapper.

The bootstrapper starts the application and sets up the necessary services. This
includes the data graph DAG as well as the associated node factory.
"""

from .bootstrap import bootstrap

__all__ = [
    "bootstrap",
]

__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"

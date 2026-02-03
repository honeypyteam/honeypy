"""HoneyPy: A lightweight, extensible framework for research data management.

This package provides a plugin architecture for managing research data, analyses,
and provenance. It serves as a core library that research teams can extend with
domain-specific functionality through plugins that inherit from the HoneyPy ABC.

The framework handles common research needs including data storage, anonymization,
transformation, analysis, and summarization across multiple datasets and projects.
"""

from .honeypy import HoneyPy
from .hypergraph import *

__version__ = "0.1.0"
__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"

__all__ = ["HoneyPy"]

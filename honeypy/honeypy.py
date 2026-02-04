"""Core module defining the HoneyPy abstract base class.

This module contains the HoneyPy ABC that serves as the foundation for all
research data management plugins. Plugins inherit from this class to provide
domain-specific functionality while maintaining a consistent interface.
"""

import uuid
from abc import ABC, abstractmethod


class HoneyPy(ABC):
    """An abstract base class for creating research data management plugins.

    This class serves as the foundation for domain-specific research packages
    that transform data in some way. Storage, anonymization, provenance, and more
    is handled by the HoneyPy class itself.

    Each plugin should inherit from this class and implement the required
    abstract methods.
    """

    @abstractmethod
    def package_id(self) -> uuid.UUID:
        """Return a unique plugin identifier.

        Returns
        -------
            uuid.UUID: A unique identifier for this plugin (e.g., 'linguistics_nlp',
                'medical_imaging').

        Note:
            This identifier should never, ever be changed once published,
            as it may be used for data provenance and plugin discovery.
        """
        raise NotImplementedError

    @abstractmethod
    def package_name(self) -> str:
        """Return human-readable name for the plugin.

        Returns
        -------
            str: A descriptive name for this plugin (e.g., 'Audio Processor',
                'Medical Imaging Pipeline').
        """
        raise NotImplementedError

    @abstractmethod
    def cli_name(self) -> str:
        """Return command-line name for the plugin.

        Commands associated with this plugin will use this name as a prefix
        or identifier in the command-line interface.

        Returns
        -------
            str: A descriptive command line name for this plugin (e.g.,
                'audio-processor', 'mip').
        """
        raise NotImplementedError

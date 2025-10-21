"""
Base Linker Interface
Abstract base class for all LOD entity linkers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseLinker(ABC):
    """
    Abstract base class for Linked Open Data entity linkers.
    All LOD source linkers must implement this interface.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize linker with optional configuration.

        Args:
            config: Optional configuration dictionary (API keys, endpoints, etc.)
        """
        self.config = config or {}
        self.source_name = self.get_source_name()
        logger.debug(f"Initialized {self.source_name} linker")

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Return the name of the LOD source.

        Returns:
            Source name (e.g., 'wikidata', 'dbpedia', 'esco')
        """
        pass

    @abstractmethod
    def link(self, entity_name: str, entity_type: Optional[str] = None) -> Optional[str]:
        """
        Link entity to LOD source and return URI.

        Args:
            entity_name: Name of entity to link
            entity_type: Optional type hint for better matching

        Returns:
            URI of linked entity or None if not found
        """
        pass

    def batch_link(self, entity_names: list[str], entity_type: Optional[str] = None) -> Dict[str, Optional[str]]:
        """
        Link multiple entities in batch.

        Args:
            entity_names: List of entity names to link
            entity_type: Optional type hint for all entities

        Returns:
            Dictionary mapping entity names to URIs
        """
        results = {}
        for entity_name in entity_names:
            results[entity_name] = self.link(entity_name, entity_type)

        logger.info(f"{self.source_name}: Batch linked {len(entity_names)} entities")
        return results

    def validate_uri(self, uri: str) -> bool:
        """
        Validate that a URI is from the expected LOD source.

        Args:
            uri: URI to validate

        Returns:
            True if valid, False otherwise
        """
        return uri is not None and isinstance(uri, str) and uri.startswith("http")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return metadata about this linker.

        Returns:
            Dictionary with linker metadata
        """
        return {
            "source": self.source_name,
            "config": self.config,
            "type": self.__class__.__name__
        }

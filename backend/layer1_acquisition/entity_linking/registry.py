"""
Linker Registry
Manages and provides access to all available LOD linkers.
"""

from typing import Dict, Optional, List, Type, Any
import logging
from .base_linker import BaseLinker
from .wikidata_linker import WikidataLinker
from .dbpedia_linker import DBpediaLinker
from .openuniversity_linker import OpenUniversityLinker
from .linkeduniversities_linker import LinkedUniversitiesLinker
from .esco_linker import ESCOLinker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkerRegistry:
    """
    Registry for managing LOD entity linkers.
    Provides plugin-style extensibility for adding new LOD sources.
    """

    def __init__(self):
        self._linkers: Dict[str, BaseLinker] = {}
        self._linker_classes: Dict[str, Type[BaseLinker]] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._register_default_linkers()

    def _register_default_linkers(self):
        """Register built-in LOD linkers."""
        self.register_linker_class("wikidata", WikidataLinker)
        self.register_linker_class("dbpedia", DBpediaLinker)
        self.register_linker_class("openuniversity", OpenUniversityLinker)
        self.register_linker_class("linkeduniversities", LinkedUniversitiesLinker)
        self.register_linker_class("esco", ESCOLinker)

        logger.info("Registered default LOD linkers")

    def register_linker_class(self, name: str, linker_class: Type[BaseLinker]):
        """
        Register a new linker class.

        Args:
            name: Unique identifier for the linker
            linker_class: Class that extends BaseLinker
        """
        if not issubclass(linker_class, BaseLinker):
            raise ValueError(f"Linker class must extend BaseLinker: {linker_class}")

        self._linker_classes[name] = linker_class
        logger.debug(f"Registered linker class: {name}")

    def register_linker_instance(self, name: str, linker: BaseLinker):
        """
        Register a pre-configured linker instance.

        Args:
            name: Unique identifier for the linker
            linker: Initialized linker instance
        """
        if not isinstance(linker, BaseLinker):
            raise ValueError(f"Linker must be instance of BaseLinker: {linker}")

        self._linkers[name] = linker
        logger.debug(f"Registered linker instance: {name}")

    def set_linker_config(self, name: str, config: Dict[str, Any]):
        """
        Set configuration for a linker.

        Args:
            name: Linker identifier
            config: Configuration dictionary
        """
        self._configs[name] = config
        logger.debug(f"Set config for linker: {name}")

    def get_linker(self, name: str) -> Optional[BaseLinker]:
        """
        Get a linker instance by name.
        Creates instance on first access if only class is registered.

        Args:
            name: Linker identifier

        Returns:
            Linker instance or None
        """
        if name in self._linkers:
            return self._linkers[name]

        if name in self._linker_classes:
            config = self._configs.get(name, {})
            linker = self._linker_classes[name](config=config)
            self._linkers[name] = linker
            logger.debug(f"Instantiated linker: {name}")
            return linker

        logger.warning(f"Linker not found: {name}")
        return None

    def get_all_linkers(self) -> Dict[str, BaseLinker]:
        """
        Get all registered linker instances.

        Returns:
            Dictionary mapping names to linker instances
        """
        linkers = {}
        for name in self._linker_classes.keys():
            linkers[name] = self.get_linker(name)
        return linkers

    def list_available_linkers(self) -> List[str]:
        """
        List names of all available linkers.

        Returns:
            List of linker names
        """
        return list(self._linker_classes.keys())

    def unregister_linker(self, name: str):
        """
        Remove a linker from the registry.

        Args:
            name: Linker identifier
        """
        if name in self._linkers:
            del self._linkers[name]
        if name in self._linker_classes:
            del self._linker_classes[name]
        if name in self._configs:
            del self._configs[name]

        logger.debug(f"Unregistered linker: {name}")

    def has_linker(self, name: str) -> bool:
        """
        Check if a linker is registered.

        Args:
            name: Linker identifier

        Returns:
            True if registered, False otherwise
        """
        return name in self._linker_classes or name in self._linkers

    def get_linker_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a registered linker.

        Args:
            name: Linker identifier

        Returns:
            Metadata dictionary or None
        """
        linker = self.get_linker(name)
        if linker:
            return linker.get_metadata()
        return None

    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the registry state.

        Returns:
            Dictionary with registry information
        """
        return {
            "total_linkers": len(self._linker_classes),
            "instantiated_linkers": len(self._linkers),
            "available_linkers": self.list_available_linkers(),
            "configured_linkers": list(self._configs.keys())
        }


# Global registry instance
_global_registry = None


def get_registry() -> LinkerRegistry:
    """
    Get the global linker registry instance.

    Returns:
        Global LinkerRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = LinkerRegistry()
        logger.debug("Created global linker registry")
    return _global_registry


def reset_registry():
    """Reset the global registry (useful for testing)."""
    global _global_registry
    _global_registry = None
    logger.debug("Reset global linker registry")

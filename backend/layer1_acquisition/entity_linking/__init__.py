"""
Entity Linking Module

Provides entity linking capabilities to multiple Linked Open Data sources.
"""

from .entity_linker import EntityLinker
from .base_linker import BaseLinker
from .wikidata_linker import WikidataLinker
from .dbpedia_linker import DBpediaLinker
from .esco_linker import ESCOLinker
from .openuniversity_linker import OpenUniversityLinker
from .linkeduniversities_linker import LinkedUniversitiesLinker
from .registry import LinkerRegistry, get_registry, reset_registry

__all__ = [
    "EntityLinker",
    "BaseLinker",
    "WikidataLinker",
    "DBpediaLinker",
    "ESCOLinker",
    "OpenUniversityLinker",
    "LinkedUniversitiesLinker",
    "LinkerRegistry",
    "get_registry",
    "reset_registry",
]

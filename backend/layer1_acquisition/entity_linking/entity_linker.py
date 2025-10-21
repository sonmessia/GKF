"""
Entity Linker
Links local entities to global URIs from multiple LOD sources.

This module provides a unified interface for linking entities to various
Linked Open Data sources including Wikidata, DBpedia, ESCO, Open University,
and LinkedUniversities.

Architecture:
- Uses a registry-based design for extensibility
- Supports multiple LOD sources through modular linkers
- Maintains backward compatibility with legacy API
"""

from typing import Dict, List, Optional, Any
from rdflib import URIRef, Namespace, Literal, XSD
import logging
from .registry import get_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityLinker:
    """
    Links local knowledge graph entities to Linked Open Data sources.

    Supports multiple LOD sources:
    - Wikidata: General knowledge base
    - DBpedia: Structured data from Wikipedia
    - ESCO: European Skills, Competences, Qualifications and Occupations
    - Open University: Academic courses and programs
    - LinkedUniversities: Global university and course data

    The linker uses a registry-based architecture for easy extensibility.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize EntityLinker with optional configuration.

        Args:
            config: Optional configuration for linkers
                   Format: {'linker_name': {'param': 'value'}}
        """
        self.registry = get_registry()
        self.config = config or {}

        if self.config:
            for linker_name, linker_config in self.config.items():
                if self.registry.has_linker(linker_name):
                    self.registry.set_linker_config(linker_name, linker_config)

        logger.debug(
            f"Initialized EntityLinker with {len(self.registry.list_available_linkers())} sources"
        )

    def link_to_wikidata(
        self, entity_name: str, entity_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Search Wikidata for entity and return best match URI.

        Args:
            entity_name: Name of entity (e.g., "Python", "Machine Learning")
            entity_type: Optional type hint (e.g., "programming language", "concept")

        Returns:
            Wikidata URI (e.g., "http://www.wikidata.org/entity/Q28865") or None
        """
        linker = self.registry.get_linker("wikidata")
        if linker:
            return linker.link(entity_name, entity_type)
        return None

    def link_to_dbpedia(
        self, entity_name: str, entity_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Search DBpedia for entity and return best match URI.

        Args:
            entity_name: Name of entity
            entity_type: Optional type hint

        Returns:
            DBpedia URI (e.g., "http://dbpedia.org/resource/Python_(programming_language)") or None
        """
        linker = self.registry.get_linker("dbpedia")
        if linker:
            return linker.link(entity_name, entity_type)
        return None

    def link_to_esco(
        self, entity_name: str, entity_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Search ESCO for entity and return best match URI.

        Args:
            entity_name: Name of entity (skill, occupation, qualification)
            entity_type: Type hint ('skill', 'occupation', 'qualification')

        Returns:
            ESCO URI or None
        """
        linker = self.registry.get_linker("esco")
        if linker:
            return linker.link(entity_name, entity_type)
        return None

    def link_to_openuniversity(
        self, entity_name: str, entity_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Search Open University LOD for entity and return URI.

        Args:
            entity_name: Name of entity (course, qualification)
            entity_type: Type hint ('course', 'qualification', 'unit')

        Returns:
            Open University URI or None
        """
        linker = self.registry.get_linker("openuniversity")
        if linker:
            return linker.link(entity_name, entity_type)
        return None

    def link_to_linkeduniversities(
        self, entity_name: str, entity_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Search LinkedUniversities for entity and return URI.

        Args:
            entity_name: Name of entity (university, course, program)
            entity_type: Type hint ('university', 'course', 'program', 'module')

        Returns:
            LinkedUniversities URI or None
        """
        linker = self.registry.get_linker("linkeduniversities")
        if linker:
            return linker.link(entity_name, entity_type)
        return None

    def link_entity(
        self,
        entity_name: str,
        entity_type: Optional[str] = None,
        sources: Optional[List[str]] = None,
        prefer_source: str = "wikidata",
    ) -> Dict[str, Optional[str]]:
        """
        Link entity to multiple LOD sources.

        Args:
            entity_name: Name of entity to link
            entity_type: Optional type hint for better matching
            sources: List of LOD sources to query (default: all available)
            prefer_source: Preferred source to try first

        Returns:
            Dictionary with linked URIs: {'wikidata': ..., 'dbpedia': ..., 'esco': ...}
        """
        if sources is None:
            sources = ["wikidata", "dbpedia"]

        links = {}

        prioritized_sources = [prefer_source] + [
            s for s in sources if s != prefer_source
        ]

        for source in prioritized_sources:
            linker = self.registry.get_linker(source)
            if linker:
                uri = linker.link(entity_name, entity_type)
                links[source] = uri
            else:
                links[source] = None
                logger.warning(f"Linker not available: {source}")

        return links

    def link_entity_to_source(
        self, entity_name: str, source: str, entity_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Link entity to a specific LOD source.

        Args:
            entity_name: Name of entity to link
            source: LOD source identifier
            entity_type: Optional type hint

        Returns:
            URI from the specified source or None
        """
        linker = self.registry.get_linker(source)
        if linker:
            return linker.link(entity_name, entity_type)

        logger.error(f"Linker not found: {source}")
        return None

    def batch_link_entities(
        self, entity_names: List[str], sources: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Link multiple entities in batch.

        Args:
            entity_names: List of entity names
            sources: List of LOD sources to query

        Returns:
            Dictionary mapping entity names to their linked URIs
        """
        results = {}

        for entity_name in entity_names:
            results[entity_name] = self.link_entity(entity_name, sources=sources)

        logger.info(
            f"Batch linked {len(entity_names)} entities across {len(sources or ['wikidata', 'dbpedia'])} sources"
        )
        return results

    def enrich_graph_with_links(
        self,
        graph,
        entity_uris: Dict[str, URIRef],
        entity_names: Dict[URIRef, str],
        sources: Optional[List[str]] = None,
    ):
        """
        Enrich an RDF graph with LOD links from multiple sources.

        Args:
            graph: RDFLib Graph object
            entity_uris: Map of entity IDs to URIRefs
            entity_names: Map of URIRefs to entity names
            sources: List of LOD sources to link (default: wikidata, dbpedia)

        Returns:
            Enriched graph
        """
        if sources is None:
            sources = ["wikidata", "dbpedia"]

        gkf = Namespace("http://gkf.org/ontology/it#")

        property_mapping = {
            "wikidata": gkf.wikidataURI,
            "dbpedia": gkf.dbpediaURI,
            "esco": gkf.escoURI,
            "openuniversity": gkf.openUniversityURI,
            "linkeduniversities": gkf.linkedUniversitiesURI,
        }

        for entity_uri, entity_name in entity_names.items():
            links = self.link_entity(entity_name, sources=sources)

            for source, uri in links.items():
                if uri and source in property_mapping:
                    graph.add(
                        (
                            entity_uri,
                            property_mapping[source],
                            Literal(uri, datatype=XSD.anyURI),
                        )
                    )

        logger.info(f"Enriched graph with LOD links from {len(sources)} sources")
        return graph

    def get_available_sources(self) -> List[str]:
        """
        Get list of available LOD sources.

        Returns:
            List of source identifiers
        """
        return self.registry.list_available_linkers()

    def get_source_metadata(self, source: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a specific LOD source.

        Args:
            source: Source identifier

        Returns:
            Metadata dictionary or None
        """
        return self.registry.get_linker_metadata(source)

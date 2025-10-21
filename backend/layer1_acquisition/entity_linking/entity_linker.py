"""
Entity Linker
Links local entities to global URIs (Wikidata, DBpedia) using NLP and API queries.
"""

import requests
from typing import Dict, List, Optional
from rdflib import URIRef
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityLinker:
    """
    Links local knowledge graph entities to Linked Open Data sources.
    Supports: Wikidata, DBpedia
    """

    def __init__(self):
        self.wikidata_api = "https://www.wikidata.org/w/api.php"
        self.dbpedia_lookup = "https://lookup.dbpedia.org/api/search"

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
        try:
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": entity_name,
                "limit": 5,
            }

            response = requests.get(self.wikidata_api, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "search" in data and data["search"]:
                # Return first match (best result)
                best_match = data["search"][0]
                wikidata_id = best_match["id"]
                wikidata_uri = f"http://www.wikidata.org/entity/{wikidata_id}"

                logger.info(f"Linked '{entity_name}' to Wikidata: {wikidata_uri}")
                return wikidata_uri

            logger.warning(f"No Wikidata match found for '{entity_name}'")
            return None

        except Exception as e:
            logger.error(f"Wikidata linking failed for '{entity_name}': {e}")
            return None

    def link_to_dbpedia(self, entity_name: str, max_results: int = 1) -> Optional[str]:
        """
        Search DBpedia for entity and return best match URI.

        Args:
            entity_name: Name of entity
            max_results: Number of results to return

        Returns:
            DBpedia URI (e.g., "http://dbpedia.org/resource/Python_(programming_language)") or None
        """
        try:
            params = {"query": entity_name, "format": "json", "maxResults": max_results}

            response = requests.get(self.dbpedia_lookup, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "docs" in data and data["docs"]:
                best_match = data["docs"][0]
                dbpedia_uri = (
                    best_match["resource"][0]
                    if isinstance(best_match["resource"], list)
                    else best_match["resource"]
                )

                logger.info(f"Linked '{entity_name}' to DBpedia: {dbpedia_uri}")
                return dbpedia_uri

            logger.warning(f"No DBpedia match found for '{entity_name}'")
            return None

        except Exception as e:
            logger.error(f"DBpedia linking failed for '{entity_name}': {e}")
            return None

    def link_entity(
        self, entity_name: str, prefer_source: str = "wikidata"
    ) -> Dict[str, Optional[str]]:
        """
        Link entity to multiple LOD sources.

        Args:
            entity_name: Name of entity to link
            prefer_source: Preferred source ('wikidata' or 'dbpedia')

        Returns:
            Dictionary with linked URIs: {'wikidata': ..., 'dbpedia': ...}
        """
        links = {"wikidata": None, "dbpedia": None}

        if prefer_source == "wikidata":
            links["wikidata"] = self.link_to_wikidata(entity_name)
            if not links["wikidata"]:
                links["dbpedia"] = self.link_to_dbpedia(entity_name)
        else:
            links["dbpedia"] = self.link_to_dbpedia(entity_name)
            if not links["dbpedia"]:
                links["wikidata"] = self.link_to_wikidata(entity_name)

        return links

    def batch_link_entities(
        self, entity_names: List[str]
    ) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Link multiple entities in batch.

        Args:
            entity_names: List of entity names

        Returns:
            Dictionary mapping entity names to their linked URIs
        """
        results = {}

        for entity_name in entity_names:
            results[entity_name] = self.link_entity(entity_name)

        logger.info(f"Batch linked {len(entity_names)} entities")
        return results

    def enrich_graph_with_links(
        self, graph, entity_uris: Dict[str, URIRef], entity_names: Dict[URIRef, str]
    ):
        """
        Enrich an RDF graph with LOD links.

        Args:
            graph: RDFLib Graph object
            entity_uris: Map of entity IDs to URIRefs
            entity_names: Map of URIRefs to entity names
        """
        from rdflib import Namespace, Literal, XSD

        gkf = Namespace("http://gkf.org/ontology/it#")

        for entity_uri, entity_name in entity_names.items():
            links = self.link_entity(entity_name)

            if links["wikidata"]:
                graph.add(
                    (
                        entity_uri,
                        gkf.wikidataURI,
                        Literal(links["wikidata"], datatype=XSD.anyURI),
                    )
                )

            if links["dbpedia"]:
                graph.add(
                    (
                        entity_uri,
                        gkf.dbpediaURI,
                        Literal(links["dbpedia"], datatype=XSD.anyURI),
                    )
                )

        logger.info(f"Enriched graph with LOD links")
        return graph

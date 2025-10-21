"""
Wikidata Linker
Links entities to Wikidata using the Wikidata Search API.
"""

import requests
from typing import Optional, Dict, Any
import logging
from .base_linker import BaseLinker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikidataLinker(BaseLinker):
    """
    Links entities to Wikidata (https://www.wikidata.org).
    Uses Wikidata Search API for entity resolution.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_endpoint = self.config.get(
            "api_endpoint", "https://www.wikidata.org/w/api.php"
        )

        self.entity_data_endpoint = self.config.get(
            "entity_data_endpoint", "https://www.wikidata.org/wiki/Special:EntityData/"
        )

        self.sparql_endpoint = self.config.get(
            "sparql_endpoint", "https://query.wikidata.org/sparql"
        )
        self.timeout = self.config.get("timeout", 10)
        self.max_results = self.config.get("max_results", 5)

    def get_source_name(self) -> str:
        return "wikidata"

    def link(
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
                "limit": self.max_results,
            }

            response = requests.get(
                self.api_endpoint, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if "search" in data and data["search"]:
                best_match = self._select_best_match(
                    data["search"], entity_name, entity_type
                )
                if best_match:
                    wikidata_id = best_match["id"]
                    wikidata_uri = f"http://www.wikidata.org/entity/{wikidata_id}"

                    logger.info(f"Linked '{entity_name}' to Wikidata: {wikidata_uri}")
                    return wikidata_uri

            logger.warning(f"No Wikidata match found for '{entity_name}'")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Wikidata API request failed for '{entity_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Wikidata linking failed for '{entity_name}': {e}")
            return None

    def _select_best_match(
        self, results: list, entity_name: str, entity_type: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Select best match from search results based on relevance.

        Args:
            results: List of search results from Wikidata
            entity_name: Original entity name
            entity_type: Optional type hint for filtering

        Returns:
            Best matching result or None
        """
        if not results:
            return None

        if entity_type:
            for result in results:
                description = result.get("description", "").lower()
                if entity_type.lower() in description:
                    return result

        return results[0]

    def get_entity_details(self, wikidata_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about a Wikidata entity.

        Args:
            wikidata_id: Wikidata entity ID (e.g., "Q28865")

        Returns:
            Dictionary with entity details or None
        """
        try:
            params = {
                "action": "wbgetentities",
                "format": "json",
                "ids": wikidata_id,
                "languages": "en",
            }

            response = requests.get(
                self.api_endpoint, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if "entities" in data and wikidata_id in data["entities"]:
                return data["entities"][wikidata_id]

            return None

        except Exception as e:
            logger.error(f"Failed to fetch Wikidata details for {wikidata_id}: {e}")
            return None

    def query_sparql(self, sparql_query: str) -> Optional[Dict[str, Any]]:
        """
        Execute a SPARQL query against the Wikidata SPARQL endpoint.

        Args:
            sparql_query: A string containing the full SPARQL query.

        Returns:
            A list of result bindings, or None if the query fails.

        Example:
            >>> linker.query_sparql(
            ...    "SELECT ?label WHERE { wd:Q28865 rdfs:label ?label . FILTER(LANG(?label) = 'en') }"
            ... )
            [{'label': {'type': 'literal', 'xml:lang': 'en', 'value': 'Python'}}]
        """
        try:
            headers = {"Accept": "application/sparql-results+json"}
            params = {"query": sparql_query, "format": "json"}

            response = requests.get(
                self.sparql_endpoint,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", {}).get("bindings", [])

        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return None

    def get_entity_as_rdf(
        self, wikidata_id: str, rdf_format: str = "turtle"
    ) -> Optional[str]:
        """
        Retrieves the full RDF data for a Wikidata entity using its Linked Data URL.

        Args:
            wikidata_id: The ID of the entity (e.g., "Q28865").
            rdf_format: The desired RDF serialization ('turtle', 'json-ld', 'rdf+xml').

        Returns:
            A string containing the RDF data, or None on failure.

        Note:
            This method uses Content Negotiation. The returned string can be
            directly parsed by rdflib: `Graph().parse(data=rdf_string, format=...)`
        """
        # Map friendly names to MIME types
        format_map = {
            "turtle": "text/turtle",
            "json-ld": "application/ld+json",
            "rdf+xml": "application/rdf+xml",
        }
        if rdf_format not in format_map:
            logger.error(f"Unsupported RDF format: {rdf_format}")
            return None

        entity_url = f"{self.entity_data_endpoint}{wikidata_id}"
        headers = {"Accept": format_map[rdf_format]}

        logger.info(f"Fetching RDF data for {wikidata_id} in {rdf_format} format...")
        try:
            response = requests.get(entity_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch RDF data for {wikidata_id}: {e}")
            return None

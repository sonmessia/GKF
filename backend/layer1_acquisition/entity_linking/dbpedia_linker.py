"""
DBpedia Linker
Links entities to DBpedia using the DBpedia Lookup API.
"""

import requests
from typing import Optional, Dict, Any
import logging
from .base_linker import BaseLinker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBpediaLinker(BaseLinker):
    """
    Links entities to DBpedia (https://dbpedia.org).
    Uses DBpedia Lookup service for entity resolution.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_endpoint = self.config.get(
            "api_endpoint", "https://lookup.dbpedia.org/api/search"
        )
        self.timeout = self.config.get("timeout", 10)
        self.max_results = self.config.get("max_results", 1)

    def get_source_name(self) -> str:
        return "dbpedia"

    def link(
        self, entity_name: str, entity_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Search DBpedia for entity and return best match URI.

        Args:
            entity_name: Name of entity
            entity_type: Optional type hint for filtering results

        Returns:
            DBpedia URI (e.g., "http://dbpedia.org/resource/Python_(programming_language)") or None
        """
        try:
            params = {
                "query": entity_name,
                "format": "json",
                "maxResults": self.max_results,
            }

            if entity_type:
                params["typeName"] = entity_type

            response = requests.get(
                self.api_endpoint, params=params, timeout=self.timeout
            )
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

        except requests.exceptions.RequestException as e:
            logger.error(f"DBpedia API request failed for '{entity_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"DBpedia linking failed for '{entity_name}': {e}")
            return None

    def get_entity_info(self, dbpedia_uri: str) -> Optional[Dict[str, Any]]:
        """
        Fetch information about a DBpedia entity.

        Args:
            dbpedia_uri: DBpedia resource URI

        Returns:
            Dictionary with entity information or None
        """
        try:
            resource_uri = (
                dbpedia_uri.replace(
                    "http://dbpedia.org/resource/", "http://dbpedia.org/data/"
                )
                + ".json"
            )

            response = requests.get(resource_uri, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if dbpedia_uri in data:
                return data[dbpedia_uri]

            return None

        except Exception as e:
            logger.error(f"Failed to fetch DBpedia info for {dbpedia_uri}: {e}")
            return None

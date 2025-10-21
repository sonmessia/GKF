"""
Open University Linker
Links entities to Open University Linked Data (data.open.ac.uk).
"""

import requests
from typing import Optional, Dict, Any
import logging
from .base_linker import BaseLinker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenUniversityLinker(BaseLinker):
    """
    Links entities to Open University LOD (data.open.ac.uk).
    Supports courses, qualifications, and organizational units.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.sparql_endpoint = self.config.get(
            "sparql_endpoint", "http://data.open.ac.uk/query"
        )
        self.base_uri = self.config.get("base_uri", "http://data.open.ac.uk")
        self.timeout = self.config.get("timeout", 15)

    def get_source_name(self) -> str:
        return "openuniversity"

    def link(self, entity_name: str, entity_type: Optional[str] = None) -> Optional[str]:
        """
        Search Open University LOD for entity and return URI.

        Args:
            entity_name: Name of entity (e.g., course name, qualification)
            entity_type: Type hint ('course', 'qualification', 'unit')

        Returns:
            Open University URI or None
        """
        try:
            query = self._build_sparql_query(entity_name, entity_type)
            params = {
                "query": query,
                "format": "json"
            }

            response = requests.get(self.sparql_endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", {}).get("bindings", [])
            if results:
                uri = results[0].get("uri", {}).get("value")
                if uri:
                    logger.info(f"Linked '{entity_name}' to Open University: {uri}")
                    return uri

            logger.warning(f"No Open University match found for '{entity_name}'")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Open University SPARQL request failed for '{entity_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Open University linking failed for '{entity_name}': {e}")
            return None

    def _build_sparql_query(self, entity_name: str, entity_type: Optional[str] = None) -> str:
        """
        Build SPARQL query for entity search.

        Args:
            entity_name: Entity name to search
            entity_type: Optional type filter

        Returns:
            SPARQL query string
        """
        type_filter = ""
        if entity_type:
            type_mapping = {
                "course": "http://purl.org/vocab/aiiso/schema#Course",
                "qualification": "http://purl.org/vocab/aiiso/schema#Qualification",
                "unit": "http://purl.org/vocab/aiiso/schema#OrganizationalUnit"
            }
            if entity_type.lower() in type_mapping:
                type_filter = f"?uri a <{type_mapping[entity_type.lower()]}> ."

        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX aiiso: <http://purl.org/vocab/aiiso/schema#>

        SELECT DISTINCT ?uri ?label WHERE {{
            ?uri rdfs:label ?label .
            {type_filter}
            FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{entity_name}")))
        }}
        LIMIT 10
        """
        return query

    def get_course_details(self, course_uri: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about an Open University course.

        Args:
            course_uri: Course URI

        Returns:
            Dictionary with course details or None
        """
        try:
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX aiiso: <http://purl.org/vocab/aiiso/schema#>
            PREFIX mlo: <http://purl.org/net/mlo/>

            SELECT ?label ?description ?credits WHERE {{
                <{course_uri}> rdfs:label ?label .
                OPTIONAL {{ <{course_uri}> rdfs:comment ?description . }}
                OPTIONAL {{ <{course_uri}> mlo:credit ?credits . }}
            }}
            """

            params = {"query": query, "format": "json"}
            response = requests.get(self.sparql_endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", {}).get("bindings", [])
            if results:
                return {
                    "label": results[0].get("label", {}).get("value"),
                    "description": results[0].get("description", {}).get("value"),
                    "credits": results[0].get("credits", {}).get("value")
                }

            return None

        except Exception as e:
            logger.error(f"Failed to fetch Open University course details: {e}")
            return None

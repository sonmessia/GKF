"""
LinkedUniversities Linker
Links entities to LinkedUniversities.org dataset.
"""

import requests
from typing import Optional, Dict, Any
import logging
from .base_linker import BaseLinker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedUniversitiesLinker(BaseLinker):
    """
    Links entities to LinkedUniversities.org.
    Covers academic institutions, courses, and programs worldwide.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.sparql_endpoint = self.config.get(
            "sparql_endpoint", "http://linkeduniversities.org/sparql"
        )
        self.base_uri = self.config.get("base_uri", "http://linkeduniversities.org/lu/index")
        self.timeout = self.config.get("timeout", 15)

    def get_source_name(self) -> str:
        return "linkeduniversities"

    def link(self, entity_name: str, entity_type: Optional[str] = None) -> Optional[str]:
        """
        Search LinkedUniversities for entity and return URI.

        Args:
            entity_name: Name of entity (university, course, program)
            entity_type: Type hint ('university', 'course', 'program', 'module')

        Returns:
            LinkedUniversities URI or None
        """
        try:
            query = self._build_sparql_query(entity_name, entity_type)
            headers = {"Accept": "application/sparql-results+json"}
            params = {"query": query}

            response = requests.get(
                self.sparql_endpoint,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", {}).get("bindings", [])
            if results:
                uri = results[0].get("uri", {}).get("value")
                if uri:
                    logger.info(f"Linked '{entity_name}' to LinkedUniversities: {uri}")
                    return uri

            logger.warning(f"No LinkedUniversities match found for '{entity_name}'")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedUniversities SPARQL request failed for '{entity_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"LinkedUniversities linking failed for '{entity_name}': {e}")
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
                "university": "http://purl.org/vocab/aiiso/schema#Institution",
                "course": "http://purl.org/vocab/aiiso/schema#Course",
                "program": "http://purl.org/vocab/aiiso/schema#Programme",
                "module": "http://purl.org/vocab/aiiso/schema#Module"
            }
            if entity_type.lower() in type_mapping:
                type_filter = f"?uri a <{type_mapping[entity_type.lower()]}> ."

        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX aiiso: <http://purl.org/vocab/aiiso/schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT DISTINCT ?uri ?label WHERE {{
            ?uri rdfs:label ?label .
            {type_filter}
            FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{entity_name}")))
        }}
        LIMIT 10
        """
        return query

    def search_university(self, university_name: str) -> Optional[str]:
        """
        Specialized search for university entities.

        Args:
            university_name: Name of the university

        Returns:
            URI of the university or None
        """
        return self.link(university_name, entity_type="university")

    def search_course(self, course_name: str) -> Optional[str]:
        """
        Specialized search for course entities.

        Args:
            course_name: Name of the course

        Returns:
            URI of the course or None
        """
        return self.link(course_name, entity_type="course")

    def get_university_details(self, university_uri: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about a university.

        Args:
            university_uri: University URI

        Returns:
            Dictionary with university details or None
        """
        try:
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX aiiso: <http://purl.org/vocab/aiiso/schema#>

            SELECT ?label ?homepage WHERE {{
                <{university_uri}> rdfs:label ?label .
                OPTIONAL {{ <{university_uri}> foaf:homepage ?homepage . }}
            }}
            """

            headers = {"Accept": "application/sparql-results+json"}
            params = {"query": query}

            response = requests.get(
                self.sparql_endpoint,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", {}).get("bindings", [])
            if results:
                return {
                    "label": results[0].get("label", {}).get("value"),
                    "homepage": results[0].get("homepage", {}).get("value")
                }

            return None

        except Exception as e:
            logger.error(f"Failed to fetch LinkedUniversities details: {e}")
            return None

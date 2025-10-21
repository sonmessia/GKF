"""
ESCO Linker
Links entities to ESCO (European Skills, Competences, Qualifications and Occupations).
"""

import requests
from typing import Optional, Dict, Any, List
import logging
from .base_linker import BaseLinker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESCOLinker(BaseLinker):
    """
    Links entities to ESCO taxonomy (ec.europa.eu/esco).
    Supports skills, competences, occupations, and qualifications.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_endpoint = self.config.get(
            "api_endpoint", "https://ec.europa.eu/esco/api"
        )
        self.base_uri = self.config.get("base_uri", "http://data.europa.eu/esco")
        self.timeout = self.config.get("timeout", 15)
        self.language = self.config.get("language", "en")

    def get_source_name(self) -> str:
        return "esco"

    def link(self, entity_name: str, entity_type: Optional[str] = None) -> Optional[str]:
        """
        Search ESCO for entity and return URI.

        Args:
            entity_name: Name of entity (skill, occupation, qualification)
            entity_type: Type hint ('skill', 'occupation', 'qualification')

        Returns:
            ESCO URI or None
        """
        try:
            type_param = self._map_entity_type(entity_type)
            results = self._search_esco(entity_name, type_param)

            if results:
                uri = results[0].get("uri")
                if uri:
                    logger.info(f"Linked '{entity_name}' to ESCO: {uri}")
                    return uri

            logger.warning(f"No ESCO match found for '{entity_name}'")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"ESCO API request failed for '{entity_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"ESCO linking failed for '{entity_name}': {e}")
            return None

    def _map_entity_type(self, entity_type: Optional[str]) -> Optional[str]:
        """
        Map generic entity type to ESCO taxonomy type.

        Args:
            entity_type: Generic type name

        Returns:
            ESCO type parameter or None
        """
        if not entity_type:
            return None

        type_mapping = {
            "skill": "skill",
            "competence": "skill",
            "occupation": "occupation",
            "job": "occupation",
            "qualification": "qualification"
        }

        return type_mapping.get(entity_type.lower())

    def _search_esco(self, entity_name: str, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search ESCO API for matching entities.

        Args:
            entity_name: Entity name to search
            entity_type: ESCO type filter

        Returns:
            List of matching entities
        """
        search_url = f"{self.api_endpoint}/search"
        params = {
            "text": entity_name,
            "language": self.language,
            "limit": 10
        }

        if entity_type:
            params["type"] = entity_type

        try:
            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return data.get("_embedded", {}).get("results", [])

        except Exception as e:
            logger.error(f"ESCO search failed: {e}")
            return []

    def search_skill(self, skill_name: str) -> Optional[str]:
        """
        Specialized search for skills.

        Args:
            skill_name: Name of the skill

        Returns:
            ESCO skill URI or None
        """
        return self.link(skill_name, entity_type="skill")

    def search_occupation(self, occupation_name: str) -> Optional[str]:
        """
        Specialized search for occupations.

        Args:
            occupation_name: Name of the occupation

        Returns:
            ESCO occupation URI or None
        """
        return self.link(occupation_name, entity_type="occupation")

    def get_skill_details(self, skill_uri: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about an ESCO skill.

        Args:
            skill_uri: ESCO skill URI

        Returns:
            Dictionary with skill details or None
        """
        try:
            skill_id = skill_uri.split("/")[-1]
            detail_url = f"{self.api_endpoint}/resource/skill/{skill_id}"

            params = {"language": self.language}
            response = requests.get(detail_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return {
                "uri": data.get("uri"),
                "title": data.get("title"),
                "description": data.get("description"),
                "skillType": data.get("skillType"),
                "reuseLevel": data.get("reuseLevel"),
                "alternativeLabels": data.get("alternativeLabels", [])
            }

        except Exception as e:
            logger.error(f"Failed to fetch ESCO skill details: {e}")
            return None

    def get_occupation_details(self, occupation_uri: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about an ESCO occupation.

        Args:
            occupation_uri: ESCO occupation URI

        Returns:
            Dictionary with occupation details or None
        """
        try:
            occupation_id = occupation_uri.split("/")[-1]
            detail_url = f"{self.api_endpoint}/resource/occupation/{occupation_id}"

            params = {"language": self.language}
            response = requests.get(detail_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return {
                "uri": data.get("uri"),
                "title": data.get("title"),
                "description": data.get("description"),
                "iscoGroup": data.get("iscoGroup"),
                "regulatedProfession": data.get("regulatedProfession"),
                "alternativeLabels": data.get("alternativeLabels", [])
            }

        except Exception as e:
            logger.error(f"Failed to fetch ESCO occupation details: {e}")
            return None

    def get_related_skills(self, occupation_uri: str) -> List[str]:
        """
        Get skills related to an occupation.

        Args:
            occupation_uri: ESCO occupation URI

        Returns:
            List of skill URIs
        """
        try:
            occupation_id = occupation_uri.split("/")[-1]
            skills_url = f"{self.api_endpoint}/resource/occupation/{occupation_id}/skills"

            params = {"language": self.language}
            response = requests.get(skills_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            skills = data.get("_embedded", {}).get("skills", [])
            return [skill.get("uri") for skill in skills if skill.get("uri")]

        except Exception as e:
            logger.error(f"Failed to fetch related skills: {e}")
            return []

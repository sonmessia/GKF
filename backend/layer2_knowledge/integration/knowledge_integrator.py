"""
Knowledge Integrator
Manages dual knowledge architecture: Foundational vs Experiential Knowledge.
"""
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeIntegrator:
    """
    Integrates and differentiates between:
    - Foundational Knowledge (objective, from authoritative sources)
    - Experiential Knowledge (community-driven, user interactions)
    """

    def __init__(self, triplestore_manager):
        self.triplestore = triplestore_manager
        self.gkf = Namespace("http://gkf.org/ontology/it#")
        self.data_ns = Namespace("http://gkf.org/data/")

        # Named graphs for different knowledge types
        self.foundational_graph_uri = "http://gkf.org/graphs/foundational"
        self.experiential_graph_uri = "http://gkf.org/graphs/experiential"

    def add_foundational_knowledge(self, graph: Graph) -> bool:
        """
        Add foundational knowledge from authoritative sources.
        This is objective, verified knowledge (e.g., from Wikidata, official docs).

        Args:
            graph: RDFLib Graph containing foundational triples

        Returns:
            Success status
        """
        try:
            # Mark all subjects as FoundationalKnowledge
            for subject in graph.subjects(RDF.type, None):
                graph.add((subject, RDF.type, self.gkf.FoundationalKnowledge))

            # Upload to foundational named graph
            success = self.triplestore.upload_graph(graph, self.foundational_graph_uri)

            if success:
                logger.info(f"Added {len(graph)} triples to foundational knowledge")

            return success

        except Exception as e:
            logger.error(f"Failed to add foundational knowledge: {e}")
            return False

    def add_experiential_knowledge(self, interaction_data: Dict) -> bool:
        """
        Add experiential knowledge from user interactions.
        This is subjective, community-driven knowledge.

        Args:
            interaction_data: {
                'user_id': 'user123',
                'interaction_type': 'course_completion' | 'skill_rating' | 'learning_path',
                'entity_uri': 'http://gkf.org/data/Course/python101',
                'metadata': {...}
            }

        Returns:
            Success status
        """
        try:
            graph = Graph()
            graph.bind("gkf", self.gkf)
            graph.bind("data", self.data_ns)

            # Create interaction entity
            interaction_id = f"interaction_{interaction_data['user_id']}_{datetime.now().timestamp()}"
            interaction_uri = self.data_ns[interaction_id]

            # Add interaction triples
            graph.add((interaction_uri, RDF.type, self.gkf.Interaction))
            graph.add((interaction_uri, RDF.type, self.gkf.ExperientialKnowledge))

            # Add user reference
            user_uri = self.data_ns[f"User/{interaction_data['user_id']}"]
            graph.add((interaction_uri, self.gkf.hasUser, user_uri))

            # Add related entity
            entity_uri = URIRef(interaction_data['entity_uri'])
            graph.add((interaction_uri, self.gkf.relatedTo, entity_uri))

            # Add timestamp
            from rdflib import XSD
            timestamp = Literal(datetime.now().isoformat(), datatype=XSD.dateTime)
            graph.add((interaction_uri, self.gkf.timestamp, timestamp))

            # Add metadata
            for key, value in interaction_data.get('metadata', {}).items():
                predicate = self.gkf[key]
                graph.add((interaction_uri, predicate, Literal(value)))

            # Upload to experiential named graph
            success = self.triplestore.upload_graph(graph, self.experiential_graph_uri)

            if success:
                logger.info(f"Added experiential knowledge: {interaction_data['interaction_type']}")

            return success

        except Exception as e:
            logger.error(f"Failed to add experiential knowledge: {e}")
            return False

    def query_foundational_knowledge(self, sparql_query: str) -> List[Dict]:
        """
        Query only foundational knowledge.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT * FROM <{self.foundational_graph_uri}>
        WHERE {{
            {sparql_query}
        }}
        """
        return self.triplestore.query(query)

    def query_experiential_knowledge(self, sparql_query: str) -> List[Dict]:
        """
        Query only experiential knowledge.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT * FROM <{self.experiential_graph_uri}>
        WHERE {{
            {sparql_query}
        }}
        """
        return self.triplestore.query(query)

    def query_integrated_knowledge(self, sparql_query: str) -> List[Dict]:
        """
        Query across both foundational and experiential knowledge.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT *
        WHERE {{
            {{
                GRAPH <{self.foundational_graph_uri}> {{
                    {sparql_query}
                }}
            }} UNION {{
                GRAPH <{self.experiential_graph_uri}> {{
                    {sparql_query}
                }}
            }}
        }}
        """
        return self.triplestore.query(query)

    def get_user_learning_history(self, user_id: str) -> List[Dict]:
        """
        Get a user's learning history from experiential knowledge.
        """
        query = f"""
        ?interaction a gkf:Interaction ;
                     gkf:hasUser data:User/{user_id} ;
                     gkf:relatedTo ?entity ;
                     gkf:timestamp ?timestamp .
        """
        return self.query_experiential_knowledge(query)

    def get_course_popularity(self, course_uri: str) -> int:
        """
        Calculate course popularity based on experiential knowledge.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT (COUNT(?interaction) as ?count) FROM <{self.experiential_graph_uri}>
        WHERE {{
            ?interaction a gkf:Interaction ;
                         gkf:relatedTo <{course_uri}> .
        }}
        """
        results = self.triplestore.query(query)
        if results:
            return int(results[0].get('count', {}).get('value', 0))
        return 0

    def enrich_with_experiential_insights(self, foundational_entity_uri: str) -> Dict:
        """
        Enrich foundational knowledge with experiential insights.

        Example: Add user ratings, completion rates to a course.
        """
        # Get foundational data
        foundational_query = f"""
        ?entity <{foundational_entity_uri}> ?property ?value .
        """
        foundational_data = self.query_foundational_knowledge(foundational_query)

        # Get experiential insights
        popularity = self.get_course_popularity(foundational_entity_uri)

        return {
            'foundational': foundational_data,
            'experiential': {
                'popularity': popularity
            }
        }

    def calculate_knowledge_confidence(self, entity_uri: str) -> float:
        """
        Calculate confidence score for an entity based on:
        - Foundational sources (high weight)
        - Experiential validation (medium weight)
        """
        # Check if entity exists in foundational knowledge
        foundational_exists = len(self.query_foundational_knowledge(
            f"<{entity_uri}> ?p ?o ."
        )) > 0

        # Count experiential interactions
        experiential_count = self.get_course_popularity(entity_uri)

        # Calculate confidence (0.0 - 1.0)
        confidence = 0.0

        if foundational_exists:
            confidence += 0.7  # Foundational knowledge gives high confidence

        if experiential_count > 0:
            # Experiential validation adds confidence (capped at 0.3)
            experiential_score = min(experiential_count / 100.0, 0.3)
            confidence += experiential_score

        return min(confidence, 1.0)

"""
Triple Store Manager
Interface for interacting with GraphDB or other SPARQL-compatible triple stores.
"""
from typing import Dict, List, Optional, Any
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TripleStoreManager:
    """
    Manages connections and operations with a triple store (GraphDB, Fuseki, etc.)
    """

    def __init__(self, config: Dict[str, str]):
        """
        config = {
            'endpoint': 'http://localhost:7200/repositories/gkf',
            'query_endpoint': 'http://localhost:7200/repositories/gkf',
            'update_endpoint': 'http://localhost:7200/repositories/gkf/statements',
            'username': 'admin' (optional),
            'password': 'password' (optional)
        }
        """
        self.endpoint = config.get('endpoint')
        self.query_endpoint = config.get('query_endpoint', self.endpoint)
        self.update_endpoint = config.get('update_endpoint', self.endpoint + '/statements')
        self.username = config.get('username')
        self.password = config.get('password')

        # Initialize SPARQL wrappers
        self.sparql_query = SPARQLWrapper(self.query_endpoint)
        self.sparql_update = SPARQLWrapper(self.update_endpoint)

        # Set authentication if provided
        if self.username and self.password:
            self.sparql_query.setHTTPAuth(DIGEST)
            self.sparql_query.setCredentials(self.username, self.password)
            self.sparql_update.setHTTPAuth(DIGEST)
            self.sparql_update.setCredentials(self.username, self.password)

    def upload_graph(self, graph: Graph, graph_uri: Optional[str] = None) -> bool:
        """
        Upload an RDF graph to the triple store.

        Args:
            graph: RDFLib Graph object
            graph_uri: Optional named graph URI

        Returns:
            Success status
        """
        try:
            # Serialize graph to Turtle format
            turtle_data = graph.serialize(format='turtle')

            # Use HTTP POST to upload data
            self.sparql_update.setMethod(POST)
            self.sparql_update.setRequestMethod('postdirectly')
            self.sparql_update.setQuery(turtle_data)

            results = self.sparql_update.query()
            logger.info(f"Uploaded {len(graph)} triples to triple store")
            return True

        except Exception as e:
            logger.error(f"Failed to upload graph: {e}")
            return False

    def query(self, sparql_query: str) -> List[Dict]:
        """
        Execute a SPARQL SELECT query.

        Args:
            sparql_query: SPARQL query string

        Returns:
            List of result bindings
        """
        try:
            self.sparql_query.setQuery(sparql_query)
            self.sparql_query.setReturnFormat(JSON)
            results = self.sparql_query.query().convert()

            bindings = results['results']['bindings']
            logger.info(f"Query returned {len(bindings)} results")
            return bindings

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def update(self, sparql_update: str) -> bool:
        """
        Execute a SPARQL UPDATE query (INSERT, DELETE).

        Args:
            sparql_update: SPARQL UPDATE query string

        Returns:
            Success status
        """
        try:
            self.sparql_update.setQuery(sparql_update)
            self.sparql_update.setMethod(POST)
            self.sparql_update.query()

            logger.info("Update executed successfully")
            return True

        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False

    def insert_triple(self, subject: str, predicate: str, obj: str, graph_uri: Optional[str] = None) -> bool:
        """
        Insert a single triple into the store.
        """
        if graph_uri:
            query = f"""
            INSERT DATA {{
                GRAPH <{graph_uri}> {{
                    <{subject}> <{predicate}> <{obj}> .
                }}
            }}
            """
        else:
            query = f"""
            INSERT DATA {{
                <{subject}> <{predicate}> <{obj}> .
            }}
            """

        return self.update(query)

    def delete_triple(self, subject: str, predicate: str, obj: str, graph_uri: Optional[str] = None) -> bool:
        """
        Delete a single triple from the store.
        """
        if graph_uri:
            query = f"""
            DELETE DATA {{
                GRAPH <{graph_uri}> {{
                    <{subject}> <{predicate}> <{obj}> .
                }}
            }}
            """
        else:
            query = f"""
            DELETE DATA {{
                <{subject}> <{predicate}> <{obj}> .
            }}
            """

        return self.update(query)

    def clear_graph(self, graph_uri: Optional[str] = None) -> bool:
        """
        Clear all triples from a graph.
        """
        if graph_uri:
            query = f"CLEAR GRAPH <{graph_uri}>"
        else:
            query = "CLEAR DEFAULT"

        return self.update(query)

    def get_all_skills(self) -> List[Dict]:
        """
        Example query: Get all skills from the knowledge graph.
        """
        query = """
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?skill ?skillName ?level
        WHERE {
            ?skill a gkf:Skill ;
                   gkf:skillName ?skillName .
            OPTIONAL { ?skill gkf:skillLevel ?level }
        }
        """
        return self.query(query)

    def get_job_required_skills(self, job_uri: str) -> List[Dict]:
        """
        Example query: Get skills required for a specific job.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?skill ?skillName
        WHERE {{
            <{job_uri}> gkf:requires ?skill .
            ?skill gkf:skillName ?skillName .
        }}
        """
        return self.query(query)

    def find_courses_for_skill(self, skill_name: str) -> List[Dict]:
        """
        Example query: Find courses that teach a specific skill.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?course ?courseName ?url
        WHERE {{
            ?course a gkf:Course ;
                    gkf:courseName ?courseName ;
                    gkf:teaches ?skill .
            ?skill gkf:skillName "{skill_name}" .
            OPTIONAL {{ ?course gkf:courseURL ?url }}
        }}
        """
        return self.query(query)

    def check_connection(self) -> bool:
        """
        Test connection to triple store.
        """
        try:
            test_query = "ASK { ?s ?p ?o }"
            self.sparql_query.setQuery(test_query)
            self.sparql_query.setReturnFormat(JSON)
            self.sparql_query.query()
            logger.info("Connection to triple store successful")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

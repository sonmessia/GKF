"""
Ontology Manager
Handles loading, validation, and versioning of ontologies.
"""
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from typing import Dict, List, Optional
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OntologyManager:
    """
    Manages ontology lifecycle: loading, validation, versioning, and querying.
    """

    def __init__(self, ontology_dir: str = "./ontologies"):
        self.ontology_dir = Path(ontology_dir)
        self.ontology_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_ontologies: Dict[str, Graph] = {}

    def load_ontology(self, ontology_path: str, ontology_name: Optional[str] = None) -> Graph:
        """
        Load an ontology file into memory.

        Args:
            ontology_path: Path to ontology file (TTL, RDF/XML, OWL)
            ontology_name: Optional name to register ontology with

        Returns:
            RDFLib Graph object
        """
        try:
            graph = Graph()

            # Detect format based on file extension
            path = Path(ontology_path)
            if path.suffix == '.ttl':
                format = 'turtle'
            elif path.suffix in ['.rdf', '.owl', '.xml']:
                format = 'xml'
            elif path.suffix == '.jsonld':
                format = 'json-ld'
            elif path.suffix == '.nt':
                format = 'nt'
            else:
                format = 'turtle'  # default

            graph.parse(ontology_path, format=format)

            # Register ontology
            if not ontology_name:
                ontology_name = path.stem

            self.loaded_ontologies[ontology_name] = graph

            logger.info(f"Loaded ontology '{ontology_name}' with {len(graph)} triples")
            return graph

        except Exception as e:
            logger.error(f"Failed to load ontology from {ontology_path}: {e}")
            raise

    def validate_ontology(self, graph: Graph) -> Dict[str, any]:
        """
        Validate ontology structure and report issues.

        Returns:
            Validation report
        """
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }

        try:
            # Check for ontology declaration
            ontology_query = """
            SELECT ?ontology WHERE {
                ?ontology a owl:Ontology .
            }
            """
            results = list(graph.query(ontology_query))

            if not results:
                report['warnings'].append("No owl:Ontology declaration found")

            # Count classes
            class_query = "SELECT (COUNT(?class) as ?count) WHERE { ?class a owl:Class }"
            class_count = list(graph.query(class_query))[0][0]
            report['stats']['classes'] = int(class_count)

            # Count properties
            prop_query = """
            SELECT (COUNT(?prop) as ?count) WHERE {
                { ?prop a owl:ObjectProperty } UNION
                { ?prop a owl:DatatypeProperty }
            }
            """
            prop_count = list(graph.query(prop_query))[0][0]
            report['stats']['properties'] = int(prop_count)

            # Check for classes without labels
            unlabeled_query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?class WHERE {
                ?class a owl:Class .
                FILTER NOT EXISTS { ?class rdfs:label ?label }
            }
            """
            unlabeled = list(graph.query(unlabeled_query))
            if unlabeled:
                report['warnings'].append(f"{len(unlabeled)} classes without rdfs:label")

            report['stats']['total_triples'] = len(graph)

            logger.info(f"Ontology validation: {report['stats']}")

        except Exception as e:
            report['valid'] = False
            report['errors'].append(str(e))
            logger.error(f"Validation failed: {e}")

        return report

    def get_ontology_classes(self, ontology_name: str) -> List[Dict]:
        """
        Get all classes defined in an ontology.
        """
        if ontology_name not in self.loaded_ontologies:
            raise ValueError(f"Ontology '{ontology_name}' not loaded")

        graph = self.loaded_ontologies[ontology_name]

        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?class ?label ?comment
        WHERE {
            ?class a owl:Class .
            OPTIONAL { ?class rdfs:label ?label }
            OPTIONAL { ?class rdfs:comment ?comment }
        }
        """

        results = []
        for row in graph.query(query):
            results.append({
                'uri': str(row.class_),
                'label': str(row.label) if row.label else None,
                'comment': str(row.comment) if row.comment else None
            })

        return results

    def get_ontology_properties(self, ontology_name: str) -> List[Dict]:
        """
        Get all properties defined in an ontology.
        """
        if ontology_name not in self.loaded_ontologies:
            raise ValueError(f"Ontology '{ontology_name}' not loaded")

        graph = self.loaded_ontologies[ontology_name]

        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?property ?type ?label ?domain ?range
        WHERE {
            {
                ?property a owl:ObjectProperty .
                BIND("object" as ?type)
            } UNION {
                ?property a owl:DatatypeProperty .
                BIND("datatype" as ?type)
            }
            OPTIONAL { ?property rdfs:label ?label }
            OPTIONAL { ?property rdfs:domain ?domain }
            OPTIONAL { ?property rdfs:range ?range }
        }
        """

        results = []
        for row in graph.query(query):
            results.append({
                'uri': str(row.property),
                'type': str(row.type),
                'label': str(row.label) if row.label else None,
                'domain': str(row.domain) if row.domain else None,
                'range': str(row.range) if row.range else None
            })

        return results

    def merge_ontologies(self, ontology_names: List[str], output_name: str) -> Graph:
        """
        Merge multiple loaded ontologies into one.
        """
        merged_graph = Graph()

        for name in ontology_names:
            if name not in self.loaded_ontologies:
                raise ValueError(f"Ontology '{name}' not loaded")

            graph = self.loaded_ontologies[name]
            for triple in graph:
                merged_graph.add(triple)

        self.loaded_ontologies[output_name] = merged_graph
        logger.info(f"Merged {len(ontology_names)} ontologies into '{output_name}' ({len(merged_graph)} triples)")

        return merged_graph

    def export_ontology(self, ontology_name: str, output_path: str, format: str = 'turtle'):
        """
        Export ontology to file.

        Formats: 'turtle', 'xml', 'json-ld', 'nt'
        """
        if ontology_name not in self.loaded_ontologies:
            raise ValueError(f"Ontology '{ontology_name}' not loaded")

        graph = self.loaded_ontologies[ontology_name]

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(graph.serialize(format=format))

        logger.info(f"Exported ontology '{ontology_name}' to {output_path}")

    def create_version_snapshot(self, ontology_name: str) -> str:
        """
        Create a versioned snapshot of an ontology.
        """
        if ontology_name not in self.loaded_ontologies:
            raise ValueError(f"Ontology '{ontology_name}' not loaded")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"{ontology_name}_v{timestamp}"
        version_path = self.ontology_dir / f"{version_name}.ttl"

        self.export_ontology(ontology_name, str(version_path), format='turtle')

        logger.info(f"Created version snapshot: {version_path}")
        return str(version_path)

    def list_loaded_ontologies(self) -> List[str]:
        """
        List all currently loaded ontologies.
        """
        return list(self.loaded_ontologies.keys())

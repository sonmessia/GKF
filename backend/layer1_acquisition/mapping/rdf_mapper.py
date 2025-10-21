"""
RDF Mapping Engine
Converts raw data to RDF triples using mapping rules.
"""
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD
from rdflib.namespace import SKOS, DCTERMS
from typing import Dict, List, Any
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MappingEngine:
    """
    Maps raw data to RDF triples based on ontology and mapping rules.
    """

    def __init__(self, ontology_namespace: str = "http://gkf.org/ontology/it#"):
        self.graph = Graph()
        self.gkf = Namespace(ontology_namespace)
        self.data_ns = Namespace("http://gkf.org/data/")

        # Bind prefixes
        self.graph.bind("gkf", self.gkf)
        self.graph.bind("data", self.data_ns)
        self.graph.bind("skos", SKOS)
        self.graph.bind("dc", DCTERMS)

    def apply_mapping(self, data: List[Dict], mapping_rules: Dict[str, Any]) -> Graph:
        """
        Apply mapping rules to transform raw data into RDF.

        mapping_rules = {
            'entity_type': 'Skill' | 'Course' | 'Job',
            'id_field': 'id',  # field to use as unique identifier
            'mappings': {
                'field_name': 'ontology_property',
                ...
            }
        }
        """
        entity_type = mapping_rules.get('entity_type')
        id_field = mapping_rules.get('id_field', 'id')
        field_mappings = mapping_rules.get('mappings', {})

        for record in data:
            try:
                # Generate URI for entity
                entity_id = record.get(id_field, str(uuid.uuid4()))
                entity_uri = self.data_ns[f"{entity_type}/{entity_id}"]

                # Add type triple
                entity_class = self.gkf[entity_type]
                self.graph.add((entity_uri, RDF.type, entity_class))

                # Map fields to properties
                for field_name, ontology_property in field_mappings.items():
                    if field_name in record and record[field_name]:
                        value = record[field_name]
                        property_uri = self.gkf[ontology_property]

                        # Handle different value types
                        if isinstance(value, str):
                            self.graph.add((entity_uri, property_uri, Literal(value, datatype=XSD.string)))
                        elif isinstance(value, int):
                            self.graph.add((entity_uri, property_uri, Literal(value, datatype=XSD.integer)))
                        elif isinstance(value, float):
                            self.graph.add((entity_uri, property_uri, Literal(value, datatype=XSD.decimal)))
                        elif isinstance(value, bool):
                            self.graph.add((entity_uri, property_uri, Literal(value, datatype=XSD.boolean)))
                        elif isinstance(value, list):
                            # Handle list values (e.g., multiple skills)
                            for item in value:
                                self.graph.add((entity_uri, property_uri, Literal(item, datatype=XSD.string)))

                logger.debug(f"Mapped entity: {entity_uri}")

            except Exception as e:
                logger.error(f"Failed to map record: {record}. Error: {e}")
                continue

        logger.info(f"Mapped {len(data)} records to {len(self.graph)} triples")
        return self.graph

    def create_skill_mapping(self, skill_data: Dict) -> URIRef:
        """Helper: Map a skill entity"""
        skill_id = skill_data.get('id', str(uuid.uuid4()))
        skill_uri = self.data_ns[f"Skill/{skill_id}"]

        self.graph.add((skill_uri, RDF.type, self.gkf.Skill))
        self.graph.add((skill_uri, self.gkf.skillName, Literal(skill_data['name'], datatype=XSD.string)))

        if 'level' in skill_data:
            self.graph.add((skill_uri, self.gkf.skillLevel, Literal(skill_data['level'], datatype=XSD.string)))

        if 'description' in skill_data:
            self.graph.add((skill_uri, self.gkf.description, Literal(skill_data['description'], datatype=XSD.string)))

        return skill_uri

    def create_course_mapping(self, course_data: Dict) -> URIRef:
        """Helper: Map a course entity"""
        course_id = course_data.get('id', str(uuid.uuid4()))
        course_uri = self.data_ns[f"Course/{course_id}"]

        self.graph.add((course_uri, RDF.type, self.gkf.Course))
        self.graph.add((course_uri, self.gkf.courseName, Literal(course_data['name'], datatype=XSD.string)))

        if 'url' in course_data:
            self.graph.add((course_uri, self.gkf.courseURL, Literal(course_data['url'], datatype=XSD.anyURI)))

        if 'duration' in course_data:
            self.graph.add((course_uri, self.gkf.duration, Literal(course_data['duration'], datatype=XSD.integer)))

        if 'difficulty' in course_data:
            self.graph.add((course_uri, self.gkf.difficulty, Literal(course_data['difficulty'], datatype=XSD.string)))

        return course_uri

    def create_job_mapping(self, job_data: Dict) -> URIRef:
        """Helper: Map a job entity"""
        job_id = job_data.get('id', str(uuid.uuid4()))
        job_uri = self.data_ns[f"Job/{job_id}"]

        self.graph.add((job_uri, RDF.type, self.gkf.Job))
        self.graph.add((job_uri, self.gkf.jobTitle, Literal(job_data['title'], datatype=XSD.string)))

        if 'salary' in job_data:
            self.graph.add((job_uri, self.gkf.salary, Literal(job_data['salary'], datatype=XSD.decimal)))

        if 'description' in job_data:
            self.graph.add((job_uri, self.gkf.description, Literal(job_data['description'], datatype=XSD.string)))

        return job_uri

    def add_relationship(self, subject_uri: URIRef, predicate: str, object_uri: URIRef):
        """Add a relationship triple between entities"""
        predicate_uri = self.gkf[predicate]
        self.graph.add((subject_uri, predicate_uri, object_uri))

    def export_graph(self, format: str = 'turtle') -> str:
        """
        Export graph in specified format.
        Formats: 'turtle', 'xml', 'json-ld', 'nt'
        """
        return self.graph.serialize(format=format)

    def save_graph(self, output_path: str, format: str = 'turtle'):
        """Save graph to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.export_graph(format=format))
        logger.info(f"Graph saved to {output_path}")

    def load_ontology(self, ontology_path: str):
        """Load ontology into graph"""
        self.graph.parse(ontology_path, format='turtle')
        logger.info(f"Ontology loaded from {ontology_path}")

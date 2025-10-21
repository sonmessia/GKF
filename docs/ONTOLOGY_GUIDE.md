# IT Ontology Guide

## Overview

The IT Education Knowledge Graph Ontology defines the conceptual model for IT skills, courses, jobs, and learning paths. This document serves as a reference for developers, data engineers, and ontology designers working with GKF.

**Ontology URI**: `http://gkf.org/ontology/it#`
**Prefix**: `gkf:`
**Format**: OWL 2 / Turtle
**Version**: 1.0.0

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Class Hierarchy](#class-hierarchy)
3. [Properties](#properties)
4. [Usage Examples](#usage-examples)
5. [Design Patterns](#design-patterns)
6. [Extension Guide](#extension-guide)

---

## Core Concepts

### Knowledge Types

The ontology distinguishes between two fundamental knowledge types:

#### Foundational Knowledge

Objective, verified knowledge from authoritative sources.

```turtle
:FoundationalKnowledge a owl:Class ;
    rdfs:subClassOf :Knowledge ;
    rdfs:comment "Objective, globally verified knowledge from authoritative sources" .
```

**Examples**:

- Python is a programming language
- Machine Learning is a subfield of AI
- React requires JavaScript as a prerequisite

#### Experiential Knowledge

Community-driven, subjective knowledge from user interactions.

```turtle
:ExperientialKnowledge a owl:Class ;
    rdfs:subClassOf :Knowledge ;
    rdfs:comment "Community-driven, user-generated knowledge based on interactions" .
```

**Examples**:

- 85% of users who learned Python also learned SQL
- Course X has an average rating of 4.5 stars
- Learning path Y has a completion rate of 70%

---

## Class Hierarchy

### Main Classes

```
:Knowledge (abstract)
  ├── :FoundationalKnowledge
  └── :ExperientialKnowledge

:Skill
  ├── :TechnicalSkill
  │     ├── Examples: Python, React, SQL, Docker
  └── :SoftSkill
        ├── Examples: Leadership, Communication, Problem Solving

:Course
  ├── Online courses, tutorials, bootcamps

:Job
  ├── Professional roles: Software Engineer, Data Scientist, etc.

:LearningPath
  ├── Structured sequences of courses

:Technology
  ├── Tools, frameworks, platforms: Docker, Kubernetes, React

:Certification
  ├── Professional certifications: AWS Certified, Google Cloud Professional

:UserProfile
  ├── Learner profiles with skills and progress

:Interaction
  ├── User actions: course completion, skill rating, job interest
```

---

## Properties

### Object Properties (Entity → Entity)

#### `gkf:requires`

- **Domain**: Job
- **Range**: Skill
- **Description**: A job requires a specific skill
- **Example**:

```turtle
data:Job/software-engineer gkf:requires data:Skill/python .
```

#### `gkf:teaches`

- **Domain**: Course
- **Range**: Skill
- **Description**: A course teaches a particular skill
- **Example**:

```turtle
data:Course/python-basics gkf:teaches data:Skill/python .
```

#### `gkf:prerequisite`

- **Domain**: Skill
- **Range**: Skill
- **Type**: Transitive Property
- **Description**: Skill A is a prerequisite for Skill B
- **Example**:

```turtle
data:Skill/react gkf:prerequisite data:Skill/javascript .
data:Skill/javascript gkf:prerequisite data:Skill/html .
# Inference: React prerequisite HTML (transitive)
```

#### `gkf:relatedTo`

- **Domain**: Skill
- **Range**: Skill
- **Type**: Symmetric Property
- **Description**: Two skills are related
- **Example**:

```turtle
data:Skill/python gkf:relatedTo data:Skill/data-science .
# Inference: data-science relatedTo python (symmetric)
```

#### `gkf:partOf`

- **Domain**: Course
- **Range**: Learning Path
- **Type**: Transitive Property
- **Description**: A course is part of a learning path
- **Example**:

```turtle
data:Course/python-basics gkf:partOf data:LearningPath/web-dev .
```

#### `gkf:usesTechnology`

- **Domain**: Job
- **Range**: Technology
- **Description**: A job uses a specific technology
- **Example**:

```turtle
data:Job/frontend-developer gkf:usesTechnology data:Technology/react .
```

#### `gkf:recommendedFor`

- **Domain**: Course
- **Range**: Job
- **Description**: A course is recommended for a job role
- **Example**:

```turtle
data:Course/react-fundamentals gkf:recommendedFor data:Job/frontend-developer .
```

#### `gkf:hasSkill`

- **Domain**: User Profile
- **Range**: Skill
- **Description**: User has acquired a skill
- **Example**:

```turtle
data:User/user123 gkf:hasSkill data:Skill/python .
```

#### `gkf:completedCourse`

- **Domain**: User Profile
- **Range**: Course
- **Description**: User has completed a course
- **Example**:

```turtle
data:User/user123 gkf:completedCourse data:Course/python-basics .
```

### Data Properties (Entity → Literal)

#### Skill Properties

```turtle
:skillName a owl:DatatypeProperty ;
    rdfs:domain :Skill ;
    rdfs:range xsd:string .

:skillLevel a owl:DatatypeProperty ;
    rdfs:domain :Skill ;
    rdfs:range xsd:string ;  # Values: Beginner, Intermediate, Advanced, Expert
    rdfs:comment "Proficiency level required" .
```

#### Course Properties

```turtle
:courseName a owl:DatatypeProperty ;
    rdfs:domain :Course ;
    rdfs:range xsd:string .

:courseURL a owl:DatatypeProperty ;
    rdfs:domain :Course ;
    rdfs:range xsd:anyURI .

:duration a owl:DatatypeProperty ;
    rdfs:domain :Course ;
    rdfs:range xsd:integer ;
    rdfs:comment "Duration in hours" .

:difficulty a owl:DatatypeProperty ;
    rdfs:domain :Course ;
    rdfs:range xsd:string ;  # Values: Beginner, Intermediate, Advanced
    rdfs:comment "Course difficulty level" .

:rating a owl:DatatypeProperty ;
    rdfs:range xsd:decimal ;
    rdfs:comment "User rating (0.0 - 5.0)" .
```

#### Job Properties

```turtle
:jobTitle a owl:DatatypeProperty ;
    rdfs:domain :Job ;
    rdfs:range xsd:string .

:salary a owl:DatatypeProperty ;
    rdfs:domain :Job ;
    rdfs:range xsd:decimal ;
    rdfs:comment "Annual salary in USD" .

:description a owl:DatatypeProperty ;
    rdfs:range xsd:string ;
    rdfs:comment "Textual description" .
```

#### Linked Open Data Properties

```turtle
:wikidataURI a owl:DatatypeProperty ;
    rdfs:range xsd:anyURI ;
    rdfs:comment "Linked to Wikidata entity" .

:dbpediaURI a owl:DatatypeProperty ;
    rdfs:range xsd:anyURI ;
    rdfs:comment "Linked to DBpedia resource" .
```

#### Temporal Properties

```turtle
:timestamp a owl:DatatypeProperty ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "Timestamp of interaction or event" .
```

---

## Usage Examples

### Example 1: Define a Skill

```turtle
data:Skill/python a gkf:TechnicalSkill ;
    gkf:skillName "Python Programming"^^xsd:string ;
    gkf:skillLevel "Intermediate"^^xsd:string ;
    gkf:description "Object-oriented programming language"^^xsd:string ;
    gkf:wikidataURI "http://www.wikidata.org/entity/Q28865"^^xsd:anyURI .
```

### Example 2: Define a Course with Skills

```turtle
data:Course/python-basics a gkf:Course ;
    gkf:courseName "Python for Beginners"^^xsd:string ;
    gkf:courseURL "https://example.com/python-basics"^^xsd:anyURI ;
    gkf:duration 40^^xsd:integer ;
    gkf:difficulty "Beginner"^^xsd:string ;
    gkf:rating 4.5^^xsd:decimal ;
    gkf:teaches data:Skill/python ;
    gkf:description "Learn Python from scratch"^^xsd:string .
```

### Example 3: Define a Job with Requirements

```turtle
data:Job/data-scientist a gkf:Job ;
    gkf:jobTitle "Data Scientist"^^xsd:string ;
    gkf:salary 110000.00^^xsd:decimal ;
    gkf:description "Analyze data and build predictive models"^^xsd:string ;
    gkf:requires data:Skill/python,
                 data:Skill/machine-learning,
                 data:Skill/sql,
                 data:Skill/statistics .
```

### Example 4: Define Skill Prerequisites

```turtle
# React requires JavaScript
data:Skill/react gkf:prerequisite data:Skill/javascript .

# JavaScript requires HTML
data:Skill/javascript gkf:prerequisite data:Skill/html .

# By transitivity: React prerequisite HTML (inferred)
```

### Example 5: User Learning Interaction

```turtle
data:Interaction/user123_course_python a gkf:Interaction, gkf:ExperientialKnowledge ;
    gkf:hasUser data:User/user123 ;
    gkf:relatedTo data:Course/python-basics ;
    gkf:timestamp "2025-10-13T10:30:00Z"^^xsd:dateTime ;
    gkf:interactionType "course_completion"^^xsd:string ;
    gkf:rating 5.0^^xsd:decimal .
```

---

## Design Patterns

### Pattern 1: Skill Prerequisite Chain

Use transitive property for prerequisite chains:

```turtle
:prerequisite a owl:ObjectProperty, owl:TransitiveProperty .

# Define chain
Skill_A :prerequisite Skill_B .
Skill_B :prerequisite Skill_C .

# Inferred
Skill_A :prerequisite Skill_C .
```

**Query**:

```sparql
SELECT ?prereq WHERE {
    :Skill_A gkf:prerequisite+ ?prereq .
}
```

### Pattern 2: Bidirectional Relationships

Use symmetric properties:

```turtle
:relatedTo a owl:ObjectProperty, owl:SymmetricProperty .

Skill_A :relatedTo Skill_B .
# Inferred: Skill_B :relatedTo Skill_A
```

### Pattern 3: Multi-Source Linking

Link entities to multiple LOD sources:

```turtle
data:Skill/python
    gkf:wikidataURI "http://www.wikidata.org/entity/Q28865"^^xsd:anyURI ;
    gkf:dbpediaURI "http://dbpedia.org/resource/Python_(programming_language)"^^xsd:anyURI .
```

### Pattern 4: Named Graphs for Knowledge Types

Separate foundational and experiential knowledge:

```turtle
# Foundational graph
GRAPH <http://gkf.org/graphs/foundational> {
    data:Skill/python a gkf:TechnicalSkill, gkf:FoundationalKnowledge .
}

# Experiential graph
GRAPH <http://gkf.org/graphs/experiential> {
    data:Interaction/123 a gkf:Interaction, gkf:ExperientialKnowledge .
}
```

---

## Extension Guide

### Adding New Domains

To extend GKF to a new domain (e.g., Healthcare):

1. **Create Domain Ontology**:

```turtle
@prefix health: <http://gkf.org/ontology/health#> .

health:Disease a owl:Class .
health:Treatment a owl:Class .
health:Symptom a owl:Class .
health:Medication a owl:Class .

health:treats a owl:ObjectProperty ;
    rdfs:domain health:Treatment ;
    rdfs:range health:Disease .
```

2. **Reuse Core Concepts**:

```turtle
# Extend from GKF core
health:Disease rdfs:subClassOf gkf:Knowledge .
```

3. **Map Data Sources**:

```python
# Use Layer 1 connectors
connector = JSONConnector(config)
data = connector.fetch()

mapper = MappingEngine(ontology_namespace="http://gkf.org/ontology/health#")
graph = mapper.apply_mapping(data, mapping_rules)
```

### Adding New Classes

```turtle
:Mentor a owl:Class ;
    rdfs:label "Mentor"@en ;
    rdfs:comment "Experienced professional who guides learners" .

:mentors a owl:ObjectProperty ;
    rdfs:domain :Mentor ;
    rdfs:range :UserProfile .
```

### Adding New Properties

```turtle
:experienceYears a owl:DatatypeProperty ;
    rdfs:domain :Job ;
    rdfs:range xsd:integer ;
    rdfs:comment "Years of experience required" .
```

---

## Validation

### Using SHACL (Future)

```turtle
# Skill Shape
:SkillShape a sh:NodeShape ;
    sh:targetClass :Skill ;
    sh:property [
        sh:path :skillName ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
    ] .
```

### Using OWL Reasoner

Load ontology into Protégé or use OWL API:

```python
from owlready2 import get_ontology

onto = get_ontology("ontologies/it-ontology.ttl").load()
onto.sync_reasoner()  # Run reasoner
```

---

## Best Practices

1. **Always provide rdfs:label**: Makes data human-readable
2. **Add rdfs:comment**: Document intent and usage
3. **Use standard vocabularies**: SKOS for taxonomies, DC for metadata
4. **Version your ontology**: Use owl:versionInfo
5. **Link to LOD**: Connect entities to Wikidata/DBpedia
6. **Separate concerns**: Use named graphs for knowledge types
7. **Document cardinality**: Use OWL restrictions when needed

---

## SPARQL Query Examples

### Get all skills with prerequisites

```sparql
PREFIX gkf: <http://gkf.org/ontology/it#>

SELECT ?skill ?skillName ?prereq ?prereqName
WHERE {
    ?skill a gkf:TechnicalSkill ;
           gkf:skillName ?skillName ;
           gkf:prerequisite ?prereq .
    ?prereq gkf:skillName ?prereqName .
}
```

### Find courses for a specific job

```sparql
PREFIX gkf: <http://gkf.org/ontology/it#>

SELECT DISTINCT ?course ?courseName
WHERE {
    <http://gkf.org/data/Job/data-scientist> gkf:requires ?skill .
    ?course gkf:teaches ?skill ;
            gkf:courseName ?courseName .
}
```

### Get skill demand (count of jobs requiring it)

```sparql
PREFIX gkf: <http://gkf.org/ontology/it#>

SELECT ?skill ?skillName (COUNT(?job) as ?demand)
WHERE {
    ?job gkf:requires ?skill .
    ?skill gkf:skillName ?skillName .
}
GROUP BY ?skill ?skillName
ORDER BY DESC(?demand)
```

---

## References

- OWL 2 Web Ontology Language: https://www.w3.org/TR/owl2-overview/
- RDF Schema: https://www.w3.org/TR/rdf-schema/
- SKOS Vocabulary: https://www.w3.org/2004/02/skos/
- Dublin Core: https://www.dublincore.org/
- Wikidata: https://www.wikidata.org/
- DBpedia: https://www.dbpedia.org/

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-13
**Maintainer**: GKF Project Team

# Genesis Knowledge Framework - Architecture Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architectural Principles](#architectural-principles)
3. [Layer-by-Layer Architecture](#layer-by-layer-architecture)
4. [Data Flow](#data-flow)
5. [Knowledge Representation](#knowledge-representation)
6. [AI Reasoning](#ai-reasoning)
7. [API Design](#api-design)
8. [Scalability & Performance](#scalability--performance)

---

## Overview

GKF implements a 4-layer architecture inspired by the Semantic Web stack and modern data architectures. Each layer has clear responsibilities and communicates through well-defined interfaces.

### Design Goals

- **Modularity**: Each layer is independent and replaceable
- **Extensibility**: Easy to add new domains, data sources, or reasoning capabilities
- **Standards Compliance**: Full adherence to W3C semantic web standards
- **AI-Ready**: Built-in support for both symbolic and statistical reasoning
- **LOD Integration**: Native support for Linked Open Data principles

---

## Architectural Principles

### 1. Ontology-First Design

Every entity, relationship, and property in GKF maps to an ontology concept. The ontology serves as:
- The schema for all data
- The contract between layers
- The basis for inference and reasoning

### 2. Dual Knowledge Architecture

GKF distinguishes between two types of knowledge:

**Foundational Knowledge**
- Source: Authoritative datasets (Wikidata, official APIs, verified databases)
- Characteristics: Objective, globally verified, high confidence
- Storage: Dedicated named graph in triple store
- Example: "Python is a programming language created by Guido van Rossum"

**Experiential Knowledge**
- Source: Community interactions, user behaviors, ratings
- Characteristics: Subjective, context-dependent, evolving
- Storage: Separate named graph with temporal metadata
- Example: "90% of users who learned Python also learned SQL"

### 3. Linked Open Data (LOD) Compliance

All entities are:
1. Assigned HTTP URIs
2. Resolvable to RDF descriptions
3. Linked to external LOD sources (Wikidata, DBpedia)
4. Published under open licenses
5. Connected via standard vocabularies (RDF, RDFS, OWL)

---

## Layer-by-Layer Architecture

### Layer 1: Knowledge Acquisition

**Purpose**: Ingest raw data from multiple sources and transform it into structured RDF.

**Components**:

1. **Data Connectors**
   - `JSONConnector`: Fetches data from JSON files or REST APIs
   - `CSVConnector`: Reads CSV files
   - `WebScraperConnector`: Scrapes web pages using BeautifulSoup
   - Extensible: Easy to add SQL, XML, GraphQL connectors

2. **Mapping Engine**
   - Transforms raw data → RDF triples
   - Uses mapping rules (JSON config)
   - Handles data type conversions
   - Generates unique URIs for entities

3. **Entity Linker**
   - Links local entities to global URIs (Wikidata, DBpedia)
   - Uses NLP-based matching
   - Enriches entities with LOD metadata
   - Example: "Python" → `wd:Q28865`

**Example Flow**:
```
JSON Data → Connector → Mapping Engine → RDF Graph → Entity Linker → Enriched RDF
```

**Code Location**: `backend/layer1_acquisition/`

---

### Layer 2: Core Knowledge Layer

**Purpose**: Centralized storage and integration of knowledge.

**Components**:

1. **Triple Store Manager**
   - Interface to GraphDB (or any SPARQL-compatible store)
   - CRUD operations on RDF triples
   - Query execution (SELECT, CONSTRUCT, ASK)
   - Named graph management

2. **Ontology Manager**
   - Loads and validates ontologies
   - Versions ontologies
   - Extracts classes, properties, hierarchies
   - Merges multiple ontologies

3. **Knowledge Integrator**
   - Manages foundational vs experiential knowledge
   - Routes queries to appropriate named graphs
   - Calculates confidence scores
   - Enriches foundational data with experiential insights

**Named Graphs**:
```turtle
<http://gkf.org/graphs/foundational>  # Objective knowledge
<http://gkf.org/graphs/experiential>  # Community knowledge
```

**Code Location**: `backend/layer2_knowledge/`

---

### Layer 3: Intelligence & Service Layer

**Purpose**: Transform static knowledge into intelligent services.

**Components**:

1. **AI Reasoning Engine**

   **Symbolic Reasoning** (OWL 2 RL):
   - Transitive inference (skill prerequisites)
   - Property reasoning (symmetric, inverse)
   - Class hierarchy reasoning
   - SPARQL query composition

   **Statistical Reasoning**:
   - Skill similarity (co-occurrence analysis)
   - Demand prediction (job market analysis)
   - Collaborative filtering (user-based recommendations)
   - Link prediction (future connections)

2. **SPARQL Endpoint**
   - Standard W3C SPARQL 1.1 interface
   - Federated query support
   - Query optimization

3. **REST API Gateway**
   - FastAPI-based RESTful interface
   - Abstracts SPARQL complexity
   - Domain-specific endpoints
   - OpenAPI documentation

**Reasoning Examples**:

```sparql
# Transitive Prerequisites
?skill gkf:prerequisite+ ?prereq

# Skill Similarity
SELECT ?skill1 ?skill2 (COUNT(?shared) as ?similarity)
WHERE {
  ?shared gkf:teaches ?skill1 .
  ?shared gkf:teaches ?skill2 .
  FILTER(?skill1 != ?skill2)
}
GROUP BY ?skill1 ?skill2
```

**Code Location**: `backend/layer3_intelligence/`

---

### Layer 4: Application & Experience Layer

**Purpose**: End-user applications built on top of the framework.

**Components**:

1. **UI Component Library**
   - Reusable React components
   - Knowledge graph viewer (D3.js)
   - Learning path visualizer
   - Skill explorer

2. **Pilot Application: IT EduGraph**
   - Personalized learning paths
   - Job skill analysis
   - Course recommendations
   - Career progression planning

**Technology Stack**:
- React 18 + Vite
- Material-UI for components
- D3.js for graph visualization
- Axios for API communication

**Code Location**: `frontend/`

---

## Data Flow

### 1. Data Ingestion Flow

```
External Source
    ↓
Data Connector (Layer 1)
    ↓
Raw Data (JSON/CSV)
    ↓
Mapping Engine
    ↓
RDF Triples
    ↓
Entity Linker (enrichment)
    ↓
Triple Store (Layer 2)
```

### 2. Query Flow

```
User Request (Frontend)
    ↓
REST API (Layer 3)
    ↓
Reasoning Engine (optional)
    ↓
SPARQL Query Composition
    ↓
Triple Store (Layer 2)
    ↓
RDF Results
    ↓
JSON Response
    ↓
Frontend Rendering
```

### 3. Recommendation Flow

```
User Profile + Target Job
    ↓
Reasoning Engine
    ↓
Foundational Knowledge Query
    ↓
Experiential Knowledge Query
    ↓
Graph Analysis (similarity, paths)
    ↓
Recommendation Ranking
    ↓
Learning Path Generation
    ↓
Frontend Display
```

---

## Knowledge Representation

### Ontology Structure

```turtle
# Core Hierarchy
:Knowledge
  ├── :FoundationalKnowledge
  └── :ExperientialKnowledge

:Skill
  ├── :TechnicalSkill
  └── :SoftSkill

:Course
:Job
:LearningPath
:Technology
:Certification
:UserProfile
:Interaction
```

### Key Properties

**Object Properties** (entity → entity):
- `gkf:requires` (Job → Skill)
- `gkf:teaches` (Course → Skill)
- `gkf:prerequisite` (Skill → Skill) [Transitive]
- `gkf:relatedTo` (Skill → Skill) [Symmetric]

**Data Properties** (entity → literal):
- `gkf:skillName` → xsd:string
- `gkf:salary` → xsd:decimal
- `gkf:duration` → xsd:integer

**LOD Properties**:
- `gkf:wikidataURI` → xsd:anyURI
- `gkf:dbpediaURI` → xsd:anyURI

---

## AI Reasoning

### Symbolic AI Techniques

1. **Transitive Reasoning**
   ```sparql
   # If A prerequisite B, and B prerequisite C, then A prerequisite C
   ?skill gkf:prerequisite+ ?prereq
   ```

2. **Property Chain Reasoning**
   ```
   Job requires Skill → Skill taught by Course
   ⇒ Course recommended for Job
   ```

3. **OWL 2 RL Inference**
   - Class subsumption
   - Property domain/range inference
   - Inverse property reasoning

### Statistical AI Techniques

1. **Collaborative Filtering**
   ```python
   # Users who learned X also learned Y
   common_skills = analyze_user_learning_patterns()
   recommend_next_skill(current_skills, common_skills)
   ```

2. **Graph Embeddings** (Future)
   - Node2Vec for entity embeddings
   - Link prediction for future connections
   - Community detection for skill clustering

3. **Demand Prediction**
   ```python
   demand_score = (job_count * 2) + (course_count * 1)
   ```

---

## API Design

### RESTful Principles

- **Resource-Based URLs**: `/api/skills`, `/api/courses`
- **HTTP Verbs**: GET (read), POST (create), PUT (update), DELETE (remove)
- **JSON Responses**: All responses in JSON-LD (future)
- **Status Codes**: 200 (success), 404 (not found), 500 (error)

### Endpoint Categories

1. **Data Access**: Get entities (`/api/skills`, `/api/jobs`)
2. **Relationships**: Get connections (`/api/skills/{id}/prerequisites`)
3. **Intelligence**: Get recommendations (`/api/recommendations/learning-path`)
4. **SPARQL**: Raw queries (`/sparql`)

### Error Handling

```json
{
  "status": "error",
  "code": 404,
  "message": "Skill not found",
  "details": "No skill with ID 'invalid-id'"
}
```

---

## Scalability & Performance

### Horizontal Scaling

- **GraphDB Cluster**: Master-worker replication
- **API Load Balancing**: Multiple FastAPI instances
- **Caching**: Redis for query results

### Query Optimization

1. **SPARQL Optimization**
   - Use LIMIT and OFFSET for pagination
   - Index frequently queried properties
   - Avoid unbounded property paths

2. **API Caching**
   - Cache static endpoints (skills, courses)
   - TTL-based cache invalidation
   - CDN for frontend assets

### Performance Targets

- API Response Time: < 200ms (p95)
- SPARQL Query: < 500ms (p95)
- Graph Visualization: < 1s for 1000 nodes
- Data Ingestion: 10K triples/second

---

## Security Considerations

1. **Authentication**: JWT tokens for user sessions
2. **Authorization**: Role-based access control (RBAC)
3. **Data Privacy**: Anonymize experiential knowledge
4. **Input Validation**: Sanitize SPARQL queries
5. **Rate Limiting**: Prevent API abuse

---

## Future Enhancements

1. **GraphQL API**: Alternative to REST
2. **Real-time Updates**: WebSocket for live data
3. **Federated Queries**: Query external SPARQL endpoints
4. **Machine Learning**: Deep learning for embeddings
5. **Blockchain**: Immutable knowledge provenance

---

## References

- W3C RDF Specification: https://www.w3.org/RDF/
- OWL 2 Web Ontology Language: https://www.w3.org/TR/owl2-overview/
- SPARQL 1.1 Query Language: https://www.w3.org/TR/sparql11-query/
- Linked Data Principles: https://www.w3.org/DesignIssues/LinkedData.html

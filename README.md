# Genesis Knowledge Framework (GKF)

**An Ontology-Driven Platform for Building Living Knowledge Ecosystems**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The Genesis Knowledge Framework (GKF) is a modular, ontology-driven platform that enables anyone to build intelligent knowledge ecosystems. It combines semantic web technologies (RDF, OWL, SPARQL) with AI reasoning to create adaptive, domain-specific knowledge graphs.

**Pilot Application:** IT EduGraph - A personalized IT learning and career roadmap recommender.

## Key Features

- **Ontology-Centric Design**: All logic revolves around definable, domain-specific ontologies
- **Linked Open Data Compliant**: Full 5-star LOD compliance (FAIR principles)
- **Dual Knowledge Architecture**:
  - Foundational Knowledge (objective, from global datasets)
  - Experiential Knowledge (community-driven, user interactions)
- **AI-Powered Intelligence**:
  - Symbolic AI (OWL reasoning, inference)
  - Statistical AI (graph ML, recommendations)
- **Modular 4-Layer Architecture**: Acquisition → Knowledge → Intelligence → Application

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Application & Experience                      │
│  - React Frontend                                        │
│  - Knowledge Graph Visualization (D3.js)                 │
│  - Learning Path Generator                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Intelligence & Service                         │
│  - AI Reasoning Engine (Symbolic + Statistical)          │
│  - REST API (FastAPI)                                    │
│  - SPARQL Endpoint                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Core Knowledge                                 │
│  - Triple Store (GraphDB)                                │
│  - Ontology Manager                                      │
│  - Knowledge Integrator (Foundational + Experiential)    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Knowledge Acquisition                          │
│  - Data Connectors (JSON, CSV, Web Scraper)              │
│  - RDF Mapping Engine                                    │
│  - Entity Linker (Wikidata, DBpedia)                     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd GKF
```

2. Start all services with Docker Compose:
```bash
docker-compose up -d
```

This will start:
- GraphDB Triple Store (http://localhost:7200)
- Backend API (http://localhost:8000)
- Frontend Application (http://localhost:3000)

3. Load the ontology and seed data:
```bash
# Access GraphDB workbench at http://localhost:7200
# Create a new repository named "gkf"
# Import ontologies/it-ontology.ttl
# Import data/rdf/seed-data.ttl
```

4. Access the application:
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- GraphDB Workbench: http://localhost:7200

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export GRAPHDB_ENDPOINT=http://localhost:7200/repositories/gkf
export PYTHONPATH=$(pwd)/..

# Run the API server
uvicorn layer3_intelligence.api.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
GKF/
├── backend/
│   ├── layer1_acquisition/       # Data ingestion & RDF mapping
│   │   ├── connectors/           # JSON, CSV, Web scrapers
│   │   ├── mapping/              # RDF mapping engine
│   │   └── entity_linking/       # LOD entity linker
│   ├── layer2_knowledge/         # Knowledge storage & integration
│   │   ├── triplestore/          # GraphDB interface
│   │   ├── ontology/             # Ontology management
│   │   └── integration/          # Foundational vs Experiential
│   ├── layer3_intelligence/      # AI reasoning & API
│   │   ├── reasoning/            # Symbolic + Statistical AI
│   │   ├── sparql/               # SPARQL service
│   │   └── api/                  # FastAPI REST endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── views/                # Page views
│   │   └── services/             # API client
│   └── package.json
├── ontologies/
│   └── it-ontology.ttl           # IT domain ontology
├── data/
│   ├── raw/                      # Raw data sources
│   ├── rdf/                      # RDF/Turtle files
│   │   └── seed-data.ttl         # Sample data
│   └── mappings/                 # Mapping rules
├── docs/
│   ├── ARCHITECTURE.md           # Detailed architecture
│   └── ONTOLOGY_GUIDE.md         # Ontology documentation
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Skills
- `GET /api/skills` - Get all skills
- `GET /api/skills/{skill_id}` - Get skill details
- `GET /api/skills/{skill_id}/prerequisites` - Get prerequisites
- `GET /api/skills/{skill_id}/related` - Get related skills

### Courses
- `GET /api/courses` - Get all courses
- `GET /api/courses/skill/{skill_name}` - Find courses for a skill

### Jobs
- `GET /api/jobs` - Get all jobs
- `GET /api/jobs/{job_id}/skills` - Get required skills
- `GET /api/jobs/{job_id}/recommended-courses` - Get course recommendations

### Intelligent Recommendations
- `POST /api/recommendations/learning-path` - Generate learning path
- `POST /api/recommendations/next-skills` - Recommend next skills
- `GET /api/recommendations/career-path` - Analyze career progression

### SPARQL
- `POST /sparql` - Execute raw SPARQL queries

Full API documentation available at: http://localhost:8000/docs

## Usage Examples

### Generate a Learning Path

```python
import requests

response = requests.post('http://localhost:8000/api/recommendations/learning-path', json={
    "target_job_uri": "http://gkf.org/data/Job/data-scientist",
    "current_skills": [
        "http://gkf.org/data/Skill/python",
        "http://gkf.org/data/Skill/sql"
    ]
})

learning_path = response.json()
print(learning_path)
```

### Query the Knowledge Graph

```python
query = """
PREFIX gkf: <http://gkf.org/ontology/it#>

SELECT ?skill ?skillName
WHERE {
    ?skill a gkf:TechnicalSkill ;
           gkf:skillName ?skillName .
}
LIMIT 10
"""

response = requests.post('http://localhost:8000/sparql', json={"query": query})
results = response.json()
```

## Extending GKF to New Domains

GKF is designed to be domain-agnostic. To adapt it to a new domain (e.g., Healthcare, Tourism):

1. **Design Your Ontology**: Create a domain-specific ontology (OWL/Turtle)
2. **Prepare Data Sources**: Identify authoritative data sources
3. **Configure Connectors**: Set up data connectors for your sources
4. **Map to RDF**: Create mapping rules for your data
5. **Load & Query**: Import into GraphDB and use the API

Example domains:
- Healthcare: Diseases, Treatments, Medications, Symptoms
- Tourism: Destinations, Attractions, Hotels, Itineraries
- Agriculture: Crops, Techniques, Equipment, Weather

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Python, FastAPI | API & Business Logic |
| Frontend | React, Vite, Material-UI | User Interface |
| Triple Store | GraphDB | RDF Storage |
| Ontology | OWL 2, Turtle | Knowledge Modeling |
| Reasoning | RDFLib, SPARQL | Semantic Inference |
| Visualization | D3.js | Graph Visualization |
| Deployment | Docker, Docker Compose | Containerization |

## Development

### Run Tests

```bash
cd backend
pytest
```

### Add New Data

1. Place raw data in `data/raw/`
2. Create mapping rules in `data/mappings/`
3. Use Layer 1 connectors to ingest and map to RDF
4. Load RDF files into GraphDB

### Extend the Ontology

1. Edit `ontologies/it-ontology.ttl`
2. Validate with Protégé or OWL validator
3. Reload into GraphDB
4. Update API endpoints accordingly

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Roadmap

- [ ] Phase 1: MVP Core (Complete)
- [ ] Phase 2: Pilot App - IT EduGraph (In Progress)
- [ ] Phase 3: Community Intelligence
  - [ ] User interaction tracking
  - [ ] Collaborative filtering
  - [ ] Reputation system
- [ ] Phase 4: Multi-Domain Support
  - [ ] Healthcare ontology
  - [ ] Tourism ontology
  - [ ] Domain switcher UI

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Ontology design inspired by Schema.org and DBpedia
- Built with open-source semantic web technologies
- Part of the Linked Open Data community

## Contact

For questions, issues, or contributions:
- GitHub Issues: [Create an issue]
- Documentation: See `docs/` folder
- Community: [Coming soon]

---

Built with semantic web technologies for the future of intelligent knowledge systems.

# Entity Linking Architecture

## Overview

The entity linking layer has been refactored to support a modular, extensible architecture that enables linking to multiple Linked Open Data (LOD) sources, with a focus on educational ontologies.

## Architecture Design

### Core Principles

1. **Modularity**: Each LOD source has its own dedicated linker class
2. **Extensibility**: Plugin-style registry allows easy addition of new sources
3. **Separation of Concerns**: Clear interfaces and responsibilities
4. **Backward Compatibility**: Maintains existing API for legacy code

### Component Structure

```
entity_linking/
├── base_linker.py              # Abstract base class for all linkers
├── registry.py                 # Central registry for managing linkers
├── entity_linker.py            # Main API facade (backward compatible)
├── wikidata_linker.py          # Wikidata integration
├── dbpedia_linker.py           # DBpedia integration
├── esco_linker.py              # ESCO (European Skills) integration
├── openuniversity_linker.py    # Open University LOD integration
├── linkeduniversities_linker.py # LinkedUniversities integration
└── __init__.py                 # Module exports
```

## Component Details

### 1. BaseLinker (base_linker.py)

Abstract base class defining the contract for all LOD linkers.

```python
class BaseLinker(ABC):
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the unique identifier for this LOD source"""
        
    @abstractmethod
    def link(self, entity_name: str, entity_type: Optional[str] = None) -> Optional[str]:
        """Link entity to LOD source and return URI"""
        
    def batch_link(self, entity_names: list[str]) -> Dict[str, Optional[str]]:
        """Link multiple entities in batch"""
```

**Key Features:**
- Enforces consistent interface across all linkers
- Provides default batch linking implementation
- Includes validation and metadata methods

### 2. LinkerRegistry (registry.py)

Central registry managing all available linkers with plugin-style extensibility.

```python
class LinkerRegistry:
    def register_linker_class(self, name: str, linker_class: Type[BaseLinker])
    def register_linker_instance(self, name: str, linker: BaseLinker)
    def get_linker(self, name: str) -> Optional[BaseLinker]
    def get_all_linkers(self) -> Dict[str, BaseLinker]
    def list_available_linkers(self) -> List[str]
```

**Key Features:**
- Lazy instantiation (creates linkers on first access)
- Configuration management per linker
- Global registry singleton pattern
- Easy registration of custom linkers

### 3. EntityLinker (entity_linker.py)

Main facade providing unified API for entity linking operations.

```python
class EntityLinker:
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    
    # Source-specific methods (backward compatible)
    def link_to_wikidata(self, entity_name: str, entity_type: Optional[str] = None)
    def link_to_dbpedia(self, entity_name: str, entity_type: Optional[str] = None)
    def link_to_esco(self, entity_name: str, entity_type: Optional[str] = None)
    def link_to_openuniversity(self, entity_name: str, entity_type: Optional[str] = None)
    def link_to_linkeduniversities(self, entity_name: str, entity_type: Optional[str] = None)
    
    # Multi-source linking
    def link_entity(self, entity_name: str, sources: List[str] = None, ...)
    def batch_link_entities(self, entity_names: List[str], sources: List[str] = None)
    
    # RDF graph enrichment
    def enrich_graph_with_links(self, graph, entity_uris, entity_names, sources: List[str] = None)
    
    # Discovery
    def get_available_sources(self) -> List[str]
    def get_source_metadata(self, source: str) -> Dict[str, Any]
```

**Key Features:**
- Backward compatible with legacy API
- Multi-source linking in single call
- Configurable source prioritization
- RDF graph enrichment with LOD URIs

### 4. Individual Linkers

Each LOD source has a dedicated linker implementing the BaseLinker interface.

#### WikidataLinker
- **API**: Wikidata Search API (wbsearchentities)
- **Features**: Type-aware matching, entity details retrieval
- **Use Cases**: General entities, concepts, persons, organizations

#### DBpediaLinker
- **API**: DBpedia Lookup Service
- **Features**: Wikipedia-derived structured data
- **Use Cases**: Named entities, topics, categories

#### ESCOLinker
- **API**: ESCO REST API (ec.europa.eu/esco/api)
- **Features**: Skills, occupations, qualifications
- **Use Cases**: Career pathways, skill matching, job requirements
- **Specializations**: `search_skill()`, `search_occupation()`, `get_related_skills()`

#### OpenUniversityLinker
- **API**: SPARQL endpoint (data.open.ac.uk/query)
- **Features**: Courses, qualifications, organizational units
- **Use Cases**: Academic content, learning resources
- **Ontologies**: AIISO, MLO

#### LinkedUniversitiesLinker
- **API**: SPARQL endpoint (linkeduniversities.org/sparql)
- **Features**: Universities, academic programs, courses
- **Use Cases**: Global higher education data
- **Ontologies**: AIISO, FOAF

## Usage Examples

### Basic Usage

```python
from layer1_acquisition.entity_linking import EntityLinker

# Initialize linker
linker = EntityLinker()

# Link to specific source
wikidata_uri = linker.link_to_wikidata("Python", entity_type="programming language")

# Link to multiple sources
links = linker.link_entity(
    "Machine Learning",
    sources=["wikidata", "dbpedia", "esco"]
)
# Returns: {'wikidata': 'http://...', 'dbpedia': 'http://...', 'esco': 'http://...'}

# Link educational content
course_uri = linker.link_to_openuniversity("Data Science", entity_type="course")
uni_uri = linker.link_to_linkeduniversities("MIT", entity_type="university")

# Batch linking
entities = ["Python", "Java", "SQL"]
results = linker.batch_link_entities(entities, sources=["wikidata", "dbpedia"])
```

### Advanced Configuration

```python
# Custom configuration for specific linkers
config = {
    "wikidata": {
        "timeout": 15,
        "max_results": 10
    },
    "esco": {
        "language": "en",
        "api_endpoint": "https://custom-esco-endpoint.com/api"
    }
}

linker = EntityLinker(config=config)
```

### RDF Graph Enrichment

```python
from rdflib import Graph, Namespace, URIRef

graph = Graph()
gkf = Namespace("http://gkf.org/ontology/it#")

entity_names = {
    URIRef("http://gkf.org/data/Skill/python"): "Python",
    URIRef("http://gkf.org/data/Skill/ml"): "Machine Learning"
}

# Enrich with LOD links from multiple sources
enriched_graph = linker.enrich_graph_with_links(
    graph,
    entity_uris={},
    entity_names=entity_names,
    sources=["wikidata", "dbpedia", "esco"]
)

# Graph now contains triples like:
# <http://gkf.org/data/Skill/python> gkf:wikidataURI "http://www.wikidata.org/entity/Q28865"
# <http://gkf.org/data/Skill/python> gkf:dbpediaURI "http://dbpedia.org/resource/Python_(programming_language)"
```

### Extending with Custom Linkers

```python
from layer1_acquisition.entity_linking import BaseLinker, get_registry

class CustomLODLinker(BaseLinker):
    def get_source_name(self) -> str:
        return "custom_lod"
    
    def link(self, entity_name: str, entity_type: Optional[str] = None) -> Optional[str]:
        # Custom linking logic
        pass

# Register custom linker
registry = get_registry()
registry.register_linker_class("custom_lod", CustomLODLinker)

# Use it
linker = EntityLinker()
uri = linker.link_entity_to_source("Entity", "custom_lod")
```

## Design Patterns

### 1. Abstract Factory Pattern
`BaseLinker` defines the interface, concrete linkers implement specific LOD sources.

### 2. Registry Pattern
`LinkerRegistry` manages linker lifecycle and provides centralized access.

### 3. Facade Pattern
`EntityLinker` provides simplified, unified API hiding internal complexity.

### 4. Strategy Pattern
Different linking strategies (API-based, SPARQL-based) implemented by linkers.

## LOD Sources and Ontologies

### Supported LOD Sources

| Source | Type | Domain | Ontology/Schema |
|--------|------|--------|-----------------|
| Wikidata | REST API | General Knowledge | Wikidata Model |
| DBpedia | REST API | Wikipedia-derived | DBpedia Ontology |
| ESCO | REST API | Skills & Occupations | ESCO Classification |
| Open University | SPARQL | Academic Courses | AIISO, MLO |
| LinkedUniversities | SPARQL | Higher Education | AIISO, FOAF |

### Educational Ontologies Used

- **AIISO** (Academic Institution Internal Structure Ontology): Universities, courses, programs
- **MLO** (Metadata for Learning Opportunities): Course descriptions, credits
- **ESCO** (European Skills/Competences/Qualifications/Occupations): Skills taxonomy
- **LRMI** (Learning Resource Metadata Initiative): Educational resources
- **Schema.org**: General structured data

## Performance Considerations

### Caching Strategy
- Implement caching layer for frequently linked entities
- Use TTL-based cache invalidation
- Consider Redis for distributed caching

### Rate Limiting
- Respect API rate limits per source
- Implement exponential backoff for retries
- Use batch endpoints where available

### Concurrent Linking
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Parallel linking to multiple sources
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(linker.link_to_wikidata, entity),
        executor.submit(linker.link_to_dbpedia, entity),
        executor.submit(linker.link_to_esco, entity)
    ]
    results = [f.result() for f in futures]
```

## Testing

### Unit Tests
```python
import pytest
from layer1_acquisition.entity_linking import EntityLinker, get_registry, reset_registry

def test_entity_linker_initialization():
    linker = EntityLinker()
    assert len(linker.get_available_sources()) == 5

def test_wikidata_linking():
    linker = EntityLinker()
    uri = linker.link_to_wikidata("Python")
    assert uri is not None
    assert "wikidata.org" in uri

def test_registry_extensibility():
    from layer1_acquisition.entity_linking import BaseLinker
    
    class TestLinker(BaseLinker):
        def get_source_name(self):
            return "test"
        def link(self, entity_name, entity_type=None):
            return "http://test.org/entity"
    
    registry = get_registry()
    registry.register_linker_class("test", TestLinker)
    assert "test" in registry.list_available_linkers()
    
    reset_registry()  # Clean up after test
```

### Integration Tests
- Mock external API calls
- Test SPARQL query construction
- Verify RDF graph enrichment

## Migration Guide

### For Existing Code

The refactored API maintains backward compatibility:

```python
# Old code (still works)
linker = EntityLinker()
wikidata_uri = linker.link_to_wikidata("Python")
dbpedia_uri = linker.link_to_dbpedia("Python")

# New features available
links = linker.link_entity("Python", sources=["wikidata", "dbpedia", "esco"])
```

### Breaking Changes

1. `EntityLinker.__init__()` now accepts optional `config` parameter
2. `link_to_dbpedia()` signature changed: removed `max_results`, added `entity_type`
3. `enrich_graph_with_links()` now accepts `sources` parameter

## Future Enhancements

### Planned Features
- [ ] Async/await support for non-blocking I/O
- [ ] Response caching with configurable backend
- [ ] Bulk/batch API endpoints for efficiency
- [ ] Confidence scoring for entity matches
- [ ] Fuzzy matching and disambiguation
- [ ] Integration with more educational LOD sources (CourseBuffet, OCW, etc.)
- [ ] Support for multilingual linking
- [ ] Entity alignment across sources

### Additional LOD Sources to Consider
- **Schema.org**: General structured data
- **FOAF**: People and social networks
- **SKOS**: Thesauri and classification schemes
- **Dublin Core**: Metadata standards
- **GeoNames**: Geographic entities
- **VIAF**: Authority files for persons and organizations

## Troubleshooting

### Common Issues

**Issue**: Linker returns `None` for valid entity
- Check network connectivity
- Verify API endpoint availability
- Ensure entity name is correctly formatted
- Try alternative spelling/formatting

**Issue**: SPARQL timeout
- Increase timeout in config
- Simplify SPARQL query
- Check endpoint availability

**Issue**: Import errors
- Ensure all dependencies installed: `pip install requests rdflib`
- Check Python path includes project root

## References

- [Wikidata API](https://www.wikidata.org/w/api.php)
- [DBpedia Lookup Service](https://lookup.dbpedia.org/)
- [ESCO API Documentation](https://ec.europa.eu/esco/api)
- [Open University LOD](http://data.open.ac.uk/)
- [LinkedUniversities](http://linkeduniversities.org/)
- [AIISO Ontology](http://purl.org/vocab/aiiso/schema)
- [Linked Open Data Principles](https://www.w3.org/DesignIssues/LinkedData.html)

## Contributing

To add a new LOD source:

1. Create new linker class extending `BaseLinker`
2. Implement `get_source_name()` and `link()` methods
3. Add to registry in `registry.py`
4. Add convenience method to `EntityLinker` if needed
5. Update documentation
6. Add unit tests

## License

Apache-2.0 License - See LICENSE file for details

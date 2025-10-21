# Entity Linking Architecture - UML Diagrams

## Class Diagram

```
┌─────────────────────────────────────────┐
│          <<abstract>>                   │
│           BaseLinker                    │
├─────────────────────────────────────────┤
│ - config: Dict[str, Any]                │
│ - source_name: str                      │
├─────────────────────────────────────────┤
│ + get_source_name(): str  «abstract»    │
│ + link(name, type): Optional[str]       │
│   «abstract»                            │
│ + batch_link(names): Dict               │
│ + validate_uri(uri): bool               │
│ + get_metadata(): Dict                  │
└─────────────────────────────────────────┘
                    △
                    │
       ┌────────────┼────────────┐
       │            │            │
       │            │            │
┌──────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
│  Wikidata   │ │ DBpedia │ │    ESCO     │
│   Linker    │ │ Linker  │ │   Linker    │
├─────────────┤ ├─────────┤ ├─────────────┤
│ - api_url   │ │- api_url│ │ - api_url   │
│ - timeout   │ │- timeout│ │ - language  │
├─────────────┤ ├─────────┤ ├─────────────┤
│ + link()    │ │+ link() │ │ + link()    │
│ + get_      │ │+ get_   │ │ + search_   │
│   entity_   │ │  entity_│ │   skill()   │
│   details() │ │  info() │ │ + search_   │
└─────────────┘ └─────────┘ │   occupation│
                            └─────────────┘

       ┌─────────────────┐ ┌──────────────────┐
       │ OpenUniversity  │ │LinkedUniversities│
       │    Linker       │ │     Linker       │
       ├─────────────────┤ ├──────────────────┤
       │- sparql_endpoint│ │- sparql_endpoint │
       │- base_uri       │ │- base_uri        │
       ├─────────────────┤ ├──────────────────┤
       │+ link()         │ │+ link()          │
       │+ get_course_    │ │+ search_         │
       │  details()      │ │  university()    │
       └─────────────────┘ └──────────────────┘


┌──────────────────────────────────────────────┐
│           LinkerRegistry                     │
├──────────────────────────────────────────────┤
│ - _linkers: Dict[str, BaseLinker]            │
│ - _linker_classes: Dict[str, Type]           │
│ - _configs: Dict[str, Dict]                  │
├──────────────────────────────────────────────┤
│ + register_linker_class(name, class)         │
│ + register_linker_instance(name, instance)   │
│ + get_linker(name): Optional[BaseLinker]     │
│ + get_all_linkers(): Dict[str, BaseLinker]   │
│ + list_available_linkers(): List[str]        │
│ + has_linker(name): bool                     │
│ + unregister_linker(name)                    │
└──────────────────────────────────────────────┘
                    △
                    │ uses
                    │
┌───────────────────┴──────────────────────────┐
│           EntityLinker                       │
├──────────────────────────────────────────────┤
│ - registry: LinkerRegistry                   │
│ - config: Dict[str, Any]                     │
├──────────────────────────────────────────────┤
│ + link_to_wikidata(name, type)               │
│ + link_to_dbpedia(name, type)                │
│ + link_to_esco(name, type)                   │
│ + link_to_openuniversity(name, type)         │
│ + link_to_linkeduniversities(name, type)     │
│ + link_entity(name, sources, prefer)         │
│ + link_entity_to_source(name, source, type)  │
│ + batch_link_entities(names, sources)        │
│ + enrich_graph_with_links(graph, ...)        │
│ + get_available_sources(): List[str]         │
│ + get_source_metadata(source): Dict          │
└──────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
┌─────────┐                ┌──────────────┐
│  Client │                │ EntityLinker │
│  Code   │                │   (Facade)   │
└────┬────┘                └──────┬───────┘
     │                            │
     │ 1. link_entity()           │
     ├───────────────────────────►│
     │                            │
     │                            │ 2. get_linker("wikidata")
     │                            ├────────────────────┐
     │                            │                    │
     │                     ┌──────▼──────┐             │
     │                     │   Linker    │             │
     │                     │  Registry   │◄────────────┘
     │                     └──────┬──────┘
     │                            │
     │                            │ 3. returns WikidataLinker
     │                            │
     │                     ┌──────▼─────────┐
     │                     │   Wikidata     │
     │                     │    Linker      │
     │                     └──────┬─────────┘
     │                            │
     │                            │ 4. link("Python")
     │                            │
     │                            │ 5. HTTP GET to Wikidata API
     │                            ├─────────────────────►
     │                            │
     │                            │ 6. returns URI
     │                            │◄────────────────────
     │                            │
     │ 7. returns links dict      │
     │◄───────────────────────────┤
     │                            │
     │   {'wikidata': 'http://...'
     │    'dbpedia': 'http://...'}
     │
```

## Sequence Diagram: Multi-Source Linking

```
Client       EntityLinker      Registry    WikidataLinker   DBpediaLinker   ESCO Linker
  │                │               │              │               │              │
  ├──link_entity()──►              │              │               │              │
  │   sources=all  │               │              │               │              │
  │                │               │              │               │              │
  │                ├─get_linker────►              │               │              │
  │                │  "wikidata"   │              │               │              │
  │                │               │              │               │              │
  │                │◄──returns─────┤              │               │              │
  │                │   WikidataLinker             │               │              │
  │                │               │              │               │              │
  │                ├────link("Python")───────────►│               │              │
  │                │               │              │               │              │
  │                │               │ API call────►│               │              │
  │                │               │             Wikidata         │              │
  │                │               │             API              │              │
  │                │               │              │               │              │
  │                │◄─────returns URI─────────────┤               │              │
  │                │               │              │               │              │
  │                ├─get_linker────►              │               │              │
  │                │  "dbpedia"    │              │               │              │
  │                │               │              │               │              │
  │                │◄──returns─────┤              │               │              │
  │                │   DBpediaLinker              │               │              │
  │                │               │              │               │              │
  │                ├────link("Python")────────────┼──────────────►│              │
  │                │               │              │               │              │
  │                │               │              │  API call────►│              │
  │                │               │              │              DBpedia         │
  │                │               │              │               API            │
  │                │               │              │               │              │
  │                │◄─────returns URI─────────────────────────────┤              │
  │                │               │              │               │              │
  │                ├─get_linker────►              │               │              │
  │                │  "esco"       │              │               │              │
  │                │               │              │               │              │
  │                │◄──returns─────┤              │               │              │
  │                │   ESCOLinker                 │               │              │
  │                │               │              │               │              │
  │                ├────link("Python")────────────┼───────────────┼─────────────►│
  │                │               │              │               │              │
  │                │               │              │               │ API call────►│
  │                │               │              │               │              ESCO
  │                │               │              │               │              API
  │                │               │              │               │              │
  │                │◄─────returns URI────────────────────────────────────────────┤
  │                │               │              │               │              │
  │◄────returns────┤               │              │               │              │
  │   links dict   │               │              │               │              │
  │   {wikidata:..}│               │              │               │              │
  │   {dbpedia:..} │               │              │               │              │
  │   {esco:...}   │               │              │               │              │
```

## State Diagram: Linker Lifecycle

```
                    ┌──────────────┐
                    │Not Registered│
                    └───────┬──────┘
                            │
                            │ register_linker_class()
                            │
                    ┌───────▼──────┐
                    │  Registered  │
                    │ (Class Only) │
                    └───────┬──────┘
                            │
                            │ get_linker() [first call]
                            │
                    ┌───────▼──────────┐
                    │   Instantiated   │
                    │   (Ready to Use) │
                    └───────┬──────────┘
                            │
                    ┌───────┴────────┐
                    │                │
            ┌───────▼───────┐ ┌──────▼──────┐
            │  Linking      │ │    Idle     │
            │  (Active API  │ │             │
            │   Calls)      │ │             │
            └───────┬───────┘ └──────┬──────┘
                    │                │
                    └───────┬────────┘
                            │
                            │ unregister_linker()
                            │
                   ┌────────▼────────┐
                   │  Unregistered   │
                   │  (Removed)      │
                   └─────────────────┘
```

## Deployment Diagram

```
┌───────────────────────────────────────────────────────────┐
│                   Application Server                      │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │       Layer 1: Knowledge Acquisition                 │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────┐   │ │
│  │  │      Entity Linking Module                    │   │ │
│  │  │                                               │   │ │
│  │  │  ┌─────────────┐    ┌──────────────────┐    │   │ │
│  │  │  │EntityLinker │────│LinkerRegistry    │    │   │ │
│  │  │  │  (Facade)   │    │                  │    │   │ │
│  │  │  └─────────────┘    └────────┬─────────┘    │   │ │
│  │  │                              │              │   │ │
│  │  │         ┌────────────────────┼────────┐     │   │ │
│  │  │         │                    │        │     │   │ │
│  │  │  ┌──────▼─────┐    ┌────────▼───┐ ┌─▼──┐  │   │ │
│  │  │  │  Wikidata  │    │  DBpedia   │ │ESCO│  │   │ │
│  │  │  │   Linker   │    │   Linker   │ │... │  │   │ │
│  │  │  └────────────┘    └────────────┘ └────┘  │   │ │
│  │  └───────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────┬─────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
    ┌─────▼────┐ ┌────▼─────┐ ┌──▼────────┐
    │ Wikidata │ │ DBpedia  │ │   ESCO    │
    │   API    │ │   API    │ │   API     │
    │(External)│ │(External)│ │(External) │
    └──────────┘ └──────────┘ └───────────┘

    ┌──────────────┐ ┌─────────────────┐
    │OpenUniversity│ │LinkedUniversities│
    │  SPARQL      │ │    SPARQL       │
    │  Endpoint    │ │    Endpoint     │
    │ (External)   │ │   (External)    │
    └──────────────┘ └─────────────────┘
```

## Package Diagram

```
┌────────────────────────────────────────────────────────┐
│    layer1_acquisition.entity_linking                   │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │            Core Interfaces                        │ │
│  │  ┌──────────────┐    ┌─────────────────────┐    │ │
│  │  │ base_linker  │    │    registry.py      │    │ │
│  │  │     .py      │    │                     │    │ │
│  │  └──────────────┘    └─────────────────────┘    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │      LOD Source Implementations                   │ │
│  │  ┌─────────────┐  ┌─────────────┐               │ │
│  │  │ wikidata    │  │  dbpedia    │               │ │
│  │  │ _linker.py  │  │  _linker.py │               │ │
│  │  └─────────────┘  └─────────────┘               │ │
│  │                                                   │ │
│  │  ┌─────────────┐  ┌──────────────────────┐      │ │
│  │  │   esco      │  │  openuniversity      │      │ │
│  │  │ _linker.py  │  │    _linker.py        │      │ │
│  │  └─────────────┘  └──────────────────────┘      │ │
│  │                                                   │ │
│  │  ┌──────────────────────┐                        │ │
│  │  │ linkeduniversities   │                        │ │
│  │  │    _linker.py        │                        │ │
│  │  └──────────────────────┘                        │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │         Main API                                  │ │
│  │  ┌─────────────────┐    ┌──────────────┐        │ │
│  │  │ entity_linker   │    │  __init__.py │        │ │
│  │  │     .py         │    │              │        │ │
│  │  └─────────────────┘    └──────────────┘        │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
                        │
                        │ depends on
                        ▼
        ┌───────────────────────────┐
        │  External Dependencies    │
        │                           │
        │  - requests               │
        │  - rdflib                 │
        │  - typing                 │
        │  - logging                │
        └───────────────────────────┘
```

## Design Patterns Applied

### 1. Abstract Factory Pattern

```
BaseLinker (Abstract Factory)
    │
    ├─ WikidataLinker (Concrete Factory)
    ├─ DBpediaLinker (Concrete Factory)
    └─ ESCOLinker (Concrete Factory)
```

### 2. Registry Pattern

```
LinkerRegistry manages all linker instances
    │
    ├─ Lazy instantiation
    ├─ Configuration injection
    └─ Lifecycle management
```

### 3. Facade Pattern

```
EntityLinker (Facade)
    │
    └─ Simplifies complex subsystem of multiple linkers
```

### 4. Strategy Pattern

```
Different linking strategies:
    ├─ REST API based (Wikidata, DBpedia, ESCO)
    └─ SPARQL based (OpenUniversity, LinkedUniversities)
```

### 5. Template Method Pattern

```
BaseLinker.batch_link() (Template Method)
    │
    └─ Calls abstract link() method for each entity
```

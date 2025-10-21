"""
Example Usage of Entity Linking Module

Demonstrates how to use the refactored entity linking system
with multiple LOD sources.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from layer1_acquisition.entity_linking import EntityLinker, get_registry


def example_basic_linking():
    """Basic entity linking to different sources."""
    print("=" * 60)
    print("Example 1: Basic Entity Linking")
    print("=" * 60)

    linker = EntityLinker()

    # Link to Wikidata
    print("\n1. Linking 'Python' to Wikidata:")
    wikidata_uri = linker.link_to_wikidata("Python", entity_type="programming language")
    print(f"   Result: {wikidata_uri}")

    # Link to DBpedia
    print("\n2. Linking 'Python' to DBpedia:")
    dbpedia_uri = linker.link_to_dbpedia("Python", entity_type="programming language")
    print(f"   Result: {dbpedia_uri}")

    # Link to ESCO (skills taxonomy)
    print("\n3. Linking 'Python Programming' to ESCO:")
    esco_uri = linker.link_to_esco("Python Programming", entity_type="skill")
    print(f"   Result: {esco_uri}")


def example_multi_source_linking():
    """Link entity to multiple sources at once."""
    print("\n" + "=" * 60)
    print("Example 2: Multi-Source Linking")
    print("=" * 60)

    linker = EntityLinker()

    entity_name = "Machine Learning"
    sources = ["wikidata", "dbpedia", "esco"]

    print(f"\nLinking '{entity_name}' to multiple sources:")
    print(f"Sources: {sources}")

    links = linker.link_entity(entity_name, sources=sources)

    print("\nResults:")
    for source, uri in links.items():
        print(f"  - {source:20s}: {uri}")


def example_batch_linking():
    """Batch link multiple entities."""
    print("\n" + "=" * 60)
    print("Example 3: Batch Linking")
    print("=" * 60)

    linker = EntityLinker()

    entities = ["Python", "Java", "Machine Learning", "Data Science"]
    sources = ["wikidata", "dbpedia"]

    print(f"\nBatch linking {len(entities)} entities:")
    print(f"Entities: {entities}")
    print(f"Sources: {sources}")

    results = linker.batch_link_entities(entities, sources=sources)

    print("\nResults:")
    for entity, links in results.items():
        print(f"\n  {entity}:")
        for source, uri in links.items():
            status = "✓" if uri else "✗"
            print(f"    [{status}] {source}: {uri[:60] if uri else 'Not found'}...")


def example_educational_linking():
    """Link educational entities to specialized sources."""
    print("\n" + "=" * 60)
    print("Example 4: Educational Entity Linking")
    print("=" * 60)

    linker = EntityLinker()

    # Link course to Open University
    print("\n1. Linking course to Open University:")
    course_name = "Introduction to Computer Science"
    course_uri = linker.link_to_openuniversity(course_name, entity_type="course")
    print(f"   Course: {course_name}")
    print(f"   Result: {course_uri}")

    # Link skill to ESCO
    print("\n2. Linking skill to ESCO:")
    skill_name = "Python Programming"
    skill_uri = linker.link_to_esco(skill_name, entity_type="skill")
    print(f"   Skill: {skill_name}")
    print(f"   Result: {skill_uri}")

    # Link university to LinkedUniversities
    print("\n3. Linking university to LinkedUniversities:")
    uni_name = "Massachusetts Institute of Technology"
    uni_uri = linker.link_to_linkeduniversities(uni_name, entity_type="university")
    print(f"   University: {uni_name}")
    print(f"   Result: {uni_uri}")


def example_custom_configuration():
    """Use custom configuration for linkers."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Configuration")
    print("=" * 60)

    # Custom configuration
    config = {
        "wikidata": {"timeout": 15, "max_results": 10},
        "esco": {"language": "en", "timeout": 20},
    }

    print("\nCustom configuration:")
    for source, settings in config.items():
        print(f"  {source}: {settings}")

    linker = EntityLinker(config=config)

    print("\n✓ EntityLinker initialized with custom config")


def example_registry_inspection():
    """Inspect registry and available sources."""
    print("\n" + "=" * 60)
    print("Example 6: Registry Inspection")
    print("=" * 60)

    linker = EntityLinker()

    # Get available sources
    sources = linker.get_available_sources()
    print(f"\nAvailable LOD sources: {len(sources)}")
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source}")

    # Get registry info
    registry = get_registry()
    info = registry.get_registry_info()

    print(f"\nRegistry Information:")
    print(f"  Total linkers: {info['total_linkers']}")
    print(f"  Instantiated: {info['instantiated_linkers']}")
    print(f"  Configured: {len(info['configured_linkers'])}")


def example_rdf_enrichment():
    """Enrich RDF graph with LOD links."""
    print("\n" + "=" * 60)
    print("Example 7: RDF Graph Enrichment")
    print("=" * 60)

    from rdflib import Graph, Namespace, URIRef, Literal, RDF

    linker = EntityLinker()

    # Create a simple RDF graph
    graph = Graph()
    gkf = Namespace("http://gkf.org/ontology/it#")
    data_ns = Namespace("http://gkf.org/data/")

    graph.bind("gkf", gkf)
    graph.bind("data", data_ns)

    # Add some entities
    python_uri = data_ns["Skill/python"]
    graph.add((python_uri, RDF.type, gkf.Skill))
    graph.add((python_uri, gkf.skillName, Literal("Python")))

    ml_uri = data_ns["Skill/ml"]
    graph.add((ml_uri, RDF.type, gkf.Skill))
    graph.add((ml_uri, gkf.skillName, Literal("Machine Learning")))

    print(f"\nOriginal graph size: {len(graph)} triples")

    # Prepare entity names mapping
    entity_names = {python_uri: "Python", ml_uri: "Machine Learning"}

    # Enrich with LOD links
    print("\nEnriching graph with LOD links from Wikidata and DBpedia...")
    enriched_graph = linker.enrich_graph_with_links(
        graph,
        entity_uris={},
        entity_names=entity_names,
        sources=["wikidata", "dbpedia"],
    )

    print(f"Enriched graph size: {len(enriched_graph)} triples")
    print(f"Added {len(enriched_graph) - 4} LOD link triples")

    # Display some results
    print("\nSample LOD links added:")
    for s, p, o in enriched_graph:
        if "URI" in str(p):
            print(f"  {s.split('/')[-1]} -> {p.split('#')[-1]}: {o}")


def main():
    """Run all examples."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Entity Linking Module - Examples" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")

    try:
        # Example 1: Basic linking
        example_basic_linking()

        # Example 2: Multi-source linking
        example_multi_source_linking()

        # Example 3: Batch linking
        example_batch_linking()

        # Example 4: Educational linking
        example_educational_linking()

        # Example 5: Custom configuration
        example_custom_configuration()

        # Example 6: Registry inspection
        example_registry_inspection()

        # Example 7: RDF enrichment
        example_rdf_enrichment()

        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

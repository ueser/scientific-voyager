"""
Example: Using DummyLLMRelationshipExtractor with the KnowledgeGraph.
"""
from scientific_voyager.storage.local_store import LocalStatementStore
from scientific_voyager.graph.knowledge_graph import KnowledgeGraph
from scientific_voyager.graph.relationship_extraction import DummyLLMRelationshipExtractor

def main():
    # Load statements from local storage
    store = LocalStatementStore(storage_dir="data/statements")
    kg = KnowledgeGraph()
    kg.load_from_storage(store)

    print(f"Loaded {len(kg.all_statements())} statements into the knowledge graph.")
    
    # Run dummy relationship extraction
    extractor = DummyLLMRelationshipExtractor()
    relations = extractor.extract_all(kg.all_statements())

    print(f"\nExtracted {len(relations)} relationships:")
    for rel in relations:
        print(rel)
        # Optionally, add to the graph as edges (with type from rel['relation_type'])
        kg.connect(from_uid=rel['from'], to_uid=rel['to'], edge_type=rel['relation_type'])

    # Show all edges in the graph
    print("\nGraph Edges (after relationship extraction):")
    for edge in kg.edges:
        print(edge)

if __name__ == "__main__":
    main()

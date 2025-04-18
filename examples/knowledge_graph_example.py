"""
Example: Loading and using the KnowledgeGraph with LocalStatementStore.
"""
from scientific_voyager.storage.local_store import LocalStatementStore
from scientific_voyager.graph.knowledge_graph import KnowledgeGraph

def main():
    # Load statements from local storage
    store = LocalStatementStore(storage_dir="data/statements")
    kg = KnowledgeGraph()
    kg.load_from_storage(store)

    print(f"Loaded {len(kg.all_statements())} statements into the knowledge graph.")
    print("Statements:")
    for stmt in kg.all_statements():
        print(f"- UID: {stmt.uid}, Text: {stmt.statement.text}, Types: {getattr(stmt.statement, 'types', [])}")

    # Example: add a dummy entity and connect it to a statement
    # (In a real pipeline, you would load entities from storage or extraction)
    from scientific_voyager.interfaces.storage_dto import StoredEntityDTO
    from scientific_voyager.interfaces.extraction_dto import EntityDTO
    entity = StoredEntityDTO(
        entity=EntityDTO(
            text="PTEN",
            type="gene",
            start_char=0,
            end_char=4,
            confidence=1.0
        ),
        uid="demo-entity-1"
    )
    kg.add_entity(entity)
    # Connect the first statement to the entity
    if kg.all_statements():
        stmt_uid = str(kg.all_statements()[0].uid)
        kg.connect(from_uid=stmt_uid, to_uid="demo-entity-1", edge_type="MENTIONS")
        print(f"Connected statement {stmt_uid} to entity 'PTEN'.")

    # Print all edges
    print("\nGraph Edges:")
    for edge in kg.edges:
        print(edge)

if __name__ == "__main__":
    main()

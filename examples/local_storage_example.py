"""
Example: Using LocalStatementStore to save and load classified statements.
"""
import os
from scientific_voyager.storage.local_store import LocalStatementStore
from scientific_voyager.interfaces.storage_dto import StoredStatementDTO
from scientific_voyager.interfaces.extraction_dto import StatementDTO

def main():
    # Set up the local store (will create data/statements/ if not exists)
    store = LocalStatementStore(storage_dir="data/statements")

    # Create a sample classified statement
    statement = StatementDTO(
        text="The PTEN gene mutation leads to increased PI3K/AKT pathway activation.",
        types=["causal", "descriptive"],
        biological_scales=["genetic", "molecular"],
        cross_scale_relations=[{
            "source_scale": "genetic",
            "target_scale": "molecular",
            "relation_type": "causal",
            "description": "Mutation in PTEN gene (genetic) leads to activation of PI3K/AKT pathway (molecular)."
        }],
        confidence=0.95,
        metadata={"source": "example", "type_confidences": {"causal": 0.95, "descriptive": 0.8}, "scale_confidences": {"genetic": 0.9, "molecular": 0.85}}
    )
    stored_statement = StoredStatementDTO(statement=statement, tags=["demo", "biology"])

    # Save the statement
    store.save_statement(stored_statement)
    print(f"Saved statement with UID: {stored_statement.uid}")

    # Create another statement
    statement2 = StatementDTO(
        text="PTEN negatively regulates the PI3K/AKT signaling pathway.",
        types=["causal"],
        biological_scales=["molecular"],
        cross_scale_relations=[],
        confidence=0.92,
        metadata={"source": "example2"}
    )
    stored_statement2 = StoredStatementDTO(statement=statement2, tags=["biology"])
    store.save_statement(stored_statement2)
    print(f"Saved statement with UID: {stored_statement2.uid}")

    # Load by UID
    loaded = store.get_statement_by_uid(str(stored_statement.uid))
    print("\nLoaded by UID:")
    print(f"Text: {loaded.statement.text}")
    print(f"Types: {loaded.statement.types}")
    print(f"Scales: {loaded.statement.biological_scales}")
    print(f"Tags: {loaded.tags}")
    print(f"Confidence: {loaded.statement.confidence}")
    print(f"Metadata: {loaded.statement.metadata}")

    # Load all statements
    all_statements = store.load_all_statements()
    print(f"\nTotal statements in store: {len(all_statements)}")
    for s in all_statements:
        print(f"- UID: {s.uid}, Text: {s.statement.text}")

    # Search by type
    search_results = store.search_statements(type="causal")
    print(f"\nSearch by type='causal': {len(search_results)} result(s)")
    for s in search_results:
        print(f"- UID: {s.uid}, Types: {s.statement.types}")

if __name__ == "__main__":
    main()

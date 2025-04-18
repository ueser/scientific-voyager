import os
import shutil
import tempfile
from scientific_voyager.storage.local_store import LocalStatementStore
from scientific_voyager.interfaces.storage_dto import StoredStatementDTO
from scientific_voyager.interfaces.extraction_dto import StatementDTO

def test_local_statement_store_basic():
    # Setup temp directory
    temp_dir = tempfile.mkdtemp()
    store = LocalStatementStore(storage_dir=temp_dir)

    # Create a StatementDTO and wrap in StoredStatementDTO
    stmt = StatementDTO(
        text="Test statement",
        types=["causal", "descriptive"],
        biological_scales=["genetic"],
        confidence=0.95,
        cross_scale_relations=[],
        metadata={"test": True}
    )
    stored_stmt = StoredStatementDTO(statement=stmt)

    # Save
    store.save_statement(stored_stmt)
    uid = str(stored_stmt.uid)
    assert os.path.exists(os.path.join(temp_dir, f"{uid}.json"))

    # Load by UID
    loaded = store.get_statement_by_uid(uid)
    assert loaded is not None
    assert loaded.statement.text == "Test statement"
    assert loaded.statement.types == ["causal", "descriptive"]

    # Load all
    all_loaded = store.load_all_statements()
    assert len(all_loaded) == 1
    assert all_loaded[0].statement.text == "Test statement"

    # Search by type
    results = store.search_statements(type="causal")
    assert len(results) == 1
    assert results[0].statement.text == "Test statement"

    # Search by scale (negative case)
    results = store.search_statements(scale="molecular")
    assert len(results) == 0

    # Cleanup
    shutil.rmtree(temp_dir)

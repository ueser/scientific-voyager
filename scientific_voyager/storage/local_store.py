import os
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from scientific_voyager.interfaces.storage_dto import StoredStatementDTO

class LocalStatementStore:
    """
    Local file-based storage for StoredStatementDTO objects.
    Each statement is stored as a separate JSON file in a target directory.
    """
    def __init__(self, storage_dir: str = "data/statements"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_statement_path(self, uid: str) -> str:
        return os.path.join(self.storage_dir, f"{uid}.json")

    def save_statement(self, stored_statement: StoredStatementDTO) -> None:
        path = self._get_statement_path(str(stored_statement.uid))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stored_statement.to_dict(), f, ensure_ascii=False, indent=2)

    def load_all_statements(self) -> List[StoredStatementDTO]:
        statements = []
        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json"):
                with open(os.path.join(self.storage_dir, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    statements.append(StoredStatementDTO.from_dict(data))
        return statements

    def get_statement_by_uid(self, uid: str) -> Optional[StoredStatementDTO]:
        path = self._get_statement_path(uid)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return StoredStatementDTO.from_dict(data)

    def search_statements(self, **filters) -> List[StoredStatementDTO]:
        # Supported filters: type, scale, tag, etc.
        all_statements = self.load_all_statements()
        results = []
        for stmt in all_statements:
            match = True
            for key, value in filters.items():
                # Example: filter by statement type
                if key == "type" and value not in getattr(stmt.statement, "types", []):
                    match = False
                if key == "scale" and value not in getattr(stmt.statement, "biological_scales", []):
                    match = False
                if key == "tag" and value not in getattr(stmt, "tags", []):
                    match = False
            if match:
                results.append(stmt)
        return results

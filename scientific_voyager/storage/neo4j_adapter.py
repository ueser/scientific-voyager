"""
Neo4jStatementStore: Adapter for storing and querying scientific statements, entities, and relations in Neo4j.
"""
from typing import List, Optional, Dict, Any
from neo4j import GraphDatabase, Driver, Session
from scientific_voyager.interfaces.storage_dto import StoredStatementDTO, StoredEntityDTO, StoredRelationDTO

class Neo4jStatementStore:
    def __init__(self, uri: str, user: str, password: str):
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def save_statement(self, stored_statement: StoredStatementDTO) -> None:
        with self.driver.session() as session:
            session.write_transaction(self._create_statement_tx, stored_statement)

    @staticmethod
    def _create_statement_tx(tx: Session, stored_statement: StoredStatementDTO):
        stmt = stored_statement.statement
        # Create statement node
        tx.run(
            """
            MERGE (s:Statement {uid: $uid})
            SET s.text = $text,
                s.types = $types,
                s.biological_scales = $biological_scales,
                s.confidence = $confidence,
                s.tags = $tags,
                s.created_at = $created_at,
                s.updated_at = $updated_at,
                s.metadata = $metadata
            """,
            uid=str(stored_statement.uid),
            text=stmt.text,
            types=getattr(stmt, "types", []),
            biological_scales=getattr(stmt, "biological_scales", []),
            confidence=stmt.confidence,
            tags=getattr(stored_statement, "tags", []),
            created_at=str(getattr(stored_statement, "created_at", "")),
            updated_at=str(getattr(stored_statement, "updated_at", "")),
            metadata=getattr(stored_statement, "metadata", {})
        )
        # TODO: Add code to create and link entities, relations, etc.

    def get_statement_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.read_transaction(self._get_statement_tx, uid)
            return result

    @staticmethod
    def _get_statement_tx(tx: Session, uid: str) -> Optional[Dict[str, Any]]:
        res = tx.run("MATCH (s:Statement {uid: $uid}) RETURN s", uid=uid)
        record = res.single()
        if record:
            return dict(record["s"])
        return None

    def close(self):
        self.driver.close()

"""
KnowledgeGraph: In-memory graph structure integrating with statement/entity/relation DTOs and storage.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID
from scientific_voyager.interfaces.storage_dto import StoredStatementDTO, StoredEntityDTO, StoredRelationDTO

class KnowledgeGraph:
    def __init__(self):
        # Nodes: {uid: StoredStatementDTO or StoredEntityDTO or StoredRelationDTO}
        self.statements: Dict[str, StoredStatementDTO] = {}
        self.entities: Dict[str, StoredEntityDTO] = {}
        self.relations: Dict[str, StoredRelationDTO] = {}
        # Edges: (statement_uid, relation_uid, entity_uid)
        self.edges: List[Dict[str, Any]] = []  # List of {from, to, type, relation_uid}

    # --- Traversal Algorithms ---
    def bfs(self, start_uid: str) -> List[str]:
        """Breadth-first traversal from a node (statement/entity/relation UID). Returns list of visited UIDs."""
        visited = set()
        queue = [start_uid]
        while queue:
            uid = queue.pop(0)
            if uid not in visited:
                visited.add(uid)
                neighbors = [e['to'] for e in self.edges if e['from'] == uid] + [e['from'] for e in self.edges if e['to'] == uid]
                for n in neighbors:
                    if n not in visited:
                        queue.append(n)
        return list(visited)

    def dfs(self, start_uid: str) -> List[str]:
        """Depth-first traversal from a node. Returns list of visited UIDs."""
        visited = set()
        stack = [start_uid]
        while stack:
            uid = stack.pop()
            if uid not in visited:
                visited.add(uid)
                neighbors = [e['to'] for e in self.edges if e['from'] == uid] + [e['from'] for e in self.edges if e['to'] == uid]
                for n in neighbors:
                    if n not in visited:
                        stack.append(n)
        return list(visited)

    def find_path(self, start_uid: str, end_uid: str) -> Optional[List[str]]:
        """Finds a path between two nodes using BFS. Returns list of UIDs or None if not found."""
        from collections import deque
        visited = set()
        queue = deque([(start_uid, [start_uid])])
        while queue:
            current, path = queue.popleft()
            if current == end_uid:
                return path
            visited.add(current)
            neighbors = [e['to'] for e in self.edges if e['from'] == current] + [e['from'] for e in self.edges if e['to'] == current]
            for n in neighbors:
                if n not in visited:
                    queue.append((n, path + [n]))
        return None

    # --- Manipulation Operations ---
    def merge_nodes(self, uids: List[str], new_uid: str, node_type: str = 'statement') -> None:
        """Merge multiple nodes into a new node with new_uid. node_type: 'statement' or 'entity'."""
        if node_type == 'statement':
            merged_text = ' '.join([self.statements[uid].statement.text for uid in uids if uid in self.statements])
            merged_types = list({t for uid in uids for t in (self.statements[uid].statement.types if uid in self.statements else [])})
            from scientific_voyager.interfaces.storage_dto import StoredStatementDTO
            from scientific_voyager.interfaces.extraction_dto import StatementDTO
            merged_stmt = StatementDTO(
                text=merged_text,
                types=merged_types,
                biological_scales=[],
                cross_scale_relations=[],
                confidence=1.0,
                metadata={"merged_from": uids}
            )
            self.statements[new_uid] = StoredStatementDTO(statement=merged_stmt, tags=["merged"])
            for uid in uids:
                if uid in self.statements:
                    del self.statements[uid]
        elif node_type == 'entity':
            merged_text = ' '.join([self.entities[uid].entity.text for uid in uids if uid in self.entities])
            merged_type = self.entities[uids[0]].entity.type if uids and uids[0] in self.entities else "entity"
            from scientific_voyager.interfaces.storage_dto import StoredEntityDTO
            from scientific_voyager.interfaces.extraction_dto import EntityDTO
            merged_entity = EntityDTO(
                text=merged_text,
                type=merged_type,
                start_char=0,
                end_char=len(merged_text),
                confidence=1.0
            )
            self.entities[new_uid] = StoredEntityDTO(entity=merged_entity)
            for uid in uids:
                if uid in self.entities:
                    del self.entities[uid]
        # Update edges to point to new_uid
        for edge in self.edges:
            if edge['from'] in uids:
                edge['from'] = new_uid
            if edge['to'] in uids:
                edge['to'] = new_uid

    def split_node(self, uid: str, new_nodes: List[Dict[str, Any]], node_type: str = 'statement') -> None:
        """Split a node into multiple new nodes. new_nodes: list of dicts for new node attributes."""
        if node_type == 'statement' and uid in self.statements:
            del self.statements[uid]
            from scientific_voyager.interfaces.storage_dto import StoredStatementDTO
            from scientific_voyager.interfaces.extraction_dto import StatementDTO
            for attrs in new_nodes:
                stmt = StatementDTO(**attrs)
                self.statements[attrs['uid']] = StoredStatementDTO(statement=stmt, tags=["split"])
        elif node_type == 'entity' and uid in self.entities:
            del self.entities[uid]
            from scientific_voyager.interfaces.storage_dto import StoredEntityDTO
            from scientific_voyager.interfaces.extraction_dto import EntityDTO
            for attrs in new_nodes:
                ent = EntityDTO(**attrs)
                self.entities[attrs['uid']] = StoredEntityDTO(entity=ent)
        # Update edges: disconnect edges involving the split node
        self.edges = [e for e in self.edges if e['from'] != uid and e['to'] != uid]

    def disconnect(self, from_uid: str, to_uid: str) -> None:
        """Remove all edges between from_uid and to_uid."""
        self.edges = [e for e in self.edges if not ((e['from'] == from_uid and e['to'] == to_uid) or (e['from'] == to_uid and e['to'] == from_uid))]

    def add_statement(self, stmt: StoredStatementDTO):
        self.statements[str(stmt.uid)] = stmt

    def add_entity(self, ent: StoredEntityDTO):
        self.entities[str(ent.uid)] = ent

    def add_relation(self, rel: StoredRelationDTO):
        self.relations[str(rel.uid)] = rel

    def connect(self, from_uid: str, to_uid: str, relation_uid: Optional[str] = None, edge_type: str = "MENTIONS"):
        self.edges.append({
            "from": from_uid,
            "to": to_uid,
            "relation_uid": relation_uid,
            "type": edge_type
        })

    def get_statement(self, uid: str) -> Optional[StoredStatementDTO]:
        return self.statements.get(uid)

    def get_entity(self, uid: str) -> Optional[StoredEntityDTO]:
        return self.entities.get(uid)

    def get_relation(self, uid: str) -> Optional[StoredRelationDTO]:
        return self.relations.get(uid)

    def find_edges(self, uid: str) -> List[Dict[str, Any]]:
        return [e for e in self.edges if e["from"] == uid or e["to"] == uid]

    def all_statements(self) -> List[StoredStatementDTO]:
        return list(self.statements.values())

    def all_entities(self) -> List[StoredEntityDTO]:
        return list(self.entities.values())

    def all_relations(self) -> List[StoredRelationDTO]:
        return list(self.relations.values())

    def load_from_storage(self, store) -> None:
        """
        Loads all statements/entities/relations from a storage backend implementing the IStorageAdapter interface.
        """
        if hasattr(store, "load_all_statements"):
            for stmt in store.load_all_statements():
                self.add_statement(stmt)
        if hasattr(store, "load_all_entities"):
            for ent in store.load_all_entities():
                self.add_entity(ent)
        if hasattr(store, "load_all_relations"):
            for rel in store.load_all_relations():
                self.add_relation(rel)

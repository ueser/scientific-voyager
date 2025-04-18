"""
Local storage adapter for the Scientific Voyager platform.

This module implements a filesystem-based storage adapter for storing
and retrieving statements, entities, and other data objects.
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
from uuid import UUID, uuid4

from scientific_voyager.interfaces.storage_interface import IStorageAdapter, IIndexManager, IUIDGenerator
from scientific_voyager.interfaces.extraction_dto import StatementDTO, EntityDTO, RelationDTO
from scientific_voyager.interfaces.classification_dto import ClassificationResultDTO
from scientific_voyager.interfaces.storage_dto import (
    StoredStatementDTO, StoredClassificationDTO, StoredEntityDTO, 
    StoredRelationDTO, StorageStatsDTO
)
from scientific_voyager.config.config_manager import get_config

# Configure logger
logger = logging.getLogger(__name__)


class UIDGenerator(IUIDGenerator):
    """Implementation of the UID generator interface."""
    
    def generate_uid(self, prefix: Optional[str] = None) -> UUID:
        """
        Generate a unique identifier.
        
        Args:
            prefix: Optional prefix for the UID (ignored in this implementation)
            
        Returns:
            A unique identifier
        """
        return uuid4()
    
    def validate_uid(self, uid: Union[str, UUID]) -> bool:
        """
        Validate a unique identifier.
        
        Args:
            uid: The UID to validate
            
        Returns:
            True if the UID is valid, False otherwise
        """
        try:
            if isinstance(uid, str):
                UUID(uid)
            return True
        except ValueError:
            return False


class LocalIndexManager(IIndexManager):
    """Implementation of the index manager interface for local storage."""
    
    def __init__(self, storage_dir: Path):
        """
        Initialize the local index manager.
        
        Args:
            storage_dir: Directory where indexes are stored
        """
        self.storage_dir = storage_dir
        self.indexes_dir = storage_dir / "indexes"
        self.indexes_dir.mkdir(exist_ok=True, parents=True)
        self._load_indexes()
    
    def _load_indexes(self):
        """Load existing indexes from disk."""
        self.indexes = {}
        index_file = self.indexes_dir / "index_metadata.json"
        
        if index_file.exists():
            try:
                with open(index_file, "r") as f:
                    self.indexes = json.load(f)
            except Exception as e:
                logger.error(f"Error loading indexes: {e}")
                self.indexes = {}
        
        # Initialize with empty indexes if file doesn't exist
        for collection in ["statements", "classifications", "entities", "relations"]:
            if collection not in self.indexes:
                self.indexes[collection] = []
    
    def _save_indexes(self):
        """Save index metadata to disk."""
        index_file = self.indexes_dir / "index_metadata.json"
        
        try:
            with open(index_file, "w") as f:
                json.dump(self.indexes, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving indexes: {e}")
    
    def create_index(self, collection: str, field: str) -> bool:
        """
        Create an index on a field in a collection.
        
        Args:
            collection: The collection to create the index on
            field: The field to index
            
        Returns:
            True if the index was created successfully, False otherwise
        """
        if collection not in self.indexes:
            self.indexes[collection] = []
        
        if field in self.indexes[collection]:
            logger.warning(f"Index already exists on {collection}.{field}")
            return True
        
        try:
            # Create the index directory
            index_dir = self.indexes_dir / collection / field
            index_dir.mkdir(exist_ok=True, parents=True)
            
            # Add to the index metadata
            self.indexes[collection].append(field)
            self._save_indexes()
            
            # Build the index
            self._build_index(collection, field)
            
            return True
        except Exception as e:
            logger.error(f"Error creating index on {collection}.{field}: {e}")
            return False
    
    def _build_index(self, collection: str, field: str):
        """
        Build an index for a field in a collection.
        
        Args:
            collection: The collection to build the index for
            field: The field to index
        """
        # Get the collection directory
        collection_dir = self.storage_dir / collection
        if not collection_dir.exists():
            return
        
        # Create the index directory
        index_dir = self.indexes_dir / collection / field
        index_dir.mkdir(exist_ok=True, parents=True)
        
        # Clear existing index
        for file in index_dir.glob("*"):
            file.unlink()
        
        # Build the index
        index_data = {}
        
        for file in collection_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                
                # Extract the field value using dot notation
                field_parts = field.split(".")
                value = data
                for part in field_parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                
                if value is not None:
                    # Convert value to string for indexing
                    if isinstance(value, (list, dict)):
                        value_str = json.dumps(value)
                    else:
                        value_str = str(value)
                    
                    # Add to index
                    if value_str not in index_data:
                        index_data[value_str] = []
                    
                    index_data[value_str].append(file.stem)
            except Exception as e:
                logger.error(f"Error indexing {file}: {e}")
        
        # Save the index
        for value, ids in index_data.items():
            # Use a hash of the value as the filename to avoid invalid characters
            import hashlib
            value_hash = hashlib.md5(value.encode()).hexdigest()
            
            with open(index_dir / f"{value_hash}.json", "w") as f:
                json.dump(ids, f)
    
    def drop_index(self, collection: str, field: str) -> bool:
        """
        Drop an index on a field in a collection.
        
        Args:
            collection: The collection containing the index
            field: The indexed field
            
        Returns:
            True if the index was dropped successfully, False otherwise
        """
        if collection not in self.indexes or field not in self.indexes[collection]:
            logger.warning(f"Index does not exist on {collection}.{field}")
            return False
        
        try:
            # Remove the index directory
            index_dir = self.indexes_dir / collection / field
            if index_dir.exists():
                shutil.rmtree(index_dir)
            
            # Remove from the index metadata
            self.indexes[collection].remove(field)
            self._save_indexes()
            
            return True
        except Exception as e:
            logger.error(f"Error dropping index on {collection}.{field}: {e}")
            return False
    
    def list_indexes(self, collection: str) -> List[str]:
        """
        List all indexes on a collection.
        
        Args:
            collection: The collection to list indexes for
            
        Returns:
            List of indexed fields
        """
        if collection not in self.indexes:
            return []
        
        return self.indexes[collection]
    
    def query_index(self, collection: str, field: str, value: Any) -> List[str]:
        """
        Query an index for a value.
        
        Args:
            collection: The collection to query
            field: The indexed field
            value: The value to query for
            
        Returns:
            List of IDs matching the query
        """
        if collection not in self.indexes or field not in self.indexes[collection]:
            logger.warning(f"Index does not exist on {collection}.{field}")
            return []
        
        try:
            # Convert value to string for indexing
            if isinstance(value, (list, dict)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            # Use a hash of the value as the filename
            import hashlib
            value_hash = hashlib.md5(value_str.encode()).hexdigest()
            
            # Check if the index file exists
            index_file = self.indexes_dir / collection / field / f"{value_hash}.json"
            if not index_file.exists():
                return []
            
            # Load the index file
            with open(index_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error querying index on {collection}.{field}: {e}")
            return []


class LocalStorageAdapter(IStorageAdapter):
    """Implementation of the storage adapter interface using local filesystem."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the local storage adapter.
        
        Args:
            storage_dir: Directory where data is stored (default: from config)
        """
        config = get_config()
        
        if storage_dir is None:
            # Use the storage directory from config, or default to user home
            storage_path = config.get("storage.local_storage_path", "~/.scientific_voyager/storage")
            storage_dir = Path(os.path.expanduser(storage_path))
        
        self.storage_dir = storage_dir
        self.statements_dir = storage_dir / "statements"
        self.classifications_dir = storage_dir / "classifications"
        self.entities_dir = storage_dir / "entities"
        self.relations_dir = storage_dir / "relations"
        
        # Create directories if they don't exist
        for directory in [self.storage_dir, self.statements_dir, self.classifications_dir, 
                         self.entities_dir, self.relations_dir]:
            directory.mkdir(exist_ok=True, parents=True)
        
        # Initialize the UID generator and index manager
        self.uid_generator = UIDGenerator()
        self.index_manager = LocalIndexManager(storage_dir)
        
        # Create default indexes
        self._create_default_indexes()
        
        logger.info(f"Initialized local storage adapter at {storage_dir}")
    
    def _create_default_indexes(self):
        """Create default indexes for better query performance."""
        # Statement indexes
        self.index_manager.create_index("statements", "statement.type")
        self.index_manager.create_index("statements", "tags")
        self.index_manager.create_index("statements", "source_id")
        
        # Classification indexes
        self.index_manager.create_index("classifications", "classification.biological_scale")
        self.index_manager.create_index("classifications", "classification.statement_type")
        self.index_manager.create_index("classifications", "statement_id")
        
        # Entity indexes
        self.index_manager.create_index("entities", "entity.type")
        self.index_manager.create_index("entities", "entity.normalized_id")
        
        # Relation indexes
        self.index_manager.create_index("relations", "relation.relation_type")
        self.index_manager.create_index("relations", "source_entity_id")
        self.index_manager.create_index("relations", "target_entity_id")
    
    def save_statement(self, statement: StatementDTO) -> UUID:
        """
        Save a statement to storage.
        
        Args:
            statement: The statement to save
            
        Returns:
            The UUID of the saved statement
        """
        # Create a stored statement DTO
        uid = self.uid_generator.generate_uid()
        stored_statement = StoredStatementDTO(
            uid=uid,
            statement=statement,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        # Save to disk
        file_path = self.statements_dir / f"{uid}.json"
        with open(file_path, "w") as f:
            json.dump(stored_statement.to_dict(), f, indent=2)
        
        logger.debug(f"Saved statement with ID {uid}")
        return uid
    
    def get_statement(self, statement_id: Union[str, UUID]) -> Optional[StatementDTO]:
        """
        Retrieve a statement by ID.
        
        Args:
            statement_id: The ID of the statement to retrieve
            
        Returns:
            The statement if found, None otherwise
        """
        # Convert string ID to UUID if necessary
        if isinstance(statement_id, str):
            try:
                statement_id = UUID(statement_id)
            except ValueError:
                logger.error(f"Invalid statement ID: {statement_id}")
                return None
        
        # Check if the file exists
        file_path = self.statements_dir / f"{statement_id}.json"
        if not file_path.exists():
            logger.warning(f"Statement not found: {statement_id}")
            return None
        
        # Load from disk
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            stored_statement = StoredStatementDTO.from_dict(data)
            return stored_statement.statement
        except Exception as e:
            logger.error(f"Error loading statement {statement_id}: {e}")
            return None
    
    def save_classification(self, classification: ClassificationResultDTO) -> UUID:
        """
        Save a classification result to storage.
        
        Args:
            classification: The classification result to save
            
        Returns:
            The UUID of the saved classification
        """
        # Create a stored classification DTO
        uid = self.uid_generator.generate_uid()
        
        # Get the statement ID from the classification
        statement_id = classification.statement_id
        if isinstance(statement_id, str):
            try:
                statement_id = UUID(statement_id)
            except ValueError:
                logger.error(f"Invalid statement ID in classification: {statement_id}")
                return uid
        
        stored_classification = StoredClassificationDTO(
            uid=uid,
            classification=classification,
            statement_id=statement_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        # Save to disk
        file_path = self.classifications_dir / f"{uid}.json"
        with open(file_path, "w") as f:
            json.dump(stored_classification.to_dict(), f, indent=2)
        
        # Update the statement's classification IDs
        self._add_classification_to_statement(statement_id, uid)
        
        logger.debug(f"Saved classification with ID {uid}")
        return uid
    
    def _add_classification_to_statement(self, statement_id: UUID, classification_id: UUID):
        """Add a classification ID to a statement's classification_ids list."""
        # Check if the statement exists
        file_path = self.statements_dir / f"{statement_id}.json"
        if not file_path.exists():
            logger.warning(f"Statement not found: {statement_id}")
            return
        
        # Load the statement
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Add the classification ID if not already present
            if str(classification_id) not in data.get("classification_ids", []):
                if "classification_ids" not in data:
                    data["classification_ids"] = []
                data["classification_ids"].append(str(classification_id))
                data["updated_at"] = datetime.now().isoformat()
                
                # Save the updated statement
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error updating statement {statement_id} with classification {classification_id}: {e}")
    
    def get_classification(self, classification_id: Union[str, UUID]) -> Optional[ClassificationResultDTO]:
        """
        Retrieve a classification result by ID.
        
        Args:
            classification_id: The ID of the classification to retrieve
            
        Returns:
            The classification result if found, None otherwise
        """
        # Convert string ID to UUID if necessary
        if isinstance(classification_id, str):
            try:
                classification_id = UUID(classification_id)
            except ValueError:
                logger.error(f"Invalid classification ID: {classification_id}")
                return None
        
        # Check if the file exists
        file_path = self.classifications_dir / f"{classification_id}.json"
        if not file_path.exists():
            logger.warning(f"Classification not found: {classification_id}")
            return None
        
        # Load from disk
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            stored_classification = StoredClassificationDTO.from_dict(data)
            return stored_classification.classification
        except Exception as e:
            logger.error(f"Error loading classification {classification_id}: {e}")
            return None
    
    def get_classifications_for_statement(self, statement_id: Union[str, UUID]) -> List[ClassificationResultDTO]:
        """
        Retrieve all classification results for a statement.
        
        Args:
            statement_id: The ID of the statement
            
        Returns:
            List of classification results for the statement
        """
        # Convert string ID to UUID if necessary
        if isinstance(statement_id, str):
            try:
                statement_id = UUID(statement_id)
            except ValueError:
                logger.error(f"Invalid statement ID: {statement_id}")
                return []
        
        # Query the index for classifications with this statement ID
        classification_ids = self.index_manager.query_index("classifications", "statement_id", str(statement_id))
        
        # Load each classification
        classifications = []
        for cid in classification_ids:
            classification = self.get_classification(cid)
            if classification:
                classifications.append(classification)
        
        return classifications
    
    def save_entity(self, entity: EntityDTO) -> UUID:
        """
        Save an entity to storage.
        
        Args:
            entity: The entity to save
            
        Returns:
            The UUID of the saved entity
        """
        # Create a stored entity DTO
        uid = self.uid_generator.generate_uid()
        stored_entity = StoredEntityDTO(
            uid=uid,
            entity=entity,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        # Save to disk
        file_path = self.entities_dir / f"{uid}.json"
        with open(file_path, "w") as f:
            json.dump(stored_entity.to_dict(), f, indent=2)
        
        logger.debug(f"Saved entity with ID {uid}")
        return uid
    
    def get_entity(self, entity_id: Union[str, UUID]) -> Optional[EntityDTO]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            The entity if found, None otherwise
        """
        # Convert string ID to UUID if necessary
        if isinstance(entity_id, str):
            try:
                entity_id = UUID(entity_id)
            except ValueError:
                logger.error(f"Invalid entity ID: {entity_id}")
                return None
        
        # Check if the file exists
        file_path = self.entities_dir / f"{entity_id}.json"
        if not file_path.exists():
            logger.warning(f"Entity not found: {entity_id}")
            return None
        
        # Load from disk
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            stored_entity = StoredEntityDTO.from_dict(data)
            return stored_entity.entity
        except Exception as e:
            logger.error(f"Error loading entity {entity_id}: {e}")
            return None
    
    def save_relation(self, relation: RelationDTO) -> UUID:
        """
        Save a relation to storage.
        
        Args:
            relation: The relation to save
            
        Returns:
            The UUID of the saved relation
        """
        # Save the source and target entities if they don't exist yet
        source_entity_id = self._ensure_entity_saved(relation.source_entity)
        target_entity_id = self._ensure_entity_saved(relation.target_entity)
        
        # Create a stored relation DTO
        uid = self.uid_generator.generate_uid()
        stored_relation = StoredRelationDTO(
            uid=uid,
            relation=relation,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        # Save to disk
        file_path = self.relations_dir / f"{uid}.json"
        with open(file_path, "w") as f:
            json.dump(stored_relation.to_dict(), f, indent=2)
        
        logger.debug(f"Saved relation with ID {uid}")
        return uid
    
    def _ensure_entity_saved(self, entity: EntityDTO) -> UUID:
        """
        Ensure an entity is saved to storage.
        
        Args:
            entity: The entity to save
            
        Returns:
            The UUID of the saved entity
        """
        # Check if the entity already exists by normalized ID or text+type
        entity_id = None
        
        if entity.normalized_id:
            # Query the index for entities with this normalized ID
            entity_ids = self.index_manager.query_index("entities", "entity.normalized_id", entity.normalized_id)
            if entity_ids:
                entity_id = entity_ids[0]
        
        if not entity_id:
            # Save as a new entity
            entity_id = self.save_entity(entity)
        
        return UUID(entity_id) if isinstance(entity_id, str) else entity_id
    
    def get_relation(self, relation_id: Union[str, UUID]) -> Optional[RelationDTO]:
        """
        Retrieve a relation by ID.
        
        Args:
            relation_id: The ID of the relation to retrieve
            
        Returns:
            The relation if found, None otherwise
        """
        # Convert string ID to UUID if necessary
        if isinstance(relation_id, str):
            try:
                relation_id = UUID(relation_id)
            except ValueError:
                logger.error(f"Invalid relation ID: {relation_id}")
                return None
        
        # Check if the file exists
        file_path = self.relations_dir / f"{relation_id}.json"
        if not file_path.exists():
            logger.warning(f"Relation not found: {relation_id}")
            return None
        
        # Load from disk
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Load the source and target entities
            source_entity_id = data.get("source_entity_id")
            target_entity_id = data.get("target_entity_id")
            
            source_entity = self.get_entity(source_entity_id) if source_entity_id else None
            target_entity = self.get_entity(target_entity_id) if target_entity_id else None
            
            if not source_entity or not target_entity:
                logger.error(f"Missing entities for relation {relation_id}")
                return None
            
            # Create the relation DTO
            stored_relation = StoredRelationDTO.from_dict(data, source_entity, target_entity)
            return stored_relation.relation
        except Exception as e:
            logger.error(f"Error loading relation {relation_id}: {e}")
            return None
    
    def search_statements(self, query: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[StatementDTO]:
        """
        Search for statements matching the query.
        
        Args:
            query: The search query (field-value pairs)
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching statements
        """
        matching_ids = set()
        first_field = True
        
        # Process each query field
        for field, value in query.items():
            # Handle special fields
            if field == "text" and isinstance(value, str):
                # Text search (simple contains for now)
                field_matches = set()
                
                # Scan all statement files (inefficient but simple)
                for file in self.statements_dir.glob("*.json"):
                    try:
                        with open(file, "r") as f:
                            data = json.load(f)
                        
                        if "statement" in data and "text" in data["statement"] and value.lower() in data["statement"]["text"].lower():
                            field_matches.add(file.stem)
                    except Exception as e:
                        logger.error(f"Error searching statement {file.stem}: {e}")
                
                if first_field:
                    matching_ids = field_matches
                    first_field = False
                else:
                    matching_ids &= field_matches
            else:
                # Use the index for other fields
                indexed_field = field.replace(".", "_")
                field_matches = set(self.index_manager.query_index("statements", indexed_field, value))
                
                if first_field:
                    matching_ids = field_matches
                    first_field = False
                else:
                    matching_ids &= field_matches
            
            # Short-circuit if no matches
            if not matching_ids:
                return []
        
        # Apply offset and limit
        matching_ids = list(matching_ids)[offset:offset+limit]
        
        # Load the matching statements
        statements = []
        for statement_id in matching_ids:
            statement = self.get_statement(statement_id)
            if statement:
                statements.append(statement)
        
        return statements
    
    def search_classifications(self, query: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[ClassificationResultDTO]:
        """
        Search for classifications matching the query.
        
        Args:
            query: The search query (field-value pairs)
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching classifications
        """
        matching_ids = set()
        first_field = True
        
        # Process each query field
        for field, value in query.items():
            # Use the index for fields
            indexed_field = field.replace(".", "_")
            field_matches = set(self.index_manager.query_index("classifications", indexed_field, value))
            
            if first_field:
                matching_ids = field_matches
                first_field = False
            else:
                matching_ids &= field_matches
            
            # Short-circuit if no matches
            if not matching_ids:
                return []
        
        # Apply offset and limit
        matching_ids = list(matching_ids)[offset:offset+limit]
        
        # Load the matching classifications
        classifications = []
        for classification_id in matching_ids:
            classification = self.get_classification(classification_id)
            if classification:
                classifications.append(classification)
        
        return classifications
    
    def get_storage_stats(self) -> StorageStatsDTO:
        """
        Get statistics about the storage system.
        
        Returns:
            Storage statistics
        """
        stats = StorageStatsDTO()
        
        # Count statements
        stats.total_statements = len(list(self.statements_dir.glob("*.json")))
        
        # Count classifications
        stats.total_classifications = len(list(self.classifications_dir.glob("*.json")))
        
        # Count entities
        stats.total_entities = len(list(self.entities_dir.glob("*.json")))
        
        # Count relations
        stats.total_relations = len(list(self.relations_dir.glob("*.json")))
        
        # Collect statement types
        for file in self.statements_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                
                if "statement" in data and "type" in data["statement"]:
                    statement_type = data["statement"]["type"]
                    stats.statement_types[statement_type] = stats.statement_types.get(statement_type, 0) + 1
            except Exception as e:
                logger.error(f"Error processing statement {file.stem}: {e}")
        
        # Collect entity types
        for file in self.entities_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                
                if "entity" in data and "type" in data["entity"]:
                    entity_type = data["entity"]["type"]
                    stats.entity_types[entity_type] = stats.entity_types.get(entity_type, 0) + 1
            except Exception as e:
                logger.error(f"Error processing entity {file.stem}: {e}")
        
        # Collect relation types
        for file in self.relations_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                
                if "relation" in data and "relation_type" in data["relation"]:
                    relation_type = data["relation"]["relation_type"]
                    stats.relation_types[relation_type] = stats.relation_types.get(relation_type, 0) + 1
            except Exception as e:
                logger.error(f"Error processing relation {file.stem}: {e}")
        
        # Collect biological scales and classification types
        for file in self.classifications_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                
                if "classification" in data:
                    classification = data["classification"]
                    
                    if "biological_scale" in classification:
                        scale = classification["biological_scale"]
                        stats.biological_scales[scale] = stats.biological_scales.get(scale, 0) + 1
                    
                    if "statement_type" in classification:
                        classification_type = classification["statement_type"]
                        stats.classification_types[classification_type] = stats.classification_types.get(classification_type, 0) + 1
            except Exception as e:
                logger.error(f"Error processing classification {file.stem}: {e}")
        
        # Calculate storage size
        stats.storage_size_bytes = self._calculate_directory_size(self.storage_dir)
        stats.index_size_bytes = self._calculate_directory_size(self.indexes_dir)
        
        stats.last_updated = datetime.now()
        return stats
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate the total size of a directory in bytes."""
        total_size = 0
        for path in directory.glob('**/*'):
            if path.is_file():
                total_size += path.stat().st_size
        return total_size

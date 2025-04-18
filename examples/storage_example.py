"""
Storage System Example

This script demonstrates the use of the local storage system for storing
and retrieving statements, classifications, entities, and relations.
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

from scientific_voyager.interfaces.extraction_dto import StatementDTO, EntityDTO, RelationDTO
from scientific_voyager.interfaces.classification_dto import ClassificationResultDTO
from scientific_voyager.interfaces.classification_interface import BiologicalScale, StatementType
from scientific_voyager.storage.local_storage import LocalStorageAdapter


def create_example_data():
    """Create example data for demonstration."""
    # Create example statements
    statements = [
        StatementDTO(
            text="The BRCA1 gene mutation increases the risk of breast and ovarian cancer.",
            type="scientific_statement",
            confidence=0.95,
            metadata={"source": "example", "id": str(uuid.uuid4())}
        ),
        StatementDTO(
            text="Insulin binds to its receptor, triggering a signaling cascade that promotes glucose uptake.",
            type="scientific_statement",
            confidence=0.90,
            metadata={"source": "example", "id": str(uuid.uuid4())}
        ),
        StatementDTO(
            text="Mitochondria produce ATP through oxidative phosphorylation.",
            type="scientific_statement",
            confidence=0.98,
            metadata={"source": "example", "id": str(uuid.uuid4())}
        ),
        StatementDTO(
            text="The immune system recognizes and eliminates pathogens through a complex network of cells and molecules.",
            type="scientific_statement",
            confidence=0.92,
            metadata={"source": "example", "id": str(uuid.uuid4())}
        ),
        StatementDTO(
            text="Coral reef biodiversity is declining due to ocean acidification.",
            type="scientific_statement",
            confidence=0.85,
            metadata={"source": "example", "id": str(uuid.uuid4())}
        )
    ]
    
    # Create example classifications
    classifications = [
        ClassificationResultDTO(
            statement_id=statements[0].metadata.get("id"),
            statement_text=statements[0].text,
            biological_scale=BiologicalScale.GENETIC.value,
            scale_confidence=0.95,
            statement_type=StatementType.CAUSAL.value,
            type_confidence=0.90,
            classification_time=datetime.now(),
            metadata={"scale_reasoning": "The statement focuses on a gene mutation.", 
                      "type_reasoning": "The statement indicates a causal relationship."}
        ),
        ClassificationResultDTO(
            statement_id=statements[1].metadata.get("id"),
            statement_text=statements[1].text,
            biological_scale=BiologicalScale.CELLULAR.value,
            scale_confidence=0.90,
            statement_type=StatementType.CAUSAL.value,
            type_confidence=0.90,
            classification_time=datetime.now(),
            metadata={"scale_reasoning": "The statement describes a cellular process.", 
                      "type_reasoning": "The statement indicates a causal relationship."}
        ),
        ClassificationResultDTO(
            statement_id=statements[2].metadata.get("id"),
            statement_text=statements[2].text,
            biological_scale=BiologicalScale.CELLULAR.value,
            scale_confidence=0.90,
            statement_type=StatementType.DESCRIPTIVE.value,
            type_confidence=0.95,
            classification_time=datetime.now(),
            metadata={"scale_reasoning": "The statement describes a cellular process.", 
                      "type_reasoning": "The statement is descriptive in nature."}
        ),
        ClassificationResultDTO(
            statement_id=statements[3].metadata.get("id"),
            statement_text=statements[3].text,
            biological_scale=BiologicalScale.SYSTEM.value,
            scale_confidence=0.90,
            statement_type=StatementType.DESCRIPTIVE.value,
            type_confidence=0.85,
            classification_time=datetime.now(),
            metadata={"scale_reasoning": "The statement describes a biological system.", 
                      "type_reasoning": "The statement is descriptive in nature."}
        ),
        ClassificationResultDTO(
            statement_id=statements[4].metadata.get("id"),
            statement_text=statements[4].text,
            biological_scale=BiologicalScale.ECOSYSTEM.value,
            scale_confidence=0.95,
            statement_type=StatementType.CAUSAL.value,
            type_confidence=0.90,
            classification_time=datetime.now(),
            metadata={"scale_reasoning": "The statement describes an ecosystem-level process.", 
                      "type_reasoning": "The statement indicates a causal relationship."}
        )
    ]
    
    # Create example entities
    entities = [
        EntityDTO(
            text="BRCA1",
            type="gene",
            start_char=4,
            end_char=9,
            confidence=0.95,
            normalized_id="HGNC:1100",
            normalized_name="BRCA1",
            ontology_references={"HGNC": "1100", "NCBI": "672"}
        ),
        EntityDTO(
            text="breast cancer",
            type="disease",
            start_char=45,
            end_char=58,
            confidence=0.95,
            normalized_id="MESH:D001943",
            normalized_name="Breast Neoplasms",
            ontology_references={"MESH": "D001943", "OMIM": "114480"}
        ),
        EntityDTO(
            text="ovarian cancer",
            type="disease",
            start_char=63,
            end_char=77,
            confidence=0.95,
            normalized_id="MESH:D010051",
            normalized_name="Ovarian Neoplasms",
            ontology_references={"MESH": "D010051", "OMIM": "167000"}
        ),
        EntityDTO(
            text="insulin",
            type="protein",
            start_char=0,
            end_char=7,
            confidence=0.95,
            normalized_id="UNIPROT:P01308",
            normalized_name="Insulin",
            ontology_references={"UNIPROT": "P01308", "MESH": "D007328"}
        ),
        EntityDTO(
            text="insulin receptor",
            type="protein",
            start_char=18,
            end_char=34,
            confidence=0.95,
            normalized_id="UNIPROT:P06213",
            normalized_name="Insulin receptor",
            ontology_references={"UNIPROT": "P06213", "MESH": "D007334"}
        )
    ]
    
    # Create example relations
    relations = [
        RelationDTO(
            source_entity=entities[0],
            target_entity=entities[1],
            relation_type="increases_risk_of",
            confidence=0.90,
            bidirectional=False,
            normalized_relation_type="causally_related_to"
        ),
        RelationDTO(
            source_entity=entities[0],
            target_entity=entities[2],
            relation_type="increases_risk_of",
            confidence=0.90,
            bidirectional=False,
            normalized_relation_type="causally_related_to"
        ),
        RelationDTO(
            source_entity=entities[3],
            target_entity=entities[4],
            relation_type="binds_to",
            confidence=0.95,
            bidirectional=False,
            normalized_relation_type="physically_interacts_with"
        )
    ]
    
    return statements, classifications, entities, relations


def demo_storage_system():
    """Demonstrate the local storage system."""
    print("\n" + "="*80)
    print("Storage System Demonstration")
    print("="*80)
    
    # Initialize the storage adapter
    storage = LocalStorageAdapter()
    print(f"Initialized storage at: {storage.storage_dir}")
    
    # Create example data
    statements, classifications, entities, relations = create_example_data()
    
    # Store statements
    print("\n1. Storing statements...")
    statement_ids = []
    for statement in statements:
        statement_id = storage.save_statement(statement)
        statement_ids.append(statement_id)
        print(f"  Saved statement: {statement.text[:50]}... (ID: {statement_id})")
    
    # Store classifications
    print("\n2. Storing classifications...")
    classification_ids = []
    for classification in classifications:
        classification_id = storage.save_classification(classification)
        classification_ids.append(classification_id)
        print(f"  Saved classification: {classification.biological_scale} / {classification.statement_type} (ID: {classification_id})")
    
    # Store entities
    print("\n3. Storing entities...")
    entity_ids = []
    for entity in entities:
        entity_id = storage.save_entity(entity)
        entity_ids.append(entity_id)
        print(f"  Saved entity: {entity.text} ({entity.type}) (ID: {entity_id})")
    
    # Store relations
    print("\n4. Storing relations...")
    relation_ids = []
    for relation in relations:
        relation_id = storage.save_relation(relation)
        relation_ids.append(relation_id)
        print(f"  Saved relation: {relation.source_entity.text} {relation.relation_type} {relation.target_entity.text} (ID: {relation_id})")
    
    # Retrieve statements
    print("\n5. Retrieving statements...")
    for statement_id in statement_ids[:2]:  # Just show a couple for brevity
        statement = storage.get_statement(statement_id)
        print(f"  Retrieved statement: {statement.text[:50]}... (ID: {statement_id})")
    
    # Retrieve classifications for a statement
    print("\n6. Retrieving classifications for a statement...")
    statement_id = statement_ids[0]
    classifications = storage.get_classifications_for_statement(statement_id)
    for classification in classifications:
        print(f"  Retrieved classification: {classification.biological_scale} / {classification.statement_type}")
    
    # Search for statements
    print("\n7. Searching for statements...")
    search_results = storage.search_statements({"statement.type": "scientific_statement"}, limit=3)
    print(f"  Found {len(search_results)} statements of type 'scientific_statement'")
    for statement in search_results:
        print(f"  - {statement.text[:50]}...")
    
    # Search for classifications
    print("\n8. Searching for classifications...")
    search_results = storage.search_classifications({"classification.biological_scale": BiologicalScale.CELLULAR.value})
    print(f"  Found {len(search_results)} classifications at the {BiologicalScale.CELLULAR.value} scale")
    
    # Get storage statistics
    print("\n9. Storage statistics...")
    stats = storage.get_storage_stats()
    print(f"  Total statements: {stats.total_statements}")
    print(f"  Total classifications: {stats.total_classifications}")
    print(f"  Total entities: {stats.total_entities}")
    print(f"  Total relations: {stats.total_relations}")
    print(f"  Storage size: {stats.storage_size_bytes / 1024:.2f} KB")
    
    print("\nStorage demonstration completed successfully!")


if __name__ == "__main__":
    demo_storage_system()

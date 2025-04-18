"""
Base implementation of the abstract extraction pipeline.

This module provides the base implementation for extracting structured information
from scientific article abstracts using NLP techniques.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import re

from scientific_voyager.interfaces.extraction_interface import IExtractor, INormalizer, IExtractionPipeline
from scientific_voyager.interfaces.extraction_dto import (
    EntityDTO, RelationDTO, StatementDTO, ExtractionResultDTO,
    BiologicalEntityDTO, MolecularEntityDTO, GeneDTO, ProteinDTO
)

logger = logging.getLogger(__name__)


class BaseExtractor(IExtractor):
    """
    Base implementation of the extractor interface.
    
    This class provides basic extraction functionality using regular expressions
    and pattern matching. It should be extended by more sophisticated implementations
    using NLP models.
    """
    
    def __init__(self):
        """Initialize the base extractor."""
        # Compile regex patterns for basic entity recognition
        self.gene_pattern = re.compile(r'\b[A-Z][A-Z0-9]+\b')  # Simple gene symbol pattern
        self.protein_pattern = re.compile(r'\b[A-Z][a-z]*[0-9]*\b')  # Simple protein name pattern
        self.disease_pattern = re.compile(r'\b(?:cancer|disease|syndrome|disorder)\b', re.IGNORECASE)
        
        # Relation patterns
        self.relation_patterns = [
            (r'(\w+)\s+(?:activates|induces|upregulates|increases|enhances)\s+(\w+)', 'activates'),
            (r'(\w+)\s+(?:inhibits|suppresses|downregulates|decreases|reduces)\s+(\w+)', 'inhibits'),
            (r'(\w+)\s+(?:binds to|interacts with)\s+(\w+)', 'binds_to'),
            (r'(\w+)\s+(?:is associated with|correlates with)\s+(\w+)', 'associated_with'),
            (r'(\w+)\s+(?:causes|leads to|results in)\s+(\w+)', 'causes'),
        ]
        self.relation_patterns = [(re.compile(pattern, re.IGNORECASE), rel_type) 
                                 for pattern, rel_type in self.relation_patterns]
        
        # Statement patterns
        self.statement_patterns = [
            (r'(?:we|our results|this study)\s+(?:show|demonstrate|reveal|indicate|suggest)s?\s+that\s+(.+?)(?:\.|\n)', 'finding'),
            (r'(?:we|our)\s+(?:conclude|hypothesis|propose)\s+that\s+(.+?)(?:\.|\n)', 'conclusion'),
            (r'(?:background|introduction)(?::|.)\s+(.+?)(?:\.|\n)', 'background'),
            (r'(?:methods|materials and methods)(?::|.)\s+(.+?)(?:\.|\n)', 'method'),
            (r'(?:results)(?::|.)\s+(.+?)(?:\.|\n)', 'result'),
            (r'(?:conclusion|conclusions|summary)(?::|.)\s+(.+?)(?:\.|\n)', 'conclusion'),
        ]
        self.statement_patterns = [(re.compile(pattern, re.IGNORECASE), stmt_type) 
                                  for pattern, stmt_type in self.statement_patterns]
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract entities from the given text using regex patterns.
        
        Args:
            text: The text to extract entities from
            
        Returns:
            A dictionary mapping entity types to lists of extracted entities
        """
        entities = {
            'gene': [],
            'protein': [],
            'disease': [],
        }
        
        # Extract genes
        for match in self.gene_pattern.finditer(text):
            start, end = match.span()
            gene_text = match.group()
            # Skip if it's likely not a gene (too short or common word)
            if len(gene_text) < 2 or gene_text.lower() in ['the', 'and', 'for', 'was', 'were']:
                continue
            entities['gene'].append({
                'text': gene_text,
                'type': 'gene',
                'start_char': start,
                'end_char': end,
                'confidence': 0.7,  # Default confidence for regex-based extraction
            })
        
        # Extract proteins
        for match in self.protein_pattern.finditer(text):
            start, end = match.span()
            protein_text = match.group()
            # Skip if it's likely not a protein (common word)
            if protein_text.lower() in ['the', 'and', 'for', 'was', 'were', 'this', 'that']:
                continue
            entities['protein'].append({
                'text': protein_text,
                'type': 'protein',
                'start_char': start,
                'end_char': end,
                'confidence': 0.6,  # Default confidence for regex-based extraction
            })
        
        # Extract diseases
        for match in self.disease_pattern.finditer(text):
            start, end = match.span()
            disease_text = match.group()
            entities['disease'].append({
                'text': disease_text,
                'type': 'disease',
                'start_char': start,
                'end_char': end,
                'confidence': 0.8,  # Default confidence for regex-based extraction
            })
        
        return entities
    
    def extract_relations(self, text: str, entities: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> List[Dict[str, Any]]:
        """
        Extract relations between entities from the given text.
        
        Args:
            text: The text to extract relations from
            entities: Optional pre-extracted entities
            
        Returns:
            A list of extracted relations
        """
        if entities is None:
            entities = self.extract_entities(text)
        
        # Flatten entities for easier lookup
        flat_entities = []
        for entity_type, entity_list in entities.items():
            flat_entities.extend(entity_list)
        
        relations = []
        
        # Extract relations using patterns
        for pattern, relation_type in self.relation_patterns:
            for match in pattern.finditer(text):
                source_text, target_text = match.groups()
                
                # Find the closest matching entities
                source_entity = self._find_closest_entity(source_text, flat_entities)
                target_entity = self._find_closest_entity(target_text, flat_entities)
                
                if source_entity and target_entity:
                    relations.append({
                        'source': source_entity,
                        'target': target_entity,
                        'relation_type': relation_type,
                        'confidence': 0.6,  # Default confidence for pattern-based extraction
                        'text': match.group(0),
                    })
        
        return relations
    
    def extract_statements(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract scientific statements from the given text.
        
        Args:
            text: The text to extract statements from
            
        Returns:
            A list of extracted statements
        """
        statements = []
        
        # Extract statements using patterns
        for pattern, statement_type in self.statement_patterns:
            for match in pattern.finditer(text):
                statement_text = match.group(1)
                statements.append({
                    'text': statement_text,
                    'type': statement_type,
                    'confidence': 0.7,  # Default confidence for pattern-based extraction
                    'source_text': match.group(0),
                })
        
        return statements
    
    def _find_closest_entity(self, text: str, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the entity that most closely matches the given text.
        
        Args:
            text: The text to match
            entities: List of entities to search
            
        Returns:
            The closest matching entity or None if no match is found
        """
        # Simple exact match first
        for entity in entities:
            if entity['text'].lower() == text.lower():
                return entity
        
        # Try substring match
        for entity in entities:
            if text.lower() in entity['text'].lower() or entity['text'].lower() in text.lower():
                return entity
        
        return None


class BaseNormalizer(INormalizer):
    """
    Base implementation of the normalizer interface.
    
    This class provides basic normalization functionality. It should be extended
    by more sophisticated implementations using ontology mapping.
    """
    
    def __init__(self):
        """Initialize the base normalizer."""
        # Simple dictionaries for entity normalization
        self.gene_dict = {
            'pten': {'id': 'HGNC:9588', 'name': 'PTEN'},
            'tp53': {'id': 'HGNC:11998', 'name': 'TP53'},
            'brca1': {'id': 'HGNC:1100', 'name': 'BRCA1'},
            'brca2': {'id': 'HGNC:1101', 'name': 'BRCA2'},
            'egfr': {'id': 'HGNC:3236', 'name': 'EGFR'},
        }
        
        self.protein_dict = {
            'p53': {'id': 'UniProt:P04637', 'name': 'Cellular tumor antigen p53'},
            'pten': {'id': 'UniProt:P60484', 'name': 'Phosphatidylinositol 3,4,5-trisphosphate 3-phosphatase and dual-specificity protein phosphatase PTEN'},
            'egfr': {'id': 'UniProt:P00533', 'name': 'Epidermal growth factor receptor'},
        }
        
        self.disease_dict = {
            'cancer': {'id': 'DOID:162', 'name': 'Cancer'},
            'breast cancer': {'id': 'DOID:1612', 'name': 'Breast cancer'},
            'lung cancer': {'id': 'DOID:1324', 'name': 'Lung cancer'},
            'diabetes': {'id': 'DOID:9351', 'name': 'Diabetes mellitus'},
        }
        
        # Relation normalization dictionary
        self.relation_dict = {
            'activates': 'RO:0002406',
            'inhibits': 'RO:0002408',
            'binds_to': 'RO:0002436',
            'associated_with': 'RO:0002451',
            'causes': 'RO:0002410',
        }
    
    def normalize_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize an entity by linking it to standard ontologies.
        
        Args:
            entity: The entity to normalize
            
        Returns:
            The normalized entity
        """
        entity_text = entity['text'].lower()
        entity_type = entity['type']
        
        normalized = entity.copy()
        
        if entity_type == 'gene':
            if entity_text in self.gene_dict:
                normalized['normalized_id'] = self.gene_dict[entity_text]['id']
                normalized['normalized_name'] = self.gene_dict[entity_text]['name']
                normalized['ontology_references'] = {'HGNC': normalized['normalized_id']}
        
        elif entity_type == 'protein':
            if entity_text in self.protein_dict:
                normalized['normalized_id'] = self.protein_dict[entity_text]['id']
                normalized['normalized_name'] = self.protein_dict[entity_text]['name']
                normalized['ontology_references'] = {'UniProt': normalized['normalized_id']}
        
        elif entity_type == 'disease':
            if entity_text in self.disease_dict:
                normalized['normalized_id'] = self.disease_dict[entity_text]['id']
                normalized['normalized_name'] = self.disease_dict[entity_text]['name']
                normalized['ontology_references'] = {'DOID': normalized['normalized_id']}
        
        return normalized
    
    def normalize_relation(self, relation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a relation by standardizing its type.
        
        Args:
            relation: The relation to normalize
            
        Returns:
            The normalized relation
        """
        normalized = relation.copy()
        
        relation_type = relation['relation_type']
        if relation_type in self.relation_dict:
            normalized['normalized_relation_type'] = self.relation_dict[relation_type]
        
        return normalized


class BaseExtractionPipeline(IExtractionPipeline):
    """
    Base implementation of the extraction pipeline interface.
    
    This class provides a complete pipeline for extracting and normalizing
    information from scientific abstracts.
    """
    
    def __init__(self, extractor: Optional[IExtractor] = None, normalizer: Optional[INormalizer] = None):
        """
        Initialize the extraction pipeline.
        
        Args:
            extractor: The extractor to use. If None, a BaseExtractor will be created.
            normalizer: The normalizer to use. If None, a BaseNormalizer will be created.
        """
        self.extractor = extractor or BaseExtractor()
        self.normalizer = normalizer or BaseNormalizer()
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process the given text through the complete extraction and normalization pipeline.
        
        Args:
            text: The text to process
            
        Returns:
            A dictionary containing all extracted and normalized information
        """
        try:
            # Extract entities
            entities_dict = self.extractor.extract_entities(text)
            
            # Extract relations
            relations = self.extractor.extract_relations(text, entities_dict)
            
            # Extract statements
            statements = self.extractor.extract_statements(text)
            
            # Normalize entities
            normalized_entities = []
            for entity_type, entity_list in entities_dict.items():
                for entity in entity_list:
                    normalized_entity = self.normalizer.normalize_entity(entity)
                    normalized_entities.append(self._convert_to_entity_dto(normalized_entity))
            
            # Normalize relations
            normalized_relations = []
            for relation in relations:
                normalized_relation = self.normalizer.normalize_relation(relation)
                # Find the corresponding EntityDTO objects
                source_entity = self._find_entity_dto(normalized_entities, relation['source'])
                target_entity = self._find_entity_dto(normalized_entities, relation['target'])
                if source_entity and target_entity:
                    normalized_relations.append(self._convert_to_relation_dto(normalized_relation, source_entity, target_entity))
            
            # Convert statements to DTOs
            statement_dtos = []
            for statement in statements:
                statement_dto = StatementDTO(
                    text=statement['text'],
                    type=statement['type'],
                    confidence=statement['confidence'],
                    source_text=statement.get('source_text'),
                    metadata={}
                )
                statement_dtos.append(statement_dto)
            
            # Create the result DTO
            result = ExtractionResultDTO(
                source_text=text,
                entities=normalized_entities,
                relations=normalized_relations,
                statements=statement_dtos,
                metadata={'extraction_method': 'base_extractor'}
            )
            
            return result.__dict__
        
        except Exception as e:
            logger.error(f"Error in extraction pipeline: {str(e)}")
            # Return a minimal result in case of error
            return ExtractionResultDTO(
                source_text=text,
                metadata={'error': str(e), 'extraction_method': 'base_extractor'}
            ).__dict__
    
    def batch_process(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple texts through the complete extraction and normalization pipeline.
        
        Args:
            texts: A list of texts to process
            
        Returns:
            A list of dictionaries containing all extracted and normalized information for each text
        """
        results = []
        for text in texts:
            results.append(self.process(text))
        return results
    
    def _convert_to_entity_dto(self, entity: Dict[str, Any]) -> EntityDTO:
        """Convert a dictionary entity to an EntityDTO object."""
        if entity['type'] == 'gene':
            return GeneDTO(
                text=entity['text'],
                type=entity['type'],
                start_char=entity['start_char'],
                end_char=entity['end_char'],
                confidence=entity['confidence'],
                metadata=entity.get('metadata', {}),
                normalized_id=entity.get('normalized_id'),
                normalized_name=entity.get('normalized_name'),
                ontology_references=entity.get('ontology_references', {}),
                molecular_type='gene',
                gene_id=entity.get('normalized_id'),
                gene_symbol=entity.get('normalized_name')
            )
        elif entity['type'] == 'protein':
            return ProteinDTO(
                text=entity['text'],
                type=entity['type'],
                start_char=entity['start_char'],
                end_char=entity['end_char'],
                confidence=entity['confidence'],
                metadata=entity.get('metadata', {}),
                normalized_id=entity.get('normalized_id'),
                normalized_name=entity.get('normalized_name'),
                ontology_references=entity.get('ontology_references', {}),
                molecular_type='protein',
                protein_id=entity.get('normalized_id'),
                protein_name=entity.get('normalized_name')
            )
        else:
            return BiologicalEntityDTO(
                text=entity['text'],
                type=entity['type'],
                start_char=entity['start_char'],
                end_char=entity['end_char'],
                confidence=entity['confidence'],
                metadata=entity.get('metadata', {}),
                normalized_id=entity.get('normalized_id'),
                normalized_name=entity.get('normalized_name'),
                ontology_references=entity.get('ontology_references', {})
            )
    
    def _convert_to_relation_dto(self, relation: Dict[str, Any], source_entity: EntityDTO, target_entity: EntityDTO) -> RelationDTO:
        """Convert a dictionary relation to a RelationDTO object."""
        return RelationDTO(
            source_entity=source_entity,
            target_entity=target_entity,
            relation_type=relation['relation_type'],
            confidence=relation['confidence'],
            metadata=relation.get('metadata', {}),
            normalized_relation_type=relation.get('normalized_relation_type')
        )
    
    def _find_entity_dto(self, entities: List[EntityDTO], entity_dict: Dict[str, Any]) -> Optional[EntityDTO]:
        """Find the EntityDTO that corresponds to the given entity dictionary."""
        for entity in entities:
            if (entity.text == entity_dict['text'] and 
                entity.start_char == entity_dict['start_char'] and
                entity.end_char == entity_dict['end_char']):
                return entity
        return None

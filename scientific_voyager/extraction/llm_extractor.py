"""
LLM-based implementation of the abstract extraction pipeline.

This module provides an implementation of the extraction pipeline that uses
language models to extract structured information from scientific abstracts.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import re

from scientific_voyager.interfaces.extraction_interface import IExtractor, INormalizer
from scientific_voyager.extraction.base_extractor import BaseExtractor, BaseNormalizer, BaseExtractionPipeline
from scientific_voyager.interfaces.extraction_dto import (
    EntityDTO, RelationDTO, StatementDTO, ExtractionResultDTO
)
from scientific_voyager.config.config_manager import get_config

logger = logging.getLogger(__name__)


class LLMExtractor(BaseExtractor):
    """
    LLM-based implementation of the extractor interface.
    
    This class uses language models to extract entities, relations, and statements
    from scientific abstracts with higher accuracy than pattern-based methods.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the LLM extractor.
        
        Args:
            model_name: The name of the language model to use. If None, the default model
                       from the configuration will be used.
        """
        super().__init__()
        self.config = get_config()
        self.model_name = model_name or self.config.get("llm.default_model", "gpt-3.5-turbo")
        self.api_key = self.config.get_config_dto().api_keys.get("openai")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found in configuration. LLM extraction will not work.")
        
        self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize the LLM client based on the configuration."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"Initialized OpenAI client with model {self.model_name}")
        except ImportError:
            logger.error("OpenAI package not installed. Please install it with 'pip install openai'.")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract entities from the given text using a language model.
        
        Args:
            text: The text to extract entities from
            
        Returns:
            A dictionary mapping entity types to lists of extracted entities
        """
        if not self.client:
            logger.warning("LLM client not initialized. Falling back to base extractor.")
            return super().extract_entities(text)
        
        try:
            # First try with the LLM
            prompt = self._create_entity_extraction_prompt(text)
            response = self._call_llm(prompt)
            entities = self._parse_entity_response(response, text)
            
            # If LLM extraction failed or returned empty results, fall back to base extractor
            if not entities:
                logger.warning("LLM entity extraction failed or returned empty results. Falling back to base extractor.")
                entities = super().extract_entities(text)
            
            return entities
        
        except Exception as e:
            logger.error(f"Error in LLM entity extraction: {str(e)}")
            return super().extract_entities(text)
    
    def extract_relations(self, text: str, entities: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> List[Dict[str, Any]]:
        """
        Extract relations between entities from the given text using a language model.
        
        Args:
            text: The text to extract relations from
            entities: Optional pre-extracted entities
            
        Returns:
            A list of extracted relations
        """
        if not self.client:
            logger.warning("LLM client not initialized. Falling back to base extractor.")
            return super().extract_relations(text, entities)
        
        if entities is None:
            entities = self.extract_entities(text)
        
        try:
            # First try with the LLM
            prompt = self._create_relation_extraction_prompt(text, entities)
            response = self._call_llm(prompt)
            relations = self._parse_relation_response(response, entities)
            
            # If LLM extraction failed or returned empty results, fall back to base extractor
            if not relations:
                logger.warning("LLM relation extraction failed or returned empty results. Falling back to base extractor.")
                relations = super().extract_relations(text, entities)
            
            return relations
        
        except Exception as e:
            logger.error(f"Error in LLM relation extraction: {str(e)}")
            return super().extract_relations(text, entities)
    
    def extract_statements(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract scientific statements from the given text using a language model.
        
        Args:
            text: The text to extract statements from
            
        Returns:
            A list of extracted statements
        """
        if not self.client:
            logger.warning("LLM client not initialized. Falling back to base extractor.")
            return super().extract_statements(text)
        
        try:
            # First try with the LLM
            prompt = self._create_statement_extraction_prompt(text)
            response = self._call_llm(prompt)
            statements = self._parse_statement_response(response)
            
            # If LLM extraction failed or returned empty results, fall back to base extractor
            if not statements:
                logger.warning("LLM statement extraction failed or returned empty results. Falling back to base extractor.")
                statements = super().extract_statements(text)
            
            return statements
        
        except Exception as e:
            logger.error(f"Error in LLM statement extraction: {str(e)}")
            return super().extract_statements(text)
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the language model with the given prompt.
        
        Args:
            prompt: The prompt to send to the language model
            
        Returns:
            The response from the language model
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a scientific information extraction system specialized in biomedical literature."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more deterministic responses
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise
    
    def _create_entity_extraction_prompt(self, text: str) -> str:
        """Create a prompt for entity extraction."""
        return f"""
        Extract all biological entities from the following scientific abstract.
        Focus on genes, proteins, diseases, and biological processes.
        
        For each entity, provide:
        1. The entity text as it appears in the abstract
        2. The entity type (gene, protein, disease, biological_process)
        3. The start and end character positions in the text
        4. A confidence score between 0 and 1
        
        Format your response as a JSON object with entity types as keys and lists of entities as values.
        Example format:
        {{
            "gene": [
                {{
                    "text": "PTEN",
                    "type": "gene",
                    "start_char": 42,
                    "end_char": 46,
                    "confidence": 0.95
                }}
            ],
            "protein": [...],
            "disease": [...],
            "biological_process": [...]
        }}
        
        Abstract:
        {text}
        """
    
    def _create_relation_extraction_prompt(self, text: str, entities: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create a prompt for relation extraction."""
        # Flatten entities for the prompt
        flat_entities = []
        for entity_type, entity_list in entities.items():
            flat_entities.extend(entity_list)
        
        entities_text = "\n".join([f"{i+1}. {e['text']} (Type: {e['type']})" for i, e in enumerate(flat_entities)])
        
        return f"""
        Extract relationships between biological entities in the following scientific abstract.
        Focus on relationships like "activates", "inhibits", "binds_to", "associated_with", and "causes".
        
        Entities found in the text:
        {entities_text}
        
        For each relationship, provide:
        1. The source entity text
        2. The target entity text
        3. The relationship type
        4. A confidence score between 0 and 1
        5. The text snippet that expresses this relationship
        
        Format your response as a JSON array of relationship objects.
        Example format:
        [
            {{
                "source": "PTEN",
                "target": "AKT",
                "relation_type": "inhibits",
                "confidence": 0.9,
                "text": "PTEN inhibits AKT phosphorylation"
            }}
        ]
        
        Abstract:
        {text}
        """
    
    def _create_statement_extraction_prompt(self, text: str) -> str:
        """Create a prompt for statement extraction."""
        return f"""
        Extract key scientific statements from the following abstract.
        Focus on findings, methods, background information, and conclusions.
        
        For each statement, provide:
        1. The statement text
        2. The statement type (finding, method, background, conclusion)
        3. A confidence score between 0 and 1
        4. The source text that contains this statement
        
        Format your response as a JSON array of statement objects.
        Example format:
        [
            {{
                "text": "PTEN inhibits AKT phosphorylation in cancer cells",
                "type": "finding",
                "confidence": 0.95,
                "source_text": "Our results show that PTEN inhibits AKT phosphorylation in cancer cells."
            }}
        ]
        
        Abstract:
        {text}
        """
    
    def _parse_entity_response(self, response: str, original_text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse the LLM response for entity extraction."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
            
            # Clean up the string to ensure it's valid JSON
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            json_str = json_str.strip()
            
            # Parse the JSON
            entities = json.loads(json_str)
            
            # Validate the structure
            if not isinstance(entities, dict):
                logger.warning(f"Invalid entity extraction response format: {response}")
                return {}
            
            # Ensure all required fields are present
            for entity_type, entity_list in entities.items():
                for i, entity in enumerate(entity_list):
                    if not all(k in entity for k in ['text', 'type', 'start_char', 'end_char', 'confidence']):
                        logger.warning(f"Entity missing required fields: {entity}")
                        # Add default values for missing fields
                        entity['text'] = entity.get('text', '')
                        entity['type'] = entity.get('type', entity_type)
                        entity['start_char'] = entity.get('start_char', 0)
                        entity['end_char'] = entity.get('end_char', 0)
                        entity['confidence'] = entity.get('confidence', 0.5)
            
            return entities
        
        except Exception as e:
            logger.error(f"Error parsing entity extraction response: {str(e)}")
            return {}
    
    def _parse_relation_response(self, response: str, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Parse the LLM response for relation extraction."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
            
            # Clean up the string to ensure it's valid JSON
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            json_str = json_str.strip()
            
            # Parse the JSON
            relations_raw = json.loads(json_str)
            
            # Validate the structure
            if not isinstance(relations_raw, list):
                logger.warning(f"Invalid relation extraction response format: {response}")
                return []
            
            # Flatten entities for easier lookup
            flat_entities = []
            for entity_type, entity_list in entities.items():
                flat_entities.extend(entity_list)
            
            # Process relations and link to entity objects
            relations = []
            for relation in relations_raw:
                if not all(k in relation for k in ['source', 'target', 'relation_type', 'confidence']):
                    logger.warning(f"Relation missing required fields: {relation}")
                    continue
                
                source_entity = self._find_closest_entity(relation['source'], flat_entities)
                target_entity = self._find_closest_entity(relation['target'], flat_entities)
                
                if source_entity and target_entity:
                    relations.append({
                        'source': source_entity,
                        'target': target_entity,
                        'relation_type': relation['relation_type'],
                        'confidence': relation['confidence'],
                        'text': relation.get('text', ''),
                    })
            
            return relations
        
        except Exception as e:
            logger.error(f"Error parsing relation extraction response: {str(e)}")
            return []
    
    def _parse_statement_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response for statement extraction."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
            
            # Clean up the string to ensure it's valid JSON
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            json_str = json_str.strip()
            
            # Parse the JSON
            statements = json.loads(json_str)
            
            # Validate the structure
            if not isinstance(statements, list):
                logger.warning(f"Invalid statement extraction response format: {response}")
                return []
            
            # Ensure all required fields are present
            for i, statement in enumerate(statements):
                if not all(k in statement for k in ['text', 'type', 'confidence']):
                    logger.warning(f"Statement missing required fields: {statement}")
                    # Add default values for missing fields
                    statement['text'] = statement.get('text', '')
                    statement['type'] = statement.get('type', 'unknown')
                    statement['confidence'] = statement.get('confidence', 0.5)
                    statement['source_text'] = statement.get('source_text', statement.get('text', ''))
            
            return statements
        
        except Exception as e:
            logger.error(f"Error parsing statement extraction response: {str(e)}")
            return []


class LLMExtractionPipeline(BaseExtractionPipeline):
    """
    LLM-based implementation of the extraction pipeline.
    
    This class uses language models to extract and normalize information
    from scientific abstracts.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the LLM extraction pipeline.
        
        Args:
            model_name: The name of the language model to use. If None, the default model
                       from the configuration will be used.
        """
        extractor = LLMExtractor(model_name)
        normalizer = BaseNormalizer()  # Use the base normalizer for now
        super().__init__(extractor, normalizer)

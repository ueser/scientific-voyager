"""
Prompt-based classifier for scientific statements.

This module implements a classifier that uses prompt engineering with
large language models to classify scientific statements into biological
scales and statement types.
"""

import json
import os
import uuid
import logging
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime

from scientific_voyager.interfaces.classification_interface import (
    IClassifier, BiologicalScale, StatementType
)
from scientific_voyager.interfaces.classification_dto import (
    ClassificationResultDTO, BatchClassificationResultDTO
)
from scientific_voyager.interfaces.extraction_dto import StatementDTO
from scientific_voyager.classification.prompt_templates import (
    SCALE_CLASSIFICATION_PROMPT,
    TYPE_CLASSIFICATION_PROMPT,
    COMBINED_CLASSIFICATION_PROMPT,
    BATCH_CLASSIFICATION_PROMPT
)
from scientific_voyager.config.config_manager import get_config
from scientific_voyager.utils.error_handling import retry, RetryStrategy
from scientific_voyager.utils.cache import cached

# Configure logging
logger = logging.getLogger(__name__)


class PromptClassifier(IClassifier):
    """
    Classifier that uses prompt engineering with large language models.
    
    This classifier uses carefully designed prompts with a large language model
    to classify scientific statements into biological scales and statement types.
    """
    
    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize the prompt classifier.
        
        Args:
            llm_provider: The LLM provider to use (default: "openai")
        """
        self.config = get_config()
        self.llm_provider = llm_provider
        
        # Initialize the LLM client based on the provider
        if llm_provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=self.config.get_config_dto().api_keys.get("openai")
                )
                self.model = self.config.get("classification.openai_model", "gpt-4o")
            except ImportError:
                logger.error("OpenAI package not installed. Please install it with: pip install openai")
                raise
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        logger.info(f"Initialized prompt classifier with {llm_provider} provider")
    
    @retry(max_attempts=3, strategy=RetryStrategy.EXPONENTIAL_JITTER)
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with the given prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response
        """
        if self.llm_provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,  # Low temperature for more deterministic outputs
                    max_tokens=1000
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                raise
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse a JSON response from the LLM.
        
        Args:
            response: The LLM's response
            
        Returns:
            Parsed JSON data
        """
        try:
            # Extract JSON from the response (in case there's additional text)
            json_start = response.find("{")
            json_end = response.rfind("}")
            
            if json_start >= 0 and json_end >= 0:
                json_str = response[json_start:json_end+1]
                return json.loads(json_str)
            
            # If no JSON object found, try parsing as a JSON array
            json_start = response.find("[")
            json_end = response.rfind("]")
            
            if json_start >= 0 and json_end >= 0:
                json_str = response[json_start:json_end+1]
                return {"results": json.loads(json_str)}
            
            # If still no JSON found, try parsing the entire response
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response: {response}")
            return {}
    
    @cached(ttl=3600, key_prefix="scale_classification")
    def classify_scale(self, statement: StatementDTO) -> Tuple[BiologicalScale, float]:
        """
        Classify a statement into a biological scale.
        
        Args:
            statement: The statement to classify
            
        Returns:
            Tuple of (biological scale, confidence score)
        """
        # Prepare the prompt
        prompt = SCALE_CLASSIFICATION_PROMPT.format(statement=statement.text)
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Parse the response
        result = self._parse_json_response(response)
        
        # Extract the scale and confidence
        scale_str = result.get("scale", "UNKNOWN")
        confidence = float(result.get("confidence", 0.0))
        
        try:
            # Convert to enum
            scale = BiologicalScale(scale_str.lower())
        except ValueError:
            logger.warning(f"Invalid scale value: {scale_str}, defaulting to UNKNOWN")
            scale = BiologicalScale.UNKNOWN
            confidence = 0.0
        
        return scale, confidence
    
    @cached(ttl=3600, key_prefix="type_classification")
    def classify_type(self, statement: StatementDTO) -> Tuple[StatementType, float]:
        """
        Classify a statement into a statement type.
        
        Args:
            statement: The statement to classify
            
        Returns:
            Tuple of (statement type, confidence score)
        """
        # Prepare the prompt
        prompt = TYPE_CLASSIFICATION_PROMPT.format(statement=statement.text)
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Parse the response
        result = self._parse_json_response(response)
        
        # Extract the type and confidence
        type_str = result.get("type", "UNKNOWN")
        confidence = float(result.get("confidence", 0.0))
        
        try:
            # Convert to enum
            statement_type = StatementType(type_str.lower())
        except ValueError:
            logger.warning(f"Invalid type value: {type_str}, defaulting to UNKNOWN")
            statement_type = StatementType.UNKNOWN
            confidence = 0.0
        
        return statement_type, confidence
    
    @cached(ttl=3600, key_prefix="combined_classification")
    def classify_statement(self, statement: StatementDTO) -> Dict[str, Any]:
        """
        Classify a statement into both scale and type.
        
        Args:
            statement: The statement to classify
            
        Returns:
            Dictionary with classification results
        """
        # Prepare the prompt
        prompt = COMBINED_CLASSIFICATION_PROMPT.format(statement=statement.text)
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Parse the response
        result = self._parse_json_response(response)
        
        # Extract the scale and confidence
        scale_str = result.get("scale", "UNKNOWN")
        scale_confidence = float(result.get("scale_confidence", 0.0))
        scale_reasoning = result.get("scale_reasoning", "")
        
        # Extract the type and confidence
        type_str = result.get("type", "UNKNOWN")
        type_confidence = float(result.get("type_confidence", 0.0))
        type_reasoning = result.get("type_reasoning", "")
        
        try:
            # Convert to enums
            scale = BiologicalScale(scale_str.lower())
        except ValueError:
            logger.warning(f"Invalid scale value: {scale_str}, defaulting to UNKNOWN")
            scale = BiologicalScale.UNKNOWN
            scale_confidence = 0.0
        
        try:
            statement_type = StatementType(type_str.lower())
        except ValueError:
            logger.warning(f"Invalid type value: {type_str}, defaulting to UNKNOWN")
            statement_type = StatementType.UNKNOWN
            type_confidence = 0.0
        
        # Create the classification result
        # Get statement ID from metadata if available, otherwise generate a new one
        statement_id = statement.metadata.get("id", str(uuid.uuid4()))
        
        classification_result = ClassificationResultDTO(
            statement_id=statement_id,
            statement_text=statement.text,
            biological_scale=scale,
            scale_confidence=scale_confidence,
            statement_type=statement_type,
            type_confidence=type_confidence,
            classification_time=datetime.now(),
            metadata={
                "scale_reasoning": scale_reasoning,
                "type_reasoning": type_reasoning
            }
        )
        
        return classification_result.to_dict()
    
    def batch_classify(self, statements: List[StatementDTO]) -> List[Dict[str, Any]]:
        """
        Classify multiple statements in batch.
        
        Args:
            statements: List of statements to classify
            
        Returns:
            List of classification results
        """
        if not statements:
            return []
        
        # For small batches, use individual classification for better caching
        if len(statements) <= 3:
            return [self.classify_statement(statement) for statement in statements]
        
        # For larger batches, use batch classification
        # Prepare the statements for the prompt
        statements_text = ""
        for i, statement in enumerate(statements):
            # Get statement ID from metadata if available, otherwise generate a new one
            statement_id = statement.metadata.get("id", str(uuid.uuid4()))
            statements_text += f"{i+1}. [ID: {statement_id}] {statement.text}\n\n"
        
        # Prepare the prompt
        prompt = BATCH_CLASSIFICATION_PROMPT.format(statements=statements_text)
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Parse the response
        result = self._parse_json_response(response)
        
        # Extract the results
        batch_results = []
        
        if "results" in result and isinstance(result["results"], list):
            # Process results from a JSON array
            for item in result["results"]:
                statement_id = item.get("statement_id", "")
                
                # Find the corresponding statement
                statement = next((s for s in statements if s.metadata.get("id") == statement_id), None)
                if not statement:
                    # Try to match by index if ID not found
                    try:
                        index = int(statement_id.split("_")[-1]) - 1
                        if 0 <= index < len(statements):
                            statement = statements[index]
                    except (ValueError, IndexError):
                        continue
                
                if not statement:
                    continue
                
                # Extract the scale and confidence
                scale_str = item.get("scale", "UNKNOWN")
                scale_confidence = float(item.get("scale_confidence", 0.0))
                
                # Extract the type and confidence
                type_str = item.get("type", "UNKNOWN")
                type_confidence = float(item.get("type_confidence", 0.0))
                
                try:
                    # Convert to enums
                    scale = BiologicalScale(scale_str.lower())
                except ValueError:
                    logger.warning(f"Invalid scale value: {scale_str}, defaulting to UNKNOWN")
                    scale = BiologicalScale.UNKNOWN
                    scale_confidence = 0.0
                
                try:
                    statement_type = StatementType(type_str.lower())
                except ValueError:
                    logger.warning(f"Invalid type value: {type_str}, defaulting to UNKNOWN")
                    statement_type = StatementType.UNKNOWN
                    type_confidence = 0.0
                
                # Create the classification result
                # Get statement ID from metadata if available, otherwise generate a new one
                statement_id = statement.metadata.get("id", str(uuid.uuid4()))
                
                classification_result = ClassificationResultDTO(
                    statement_id=statement_id,
                    statement_text=statement.text,
                    biological_scale=scale,
                    scale_confidence=scale_confidence,
                    statement_type=statement_type,
                    type_confidence=type_confidence,
                    classification_time=datetime.now(),
                    metadata={}
                )
                
                batch_results.append(classification_result.to_dict())
        
        # If no results were parsed, fall back to individual classification
        if not batch_results:
            logger.warning("Batch classification failed, falling back to individual classification")
            return [self.classify_statement(statement) for statement in statements]
        
        return batch_results

"""
Validation module for classification results.

This module implements validation mechanisms to ensure the quality
of classification results.
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional, Union, Tuple, cast
from datetime import datetime

from scientific_voyager.interfaces.classification_interface import (
    IClassificationValidator, BiologicalScale, StatementType
)
from scientific_voyager.interfaces.classification_dto import (
    ClassificationResultDTO, FeedbackDTO
)
from scientific_voyager.interfaces.extraction_dto import StatementDTO
from scientific_voyager.classification.prompt_templates import VALIDATION_PROMPT
from scientific_voyager.config.config_manager import get_config
from scientific_voyager.utils.error_handling import retry, RetryStrategy

# Configure logging
logger = logging.getLogger(__name__)


class PromptValidator(IClassificationValidator):
    """
    Validator that uses prompt engineering with large language models.
    
    This validator uses carefully designed prompts with a large language model
    to validate classification results and suggest improvements.
    """
    
    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize the prompt validator.
        
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
        
        # Set validation thresholds
        self.confidence_threshold = self.config.get("classification.validation.confidence_threshold", 0.7)
        
        logger.info(f"Initialized prompt validator with {llm_provider} provider")
    
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
            
            # If no JSON found, try parsing the entire response
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response: {response}")
            return {}
    
    def validate_classification(self, 
                               statement: StatementDTO,
                               classification: Dict[str, Any]) -> bool:
        """
        Validate a classification result.
        
        Args:
            statement: The classified statement
            classification: The classification result
            
        Returns:
            True if the classification is valid, False otherwise
        """
        # First, perform basic validation checks
        if not classification:
            logger.warning("Empty classification result")
            return False
        
        # Check if confidence scores are below threshold
        scale_confidence = classification.get("scale_confidence", 0.0)
        type_confidence = classification.get("type_confidence", 0.0)
        
        if scale_confidence < self.confidence_threshold or type_confidence < self.confidence_threshold:
            logger.warning(f"Low confidence scores: scale={scale_confidence}, type={type_confidence}")
            return False
        
        # For high-confidence classifications, we can skip LLM validation
        if scale_confidence > 0.9 and type_confidence > 0.9:
            return True
        
        # For medium-confidence classifications, use LLM validation
        # Prepare the prompt
        prompt = VALIDATION_PROMPT.format(
            statement=statement.text,
            scale=classification.get("biological_scale", "UNKNOWN"),
            scale_confidence=scale_confidence,
            type=classification.get("statement_type", "UNKNOWN"),
            type_confidence=type_confidence
        )
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Parse the response
        result = self._parse_json_response(response)
        
        # Extract the validation result
        is_valid = result.get("is_valid", False)
        
        if not is_valid:
            logger.warning(f"Classification validation failed: {result.get('reasoning', 'No reason provided')}")
        
        return is_valid
    
    def suggest_improvements(self, 
                            statement: StatementDTO,
                            classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest improvements for a classification result.
        
        Args:
            statement: The classified statement
            classification: The classification result
            
        Returns:
            Dictionary with suggested improvements
        """
        # Prepare the prompt
        prompt = VALIDATION_PROMPT.format(
            statement=statement.text,
            scale=classification.get("biological_scale", "UNKNOWN"),
            scale_confidence=classification.get("scale_confidence", 0.0),
            type=classification.get("statement_type", "UNKNOWN"),
            type_confidence=classification.get("type_confidence", 0.0)
        )
        
        # Call the LLM
        response = self._call_llm(prompt)
        
        # Parse the response
        result = self._parse_json_response(response)
        
        # Extract the suggested improvements
        suggested_scale = result.get("suggested_scale")
        suggested_type = result.get("suggested_type")
        scale_feedback = result.get("scale_feedback")
        type_feedback = result.get("type_feedback")
        confidence_feedback = result.get("confidence_feedback")
        reasoning = result.get("reasoning")
        
        # Create a feedback DTO
        try:
            # Convert original classification to DTO
            original_classification = ClassificationResultDTO.from_dict(classification)
            
            # Convert suggested scale and type to enums if present
            corrected_scale = None
            if suggested_scale and suggested_scale.lower() != classification.get("biological_scale", "").lower():
                try:
                    corrected_scale = BiologicalScale(suggested_scale.lower())
                except ValueError:
                    logger.warning(f"Invalid suggested scale: {suggested_scale}")
            
            corrected_type = None
            if suggested_type and suggested_type.lower() != classification.get("statement_type", "").lower():
                try:
                    corrected_type = StatementType(suggested_type.lower())
                except ValueError:
                    logger.warning(f"Invalid suggested type: {suggested_type}")
            
            # Create the feedback
            feedback = FeedbackDTO(
                statement_id=statement.id,
                original_classification=original_classification,
                corrected_scale=corrected_scale,
                corrected_type=corrected_type,
                feedback_text=reasoning or "",
                feedback_source="validator",
                feedback_time=datetime.now(),
                metadata={
                    "scale_feedback": scale_feedback,
                    "type_feedback": type_feedback,
                    "confidence_feedback": confidence_feedback
                }
            )
            
            return feedback.to_dict()
            
        except Exception as e:
            logger.error(f"Error creating feedback: {e}")
            return {
                "error": str(e),
                "suggested_scale": suggested_scale,
                "suggested_type": suggested_type,
                "reasoning": reasoning
            }


class RuleBasedValidator(IClassificationValidator):
    """
    Validator that uses rule-based heuristics.
    
    This validator uses predefined rules and heuristics to validate
    classification results without calling an external LLM.
    """
    
    def __init__(self):
        """Initialize the rule-based validator."""
        self.config = get_config()
        
        # Set validation thresholds
        self.confidence_threshold = self.config.get("classification.validation.confidence_threshold", 0.7)
        
        # Define keyword mappings for scales
        self.scale_keywords = {
            BiologicalScale.GENETIC: [
                "gene", "dna", "rna", "chromosome", "genome", "genomic", "nucleotide",
                "mutation", "allele", "transcription", "expression", "promoter"
            ],
            BiologicalScale.MOLECULAR: [
                "protein", "enzyme", "molecule", "receptor", "ligand", "metabolite",
                "peptide", "antibody", "kinase", "phosphorylation", "binding"
            ],
            BiologicalScale.CELLULAR: [
                "cell", "cellular", "organelle", "mitochondria", "nucleus", "cytoplasm",
                "membrane", "vesicle", "endoplasmic", "golgi", "lysosome"
            ],
            BiologicalScale.TISSUE: [
                "tissue", "epithelial", "connective", "muscle", "neural", "histology",
                "fibroblast", "extracellular matrix", "stroma"
            ],
            BiologicalScale.ORGAN: [
                "organ", "heart", "liver", "brain", "kidney", "lung", "pancreas",
                "spleen", "stomach", "intestine", "skin"
            ],
            BiologicalScale.SYSTEM: [
                "system", "nervous", "immune", "cardiovascular", "respiratory",
                "digestive", "endocrine", "reproductive", "urinary", "lymphatic"
            ],
            BiologicalScale.ORGANISM: [
                "organism", "patient", "individual", "human", "mouse", "rat", "animal",
                "physiology", "behavior", "development", "aging"
            ],
            BiologicalScale.POPULATION: [
                "population", "epidemiology", "prevalence", "incidence", "demographic",
                "cohort", "public health", "community"
            ],
            BiologicalScale.ECOSYSTEM: [
                "ecosystem", "environment", "ecological", "biodiversity", "species",
                "habitat", "climate", "pollution"
            ]
        }
        
        # Define keyword mappings for statement types
        self.type_keywords = {
            StatementType.CAUSAL: [
                "cause", "lead to", "result in", "induce", "trigger", "activate",
                "inhibit", "suppress", "promote", "prevent", "block"
            ],
            StatementType.CORRELATIONAL: [
                "associate", "correlate", "relate", "link", "connection", "relationship",
                "co-occur", "coincide", "correspond"
            ],
            StatementType.DESCRIPTIVE: [
                "characterize", "describe", "exhibit", "display", "show", "demonstrate",
                "present", "possess", "contain", "comprise"
            ],
            StatementType.DEFINITIONAL: [
                "define", "refer to", "known as", "called", "termed", "classified as",
                "categorized as", "identified as", "recognized as"
            ],
            StatementType.METHODOLOGICAL: [
                "measure", "analyze", "assess", "evaluate", "quantify", "detect",
                "identify", "determine", "examine", "investigate", "method"
            ],
            StatementType.COMPARATIVE: [
                "compare", "contrast", "differ", "similar", "higher", "lower",
                "greater", "less", "increase", "decrease", "reduce", "enhance"
            ],
            StatementType.INTERVENTION: [
                "treat", "therapy", "intervention", "administer", "dose", "regimen",
                "prescribe", "medication", "drug", "compound", "surgery"
            ],
            StatementType.PREDICTIVE: [
                "predict", "forecast", "anticipate", "expect", "project", "estimate",
                "likelihood", "probability", "risk", "chance", "odds"
            ],
            StatementType.HYPOTHESIS: [
                "hypothesize", "propose", "suggest", "speculate", "theorize", "postulate",
                "conjecture", "might", "may", "could", "possibly", "potentially"
            ],
            StatementType.REVIEW: [
                "review", "summarize", "overview", "literature", "current knowledge",
                "state of the art", "recent advances", "progress", "developments"
            ]
        }
        
        logger.info("Initialized rule-based validator")
    
    def _check_keywords(self, text: str, keywords: List[str]) -> int:
        """
        Count the number of keyword matches in the text.
        
        Args:
            text: The text to check
            keywords: List of keywords to check for
            
        Returns:
            Number of keyword matches
        """
        text_lower = text.lower()
        count = 0
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                count += 1
        
        return count
    
    def validate_classification(self, 
                               statement: StatementDTO,
                               classification: Dict[str, Any]) -> bool:
        """
        Validate a classification result using rule-based heuristics.
        
        Args:
            statement: The classified statement
            classification: The classification result
            
        Returns:
            True if the classification is valid, False otherwise
        """
        # First, perform basic validation checks
        if not classification:
            logger.warning("Empty classification result")
            return False
        
        # Check if confidence scores are below threshold
        scale_confidence = classification.get("scale_confidence", 0.0)
        type_confidence = classification.get("type_confidence", 0.0)
        
        if scale_confidence < self.confidence_threshold or type_confidence < self.confidence_threshold:
            logger.warning(f"Low confidence scores: scale={scale_confidence}, type={type_confidence}")
            return False
        
        # Get the classified scale and type
        scale_str = classification.get("biological_scale", "unknown")
        type_str = classification.get("statement_type", "unknown")
        
        try:
            scale = BiologicalScale(scale_str.lower())
            statement_type = StatementType(type_str.lower())
        except ValueError:
            logger.warning(f"Invalid scale or type: scale={scale_str}, type={type_str}")
            return False
        
        # Check if the statement contains keywords associated with the classified scale
        scale_keywords = self.scale_keywords.get(scale, [])
        scale_keyword_count = self._check_keywords(statement.text, scale_keywords)
        
        # Check if the statement contains keywords associated with the classified type
        type_keywords = self.type_keywords.get(statement_type, [])
        type_keyword_count = self._check_keywords(statement.text, type_keywords)
        
        # Validate based on keyword matches
        # If both scale and type have keyword matches, the classification is likely valid
        if scale_keyword_count > 0 and type_keyword_count > 0:
            return True
        
        # If the confidence is high but no keywords match, still consider it valid
        # (the LLM might be picking up on subtle cues not captured by keywords)
        if scale_confidence > 0.9 and type_confidence > 0.9:
            return True
        
        # If only one has keyword matches and the confidence is reasonable, consider it valid
        if (scale_keyword_count > 0 and scale_confidence > 0.8) or (type_keyword_count > 0 and type_confidence > 0.8):
            return True
        
        # Otherwise, consider it invalid
        logger.warning(f"Insufficient keyword matches: scale={scale_keyword_count}, type={type_keyword_count}")
        return False
    
    def suggest_improvements(self, 
                            statement: StatementDTO,
                            classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest improvements for a classification result based on keywords.
        
        Args:
            statement: The classified statement
            classification: The classification result
            
        Returns:
            Dictionary with suggested improvements
        """
        # Get the classified scale and type
        scale_str = classification.get("biological_scale", "unknown")
        type_str = classification.get("statement_type", "unknown")
        
        try:
            current_scale = BiologicalScale(scale_str.lower())
            current_type = StatementType(type_str.lower())
        except ValueError:
            logger.warning(f"Invalid scale or type: scale={scale_str}, type={type_str}")
            current_scale = BiologicalScale.UNKNOWN
            current_type = StatementType.UNKNOWN
        
        # Check keyword matches for all scales and types
        scale_matches = {}
        for scale, keywords in self.scale_keywords.items():
            count = self._check_keywords(statement.text, keywords)
            if count > 0:
                scale_matches[scale] = count
        
        type_matches = {}
        for stmt_type, keywords in self.type_keywords.items():
            count = self._check_keywords(statement.text, keywords)
            if count > 0:
                type_matches[stmt_type] = count
        
        # Find the scale and type with the most keyword matches
        suggested_scale = current_scale
        suggested_type = current_type
        
        if scale_matches:
            max_scale = max(scale_matches.items(), key=lambda x: x[1])[0]
            if max_scale != current_scale and scale_matches[max_scale] > 1:
                suggested_scale = max_scale
        
        if type_matches:
            max_type = max(type_matches.items(), key=lambda x: x[1])[0]
            if max_type != current_type and type_matches[max_type] > 1:
                suggested_type = max_type
        
        # Create a feedback DTO if there are suggested improvements
        if suggested_scale != current_scale or suggested_type != current_type:
            try:
                # Convert original classification to DTO
                original_classification = ClassificationResultDTO.from_dict(classification)
                
                # Create the feedback
                feedback = FeedbackDTO(
                    statement_id=statement.id,
                    original_classification=original_classification,
                    corrected_scale=suggested_scale if suggested_scale != current_scale else None,
                    corrected_type=suggested_type if suggested_type != current_type else None,
                    feedback_text=f"Keyword analysis suggests different classification",
                    feedback_source="rule_validator",
                    feedback_time=datetime.now(),
                    metadata={
                        "scale_matches": {scale.value: count for scale, count in scale_matches.items()},
                        "type_matches": {stmt_type.value: count for stmt_type, count in type_matches.items()}
                    }
                )
                
                return feedback.to_dict()
                
            except Exception as e:
                logger.error(f"Error creating feedback: {e}")
                return {
                    "error": str(e),
                    "suggested_scale": suggested_scale.value,
                    "suggested_type": suggested_type.value
                }
        
        # No improvements suggested
        return {}

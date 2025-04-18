"""
Example script demonstrating the biological scale classification system.

This script shows how to use the prompt-based classifier to categorize
scientific statements into biological scales and statement types.
"""

import os
import sys
import time
import uuid
from pathlib import Path
import logging
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scientific_voyager.interfaces.extraction_dto import StatementDTO
from scientific_voyager.classification.prompt_classifier import PromptClassifier
from scientific_voyager.classification.validation import PromptValidator, RuleBasedValidator
from scientific_voyager.interfaces.classification_interface import BiologicalScale, StatementType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_classification_result(result):
    """Print classification result in a readable format."""
    print(f"Statement: {result['statement_text']}")
    print(f"Biological Scale: {result['biological_scale']} (Confidence: {result['scale_confidence']:.2f})")
    print(f"Statement Type: {result['statement_type']} (Confidence: {result['type_confidence']:.2f})")
    
    if "metadata" in result and result["metadata"]:
        if "scale_reasoning" in result["metadata"]:
            print(f"Scale Reasoning: {result['metadata']['scale_reasoning']}")
        if "type_reasoning" in result["metadata"]:
            print(f"Type Reasoning: {result['metadata']['type_reasoning']}")
    
    print("-" * 80)


def example_single_classification():
    """Example of classifying a single statement."""
    print("=" * 80)
    print("Example 1: Single Statement Classification")
    print("=" * 80)
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example statements representing different biological scales
    statements = [
        "The PTEN gene mutation leads to increased PI3K/AKT pathway activation.",
        "Protein kinase C phosphorylates the receptor, leading to its internalization.",
        "T cells release cytokines that activate macrophages in the inflammatory response.",
        "The epithelial tissue forms a protective barrier against pathogens.",
        "The liver metabolizes drugs and toxins to facilitate their elimination from the body.",
        "The immune system produces antibodies in response to viral infections.",
        "Patients with type 2 diabetes often develop insulin resistance over time.",
        "The prevalence of obesity has increased significantly in urban populations.",
        "Climate change affects the distribution of disease vectors in tropical ecosystems."
    ]
    
    # Select one statement for this example
    statement_text = statements[0]
    
    # Create a statement DTO (using new multi-label fields)
    statement = StatementDTO(
        text=statement_text,
        types=[],  # will be filled by classifier
        biological_scales=[],  # will be filled by classifier
        confidence=1.0,
        cross_scale_relations=[],
        metadata={"source": "example"}
    )

    # Classify the statement (simulate multi-label output for MVP)
    print(f"Classifying statement: {statement_text}")
    # For MVP: simulate multi-label output (hardcoded for demonstration)
    statement.types = ["causal", "descriptive"]
    statement.biological_scales = ["genetic", "molecular"]
    statement.cross_scale_relations = [
        {
            "source_scale": "genetic",
            "target_scale": "molecular",
            "relation_type": "causal",
            "description": "Mutation in PTEN gene (genetic) leads to activation of PI3K/AKT pathway (molecular)."
        }
    ]
    # Minimal confidence scoring: assign a confidence to each label
    type_confidences = {"causal": 0.95, "descriptive": 0.8}
    scale_confidences = {"genetic": 0.9, "molecular": 0.85}
    statement.metadata["type_confidences"] = type_confidences
    statement.metadata["scale_confidences"] = scale_confidences

    # Print the result (MVP)
    print("\nClassification Result:")
    print(f"Statement: {statement.text}")
    print(f"Statement Types: {statement.types}")
    print("Type Confidences:")
    for t in statement.types:
        conf = statement.metadata.get("type_confidences", {}).get(t, None)
        print(f"  {t}: {conf if conf is not None else 'n/a'}")
    print(f"Biological Scales: {statement.biological_scales}")
    print("Scale Confidences:")
    for s in statement.biological_scales:
        conf = statement.metadata.get("scale_confidences", {}).get(s, None)
        print(f"  {s}: {conf if conf is not None else 'n/a'}")
    print("Cross-scale Relations:")
    for rel in statement.cross_scale_relations:
        print(f"  {rel}")
    print("-" * 80)

    # Minimal validation logic
    allowed_scales = [
        "genetic", "molecular", "cellular", "tissue", "organ", "system", "organism", "population", "ecosystem"
    ]
    allowed_types = [
        "causal", "correlational", "descriptive", "definitional", "methodological", "comparative", "intervention", "predictive", "hypothesis", "review"
    ]
    def validate_statement(stmt):
        errors = []
        if not stmt.types:
            errors.append("No statement types assigned.")
        else:
            for t in stmt.types:
                if t not in allowed_types:
                    errors.append(f"Invalid statement type: {t}")
        if not stmt.biological_scales:
            errors.append("No biological scales assigned.")
        else:
            for s in stmt.biological_scales:
                if s not in allowed_scales:
                    errors.append(f"Invalid biological scale: {s}")
        # Optionally, check cross-scale relations
        for rel in stmt.cross_scale_relations:
            if rel["source_scale"] not in stmt.biological_scales:
                errors.append(f"Cross-scale relation source_scale {rel['source_scale']} not in biological_scales.")
            if rel["target_scale"] not in stmt.biological_scales:
                errors.append(f"Cross-scale relation target_scale {rel['target_scale']} not in biological_scales.")
        return errors

    validation_errors = validate_statement(statement)
    if not validation_errors:
        print("Validation: PASS")
    else:
        print("Validation: FAIL")
        for err in validation_errors:
            print(f"  - {err}")
    print("-" * 80)

    # Minimal feedback loop
    feedback_log = []
    print("Feedback: If you would like to correct the classification, enter comma-separated values.")
    user_types = input(f"Enter correct statement types (or leave blank to keep {statement.types}): ").strip()
    user_scales = input(f"Enter correct biological scales (or leave blank to keep {statement.biological_scales}): ").strip()
    feedback = {}
    if user_types:
        corrected_types = [t.strip() for t in user_types.split(",") if t.strip()]
        feedback["corrected_types"] = corrected_types
        statement.types = corrected_types
        # Assign default confidence to corrected types
        statement.metadata["type_confidences"] = {t: 0.7 for t in corrected_types}
    if user_scales:
        corrected_scales = [s.strip() for s in user_scales.split(",") if s.strip()]
        feedback["corrected_biological_scales"] = corrected_scales
        statement.biological_scales = corrected_scales
        # Assign default confidence to corrected scales
        statement.metadata["scale_confidences"] = {s: 0.7 for s in corrected_scales}
    if feedback:
        feedback["statement_text"] = statement.text
        feedback_log.append(feedback)
        print("Feedback received and applied.")
    else:
        print("No feedback provided. Keeping original classification.")
    print("Final Classification After Feedback:")
    print(f"Statement: {statement.text}")
    print(f"Statement Types: {statement.types}")
    print("Type Confidences:")
    for t in statement.types:
        conf = statement.metadata.get("type_confidences", {}).get(t, None)
        print(f"  {t}: {conf if conf is not None else 'n/a'}")
    print(f"Biological Scales: {statement.biological_scales}")
    print("Scale Confidences:")
    for s in statement.biological_scales:
        conf = statement.metadata.get("scale_confidences", {}).get(s, None)
        print(f"  {s}: {conf if conf is not None else 'n/a'}")
    print("Cross-scale Relations:")
    for rel in statement.cross_scale_relations:
        print(f"  {rel}")
    print("-" * 80)
    if feedback_log:
        print("Feedback Log:")
        for fb in feedback_log:
            print(fb)
        print("-" * 80)


def example_batch_classification():
    """Example of classifying multiple statements in batch."""
    print("\n" + "=" * 80)
    print("Example 2: Batch Classification")
    print("=" * 80)
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example statements representing different biological scales
    statements = [
        "The PTEN gene mutation leads to increased PI3K/AKT pathway activation.",
        "Protein kinase C phosphorylates the receptor, leading to its internalization.",
        "T cells release cytokines that activate macrophages in the inflammatory response.",
        "The epithelial tissue forms a protective barrier against pathogens.",
        "The liver metabolizes drugs and toxins to facilitate their elimination from the body.",
        "The immune system produces antibodies in response to viral infections.",
        "Patients with type 2 diabetes often develop insulin resistance over time.",
        "The prevalence of obesity has increased significantly in urban populations.",
        "Climate change affects the distribution of disease vectors in tropical ecosystems."
    ]
    
    # Create statement DTOs
    statement_dtos = []
    for text in statements[:3]:  # Use only the first 3 statements for this example
        statement = StatementDTO(
            id=str(uuid.uuid4()),
            text=text,
            source="example",
            confidence=1.0
        )
        statement_dtos.append(statement)
    
    # Classify the statements in batch
    print(f"Classifying {len(statement_dtos)} statements in batch...")
    results = classifier.batch_classify(statement_dtos)
    
    # Print the results
    print("\nBatch Classification Results:")
    for result in results:
        print_classification_result(result)


def example_validation():
    """Example of validating classification results."""
    print("\n" + "=" * 80)
    print("Example 3: Classification Validation")
    print("=" * 80)
    
    # Create the classifier and validators
    classifier = PromptClassifier()
    prompt_validator = PromptValidator()
    rule_validator = RuleBasedValidator()
    
    # Example statements with potentially ambiguous classifications
    statements = [
        "The BRCA1 gene is associated with an increased risk of breast cancer.",
        "Patients taking statins showed a 30% reduction in LDL cholesterol levels.",
        "The study measured cortisol levels in saliva samples from stressed individuals."
    ]
    
    # Create statement DTOs
    statement_dtos = []
    for text in statements:
        statement = StatementDTO(
            id=str(uuid.uuid4()),
            text=text,
            source="example",
            confidence=1.0
        )
        statement_dtos.append(statement)
    
    # Classify and validate each statement
    for statement in statement_dtos:
        print(f"\nStatement: {statement.text}")
        
        # Classify the statement
        result = classifier.classify_statement(statement)
        
        print("Classification Result:")
        print(f"Biological Scale: {result['biological_scale']} (Confidence: {result['scale_confidence']:.2f})")
        print(f"Statement Type: {result['statement_type']} (Confidence: {result['type_confidence']:.2f})")
        
        # Validate using rule-based validator
        rule_valid = rule_validator.validate_classification(statement, result)
        print(f"Rule-Based Validation: {'Valid' if rule_valid else 'Invalid'}")
        
        if not rule_valid:
            improvements = rule_validator.suggest_improvements(statement, result)
            if improvements and "corrected_scale" in improvements and improvements["corrected_scale"]:
                print(f"Suggested Scale: {improvements['corrected_scale']}")
            if improvements and "corrected_type" in improvements and improvements["corrected_type"]:
                print(f"Suggested Type: {improvements['corrected_type']}")
        
        # Validate using prompt-based validator (only for the first statement to save API calls)
        if statement.text == statements[0]:
            prompt_valid = prompt_validator.validate_classification(statement, result)
            print(f"Prompt-Based Validation: {'Valid' if prompt_valid else 'Invalid'}")
            
            if not prompt_valid:
                improvements = prompt_validator.suggest_improvements(statement, result)
                if improvements and "corrected_scale" in improvements and improvements["corrected_scale"]:
                    print(f"Suggested Scale: {improvements['corrected_scale']}")
                if improvements and "corrected_type" in improvements and improvements["corrected_type"]:
                    print(f"Suggested Type: {improvements['corrected_type']}")
        
        print("-" * 80)


def example_scale_distribution():
    """Example of analyzing the distribution of biological scales in a set of statements."""
    print("\n" + "=" * 80)
    print("Example 4: Biological Scale Distribution Analysis")
    print("=" * 80)
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example statements from a scientific abstract
    abstract_statements = [
        "Mutations in the PTEN gene are commonly found in various types of cancer.",
        "The PTEN protein acts as a phosphatase that dephosphorylates PIP3 to PIP2.",
        "This dephosphorylation inhibits the PI3K/AKT signaling pathway.",
        "At the cellular level, PTEN regulates cell cycle progression and apoptosis.",
        "In breast tissue, loss of PTEN function leads to abnormal cell proliferation.",
        "The liver shows high expression of PTEN compared to other organs.",
        "The immune system is affected by PTEN through regulation of T cell activation.",
        "Patients with PTEN mutations often develop multiple types of cancer throughout life.",
        "The prevalence of PTEN mutations varies across different populations."
    ]
    
    # Create statement DTOs
    statement_dtos = []
    for text in abstract_statements:
        statement = StatementDTO(
            id=str(uuid.uuid4()),
            text=text,
            source="example",
            confidence=1.0
        )
        statement_dtos.append(statement)
    
    # Classify each statement
    print("Classifying statements from a scientific abstract about PTEN...")
    scale_counts = {scale.value: 0 for scale in BiologicalScale}
    type_counts = {stmt_type.value: 0 for stmt_type in StatementType}
    
    for statement in statement_dtos:
        # For this example, we'll use individual classification to better demonstrate the distribution
        scale, scale_confidence = classifier.classify_scale(statement)
        stmt_type, type_confidence = classifier.classify_type(statement)
        
        scale_counts[scale.value] += 1
        type_counts[stmt_type.value] += 1
        
        print(f"Statement: {statement.text}")
        print(f"Scale: {scale.value} (Confidence: {scale_confidence:.2f})")
        print(f"Type: {stmt_type.value} (Confidence: {type_confidence:.2f})")
        print()
    
    # Print the distribution
    print("\nBiological Scale Distribution:")
    for scale, count in scale_counts.items():
        if count > 0:
            print(f"{scale}: {count} statements")
    
    print("\nStatement Type Distribution:")
    for stmt_type, count in type_counts.items():
        if count > 0:
            print(f"{stmt_type}: {count} statements")


def main():
    """Main function to run the examples."""
    # Uncomment the examples you want to run
    example_single_classification()
    # example_batch_classification()
    # example_validation()
    # example_scale_distribution()


if __name__ == "__main__":
    main()

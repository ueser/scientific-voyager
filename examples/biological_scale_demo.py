"""
Biological Scale Classification Demo

This script demonstrates the multi-scale hierarchical model and categorization system
for scientific statements, showing how statements are classified into different
biological scales and statement types.
"""

import os
import sys
import time
import uuid
import json
from pathlib import Path
import logging
from typing import List, Dict, Any
from datetime import datetime
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
from scientific_voyager.interfaces.classification_dto import ClassificationResultDTO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)


def print_classification_result(result, include_reasoning=True):
    """Print classification result in a readable format."""
    print(f"\nStatement: {result['statement_text']}")
    print(f"Biological Scale: {result['biological_scale']} (Confidence: {result['scale_confidence']:.2f})")
    print(f"Statement Type: {result['statement_type']} (Confidence: {result['type_confidence']:.2f})")
    
    if include_reasoning and "metadata" in result and result["metadata"]:
        if "scale_reasoning" in result["metadata"] and result["metadata"]["scale_reasoning"]:
            print(f"\nScale Reasoning: {result['metadata']['scale_reasoning']}")
        if "type_reasoning" in result["metadata"] and result["metadata"]["type_reasoning"]:
            print(f"\nType Reasoning: {result['metadata']['type_reasoning']}")
    
    print("-" * 80)


def create_statement_dto(text, source="example"):
    """Create a statement DTO from text."""
    return StatementDTO(
        text=text,
        type="scientific_statement",  # Statement type as per StatementDTO definition
        confidence=1.0,
        metadata={"source": source, "id": str(uuid.uuid4())}
    )


def demo_scale_classification():
    """Demonstrate classification of statements across different biological scales."""
    print_header("1. Biological Scale Classification Demonstration")
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example statements for each biological scale
    scale_examples = {
        BiologicalScale.GENETIC: [
            "The BRCA1 gene mutation increases the risk of breast and ovarian cancer.",
            "DNA methylation patterns regulate gene expression without altering the genetic sequence."
        ],
        BiologicalScale.MOLECULAR: [
            "Insulin binds to its receptor, triggering a signaling cascade that promotes glucose uptake.",
            "Amyloid-beta proteins aggregate to form plaques in Alzheimer's disease."
        ],
        BiologicalScale.CELLULAR: [
            "Mitochondria produce ATP through oxidative phosphorylation.",
            "T cells recognize antigens presented by dendritic cells and become activated."
        ],
        BiologicalScale.TISSUE: [
            "Epithelial tissue forms a protective barrier against pathogens and environmental damage.",
            "Fibroblasts secrete collagen and elastin to maintain the extracellular matrix in connective tissue."
        ],
        BiologicalScale.ORGAN: [
            "The liver detoxifies harmful substances and produces bile for fat digestion.",
            "The hippocampus plays a crucial role in forming new memories and spatial navigation."
        ],
        BiologicalScale.SYSTEM: [
            "The immune system distinguishes between self and non-self to protect against pathogens.",
            "The endocrine system regulates metabolism, growth, and development through hormone signaling."
        ],
        BiologicalScale.ORGANISM: [
            "Patients with type 2 diabetes often develop insulin resistance and hyperglycemia.",
            "Sleep deprivation impairs cognitive function and immune response in humans."
        ],
        BiologicalScale.POPULATION: [
            "The prevalence of obesity has increased by 30% in urban populations over the past decade.",
            "Vaccination programs have reduced the incidence of measles by 80% in developing countries."
        ],
        BiologicalScale.ECOSYSTEM: [
            "Climate change alters the geographic distribution of disease vectors like mosquitoes.",
            "Microplastic pollution affects marine ecosystems by entering the food chain."
        ]
    }
    
    # Classify one example from each scale
    print("Classifying statements across different biological scales:")
    
    for scale, examples in scale_examples.items():
        print(f"\n--- {scale.value.upper()} SCALE EXAMPLE ---")
        
        # Create statement DTO
        statement = create_statement_dto(examples[0])
        
        # Classify the statement
        start_time = time.time()
        result = classifier.classify_statement(statement)
        elapsed_time = time.time() - start_time
        
        # Print the result
        print(f"Expected scale: {scale.value}")
        print(f"Classification time: {elapsed_time:.2f} seconds")
        print_classification_result(result)


def demo_statement_types():
    """Demonstrate classification of different statement types."""
    print_header("2. Statement Type Classification Demonstration")
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example statements for different statement types
    type_examples = {
        StatementType.CAUSAL: 
            "Chronic inflammation causes tissue damage and promotes tumor development.",
        
        StatementType.CORRELATIONAL: 
            "Higher vitamin D levels are associated with lower risk of respiratory infections.",
        
        StatementType.DESCRIPTIVE: 
            "The human brain contains approximately 86 billion neurons and an equal number of non-neuronal cells.",
        
        StatementType.DEFINITIONAL: 
            "Apoptosis is defined as programmed cell death that occurs in multicellular organisms.",
        
        StatementType.METHODOLOGICAL: 
            "Gene expression was measured using RNA sequencing with a minimum read depth of 30 million reads per sample.",
        
        StatementType.COMPARATIVE: 
            "Patients treated with the new drug showed 40% greater reduction in tumor size compared to the standard treatment.",
        
        StatementType.INTERVENTION: 
            "Administration of metformin reduced blood glucose levels and improved insulin sensitivity in diabetic patients.",
        
        StatementType.PREDICTIVE: 
            "The machine learning model predicts patient response to immunotherapy with 85% accuracy based on tumor mutational burden.",
        
        StatementType.HYPOTHESIS: 
            "We hypothesize that gut microbiome composition may influence the efficacy of cancer immunotherapy.",
        
        StatementType.REVIEW: 
            "Recent advances in CRISPR technology have expanded its applications in gene therapy, diagnostics, and synthetic biology."
    }
    
    # Classify each statement type
    print("Classifying statements of different types:")
    
    for stmt_type, example in type_examples.items():
        print(f"\n--- {stmt_type.value.upper()} STATEMENT EXAMPLE ---")
        
        # Create statement DTO
        statement = create_statement_dto(example)
        
        # Classify the statement
        result = classifier.classify_statement(statement)
        
        # Print the result
        print(f"Expected type: {stmt_type.value}")
        print_classification_result(result)


def demo_batch_processing():
    """Demonstrate batch processing of multiple statements."""
    print_header("3. Batch Classification Demonstration")
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example statements from a scientific abstract about Alzheimer's disease
    abstract_statements = [
        "Alzheimer's disease (AD) is characterized by the accumulation of amyloid-beta plaques and neurofibrillary tangles in the brain.",
        "The APOE4 gene variant is the strongest genetic risk factor for late-onset Alzheimer's disease.",
        "Amyloid-beta peptides aggregate to form oligomers that disrupt synaptic function.",
        "Microglia, the brain's immune cells, play a dual role in AD by clearing amyloid deposits but also contributing to inflammation.",
        "In the hippocampus, neuronal loss correlates with cognitive decline in AD patients.",
        "The cholinergic system is severely affected in AD, leading to memory and attention deficits.",
        "Patients with Alzheimer's disease exhibit progressive memory loss and cognitive impairment.",
        "The prevalence of Alzheimer's disease doubles every 5 years after age 65 in the population.",
        "Environmental factors such as air pollution may increase the risk of neurodegenerative diseases including AD."
    ]
    
    # Create statement DTOs
    statements = [create_statement_dto(text, "alzheimer_abstract") for text in abstract_statements]
    
    # Classify statements in batch
    print("Classifying statements from an Alzheimer's disease abstract in batch:")
    
    start_time = time.time()
    results = classifier.batch_classify(statements)
    elapsed_time = time.time() - start_time
    
    # Print results
    print(f"Classified {len(results)} statements in {elapsed_time:.2f} seconds")
    print(f"Average time per statement: {elapsed_time/len(results):.2f} seconds")
    
    for result in results:
        print_classification_result(result, include_reasoning=False)
    
    # Analyze distribution of scales and types
    scale_counts = {}
    type_counts = {}
    
    for result in results:
        scale = result["biological_scale"]
        stmt_type = result["statement_type"]
        
        scale_counts[scale] = scale_counts.get(scale, 0) + 1
        type_counts[stmt_type] = type_counts.get(stmt_type, 0) + 1
    
    print("\nDistribution of Biological Scales:")
    for scale, count in scale_counts.items():
        print(f"  {scale}: {count} statements ({count/len(results)*100:.1f}%)")
    
    print("\nDistribution of Statement Types:")
    for stmt_type, count in type_counts.items():
        print(f"  {stmt_type}: {count} statements ({count/len(results)*100:.1f}%)")


def demo_validation():
    """Demonstrate validation of classification results."""
    print_header("4. Classification Validation Demonstration")
    
    # Create the classifier and validators
    classifier = PromptClassifier()
    rule_validator = RuleBasedValidator()
    
    # Example statements with potentially ambiguous classifications
    statements_text = [
        "The study measured cortisol levels in saliva samples from stressed individuals.",
        "Mice lacking the PTEN gene in neurons develop macrocephaly and behavioral abnormalities.",
        "The meta-analysis found no significant association between coffee consumption and cancer risk."
    ]
    
    # Create statement DTOs
    statements = [create_statement_dto(text) for text in statements_text]
    
    # Classify and validate each statement
    print("Validating classification results:")
    
    for statement in statements:
        print(f"\nStatement: {statement.text}")
        
        # Classify the statement
        result = classifier.classify_statement(statement)
        
        print("Classification Result:")
        print(f"Biological Scale: {result['biological_scale']} (Confidence: {result['scale_confidence']:.2f})")
        print(f"Statement Type: {result['statement_type']} (Confidence: {result['type_confidence']:.2f})")
        
        # Validate using rule-based validator
        is_valid = rule_validator.validate_classification(statement, result)
        print(f"Validation Result: {'Valid' if is_valid else 'Invalid'}")
        
        if not is_valid:
            improvements = rule_validator.suggest_improvements(statement, result)
            if improvements:
                if "corrected_scale" in improvements and improvements["corrected_scale"]:
                    print(f"Suggested Scale: {improvements['corrected_scale']}")
                if "corrected_type" in improvements and improvements["corrected_type"]:
                    print(f"Suggested Type: {improvements['corrected_type']}")
                if "feedback_text" in improvements:
                    print(f"Feedback: {improvements['feedback_text']}")
        
        print("-" * 80)


def demo_cross_scale_analysis():
    """Demonstrate analysis of statements that span multiple biological scales."""
    print_header("5. Cross-Scale Statement Analysis")
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example statements that span multiple biological scales
    cross_scale_statements = [
        "Mutations in the CFTR gene cause defective chloride channels in epithelial cells, leading to thick mucus production and recurrent lung infections in cystic fibrosis patients.",
        "Insulin resistance at the cellular level contributes to pancreatic beta-cell dysfunction, resulting in systemic glucose dysregulation and type 2 diabetes in obese individuals.",
        "The gut microbiome influences neurotransmitter production, affecting brain function and behavior, with implications for neuropsychiatric disorders across populations."
    ]
    
    # Create statement DTOs
    statements = [create_statement_dto(text) for text in cross_scale_statements]
    
    # Classify each statement
    print("Analyzing statements that span multiple biological scales:")
    
    for statement in statements:
        print(f"\nMulti-scale statement: {statement.text}")
        
        # Classify the statement
        result = classifier.classify_statement(statement)
        
        # Print the result
        print(f"Primary Scale: {result['biological_scale']} (Confidence: {result['scale_confidence']:.2f})")
        print(f"Statement Type: {result['statement_type']} (Confidence: {result['type_confidence']:.2f})")
        
        if "metadata" in result and "scale_reasoning" in result["metadata"]:
            print(f"\nScale Reasoning: {result['metadata']['scale_reasoning']}")
        
        # Identify the scales mentioned in the statement
        scales_mentioned = []
        for scale in BiologicalScale:
            if scale != BiologicalScale.UNKNOWN:
                keywords = [kw for kw in rule_validator.scale_keywords.get(scale, [])]
                matches = [kw for kw in keywords if kw.lower() in statement.text.lower()]
                if matches:
                    scales_mentioned.append((scale, matches))
        
        print("\nScales mentioned in the statement:")
        for scale, matches in scales_mentioned:
            print(f"  - {scale.value}: {', '.join(matches)}")
        
        print("-" * 80)


def demo_real_world_abstract():
    """Demonstrate classification of statements from a real scientific abstract."""
    print_header("6. Real Scientific Abstract Analysis")
    
    # Create the classifier
    classifier = PromptClassifier()
    
    # Example abstract from a real scientific paper (about COVID-19)
    abstract = """
    The COVID-19 pandemic caused by SARS-CoV-2 has resulted in a global health crisis. 
    The virus enters host cells through the interaction between its spike protein and the ACE2 receptor on human cells. 
    Within infected cells, SARS-CoV-2 replicates its RNA genome and produces viral proteins that assemble into new virions. 
    The infection triggers a robust immune response, including the production of cytokines that can lead to hyperinflammation in severe cases. 
    At the tissue level, COVID-19 primarily affects the respiratory epithelium, causing diffuse alveolar damage in the lungs. 
    The cardiovascular system is also impacted, with evidence of myocardial injury and thromboembolic complications. 
    Patients with severe COVID-19 often develop acute respiratory distress syndrome (ARDS) requiring mechanical ventilation. 
    Epidemiological studies have identified age, obesity, and pre-existing conditions as major risk factors for severe disease across populations. 
    Global vaccination efforts have significantly reduced mortality rates, though viral evolution continues to present challenges for pandemic control.
    """
    
    # Split the abstract into sentences
    import re
    sentences = re.split(r'(?<=[.!?])\s+', abstract.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Create statement DTOs
    statements = [create_statement_dto(text, "covid_abstract") for text in sentences]
    
    # Classify statements in batch
    print("Analyzing statements from a COVID-19 research abstract:")
    
    results = classifier.batch_classify(statements)
    
    # Organize results by biological scale
    scale_results = {}
    for result in results:
        scale = result["biological_scale"]
        if scale not in scale_results:
            scale_results[scale] = []
        scale_results[scale].append(result)
    
    # Print results organized by scale
    for scale in [s.value for s in BiologicalScale if s != BiologicalScale.UNKNOWN]:
        if scale in scale_results:
            print(f"\n--- {scale.upper()} SCALE STATEMENTS ---")
            for result in scale_results[scale]:
                print(f"• {result['statement_text']}")
                print(f"  Type: {result['statement_type']} (Confidence: {result['scale_confidence']:.2f})")
    
    # Create a summary of the abstract's biological scale distribution
    print("\nBiological Scale Distribution in the Abstract:")
    for scale, results_list in scale_results.items():
        percentage = len(results_list) / len(results) * 100
        print(f"  {scale}: {len(results_list)} statements ({percentage:.1f}%)")
    
    # Visualize the scale distribution (text-based)
    print("\nScale Distribution Visualization:")
    for scale, results_list in sorted(scale_results.items(), key=lambda x: len(x[1]), reverse=True):
        bar = "█" * len(results_list)
        print(f"  {scale.ljust(10)}: {bar} ({len(results_list)})")


if __name__ == "__main__":
    # Create rule validator for use in demos
    rule_validator = RuleBasedValidator()
    
    # Run demonstrations
    demo_scale_classification()
    demo_statement_types()
    demo_batch_processing()
    demo_validation()
    demo_cross_scale_analysis()
    demo_real_world_abstract()

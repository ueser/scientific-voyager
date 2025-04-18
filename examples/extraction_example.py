"""
Example script demonstrating the use of the abstract extraction pipeline.

This script shows how to use the extraction pipeline to process scientific abstracts
and extract structured information from them.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scientific_voyager.extraction.base_extractor import BaseExtractionPipeline
from scientific_voyager.extraction.llm_extractor import LLMExtractionPipeline
from scientific_voyager.literature.pubmed_adapter import PubMedAdapter


def print_extraction_result(result, indent=2):
    """Print the extraction result in a readable format."""
    print(f"Source text: {result['source_text'][:100]}...")
    
    print("\nEntities:")
    for entity in result['entities']:
        print(f"  - {entity['text']} (Type: {entity['type']}, Confidence: {entity['confidence']:.2f})")
        if entity.get('normalized_name'):
            print(f"    Normalized: {entity['normalized_name']} ({entity['normalized_id']})")
    
    print("\nRelations:")
    for relation in result['relations']:
        source = relation['source_entity']['text']
        target = relation['target_entity']['text']
        rel_type = relation['relation_type']
        confidence = relation['confidence']
        print(f"  - {source} {rel_type} {target} (Confidence: {confidence:.2f})")
    
    print("\nStatements:")
    for statement in result['statements']:
        print(f"  - Type: {statement['type']}")
        print(f"    Text: {statement['text']}")
        print(f"    Confidence: {statement['confidence']:.2f}")


def extract_from_pubmed(article_id, use_llm=False):
    """Extract information from a PubMed article."""
    # Initialize the PubMed adapter
    pubmed = PubMedAdapter()
    
    # Get the article abstract
    abstract = pubmed.get_article_abstract(article_id)
    if not abstract:
        print(f"No abstract found for article {article_id}")
        return
    
    # Get the article metadata
    article = pubmed.get_article_by_id(article_id)
    print(f"Processing article: {article['title']}")
    print(f"Authors: {', '.join(article['authors'])}")
    print(f"Journal: {article['journal']}")
    print(f"Publication date: {article['publication_date']}")
    print(f"Abstract length: {len(abstract)} characters")
    
    # Initialize the extraction pipeline
    if use_llm:
        print("\nUsing LLM-based extraction pipeline...")
        pipeline = LLMExtractionPipeline()
    else:
        print("\nUsing base extraction pipeline...")
        pipeline = BaseExtractionPipeline()
    
    # Process the abstract
    result = pipeline.process(abstract)
    
    # Print the results
    print("\nExtraction Results:")
    print_extraction_result(result)
    
    return result


def extract_from_text(text, use_llm=False):
    """Extract information from a text string."""
    print(f"Processing text: {text[:100]}...")
    
    # Initialize the extraction pipeline
    if use_llm:
        print("\nUsing LLM-based extraction pipeline...")
        pipeline = LLMExtractionPipeline()
    else:
        print("\nUsing base extraction pipeline...")
        pipeline = BaseExtractionPipeline()
    
    # Process the text
    result = pipeline.process(text)
    
    # Print the results
    print("\nExtraction Results:")
    print_extraction_result(result)
    
    return result


def main():
    """Main function to run the example."""
    # Example PubMed article IDs
    article_ids = [
        "34687244",  # PTEN and cancer
        "35617021",  # COVID-19 research
        "36149813",  # Neuroscience research
    ]
    
    # Example text for extraction
    example_text = """
    PTEN is a tumor suppressor gene that is frequently mutated in human cancers.
    Loss of PTEN function leads to increased activation of the PI3K/AKT signaling pathway,
    which promotes cell growth and survival. Studies have shown that PTEN regulates
    various cellular processes, including cell cycle progression, apoptosis, and metabolism.
    In breast cancer, PTEN mutations are associated with poor prognosis and resistance to therapy.
    Recent research has focused on developing strategies to restore PTEN function or
    target downstream effectors of the PI3K/AKT pathway in PTEN-deficient tumors.
    """
    
    # Process an example PubMed article
    print("=" * 80)
    print("Example 1: Extracting information from a PubMed article")
    print("=" * 80)
    extract_from_pubmed(article_ids[0])
    
    # Process example text
    print("\n" + "=" * 80)
    print("Example 2: Extracting information from example text")
    print("=" * 80)
    extract_from_text(example_text)
    
    # Uncomment to use LLM-based extraction (requires OpenAI API key)
    # print("\n" + "=" * 80)
    # print("Example 3: Using LLM-based extraction")
    # print("=" * 80)
    # extract_from_text(example_text, use_llm=True)


if __name__ == "__main__":
    main()

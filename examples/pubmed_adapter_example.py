"""
PubMed API Adapter Example

This example demonstrates how to use the PubMed API Adapter to search for
scientific literature and retrieve article metadata.
"""

import os
import sys
import logging
from pathlib import Path
from pprint import pprint

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scientific_voyager.literature.pubmed_adapter import PubMedAdapter
from scientific_voyager.config.config_manager import get_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def main():
    """Demonstrate PubMed API Adapter usage."""
    print("Scientific Voyager - PubMed API Adapter Example")
    print("=" * 50)
    
    # Initialize the PubMed adapter
    adapter = PubMedAdapter()
    
    # Example 1: Search for articles
    print("\nExample 1: Search for articles")
    print("-" * 30)
    
    search_query = "PTEN cancer signaling"
    max_results = 5
    
    print(f"Searching for: '{search_query}' (max_results={max_results})")
    try:
        articles = adapter.search_articles(search_query, max_results=max_results)
        
        print(f"Found {len(articles)} articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Authors: {', '.join(article['authors'][:3])}" + 
                  (f" et al." if len(article['authors']) > 3 else ""))
            print(f"   Journal: {article['journal']}")
            print(f"   Date: {article['publication_date']}")
            print(f"   PubMed ID: {article['article_id']}")
            
            # Print a snippet of the abstract
            abstract = article['abstract']
            if abstract:
                abstract_snippet = abstract[:150] + "..." if len(abstract) > 150 else abstract
                print(f"   Abstract: {abstract_snippet}")
    
    except Exception as e:
        print(f"Error searching for articles: {e}")
    
    # Example 2: Get article by ID
    print("\nExample 2: Get article by ID")
    print("-" * 30)
    
    # Use the first article ID from the search results, or a default one
    article_id = articles[0]['article_id'] if articles else "34162885"
    
    print(f"Fetching article with ID: {article_id}")
    try:
        article = adapter.get_article_by_id(article_id)
        
        print(f"Title: {article['title']}")
        print(f"Authors: {', '.join(article['authors'])}")
        print(f"Journal: {article['journal']}")
        print(f"Date: {article['publication_date']}")
        print(f"DOI: {article['doi']}")
        print(f"Keywords: {', '.join(article['keywords'])}")
        print(f"URL: {article['url']}")
        
        # Print the abstract
        if article['abstract']:
            print("\nAbstract:")
            print(article['abstract'])
    
    except Exception as e:
        print(f"Error fetching article: {e}")
    
    # Example 3: Get related articles
    print("\nExample 3: Get related articles")
    print("-" * 30)
    
    print(f"Finding articles related to ID: {article_id}")
    try:
        related_articles = adapter.get_related_articles(article_id, max_results=3)
        
        print(f"Found {len(related_articles)} related articles:")
        for i, related in enumerate(related_articles, 1):
            print(f"\n{i}. {related['title']}")
            print(f"   Authors: {', '.join(related['authors'][:3])}" + 
                  (f" et al." if len(related['authors']) > 3 else ""))
            print(f"   Journal: {related['journal']}")
            print(f"   Date: {related['publication_date']}")
            print(f"   PubMed ID: {related['article_id']}")
    
    except Exception as e:
        print(f"Error finding related articles: {e}")


if __name__ == "__main__":
    main()

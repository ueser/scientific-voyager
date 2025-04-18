"""
Example script demonstrating the enhanced PubMed adapter with caching and error handling.

This script shows how to use the enhanced PubMed adapter to search for articles,
fetch article metadata, and extract abstracts with caching and error handling.
"""

import os
import sys
import time
from pathlib import Path
import logging
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scientific_voyager.literature.enhanced_pubmed_adapter import PubMedAdapter
from scientific_voyager.utils.cache import get_cache_manager
from scientific_voyager.utils.error_handling import NetworkError, APIError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_article(article):
    """Print article metadata in a readable format."""
    print(f"Title: {article['title']}")
    print(f"PMID: {article['pmid']}")
    print(f"Journal: {article['journal']}")
    print(f"Publication Date: {article['pub_date']}")
    
    if article['authors']:
        print("Authors:")
        for author in article['authors']:
            print(f"  - {author}")
    
    if article['keywords']:
        print("Keywords:")
        for keyword in article['keywords']:
            print(f"  - {keyword}")
    
    if article['abstract']:
        print("\nAbstract:")
        print(article['abstract'][:300] + "..." if len(article['abstract']) > 300 else article['abstract'])
    
    print("\n" + "-" * 80 + "\n")


def example_search():
    """Example of searching for articles with caching."""
    print("=" * 80)
    print("Example 1: Searching for articles with caching")
    print("=" * 80)
    
    # Create the PubMed adapter
    adapter = PubMedAdapter()
    
    try:
        # First search - should hit the API
        print("First search (cache miss):")
        start_time = time.time()
        articles = adapter.search_articles("PTEN cancer", max_results=5)
        elapsed_time = time.time() - start_time
        
        print(f"Found {len(articles)} articles in {elapsed_time:.2f} seconds")
        if articles:
            print_article(articles[0])
        
        # Second search with the same query - should use cache
        print("Second search (cache hit):")
        start_time = time.time()
        articles = adapter.search_articles("PTEN cancer", max_results=5)
        elapsed_time = time.time() - start_time
        
        print(f"Found {len(articles)} articles in {elapsed_time:.2f} seconds (should be faster)")
        
        # Print cache statistics
        cache_manager = get_cache_manager()
        cache_stats = cache_manager.get_stats()
        print("\nCache Statistics:")
        print(f"Memory Cache: {cache_stats['memory']['total_items']} items ({cache_stats['memory']['valid_items']} valid)")
        print(f"Disk Cache: {cache_stats['disk']['total_items']} items ({cache_stats['disk']['valid_items']} valid)")
        
    except Exception as e:
        logger.error(f"Error in search example: {e}")


def example_error_handling():
    """Example of error handling with retries."""
    print("\n" + "=" * 80)
    print("Example 2: Error handling with retries")
    print("=" * 80)
    
    # Create the PubMed adapter
    adapter = PubMedAdapter()
    
    try:
        # Try to fetch a non-existent article ID
        print("Trying to fetch a non-existent article ID:")
        article = adapter.get_article_by_id("invalid_id")
        
    except ValueError as e:
        print(f"Caught ValueError: {e}")
        
    except KeyError as e:
        print(f"Caught KeyError: {e}")
        
    except NetworkError as e:
        print(f"Caught NetworkError: {e}")
        
    except APIError as e:
        print(f"Caught APIError: {e}")
        
    except Exception as e:
        print(f"Caught unexpected error: {e}")


def example_get_article_abstract():
    """Example of getting article abstracts with caching."""
    print("\n" + "=" * 80)
    print("Example 3: Getting article abstracts with caching")
    print("=" * 80)
    
    # Create the PubMed adapter
    adapter = PubMedAdapter()
    
    try:
        # Article IDs to fetch
        article_ids = ["34687244", "35617021", "36149813"]
        
        for article_id in article_ids:
            # First fetch - should hit the API
            print(f"First fetch for article {article_id} (cache miss):")
            start_time = time.time()
            abstract = adapter.get_article_abstract(article_id)
            elapsed_time = time.time() - start_time
            
            print(f"Fetched abstract in {elapsed_time:.2f} seconds")
            if abstract:
                print(f"Abstract length: {len(abstract)} characters")
                print(f"Preview: {abstract[:150]}...")
            else:
                print("No abstract available")
            
            # Second fetch - should use cache
            print(f"\nSecond fetch for article {article_id} (cache hit):")
            start_time = time.time()
            abstract = adapter.get_article_abstract(article_id)
            elapsed_time = time.time() - start_time
            
            print(f"Fetched abstract in {elapsed_time:.2f} seconds (should be faster)")
            print("\n" + "-" * 40 + "\n")
        
    except Exception as e:
        logger.error(f"Error in abstract example: {e}")


def example_related_articles():
    """Example of finding related articles with caching."""
    print("\n" + "=" * 80)
    print("Example 4: Finding related articles with caching")
    print("=" * 80)
    
    # Create the PubMed adapter
    adapter = PubMedAdapter()
    
    try:
        # Article ID to find related articles for
        article_id = "34687244"  # PTEN and cancer
        
        # First fetch - should hit the API
        print(f"First fetch for related articles to {article_id} (cache miss):")
        start_time = time.time()
        related_articles = adapter.get_related_articles(article_id, max_results=3)
        elapsed_time = time.time() - start_time
        
        print(f"Found {len(related_articles)} related articles in {elapsed_time:.2f} seconds")
        for i, article in enumerate(related_articles):
            print(f"\nRelated Article {i+1}:")
            print(f"Title: {article['title']}")
            print(f"PMID: {article['pmid']}")
        
        # Second fetch - should use cache
        print(f"\nSecond fetch for related articles to {article_id} (cache hit):")
        start_time = time.time()
        related_articles = adapter.get_related_articles(article_id, max_results=3)
        elapsed_time = time.time() - start_time
        
        print(f"Found {len(related_articles)} related articles in {elapsed_time:.2f} seconds (should be faster)")
        
    except Exception as e:
        logger.error(f"Error in related articles example: {e}")


def main():
    """Main function to run the examples."""
    # Uncomment the examples you want to run
    example_search()
    example_error_handling()
    example_get_article_abstract()
    example_related_articles()
    
    # Clean up cache at the end
    cache_manager = get_cache_manager()
    cleanup_stats = cache_manager.cleanup()
    print("\nCache Cleanup:")
    print(f"Removed {cleanup_stats['memory_removed']} memory items and {cleanup_stats['disk_removed']} disk items")


if __name__ == "__main__":
    main()

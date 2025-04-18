"""
Example script demonstrating the use of the literature extraction queue system.

This script shows how to use the queue system to process scientific literature
extraction jobs in batch mode.
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

from scientific_voyager.queue.literature_queue import LiteratureExtractionQueueManager
from scientific_voyager.interfaces.queue_interface import JobStatus, JobPriority


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def print_job_result(result):
    """Print the job result in a readable format."""
    if not result:
        print("No result available")
        return
    
    print(f"Source text: {result['source_text'][:100]}...")
    
    print("\nEntities:")
    for entity in result['entities']:
        print(f"  - {entity.text} (Type: {entity.type}, Confidence: {entity.confidence:.2f})")
        if entity.normalized_name:
            print(f"    Normalized: {entity.normalized_name} ({entity.normalized_id})")
    
    print("\nRelations:")
    for relation in result['relations']:
        source = relation.source_entity.text
        target = relation.target_entity.text
        rel_type = relation.relation_type
        confidence = relation.confidence
        print(f"  - {source} {rel_type} {target} (Confidence: {confidence:.2f})")
    
    print("\nStatements:")
    for statement in result['statements']:
        print(f"  - Type: {statement.type}")
        print(f"    Text: {statement.text}")
        print(f"    Confidence: {statement.confidence:.2f}")


def print_batch_status(batch_status):
    """Print the batch status in a readable format."""
    if not batch_status:
        print("No batch status available")
        return
    
    print(f"Batch status:")
    print(f"  - Total jobs: {len(batch_status.job_ids)}")
    print(f"  - Completed: {batch_status.completed}")
    print(f"  - Failed: {batch_status.failed}")
    print(f"  - Pending: {batch_status.pending}")
    print(f"  - Running: {batch_status.running}")
    print(f"  - Cancelled: {batch_status.cancelled}")
    
    if batch_status.errors:
        print("\nErrors:")
        for job_id, error in batch_status.errors.items():
            print(f"  - Job {job_id}: {error}")


def example_single_job():
    """Example of processing a single job."""
    print("=" * 80)
    print("Example 1: Processing a single job")
    print("=" * 80)
    
    # Create the queue manager
    manager = LiteratureExtractionQueueManager(num_threads=2)
    
    # Start the queue manager
    manager.start()
    
    try:
        # Submit a job to extract information from a PubMed article
        article_id = "34687244"  # PTEN and cancer
        print(f"Submitting article ID {article_id} for extraction...")
        job_id = manager.submit_article_id(article_id)
        
        # Wait for the job to complete
        print("Waiting for job to complete...")
        status = None
        while status != JobStatus.COMPLETED:
            status = manager.get_job_status(job_id)
            print(f"Job status: {status.value if status else 'Unknown'}")
            
            if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                break
                
            time.sleep(1)
        
        # Get the job result
        print("\nJob completed. Getting result...")
        result = manager.get_job_result(job_id)
        
        # Print the result
        print("\nExtraction result:")
        print_job_result(result)
        
    finally:
        # Stop the queue manager
        manager.stop()


def example_batch_processing():
    """Example of batch processing."""
    print("\n" + "=" * 80)
    print("Example 2: Batch processing")
    print("=" * 80)
    
    # Create the queue manager
    manager = LiteratureExtractionQueueManager(num_threads=4)
    
    # Start the queue manager
    manager.start()
    
    try:
        # Submit a batch of jobs to extract information from PubMed articles
        article_ids = [
            "34687244",  # PTEN and cancer
            "35617021",  # COVID-19 research
            "36149813",  # Neuroscience research
        ]
        print(f"Submitting batch of {len(article_ids)} article IDs for extraction...")
        batch_id = manager.submit_batch_article_ids(article_ids)
        
        # Wait for the batch to complete
        print("Waiting for batch to complete...")
        batch_status = manager.get_batch_status(batch_id)
        while batch_status.pending + batch_status.running > 0:
            batch_status = manager.get_batch_status(batch_id)
            print_batch_status(batch_status)
            
            if batch_status.pending + batch_status.running == 0:
                break
                
            time.sleep(2)
        
        # Print the final batch status
        print("\nBatch completed. Final status:")
        batch_status = manager.get_batch_status(batch_id)
        print_batch_status(batch_status)
        
        # Print the results for each completed job
        print("\nResults for completed jobs:")
        for job_id in batch_status.job_ids:
            result = manager.get_job_result(job_id)
            if result:
                print(f"\nResult for job {job_id}:")
                print_job_result(result)
        
    finally:
        # Stop the queue manager
        manager.stop()


def example_text_extraction():
    """Example of extracting information from text."""
    print("\n" + "=" * 80)
    print("Example 3: Text extraction")
    print("=" * 80)
    
    # Create the queue manager
    manager = LiteratureExtractionQueueManager(num_threads=2)
    
    # Start the queue manager
    manager.start()
    
    try:
        # Sample text for extraction
        text = """
        PTEN is a tumor suppressor gene that is frequently mutated in human cancers.
        Loss of PTEN function leads to increased activation of the PI3K/AKT signaling pathway,
        which promotes cell growth and survival. Studies have shown that PTEN regulates
        various cellular processes, including cell cycle progression, apoptosis, and metabolism.
        In breast cancer, PTEN mutations are associated with poor prognosis and resistance to therapy.
        Recent research has focused on developing strategies to restore PTEN function or
        target downstream effectors of the PI3K/AKT pathway in PTEN-deficient tumors.
        """
        
        print("Submitting text for extraction...")
        job_id = manager.submit_text(text)
        
        # Wait for the job to complete
        print("Waiting for job to complete...")
        status = None
        while status != JobStatus.COMPLETED:
            status = manager.get_job_status(job_id)
            print(f"Job status: {status.value if status else 'Unknown'}")
            
            if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                break
                
            time.sleep(1)
        
        # Get the job result
        print("\nJob completed. Getting result...")
        result = manager.get_job_result(job_id)
        
        # Print the result
        print("\nExtraction result:")
        print_job_result(result)
        
    finally:
        # Stop the queue manager
        manager.stop()


def example_queue_stats():
    """Example of getting queue statistics."""
    print("\n" + "=" * 80)
    print("Example 4: Queue statistics")
    print("=" * 80)
    
    # Create the queue manager
    manager = LiteratureExtractionQueueManager(num_threads=4)
    
    # Start the queue manager
    manager.start()
    
    try:
        # Submit some jobs
        print("Submitting jobs...")
        for i in range(5):
            text = f"Sample text {i} for extraction."
            manager.submit_text(text)
        
        # Wait a bit for some jobs to be processed
        print("Waiting for some jobs to be processed...")
        time.sleep(5)
        
        # Get queue statistics
        print("\nQueue statistics:")
        stats = manager.get_queue_stats()
        print(f"  - Total jobs: {stats.total_jobs}")
        print(f"  - Pending jobs: {stats.pending_jobs}")
        print(f"  - Running jobs: {stats.running_jobs}")
        print(f"  - Completed jobs: {stats.completed_jobs}")
        print(f"  - Failed jobs: {stats.failed_jobs}")
        print(f"  - Cancelled jobs: {stats.cancelled_jobs}")
        
        if stats.avg_processing_time:
            print(f"  - Average processing time: {stats.avg_processing_time:.2f} seconds")
        if stats.avg_wait_time:
            print(f"  - Average wait time: {stats.avg_wait_time:.2f} seconds")
        if stats.throughput:
            print(f"  - Throughput: {stats.throughput:.2f} jobs per minute")
        
    finally:
        # Stop the queue manager
        manager.stop()


def main():
    """Main function to run the examples."""
    # Uncomment the examples you want to run
    example_single_job()
    # example_batch_processing()
    # example_text_extraction()
    # example_queue_stats()


if __name__ == "__main__":
    main()

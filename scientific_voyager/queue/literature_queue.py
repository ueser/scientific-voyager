"""
Literature extraction queue manager.

This module provides a queue manager for processing scientific literature
extraction jobs using the queue system.
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import uuid
import json

from scientific_voyager.interfaces.queue_interface import (
    IQueue, IWorker, IJobFactory, JobStatus, JobPriority
)
from scientific_voyager.interfaces.queue_dto import (
    JobDTO, QueueStatsDTO, BatchJobResultDTO, LiteratureExtractionJobDTO
)
from scientific_voyager.queue.memory_queue import MemoryQueue, MemoryWorker, JobFactory
from scientific_voyager.interfaces.extraction_interface import IExtractionPipeline
from scientific_voyager.extraction.base_extractor import BaseExtractionPipeline
from scientific_voyager.extraction.llm_extractor import LLMExtractionPipeline
from scientific_voyager.literature.pubmed_adapter import PubMedAdapter
from scientific_voyager.config.config_manager import get_config

logger = logging.getLogger(__name__)


class LiteratureExtractionQueueManager:
    """
    Queue manager for processing scientific literature extraction jobs.
    
    This class provides a manager for processing scientific literature extraction jobs
    using the queue system. It handles job creation, submission, and monitoring.
    """
    
    def __init__(self, 
                 queue: Optional[IQueue] = None, 
                 worker: Optional[IWorker] = None,
                 job_factory: Optional[IJobFactory] = None,
                 extraction_pipeline: Optional[IExtractionPipeline] = None,
                 pubmed_adapter: Optional[PubMedAdapter] = None,
                 num_threads: int = 4,
                 use_llm: bool = False):
        """
        Initialize the literature extraction queue manager.
        
        Args:
            queue: The queue to use. If None, a MemoryQueue will be created.
            worker: The worker to use. If None, a MemoryWorker will be created.
            job_factory: The job factory to use. If None, a JobFactory will be created.
            extraction_pipeline: The extraction pipeline to use. If None, a pipeline will be created.
            pubmed_adapter: The PubMed adapter to use. If None, a PubMedAdapter will be created.
            num_threads: The number of worker threads to use.
            use_llm: Whether to use the LLM-based extraction pipeline.
        """
        self.config = get_config()
        self.queue = queue or MemoryQueue()
        self.job_factory = job_factory or JobFactory()
        self.pubmed_adapter = pubmed_adapter or PubMedAdapter()
        
        # Create extraction pipeline if not provided
        if extraction_pipeline is None:
            if use_llm:
                self.extraction_pipeline = LLMExtractionPipeline()
            else:
                self.extraction_pipeline = BaseExtractionPipeline()
        else:
            self.extraction_pipeline = extraction_pipeline
        
        # Create worker if not provided
        if worker is None:
            self.worker = MemoryWorker(
                queue=self.queue,
                job_processor=self._process_job,
                num_threads=num_threads
            )
        else:
            self.worker = worker
        
        # Batch job tracking
        self.batch_results: Dict[str, BatchJobResultDTO] = {}
        self.batch_lock = threading.RLock()
        
        logger.info("Initialized literature extraction queue manager")
    
    def start(self) -> None:
        """Start the queue manager."""
        self.worker.start()
        logger.info("Started literature extraction queue manager")
    
    def stop(self) -> None:
        """Stop the queue manager."""
        self.worker.stop()
        logger.info("Stopped literature extraction queue manager")
    
    def is_running(self) -> bool:
        """Check if the queue manager is running."""
        return self.worker.is_running()
    
    def submit_article_id(self, 
                          article_id: str, 
                          priority: JobPriority = JobPriority.NORMAL,
                          options: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a job to extract information from a PubMed article.
        
        Args:
            article_id: The PubMed article ID
            priority: The job priority
            options: Extraction options
            
        Returns:
            The job ID
        """
        # Create the job payload
        payload = {
            'article_id': article_id,
            'options': options or {}
        }
        
        # Create and enqueue the job
        job = self.job_factory.create_job(payload, priority)
        job_id = self.queue.enqueue(job)
        
        logger.info(f"Submitted article ID {article_id} for extraction (job ID: {job_id})")
        
        return job_id
    
    def submit_text(self, 
                    text: str, 
                    priority: JobPriority = JobPriority.NORMAL,
                    options: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a job to extract information from text.
        
        Args:
            text: The text to extract information from
            priority: The job priority
            options: Extraction options
            
        Returns:
            The job ID
        """
        # Create the job payload
        payload = {
            'text': text,
            'options': options or {}
        }
        
        # Create and enqueue the job
        job = self.job_factory.create_job(payload, priority)
        job_id = self.queue.enqueue(job)
        
        logger.info(f"Submitted text for extraction (job ID: {job_id})")
        
        return job_id
    
    def submit_batch_article_ids(self, 
                                 article_ids: List[str], 
                                 priority: JobPriority = JobPriority.NORMAL,
                                 options: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a batch of jobs to extract information from PubMed articles.
        
        Args:
            article_ids: The PubMed article IDs
            priority: The job priority
            options: Extraction options
            
        Returns:
            The batch ID
        """
        # Create job payloads
        payloads = [
            {'article_id': article_id, 'options': options or {}}
            for article_id in article_ids
        ]
        
        # Create and enqueue the jobs
        jobs = self.job_factory.create_batch_jobs(payloads, priority)
        job_ids = [self.queue.enqueue(job) for job in jobs]
        
        # Create a batch result
        batch_id = str(uuid.uuid4())
        batch_result = BatchJobResultDTO(
            job_ids=job_ids,
            pending=len(job_ids)
        )
        
        # Store the batch result
        with self.batch_lock:
            self.batch_results[batch_id] = batch_result
        
        logger.info(f"Submitted batch of {len(article_ids)} article IDs for extraction (batch ID: {batch_id})")
        
        return batch_id
    
    def submit_batch_texts(self, 
                           texts: List[str], 
                           priority: JobPriority = JobPriority.NORMAL,
                           options: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a batch of jobs to extract information from texts.
        
        Args:
            texts: The texts to extract information from
            priority: The job priority
            options: Extraction options
            
        Returns:
            The batch ID
        """
        # Create job payloads
        payloads = [
            {'text': text, 'options': options or {}}
            for text in texts
        ]
        
        # Create and enqueue the jobs
        jobs = self.job_factory.create_batch_jobs(payloads, priority)
        job_ids = [self.queue.enqueue(job) for job in jobs]
        
        # Create a batch result
        batch_id = str(uuid.uuid4())
        batch_result = BatchJobResultDTO(
            job_ids=job_ids,
            pending=len(job_ids)
        )
        
        # Store the batch result
        with self.batch_lock:
            self.batch_results[batch_id] = batch_result
        
        logger.info(f"Submitted batch of {len(texts)} texts for extraction (batch ID: {batch_id})")
        
        return batch_id
    
    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """
        Get the status of a job.
        
        Args:
            job_id: The job ID
            
        Returns:
            The job status, or None if the job is not found
        """
        job = self.queue.get_job(job_id)
        return job.status if job else None
    
    def get_job_result(self, job_id: str) -> Optional[Any]:
        """
        Get the result of a job.
        
        Args:
            job_id: The job ID
            
        Returns:
            The job result, or None if the job is not found or not completed
        """
        job = self.queue.get_job(job_id)
        if job and job.status == JobStatus.COMPLETED:
            return job.result
        return None
    
    def get_batch_status(self, batch_id: str) -> Optional[BatchJobResultDTO]:
        """
        Get the status of a batch.
        
        Args:
            batch_id: The batch ID
            
        Returns:
            The batch status, or None if the batch is not found
        """
        with self.batch_lock:
            if batch_id not in self.batch_results:
                return None
            
            batch_result = self.batch_results[batch_id]
            
            # Update the batch result from the jobs
            jobs = [self.queue.get_job(job_id) for job_id in batch_result.job_ids]
            jobs = [job for job in jobs if job]  # Filter out None values
            
            batch_result.update_from_jobs(jobs)
            
            return batch_result
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: The job ID
            
        Returns:
            True if the job was cancelled, False otherwise
        """
        job = self.queue.get_job(job_id)
        if not job:
            return False
        
        # Only pending jobs can be cancelled
        if job.status != JobStatus.PENDING:
            return False
        
        # Update job status
        job.update_status(JobStatus.CANCELLED)
        self.queue.update_job(job)
        
        logger.info(f"Cancelled job {job_id}")
        
        return True
    
    def cancel_batch(self, batch_id: str) -> bool:
        """
        Cancel a batch.
        
        Args:
            batch_id: The batch ID
            
        Returns:
            True if the batch was cancelled, False otherwise
        """
        with self.batch_lock:
            if batch_id not in self.batch_results:
                return False
            
            batch_result = self.batch_results[batch_id]
            
            # Cancel all pending jobs in the batch
            cancelled = False
            for job_id in batch_result.job_ids:
                if self.cancel_job(job_id):
                    cancelled = True
            
            logger.info(f"Cancelled batch {batch_id}")
            
            return cancelled
    
    def get_queue_stats(self) -> QueueStatsDTO:
        """
        Get queue statistics.
        
        Returns:
            Queue statistics
        """
        return self.queue.get_stats()
    
    def _process_job(self, job: JobDTO) -> None:
        """
        Process a job.
        
        Args:
            job: The job to process
        """
        if not isinstance(job, LiteratureExtractionJobDTO):
            raise ValueError(f"Expected LiteratureExtractionJobDTO, got {type(job)}")
        
        # Get the text to process
        text = None
        if job.article_id:
            # Get the article abstract from PubMed
            text = self.pubmed_adapter.get_article_abstract(job.article_id)
            if not text:
                raise ValueError(f"No abstract found for article ID {job.article_id}")
        elif job.text:
            # Use the provided text
            text = job.text
        else:
            raise ValueError("Job must have either article_id or text")
        
        # Process the text
        result = self.extraction_pipeline.process(text)
        
        # Set the job result
        job.set_extraction_result(result)
        
        logger.info(f"Processed extraction job {job.job_id}")

"""
In-memory implementation of the queue system.

This module provides an in-memory implementation of the queue system for
batch processing scientific literature.
"""

import logging
import threading
import time
import heapq
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from datetime import datetime
import uuid
from queue import PriorityQueue, Empty
from concurrent.futures import ThreadPoolExecutor
import json

from scientific_voyager.interfaces.queue_interface import (
    IQueue, IWorker, IJob, IJobFactory, JobStatus, JobPriority
)
from scientific_voyager.interfaces.queue_dto import (
    JobDTO, QueueStatsDTO, BatchJobResultDTO, LiteratureExtractionJobDTO
)

logger = logging.getLogger(__name__)


class MemoryQueue(IQueue):
    """
    In-memory implementation of the queue interface.
    
    This class provides a simple in-memory queue implementation using a priority queue.
    It is suitable for development and testing, but not for production use as it
    does not persist jobs across application restarts.
    """
    
    def __init__(self):
        """Initialize the memory queue."""
        self.queue = PriorityQueue()
        self.jobs: Dict[str, JobDTO] = {}
        self.lock = threading.RLock()
        self.stats = QueueStatsDTO()
        self.last_job_time = datetime.now()
        self.processing_times: List[float] = []
        self.wait_times: List[float] = []
    
    def enqueue(self, job: JobDTO) -> str:
        """
        Add a job to the queue.
        
        Args:
            job: The job to add to the queue
            
        Returns:
            The job ID
        """
        with self.lock:
            # Store the job
            self.jobs[job.job_id] = job
            
            # Add the job to the priority queue
            # We use a tuple with (priority, created_at, job_id) to ensure stable sorting
            priority_tuple = (
                -job.priority.value,  # Negate priority so higher values have higher priority
                job.created_at.timestamp(),
                job.job_id
            )
            self.queue.put((priority_tuple, job.job_id))
            
            # Update stats
            self._update_stats()
            
            logger.info(f"Enqueued job {job.job_id} with priority {job.priority.name}")
            
            return job.job_id
    
    def dequeue(self) -> Optional[JobDTO]:
        """
        Get the next job from the queue.
        
        Returns:
            The next job, or None if the queue is empty
        """
        with self.lock:
            try:
                # Get the next job from the priority queue
                _, job_id = self.queue.get(block=False)
                job = self.jobs[job_id]
                
                # Update job status
                job.update_status(JobStatus.RUNNING)
                
                # Update stats
                self._update_stats()
                
                # Calculate wait time
                if job.started_at and job.created_at:
                    wait_time = (job.started_at - job.created_at).total_seconds()
                    self.wait_times.append(wait_time)
                
                logger.info(f"Dequeued job {job.job_id}")
                
                return job
            except Empty:
                return None
    
    def get_job(self, job_id: str) -> Optional[JobDTO]:
        """
        Get a job by its ID.
        
        Args:
            job_id: The job ID
            
        Returns:
            The job, or None if not found
        """
        with self.lock:
            return self.jobs.get(job_id)
    
    def update_job(self, job: JobDTO) -> bool:
        """
        Update a job in the queue.
        
        Args:
            job: The job to update
            
        Returns:
            True if the job was updated, False otherwise
        """
        with self.lock:
            if job.job_id not in self.jobs:
                return False
            
            # Update the job
            self.jobs[job.job_id] = job
            
            # Calculate processing time for completed jobs
            if job.status == JobStatus.COMPLETED and job.started_at and job.completed_at:
                processing_time = (job.completed_at - job.started_at).total_seconds()
                self.processing_times.append(processing_time)
                self.last_job_time = datetime.now()
            
            # Update stats
            self._update_stats()
            
            logger.info(f"Updated job {job.job_id} with status {job.status.name}")
            
            return True
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a job from the queue.
        
        Args:
            job_id: The job ID
            
        Returns:
            True if the job was removed, False otherwise
        """
        with self.lock:
            if job_id not in self.jobs:
                return False
            
            # Remove the job from the jobs dictionary
            del self.jobs[job_id]
            
            # Note: We can't easily remove the job from the priority queue,
            # so we'll just ignore it when it comes up in dequeue
            
            # Update stats
            self._update_stats()
            
            logger.info(f"Removed job {job_id}")
            
            return True
    
    def get_jobs_by_status(self, status: JobStatus) -> List[JobDTO]:
        """
        Get all jobs with the specified status.
        
        Args:
            status: The job status
            
        Returns:
            A list of jobs with the specified status
        """
        with self.lock:
            return [job for job in self.jobs.values() if job.status == status]
    
    def get_queue_length(self) -> int:
        """
        Get the number of jobs in the queue.
        
        Returns:
            The number of jobs in the queue
        """
        with self.lock:
            return self.queue.qsize()
    
    def clear(self) -> None:
        """Clear the queue."""
        with self.lock:
            self.queue = PriorityQueue()
            self.jobs.clear()
            self.stats = QueueStatsDTO()
            self.processing_times.clear()
            self.wait_times.clear()
            logger.info("Queue cleared")
    
    def get_stats(self) -> QueueStatsDTO:
        """
        Get queue statistics.
        
        Returns:
            Queue statistics
        """
        with self.lock:
            return self.stats
    
    def _update_stats(self) -> None:
        """Update queue statistics."""
        self.stats.total_jobs = len(self.jobs)
        self.stats.pending_jobs = len(self.get_jobs_by_status(JobStatus.PENDING))
        self.stats.running_jobs = len(self.get_jobs_by_status(JobStatus.RUNNING))
        self.stats.completed_jobs = len(self.get_jobs_by_status(JobStatus.COMPLETED))
        self.stats.failed_jobs = len(self.get_jobs_by_status(JobStatus.FAILED))
        self.stats.cancelled_jobs = len(self.get_jobs_by_status(JobStatus.CANCELLED))
        
        # Calculate average processing time
        if self.processing_times:
            self.stats.avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        # Calculate average wait time
        if self.wait_times:
            self.stats.avg_wait_time = sum(self.wait_times) / len(self.wait_times)
        
        # Calculate throughput (jobs per minute)
        time_diff = (datetime.now() - self.last_job_time).total_seconds()
        if time_diff > 0 and self.stats.completed_jobs > 0:
            self.stats.throughput = self.stats.completed_jobs / (time_diff / 60)


class MemoryWorker(IWorker):
    """
    In-memory implementation of the worker interface.
    
    This class provides a simple in-memory worker implementation using a thread pool.
    It processes jobs from a queue and executes them using the provided job processor.
    """
    
    def __init__(self, queue: IQueue, job_processor: Callable[[JobDTO], None], num_threads: int = 4):
        """
        Initialize the memory worker.
        
        Args:
            queue: The queue to process jobs from
            job_processor: A function that processes a job
            num_threads: The number of worker threads to use
        """
        self.queue = queue
        self.job_processor = job_processor
        self.num_threads = num_threads
        self.running = False
        self.threads: List[threading.Thread] = []
        self.executor = ThreadPoolExecutor(max_workers=num_threads)
        self.stop_event = threading.Event()
    
    def start(self) -> None:
        """Start the worker."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Start worker threads
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker_loop)
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
        logger.info(f"Started worker with {self.num_threads} threads")
    
    def stop(self) -> None:
        """Stop the worker."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=1.0)
        
        self.threads.clear()
        logger.info("Stopped worker")
    
    def is_running(self) -> bool:
        """Check if the worker is running."""
        return self.running
    
    def process_job(self, job: JobDTO) -> None:
        """
        Process a job.
        
        Args:
            job: The job to process
        """
        try:
            # Process the job
            self.job_processor(job)
            
            # Update job status if not already done by the processor
            if job.status == JobStatus.RUNNING:
                job.update_status(JobStatus.COMPLETED)
            
            # Update the job in the queue
            self.queue.update_job(job)
            
            logger.info(f"Processed job {job.job_id}")
        except Exception as e:
            # Update job status and error
            job.error = str(e)
            job.update_status(JobStatus.FAILED)
            
            # Update the job in the queue
            self.queue.update_job(job)
            
            logger.error(f"Error processing job {job.job_id}: {str(e)}")
    
    def _worker_loop(self) -> None:
        """Worker thread loop that processes jobs from the queue."""
        while self.running and not self.stop_event.is_set():
            try:
                # Get the next job from the queue
                job = self.queue.dequeue()
                
                if job:
                    # Process the job
                    self.process_job(job)
                else:
                    # No jobs available, sleep for a bit
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")
                time.sleep(1.0)  # Sleep to avoid tight loop on error


class JobFactory(IJobFactory):
    """
    Implementation of the job factory interface.
    
    This class provides a factory for creating jobs of different types.
    """
    
    def create_job(self, payload: Dict[str, Any], priority: JobPriority = JobPriority.NORMAL) -> JobDTO:
        """
        Create a new job.
        
        Args:
            payload: The job payload
            priority: The job priority
            
        Returns:
            A new job
        """
        # Determine the job type based on the payload
        if 'article_id' in payload or 'text' in payload:
            return LiteratureExtractionJobDTO(payload=payload, priority=priority)
        else:
            return JobDTO(payload=payload, priority=priority)
    
    def create_batch_jobs(self, payloads: List[Dict[str, Any]], priority: JobPriority = JobPriority.NORMAL) -> List[JobDTO]:
        """
        Create multiple jobs.
        
        Args:
            payloads: A list of job payloads
            priority: The job priority
            
        Returns:
            A list of new jobs
        """
        return [self.create_job(payload, priority) for payload in payloads]

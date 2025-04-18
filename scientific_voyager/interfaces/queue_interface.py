"""
Interfaces for the queue system.

This module defines the interfaces for the queue system that handles batch processing
of scientific literature.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import uuid


class JobStatus(str, Enum):
    """Enum for job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    """Enum for job priority."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class IJob(ABC):
    """Interface for a job in the queue system."""
    
    @property
    @abstractmethod
    def job_id(self) -> str:
        """Get the job ID."""
        pass
    
    @property
    @abstractmethod
    def status(self) -> JobStatus:
        """Get the job status."""
        pass
    
    @status.setter
    @abstractmethod
    def status(self, value: JobStatus):
        """Set the job status."""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> JobPriority:
        """Get the job priority."""
        pass
    
    @property
    @abstractmethod
    def payload(self) -> Dict[str, Any]:
        """Get the job payload."""
        pass
    
    @property
    @abstractmethod
    def result(self) -> Optional[Any]:
        """Get the job result."""
        pass
    
    @result.setter
    @abstractmethod
    def result(self, value: Any):
        """Set the job result."""
        pass
    
    @property
    @abstractmethod
    def error(self) -> Optional[str]:
        """Get the job error."""
        pass
    
    @error.setter
    @abstractmethod
    def error(self, value: str):
        """Set the job error."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the job to a dictionary."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IJob':
        """Create a job from a dictionary."""
        pass


class IQueue(ABC):
    """Interface for the queue system."""
    
    @abstractmethod
    def enqueue(self, job: IJob) -> str:
        """
        Add a job to the queue.
        
        Args:
            job: The job to add to the queue
            
        Returns:
            The job ID
        """
        pass
    
    @abstractmethod
    def dequeue(self) -> Optional[IJob]:
        """
        Get the next job from the queue.
        
        Returns:
            The next job, or None if the queue is empty
        """
        pass
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional[IJob]:
        """
        Get a job by its ID.
        
        Args:
            job_id: The job ID
            
        Returns:
            The job, or None if not found
        """
        pass
    
    @abstractmethod
    def update_job(self, job: IJob) -> bool:
        """
        Update a job in the queue.
        
        Args:
            job: The job to update
            
        Returns:
            True if the job was updated, False otherwise
        """
        pass
    
    @abstractmethod
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a job from the queue.
        
        Args:
            job_id: The job ID
            
        Returns:
            True if the job was removed, False otherwise
        """
        pass
    
    @abstractmethod
    def get_jobs_by_status(self, status: JobStatus) -> List[IJob]:
        """
        Get all jobs with the specified status.
        
        Args:
            status: The job status
            
        Returns:
            A list of jobs with the specified status
        """
        pass
    
    @abstractmethod
    def get_queue_length(self) -> int:
        """
        Get the number of jobs in the queue.
        
        Returns:
            The number of jobs in the queue
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the queue."""
        pass


class IWorker(ABC):
    """Interface for a worker that processes jobs from the queue."""
    
    @abstractmethod
    def start(self) -> None:
        """Start the worker."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the worker."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if the worker is running."""
        pass
    
    @abstractmethod
    def process_job(self, job: IJob) -> None:
        """
        Process a job.
        
        Args:
            job: The job to process
        """
        pass


class IJobFactory(ABC):
    """Interface for a factory that creates jobs."""
    
    @abstractmethod
    def create_job(self, payload: Dict[str, Any], priority: JobPriority = JobPriority.NORMAL) -> IJob:
        """
        Create a new job.
        
        Args:
            payload: The job payload
            priority: The job priority
            
        Returns:
            A new job
        """
        pass
    
    @abstractmethod
    def create_batch_jobs(self, payloads: List[Dict[str, Any]], priority: JobPriority = JobPriority.NORMAL) -> List[IJob]:
        """
        Create multiple jobs.
        
        Args:
            payloads: A list of job payloads
            priority: The job priority
            
        Returns:
            A list of new jobs
        """
        pass

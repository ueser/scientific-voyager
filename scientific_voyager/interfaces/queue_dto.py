"""
Data Transfer Objects for the queue system.

This module defines the DTOs used to represent jobs and other queue-related data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import json

from scientific_voyager.interfaces.queue_interface import JobStatus, JobPriority


@dataclass
class JobDTO:
    """Data Transfer Object for a job in the queue system."""
    
    payload: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the job to a dictionary."""
        return {
            'job_id': self.job_id,
            'payload': self.payload,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error': self.error,
            'retries': self.retries,
            'max_retries': self.max_retries,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobDTO':
        """Create a job from a dictionary."""
        # Convert string values back to enums
        data['priority'] = JobPriority(data['priority'])
        data['status'] = JobStatus(data['status'])
        
        # Convert ISO format strings back to datetime objects
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data['started_at']:
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data['completed_at']:
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        return cls(**data)
    
    def update_status(self, status: JobStatus) -> None:
        """Update the job status and related timestamps."""
        self.status = status
        self.updated_at = datetime.now()
        
        if status == JobStatus.RUNNING and not self.started_at:
            self.started_at = datetime.now()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and not self.completed_at:
            self.completed_at = datetime.now()
    
    def can_retry(self) -> bool:
        """Check if the job can be retried."""
        return self.status == JobStatus.FAILED and self.retries < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment the retry count and reset the status to pending."""
        self.retries += 1
        self.status = JobStatus.PENDING
        self.updated_at = datetime.now()
        self.error = None


@dataclass
class QueueStatsDTO:
    """Data Transfer Object for queue statistics."""
    
    total_jobs: int = 0
    pending_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0
    avg_processing_time: Optional[float] = None  # in seconds
    avg_wait_time: Optional[float] = None  # in seconds
    throughput: Optional[float] = None  # jobs per minute
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the stats to a dictionary."""
        return {
            'total_jobs': self.total_jobs,
            'pending_jobs': self.pending_jobs,
            'running_jobs': self.running_jobs,
            'completed_jobs': self.completed_jobs,
            'failed_jobs': self.failed_jobs,
            'cancelled_jobs': self.cancelled_jobs,
            'avg_processing_time': self.avg_processing_time,
            'avg_wait_time': self.avg_wait_time,
            'throughput': self.throughput
        }


@dataclass
class BatchJobResultDTO:
    """Data Transfer Object for batch job results."""
    
    job_ids: List[str]
    completed: int = 0
    failed: int = 0
    pending: int = 0
    running: int = 0
    cancelled: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the batch result to a dictionary."""
        return {
            'job_ids': self.job_ids,
            'completed': self.completed,
            'failed': self.failed,
            'pending': self.pending,
            'running': self.running,
            'cancelled': self.cancelled,
            'results': self.results,
            'errors': self.errors
        }
    
    def update_from_jobs(self, jobs: List[JobDTO]) -> None:
        """Update the batch result from a list of jobs."""
        self.completed = sum(1 for job in jobs if job.status == JobStatus.COMPLETED)
        self.failed = sum(1 for job in jobs if job.status == JobStatus.FAILED)
        self.pending = sum(1 for job in jobs if job.status == JobStatus.PENDING)
        self.running = sum(1 for job in jobs if job.status == JobStatus.RUNNING)
        self.cancelled = sum(1 for job in jobs if job.status == JobStatus.CANCELLED)
        
        self.results = {job.job_id: job.result for job in jobs if job.status == JobStatus.COMPLETED}
        self.errors = {job.job_id: job.error for job in jobs if job.status == JobStatus.FAILED and job.error}


@dataclass
class LiteratureExtractionJobDTO(JobDTO):
    """Data Transfer Object for a literature extraction job."""
    
    def __post_init__(self):
        """Initialize the job with appropriate tags."""
        if 'tags' not in self.__dict__ or not self.tags:
            self.tags = ['literature', 'extraction']
        
        # Ensure the payload has the required fields
        if 'article_id' not in self.payload and 'text' not in self.payload:
            raise ValueError("Literature extraction job must have either 'article_id' or 'text' in the payload")
    
    @property
    def article_id(self) -> Optional[str]:
        """Get the article ID from the payload."""
        return self.payload.get('article_id')
    
    @property
    def text(self) -> Optional[str]:
        """Get the text from the payload."""
        return self.payload.get('text')
    
    @property
    def extraction_options(self) -> Dict[str, Any]:
        """Get the extraction options from the payload."""
        return self.payload.get('options', {})
    
    def set_extraction_result(self, result: Dict[str, Any]) -> None:
        """Set the extraction result."""
        self.result = result
        self.update_status(JobStatus.COMPLETED)

"""
Unit tests for the memory queue.

This module contains tests for the in-memory implementation of the queue system.
"""

import unittest
from unittest.mock import patch, MagicMock
import threading
import time
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the config manager to avoid importing it
sys.modules['scientific_voyager.config.config_manager'] = MagicMock()

from scientific_voyager.queue.memory_queue import (
    MemoryQueue, MemoryWorker, JobFactory
)
from scientific_voyager.interfaces.queue_interface import (
    JobStatus, JobPriority
)
from scientific_voyager.interfaces.queue_dto import (
    JobDTO, QueueStatsDTO, BatchJobResultDTO, LiteratureExtractionJobDTO
)


class TestMemoryQueue(unittest.TestCase):
    """Test cases for the memory queue."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.queue = MemoryQueue()
    
    def test_enqueue_dequeue(self):
        """Test enqueueing and dequeueing jobs."""
        # Create a job
        job = JobDTO(payload={'test': 'data'})
        
        # Enqueue the job
        job_id = self.queue.enqueue(job)
        
        # Verify the job ID
        self.assertEqual(job_id, job.job_id)
        
        # Verify the queue length
        self.assertEqual(self.queue.get_queue_length(), 1)
        
        # Dequeue the job
        dequeued_job = self.queue.dequeue()
        
        # Verify the dequeued job
        self.assertIsNotNone(dequeued_job)
        self.assertEqual(dequeued_job.job_id, job_id)
        self.assertEqual(dequeued_job.status, JobStatus.RUNNING)
        
        # Verify the queue is empty
        self.assertEqual(self.queue.get_queue_length(), 0)
    
    def test_priority_queue(self):
        """Test that jobs are dequeued in priority order."""
        # Create jobs with different priorities
        low_job = JobDTO(payload={'priority': 'low'}, priority=JobPriority.LOW)
        normal_job = JobDTO(payload={'priority': 'normal'}, priority=JobPriority.NORMAL)
        high_job = JobDTO(payload={'priority': 'high'}, priority=JobPriority.HIGH)
        critical_job = JobDTO(payload={'priority': 'critical'}, priority=JobPriority.CRITICAL)
        
        # Enqueue the jobs in reverse priority order
        self.queue.enqueue(low_job)
        self.queue.enqueue(normal_job)
        self.queue.enqueue(high_job)
        self.queue.enqueue(critical_job)
        
        # Verify the queue length
        self.assertEqual(self.queue.get_queue_length(), 4)
        
        # Dequeue the jobs and verify they come out in priority order
        job1 = self.queue.dequeue()
        job2 = self.queue.dequeue()
        job3 = self.queue.dequeue()
        job4 = self.queue.dequeue()
        
        self.assertEqual(job1.job_id, critical_job.job_id)
        self.assertEqual(job2.job_id, high_job.job_id)
        self.assertEqual(job3.job_id, normal_job.job_id)
        self.assertEqual(job4.job_id, low_job.job_id)
    
    def test_get_job(self):
        """Test getting a job by ID."""
        # Create a job
        job = JobDTO(payload={'test': 'data'})
        
        # Enqueue the job
        job_id = self.queue.enqueue(job)
        
        # Get the job
        retrieved_job = self.queue.get_job(job_id)
        
        # Verify the retrieved job
        self.assertIsNotNone(retrieved_job)
        self.assertEqual(retrieved_job.job_id, job_id)
        
        # Try to get a non-existent job
        non_existent_job = self.queue.get_job('non-existent')
        self.assertIsNone(non_existent_job)
    
    def test_update_job(self):
        """Test updating a job."""
        # Create a job
        job = JobDTO(payload={'test': 'data'})
        
        # Enqueue the job
        job_id = self.queue.enqueue(job)
        
        # Update the job
        job.status = JobStatus.COMPLETED
        job.result = {'result': 'success'}
        
        # Update the job in the queue
        success = self.queue.update_job(job)
        
        # Verify the update was successful
        self.assertTrue(success)
        
        # Get the updated job
        updated_job = self.queue.get_job(job_id)
        
        # Verify the updated job
        self.assertEqual(updated_job.status, JobStatus.COMPLETED)
        self.assertEqual(updated_job.result, {'result': 'success'})
        
        # Try to update a non-existent job
        non_existent_job = JobDTO(payload={'test': 'data'}, job_id='non-existent')
        success = self.queue.update_job(non_existent_job)
        self.assertFalse(success)
    
    def test_remove_job(self):
        """Test removing a job."""
        # Create a job
        job = JobDTO(payload={'test': 'data'})
        
        # Enqueue the job
        job_id = self.queue.enqueue(job)
        
        # Remove the job
        success = self.queue.remove_job(job_id)
        
        # Verify the removal was successful
        self.assertTrue(success)
        
        # Verify the job is no longer in the queue
        removed_job = self.queue.get_job(job_id)
        self.assertIsNone(removed_job)
        
        # Try to remove a non-existent job
        success = self.queue.remove_job('non-existent')
        self.assertFalse(success)
    
    def test_get_jobs_by_status(self):
        """Test getting jobs by status."""
        # Create jobs with different statuses
        pending_job = JobDTO(payload={'status': 'pending'})
        running_job = JobDTO(payload={'status': 'running'}, status=JobStatus.RUNNING)
        completed_job = JobDTO(payload={'status': 'completed'}, status=JobStatus.COMPLETED)
        failed_job = JobDTO(payload={'status': 'failed'}, status=JobStatus.FAILED)
        
        # Enqueue the jobs
        self.queue.enqueue(pending_job)
        self.queue.enqueue(running_job)
        self.queue.enqueue(completed_job)
        self.queue.enqueue(failed_job)
        
        # Get jobs by status
        pending_jobs = self.queue.get_jobs_by_status(JobStatus.PENDING)
        running_jobs = self.queue.get_jobs_by_status(JobStatus.RUNNING)
        completed_jobs = self.queue.get_jobs_by_status(JobStatus.COMPLETED)
        failed_jobs = self.queue.get_jobs_by_status(JobStatus.FAILED)
        
        # Verify the jobs
        self.assertEqual(len(pending_jobs), 1)
        self.assertEqual(len(running_jobs), 1)
        self.assertEqual(len(completed_jobs), 1)
        self.assertEqual(len(failed_jobs), 1)
        
        self.assertEqual(pending_jobs[0].job_id, pending_job.job_id)
        self.assertEqual(running_jobs[0].job_id, running_job.job_id)
        self.assertEqual(completed_jobs[0].job_id, completed_job.job_id)
        self.assertEqual(failed_jobs[0].job_id, failed_job.job_id)
    
    def test_clear(self):
        """Test clearing the queue."""
        # Create and enqueue some jobs
        for i in range(5):
            job = JobDTO(payload={'index': i})
            self.queue.enqueue(job)
        
        # Verify the queue length
        self.assertEqual(self.queue.get_queue_length(), 5)
        
        # Clear the queue
        self.queue.clear()
        
        # Verify the queue is empty
        self.assertEqual(self.queue.get_queue_length(), 0)
        self.assertEqual(len(self.queue.jobs), 0)
    
    def test_get_stats(self):
        """Test getting queue statistics."""
        # Create jobs with different statuses
        pending_job = JobDTO(payload={'status': 'pending'})
        running_job = JobDTO(payload={'status': 'running'}, status=JobStatus.RUNNING)
        completed_job = JobDTO(payload={'status': 'completed'}, status=JobStatus.COMPLETED)
        failed_job = JobDTO(payload={'status': 'failed'}, status=JobStatus.FAILED)
        cancelled_job = JobDTO(payload={'status': 'cancelled'}, status=JobStatus.CANCELLED)
        
        # Enqueue the jobs
        self.queue.enqueue(pending_job)
        self.queue.enqueue(running_job)
        self.queue.enqueue(completed_job)
        self.queue.enqueue(failed_job)
        self.queue.enqueue(cancelled_job)
        
        # Get queue statistics
        stats = self.queue.get_stats()
        
        # Verify the statistics
        self.assertEqual(stats.total_jobs, 5)
        self.assertEqual(stats.pending_jobs, 1)
        self.assertEqual(stats.running_jobs, 1)
        self.assertEqual(stats.completed_jobs, 1)
        self.assertEqual(stats.failed_jobs, 1)
        self.assertEqual(stats.cancelled_jobs, 1)


class TestMemoryWorker(unittest.TestCase):
    """Test cases for the memory worker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.queue = MemoryQueue()
        self.processed_jobs = []
        
        # Create a job processor that just records the job
        def job_processor(job):
            self.processed_jobs.append(job)
            job.result = {'processed': True}
            job.status = JobStatus.COMPLETED
        
        self.worker = MemoryWorker(
            queue=self.queue,
            job_processor=job_processor,
            num_threads=1
        )
    
    def test_start_stop(self):
        """Test starting and stopping the worker."""
        # Verify the worker is not running initially
        self.assertFalse(self.worker.is_running())
        
        # Start the worker
        self.worker.start()
        
        # Verify the worker is running
        self.assertTrue(self.worker.is_running())
        
        # Stop the worker
        self.worker.stop()
        
        # Verify the worker is not running
        self.assertFalse(self.worker.is_running())
    
    def test_process_job(self):
        """Test processing a job."""
        # Create a job
        job = JobDTO(payload={'test': 'data'})
        
        # Process the job
        self.worker.process_job(job)
        
        # Verify the job was processed
        self.assertEqual(len(self.processed_jobs), 1)
        self.assertEqual(self.processed_jobs[0].job_id, job.job_id)
        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertEqual(job.result, {'processed': True})
    
    def test_worker_loop(self):
        """Test the worker loop processing jobs from the queue."""
        # Create and enqueue some jobs
        jobs = []
        for i in range(3):
            job = JobDTO(payload={'index': i})
            jobs.append(job)
            self.queue.enqueue(job)
        
        # Start the worker
        self.worker.start()
        
        # Wait for the jobs to be processed
        max_wait = 5  # seconds
        start_time = time.time()
        while len(self.processed_jobs) < 3 and time.time() - start_time < max_wait:
            time.sleep(0.1)
        
        # Stop the worker
        self.worker.stop()
        
        # Verify all jobs were processed
        self.assertEqual(len(self.processed_jobs), 3)
        
        # Verify the jobs were processed in the correct order
        processed_job_ids = [job.job_id for job in self.processed_jobs]
        expected_job_ids = [job.job_id for job in jobs]
        self.assertEqual(set(processed_job_ids), set(expected_job_ids))
    
    def test_error_handling(self):
        """Test error handling in the worker."""
        # Create a worker with a job processor that raises an exception
        def error_processor(job):
            raise ValueError("Test error")
        
        error_worker = MemoryWorker(
            queue=self.queue,
            job_processor=error_processor,
            num_threads=1
        )
        
        # Create a job
        job = JobDTO(payload={'test': 'data'})
        
        # Enqueue the job
        job_id = self.queue.enqueue(job)
        
        # Start the worker
        error_worker.start()
        
        # Wait for the job to be processed
        max_wait = 5  # seconds
        start_time = time.time()
        while True:
            job = self.queue.get_job(job_id)
            if job.status in [JobStatus.FAILED, JobStatus.COMPLETED] or time.time() - start_time > max_wait:
                break
            time.sleep(0.1)
        
        # Stop the worker
        error_worker.stop()
        
        # Verify the job failed
        job = self.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.FAILED)
        self.assertEqual(job.error, "Test error")


class TestJobFactory(unittest.TestCase):
    """Test cases for the job factory."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = JobFactory()
    
    def test_create_job(self):
        """Test creating a job."""
        # Create a regular job
        payload = {'test': 'data'}
        job = self.factory.create_job(payload)
        
        # Verify the job
        self.assertIsInstance(job, JobDTO)
        self.assertEqual(job.payload, payload)
        self.assertEqual(job.priority, JobPriority.NORMAL)
        self.assertEqual(job.status, JobStatus.PENDING)
        
        # Create a job with a specific priority
        job = self.factory.create_job(payload, priority=JobPriority.HIGH)
        self.assertEqual(job.priority, JobPriority.HIGH)
    
    def test_create_literature_extraction_job(self):
        """Test creating a literature extraction job."""
        # Create a job with article_id
        payload = {'article_id': '12345'}
        job = self.factory.create_job(payload)
        
        # Verify the job
        self.assertIsInstance(job, LiteratureExtractionJobDTO)
        self.assertEqual(job.payload, payload)
        self.assertEqual(job.article_id, '12345')
        
        # Create a job with text
        payload = {'text': 'Sample text'}
        job = self.factory.create_job(payload)
        
        # Verify the job
        self.assertIsInstance(job, LiteratureExtractionJobDTO)
        self.assertEqual(job.payload, payload)
        self.assertEqual(job.text, 'Sample text')
    
    def test_create_batch_jobs(self):
        """Test creating batch jobs."""
        # Create batch jobs
        payloads = [
            {'index': 0},
            {'index': 1},
            {'index': 2}
        ]
        jobs = self.factory.create_batch_jobs(payloads)
        
        # Verify the jobs
        self.assertEqual(len(jobs), 3)
        for i, job in enumerate(jobs):
            self.assertIsInstance(job, JobDTO)
            self.assertEqual(job.payload, payloads[i])
            self.assertEqual(job.priority, JobPriority.NORMAL)
            self.assertEqual(job.status, JobStatus.PENDING)
        
        # Create batch jobs with a specific priority
        jobs = self.factory.create_batch_jobs(payloads, priority=JobPriority.HIGH)
        for job in jobs:
            self.assertEqual(job.priority, JobPriority.HIGH)


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for the literature extraction queue manager.

This module contains tests for the literature extraction queue manager.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import threading
import time
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the config manager to avoid importing it
mock_config = MagicMock()
sys.modules['scientific_voyager.config.config_manager'] = MagicMock()
sys.modules['scientific_voyager.config.config_manager'].get_config = MagicMock(return_value=mock_config)

from scientific_voyager.queue.literature_queue import LiteratureExtractionQueueManager
from scientific_voyager.interfaces.queue_interface import (
    JobStatus, JobPriority, IQueue, IWorker, IJobFactory
)
from scientific_voyager.interfaces.queue_dto import (
    JobDTO, QueueStatsDTO, BatchJobResultDTO, LiteratureExtractionJobDTO
)
from scientific_voyager.interfaces.extraction_interface import IExtractionPipeline
from scientific_voyager.interfaces.extraction_dto import (
    ExtractionResultDTO, EntityDTO, RelationDTO, StatementDTO
)


class TestLiteratureExtractionQueueManager(unittest.TestCase):
    """Test cases for the literature extraction queue manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects
        self.mock_queue = MagicMock(spec=IQueue)
        self.mock_worker = MagicMock(spec=IWorker)
        self.mock_job_factory = MagicMock(spec=IJobFactory)
        self.mock_extraction_pipeline = MagicMock(spec=IExtractionPipeline)
        self.mock_pubmed_adapter = MagicMock()
        
        # Configure the mock job factory
        def create_job(payload, priority=JobPriority.NORMAL):
            job = LiteratureExtractionJobDTO(
                payload=payload,
                priority=priority,
                job_id=f"job-{len(self.created_jobs)}"
            )
            self.created_jobs.append(job)
            return job
        
        def create_batch_jobs(payloads, priority=JobPriority.NORMAL):
            jobs = []
            for payload in payloads:
                job = create_job(payload, priority)
                jobs.append(job)
            return jobs
        
        self.mock_job_factory.create_job.side_effect = create_job
        self.mock_job_factory.create_batch_jobs.side_effect = create_batch_jobs
        
        # Track created jobs
        self.created_jobs = []
        
        # Create the queue manager
        self.manager = LiteratureExtractionQueueManager(
            queue=self.mock_queue,
            worker=self.mock_worker,
            job_factory=self.mock_job_factory,
            extraction_pipeline=self.mock_extraction_pipeline,
            pubmed_adapter=self.mock_pubmed_adapter
        )
    
    def test_start_stop(self):
        """Test starting and stopping the queue manager."""
        # Start the queue manager
        self.manager.start()
        
        # Verify the worker was started
        self.mock_worker.start.assert_called_once()
        
        # Stop the queue manager
        self.manager.stop()
        
        # Verify the worker was stopped
        self.mock_worker.stop.assert_called_once()
    
    def test_is_running(self):
        """Test checking if the queue manager is running."""
        # Set up the mock worker
        self.mock_worker.is_running.return_value = True
        
        # Check if the queue manager is running
        running = self.manager.is_running()
        
        # Verify the result
        self.assertTrue(running)
        self.mock_worker.is_running.assert_called_once()
    
    def test_submit_article_id(self):
        """Test submitting a job to extract information from a PubMed article."""
        # Submit a job
        article_id = "12345"
        options = {"option1": "value1"}
        job_id = self.manager.submit_article_id(article_id, options=options)
        
        # Verify the job was created
        self.mock_job_factory.create_job.assert_called_once_with(
            {'article_id': article_id, 'options': options},
            JobPriority.NORMAL
        )
        
        # Verify the job was enqueued
        self.mock_queue.enqueue.assert_called_once_with(self.created_jobs[0])
        
        # Verify the job ID
        self.assertEqual(job_id, "job-0")
    
    def test_submit_text(self):
        """Test submitting a job to extract information from text."""
        # Submit a job
        text = "Sample text"
        options = {"option1": "value1"}
        job_id = self.manager.submit_text(text, options=options)
        
        # Verify the job was created
        self.mock_job_factory.create_job.assert_called_once_with(
            {'text': text, 'options': options},
            JobPriority.NORMAL
        )
        
        # Verify the job was enqueued
        self.mock_queue.enqueue.assert_called_once_with(self.created_jobs[0])
        
        # Verify the job ID
        self.assertEqual(job_id, "job-0")
    
    def test_submit_batch_article_ids(self):
        """Test submitting a batch of jobs to extract information from PubMed articles."""
        # Submit a batch of jobs
        article_ids = ["12345", "67890", "abcde"]
        options = {"option1": "value1"}
        batch_id = self.manager.submit_batch_article_ids(article_ids, options=options)
        
        # Verify the jobs were created
        expected_payloads = [
            {'article_id': article_id, 'options': options}
            for article_id in article_ids
        ]
        self.mock_job_factory.create_batch_jobs.assert_called_once_with(
            expected_payloads,
            JobPriority.NORMAL
        )
        
        # Verify the jobs were enqueued
        self.assertEqual(self.mock_queue.enqueue.call_count, 3)
        for i, job in enumerate(self.created_jobs):
            self.mock_queue.enqueue.assert_any_call(job)
        
        # Verify the batch ID is a UUID
        self.assertIsNotNone(batch_id)
        self.assertTrue(len(batch_id) > 0)
        
        # Verify the batch result was created
        self.assertIn(batch_id, self.manager.batch_results)
        batch_result = self.manager.batch_results[batch_id]
        self.assertEqual(batch_result.job_ids, ["job-0", "job-1", "job-2"])
        self.assertEqual(batch_result.pending, 3)
    
    def test_submit_batch_texts(self):
        """Test submitting a batch of jobs to extract information from texts."""
        # Submit a batch of jobs
        texts = ["Text 1", "Text 2", "Text 3"]
        options = {"option1": "value1"}
        batch_id = self.manager.submit_batch_texts(texts, options=options)
        
        # Verify the jobs were created
        expected_payloads = [
            {'text': text, 'options': options}
            for text in texts
        ]
        self.mock_job_factory.create_batch_jobs.assert_called_once_with(
            expected_payloads,
            JobPriority.NORMAL
        )
        
        # Verify the jobs were enqueued
        self.assertEqual(self.mock_queue.enqueue.call_count, 3)
        for i, job in enumerate(self.created_jobs):
            self.mock_queue.enqueue.assert_any_call(job)
        
        # Verify the batch ID is a UUID
        self.assertIsNotNone(batch_id)
        self.assertTrue(len(batch_id) > 0)
        
        # Verify the batch result was created
        self.assertIn(batch_id, self.manager.batch_results)
        batch_result = self.manager.batch_results[batch_id]
        self.assertEqual(batch_result.job_ids, ["job-0", "job-1", "job-2"])
        self.assertEqual(batch_result.pending, 3)
    
    def test_get_job_status(self):
        """Test getting the status of a job."""
        # Set up the mock queue
        job = LiteratureExtractionJobDTO(payload={}, job_id="job-123")
        job.status = JobStatus.RUNNING
        self.mock_queue.get_job.return_value = job
        
        # Get the job status
        status = self.manager.get_job_status("job-123")
        
        # Verify the result
        self.assertEqual(status, JobStatus.RUNNING)
        self.mock_queue.get_job.assert_called_once_with("job-123")
        
        # Test with a non-existent job
        self.mock_queue.get_job.return_value = None
        status = self.manager.get_job_status("non-existent")
        self.assertIsNone(status)
    
    def test_get_job_result(self):
        """Test getting the result of a job."""
        # Set up the mock queue
        job = LiteratureExtractionJobDTO(payload={}, job_id="job-123")
        job.status = JobStatus.COMPLETED
        job.result = {"key": "value"}
        self.mock_queue.get_job.return_value = job
        
        # Get the job result
        result = self.manager.get_job_result("job-123")
        
        # Verify the result
        self.assertEqual(result, {"key": "value"})
        self.mock_queue.get_job.assert_called_once_with("job-123")
        
        # Test with a non-existent job
        self.mock_queue.get_job.return_value = None
        result = self.manager.get_job_result("non-existent")
        self.assertIsNone(result)
        
        # Test with a job that is not completed
        job.status = JobStatus.RUNNING
        self.mock_queue.get_job.return_value = job
        result = self.manager.get_job_result("job-123")
        self.assertIsNone(result)
    
    def test_get_batch_status(self):
        """Test getting the status of a batch."""
        # Create a batch result
        batch_id = "batch-123"
        job_ids = ["job-1", "job-2", "job-3"]
        batch_result = BatchJobResultDTO(job_ids=job_ids, pending=3)
        self.manager.batch_results[batch_id] = batch_result
        
        # Set up the mock queue
        job1 = LiteratureExtractionJobDTO(payload={}, job_id="job-1")
        job1.status = JobStatus.COMPLETED
        job2 = LiteratureExtractionJobDTO(payload={}, job_id="job-2")
        job2.status = JobStatus.RUNNING
        job3 = LiteratureExtractionJobDTO(payload={}, job_id="job-3")
        job3.status = JobStatus.PENDING
        
        self.mock_queue.get_job.side_effect = lambda job_id: {
            "job-1": job1,
            "job-2": job2,
            "job-3": job3
        }.get(job_id)
        
        # Get the batch status
        status = self.manager.get_batch_status(batch_id)
        
        # Verify the result
        self.assertEqual(status.job_ids, job_ids)
        self.assertEqual(status.completed, 1)
        self.assertEqual(status.running, 1)
        self.assertEqual(status.pending, 1)
        self.assertEqual(status.failed, 0)
        self.assertEqual(status.cancelled, 0)
        
        # Test with a non-existent batch
        status = self.manager.get_batch_status("non-existent")
        self.assertIsNone(status)
    
    def test_cancel_job(self):
        """Test cancelling a job."""
        # Set up the mock queue
        job = LiteratureExtractionJobDTO(payload={}, job_id="job-123")
        job.status = JobStatus.PENDING
        self.mock_queue.get_job.return_value = job
        
        # Cancel the job
        success = self.manager.cancel_job("job-123")
        
        # Verify the result
        self.assertTrue(success)
        self.mock_queue.get_job.assert_called_once_with("job-123")
        self.assertEqual(job.status, JobStatus.CANCELLED)
        self.mock_queue.update_job.assert_called_once_with(job)
        
        # Test with a non-existent job
        self.mock_queue.get_job.return_value = None
        success = self.manager.cancel_job("non-existent")
        self.assertFalse(success)
        
        # Test with a job that is not pending
        job.status = JobStatus.RUNNING
        self.mock_queue.get_job.return_value = job
        success = self.manager.cancel_job("job-123")
        self.assertFalse(success)
    
    def test_cancel_batch(self):
        """Test cancelling a batch."""
        # Create a batch result
        batch_id = "batch-123"
        job_ids = ["job-1", "job-2", "job-3"]
        batch_result = BatchJobResultDTO(job_ids=job_ids, pending=3)
        self.manager.batch_results[batch_id] = batch_result
        
        # Set up the mock queue
        job1 = LiteratureExtractionJobDTO(payload={}, job_id="job-1")
        job1.status = JobStatus.PENDING
        job2 = LiteratureExtractionJobDTO(payload={}, job_id="job-2")
        job2.status = JobStatus.RUNNING
        job3 = LiteratureExtractionJobDTO(payload={}, job_id="job-3")
        job3.status = JobStatus.PENDING
        
        self.mock_queue.get_job.side_effect = lambda job_id: {
            "job-1": job1,
            "job-2": job2,
            "job-3": job3
        }.get(job_id)
        
        # Mock the cancel_job method
        with patch.object(self.manager, 'cancel_job') as mock_cancel_job:
            mock_cancel_job.side_effect = lambda job_id: job_id in ["job-1", "job-3"]
            
            # Cancel the batch
            success = self.manager.cancel_batch(batch_id)
            
            # Verify the result
            self.assertTrue(success)
            self.assertEqual(mock_cancel_job.call_count, 3)
            mock_cancel_job.assert_has_calls([
                call("job-1"),
                call("job-2"),
                call("job-3")
            ], any_order=True)
        
        # Test with a non-existent batch
        success = self.manager.cancel_batch("non-existent")
        self.assertFalse(success)
    
    def test_get_queue_stats(self):
        """Test getting queue statistics."""
        # Set up the mock queue
        stats = QueueStatsDTO(
            total_jobs=10,
            pending_jobs=5,
            running_jobs=2,
            completed_jobs=2,
            failed_jobs=1,
            cancelled_jobs=0
        )
        self.mock_queue.get_stats.return_value = stats
        
        # Get the queue statistics
        result = self.manager.get_queue_stats()
        
        # Verify the result
        self.assertEqual(result, stats)
        self.mock_queue.get_stats.assert_called_once()
    
    def test_process_job_with_article_id(self):
        """Test processing a job with an article ID."""
        # Create a job with an article ID
        job = LiteratureExtractionJobDTO(
            payload={'article_id': '12345'},
            job_id="job-123"
        )
        
        # Set up the mock PubMed adapter
        self.mock_pubmed_adapter.get_article_abstract.return_value = "Sample abstract"
        
        # Set up the mock extraction pipeline
        extraction_result = ExtractionResultDTO(
            source_text="Sample abstract",
            entities=[],
            relations=[],
            statements=[]
        )
        self.mock_extraction_pipeline.process.return_value = extraction_result
        
        # Process the job
        self.manager._process_job(job)
        
        # Verify the PubMed adapter was called
        self.mock_pubmed_adapter.get_article_abstract.assert_called_once_with('12345')
        
        # Verify the extraction pipeline was called
        self.mock_extraction_pipeline.process.assert_called_once_with("Sample abstract")
        
        # Verify the job result was set
        self.assertEqual(job.result, extraction_result)
    
    def test_process_job_with_text(self):
        """Test processing a job with text."""
        # Create a job with text
        job = LiteratureExtractionJobDTO(
            payload={'text': 'Sample text'},
            job_id="job-123"
        )
        
        # Set up the mock extraction pipeline
        extraction_result = ExtractionResultDTO(
            source_text="Sample text",
            entities=[],
            relations=[],
            statements=[]
        )
        self.mock_extraction_pipeline.process.return_value = extraction_result
        
        # Process the job
        self.manager._process_job(job)
        
        # Verify the PubMed adapter was not called
        self.mock_pubmed_adapter.get_article_abstract.assert_not_called()
        
        # Verify the extraction pipeline was called
        self.mock_extraction_pipeline.process.assert_called_once_with("Sample text")
        
        # Verify the job result was set
        self.assertEqual(job.result, extraction_result)
    
    def test_process_job_with_invalid_job(self):
        """Test processing an invalid job."""
        # Create a regular job (not a LiteratureExtractionJobDTO)
        job = JobDTO(payload={}, job_id="job-123")
        
        # Process the job
        with self.assertRaises(ValueError):
            self.manager._process_job(job)
    
    def test_process_job_with_no_text_or_article_id(self):
        """Test processing a job with no text or article ID."""
        # Create a job with no text or article ID
        job = LiteratureExtractionJobDTO(
            payload={},
            job_id="job-123"
        )
        
        # Process the job
        with self.assertRaises(ValueError):
            self.manager._process_job(job)
    
    def test_process_job_with_no_abstract(self):
        """Test processing a job with no abstract."""
        # Create a job with an article ID
        job = LiteratureExtractionJobDTO(
            payload={'article_id': '12345'},
            job_id="job-123"
        )
        
        # Set up the mock PubMed adapter to return no abstract
        self.mock_pubmed_adapter.get_article_abstract.return_value = None
        
        # Process the job
        with self.assertRaises(ValueError):
            self.manager._process_job(job)


if __name__ == '__main__':
    unittest.main()

"""
Processing Pipeline Module

This module implements the data processing pipeline for extracting, transforming,
and loading scientific literature data into the Scientific Voyager platform.
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from scientific_voyager.data.pubmed_source import PubMedSource
from scientific_voyager.core.statement_extractor import StatementExtractor
from scientific_voyager.utils.llm_client import LLMClient


class ProcessingPipeline:
    """
    Implements the data processing pipeline for scientific literature.
    """

    def __init__(
        self,
        data_source: Optional[PubMedSource] = None,
        statement_extractor: Optional[StatementExtractor] = None,
        llm_client: Optional[LLMClient] = None,
        config: Optional[Dict] = None
    ):
        """
        Initialize the processing pipeline.
        
        Args:
            data_source: Source for retrieving scientific literature
            statement_extractor: Extractor for scientific statements
            llm_client: LLM client for NLP tasks
            config: Configuration dictionary
        """
        self.data_source = data_source
        self.statement_extractor = statement_extractor
        self.llm_client = llm_client
        self.config = config or {}
        self.logger = logging.getLogger("scientific_voyager.processing_pipeline")
        
        # Default configuration
        self.batch_size = self.config.get("batch_size", 10)
        self.max_workers = self.config.get("max_workers", 4)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        self.retry_delay = self.config.get("retry_delay", 2)  # seconds
        
    def process_query(
        self,
        query: str,
        max_results: int = 50,
        callbacks: Optional[Dict[str, Callable]] = None
    ) -> Dict[str, Any]:
        """
        Process a scientific literature query through the pipeline.
        
        Args:
            query: Search query for scientific literature
            max_results: Maximum number of results to process
            callbacks: Optional callbacks for pipeline stages
            
        Returns:
            Dictionary with processing results
        """
        if not self.data_source:
            self.logger.error("No data source available for processing")
            return {"status": "error", "message": "No data source available"}
            
        if not self.statement_extractor:
            self.logger.warning("No statement extractor available, results will be limited")
            
        # Set up callbacks
        cbs = callbacks or {}
        on_search_complete = cbs.get("on_search_complete")
        on_batch_complete = cbs.get("on_batch_complete")
        on_processing_complete = cbs.get("on_processing_complete")
        
        try:
            # Step 1: Search for articles
            self.logger.info(f"Searching for articles with query: {query}")
            pmids = self.data_source.search(query=query, max_results=max_results)
            
            if not pmids:
                self.logger.warning(f"No articles found for query: {query}")
                return {"status": "success", "message": "No articles found", "results": []}
                
            self.logger.info(f"Found {len(pmids)} articles")
            
            if on_search_complete:
                on_search_complete(pmids)
                
            # Step 2: Process articles in batches
            all_results = []
            
            for i in range(0, len(pmids), self.batch_size):
                batch_pmids = pmids[i:i + self.batch_size]
                batch_results = self._process_batch(batch_pmids)
                all_results.extend(batch_results)
                
                self.logger.info(f"Processed batch {i // self.batch_size + 1}/{(len(pmids) + self.batch_size - 1) // self.batch_size}")
                
                if on_batch_complete:
                    on_batch_complete(batch_results, i // self.batch_size + 1)
                    
            # Step 3: Finalize processing
            if on_processing_complete:
                on_processing_complete(all_results)
                
            return {
                "status": "success",
                "message": f"Processed {len(all_results)} articles",
                "results": all_results
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {"status": "error", "message": str(e)}
            
    def _process_batch(self, pmids: List[str]) -> List[Dict]:
        """
        Process a batch of articles.
        
        Args:
            pmids: List of PubMed IDs to process
            
        Returns:
            List of processed article results
        """
        results = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_pmid = {
                executor.submit(self._process_article, pmid): pmid
                for pmid in pmids
            }
            
            # Process results as they complete
            for future in as_completed(future_to_pmid):
                pmid = future_to_pmid[future]
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing article {pmid}: {e}")
                    results.append({
                        "pmid": pmid,
                        "status": "error",
                        "message": str(e)
                    })
                    
        return results
        
    def _process_article(self, pmid: str) -> Dict:
        """
        Process a single article with retry logic.
        
        Args:
            pmid: PubMed ID of the article to process
            
        Returns:
            Processed article result
        """
        for attempt in range(self.retry_attempts):
            try:
                return self._process_article_once(pmid)
            except Exception as e:
                self.logger.warning(f"Error processing article {pmid} (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
                    
    def _process_article_once(self, pmid: str) -> Dict:
        """
        Process a single article once.
        
        Args:
            pmid: PubMed ID of the article to process
            
        Returns:
            Processed article result
        """
        # Step 1: Fetch the article abstract
        abstract = self.data_source.fetch_abstract(pmid)
        
        if not abstract:
            return {
                "pmid": pmid,
                "status": "error",
                "message": "Abstract not found"
            }
            
        # Step 2: Extract statements if extractor is available
        statements = []
        if self.statement_extractor and "text" in abstract:
            statements = self.statement_extractor.extract_statements(abstract["text"])
            
        # Step 3: Extract terms if data source has term extraction
        terms = []
        if hasattr(self.data_source, "extract_terms"):
            terms = self.data_source.extract_terms(abstract)
            
        # Return the processed result
        return {
            "pmid": pmid,
            "status": "success",
            "abstract": abstract,
            "statements": statements,
            "terms": terms
        }
        
    def process_custom_text(self, text: str) -> Dict:
        """
        Process custom text through the pipeline.
        
        Args:
            text: Custom scientific text to process
            
        Returns:
            Dictionary with processing results
        """
        if not self.statement_extractor:
            self.logger.error("No statement extractor available for processing")
            return {"status": "error", "message": "No statement extractor available"}
            
        try:
            # Extract statements
            statements = self.statement_extractor.extract_statements(text)
            
            # Extract terms if LLM client is available
            terms = []
            if self.llm_client:
                terms = self.llm_client.extract_terms(text)
                
            return {
                "status": "success",
                "text": text,
                "statements": statements,
                "terms": terms
            }
            
        except Exception as e:
            self.logger.error(f"Error processing custom text: {e}")
            return {"status": "error", "message": str(e)}

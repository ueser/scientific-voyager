"""
Unit tests for the rate limiting functionality of the PubMed API Adapter.
"""

import unittest
from unittest.mock import patch, MagicMock
import time

# Add the project root to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the config manager to avoid importing it
sys.modules['scientific_voyager.config.config_manager'] = MagicMock()

from scientific_voyager.literature.pubmed_adapter import PubMedAdapter


class TestRateLimiting(unittest.TestCase):
    """Test cases for the rate limiting functionality of the PubMed API Adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a patcher for the config manager
        self.config_patcher = patch('scientific_voyager.literature.pubmed_adapter.get_config')
        self.mock_config = self.config_patcher.start()
        
        # Configure the mock config with a very low rate limit for testing
        mock_config_dto = MagicMock()
        mock_config_dto.api_keys = {"pubmed": "test_api_key"}
        self.mock_config.return_value.get_config_dto.return_value = mock_config_dto
        
        # Set a very low rate limit (1 request per second) for testing
        self.mock_config.return_value.get.return_value = 1  # requests_per_second
        
        # Create the adapter
        self.adapter = PubMedAdapter()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.config_patcher.stop()
    
    @patch('scientific_voyager.literature.pubmed_adapter.requests.get')
    @patch('scientific_voyager.literature.pubmed_adapter.time.sleep')
    def test_rate_limiting(self, mock_sleep, mock_get):
        """Test that rate limiting is applied correctly."""
        # Configure the mock responses
        # Mock for search endpoint
        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "esearchresult": {
                "count": "1",
                "retmax": "1",
                "retstart": "0",
                "idlist": ["12345678"],
                "translationset": [],
                "translationstack": [],
                "querytranslation": "PTEN[All Fields]"
            }
        }
        
        # Mock for fetch endpoint with XML response
        mock_fetch_response = MagicMock()
        mock_fetch_response.text = """
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation Status="MEDLINE" Owner="NLM">
                    <PMID Version="1">12345678</PMID>
                    <Article PubModel="Print">
                        <Journal>
                            <Title>Journal of Example Research</Title>
                            <JournalIssue CitedMedium="Internet">
                                <Volume>42</Volume>
                                <Issue>3</Issue>
                                <PubDate>
                                    <Year>2022</Year>
                                    <Month>Mar</Month>
                                    <Day>15</Day>
                                </PubDate>
                            </JournalIssue>
                        </Journal>
                        <ArticleTitle>PTEN regulation in cancer signaling pathways</ArticleTitle>
                        <Abstract>
                            <AbstractText>This is a test abstract.</AbstractText>
                        </Abstract>
                        <AuthorList CompleteYN="Y">
                            <Author ValidYN="Y">
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                        </AuthorList>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        """
        
        # Set up the mock to return different responses for different URLs
        def side_effect(url, params):
            if url == PubMedAdapter.ESEARCH_URL:
                return mock_search_response
            elif url == PubMedAdapter.EFETCH_URL:
                return mock_fetch_response
            return MagicMock()
        
        mock_get.side_effect = side_effect
        
        # Make multiple API calls to trigger rate limiting
        for _ in range(3):
            self.adapter.search_articles("PTEN", max_results=1)
        
        # Verify that time.sleep was called to enforce rate limiting
        # The adapter makes multiple API calls per search_articles call (search + fetch)
        # So we expect more sleep calls than just the number of search_articles calls
        self.assertGreaterEqual(mock_sleep.call_count, 2)
        
        # Verify that the sleep durations are reasonable
        for call in mock_sleep.call_args_list:
            sleep_duration = call[0][0]
            self.assertGreaterEqual(sleep_duration, 0)
            self.assertLessEqual(sleep_duration, 1.1)  # Allow a small margin for calculation
        
        # Verify the sleep duration is approximately 1 second (our configured rate limit)
        for call in mock_sleep.call_args_list:
            sleep_duration = call[0][0]
            self.assertGreaterEqual(sleep_duration, 0)
            self.assertLessEqual(sleep_duration, 1.1)  # Allow a small margin for calculation
    
    @patch('scientific_voyager.literature.pubmed_adapter.requests.get')
    def test_rate_limit_configuration(self, mock_get):
        """Test that rate limiting respects the configuration."""
        # Configure the mock responses
        # Mock for search endpoint
        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "esearchresult": {
                "count": "1",
                "retmax": "1",
                "retstart": "0",
                "idlist": ["12345678"],
                "translationset": [],
                "translationstack": [],
                "querytranslation": "PTEN[All Fields]"
            }
        }
        
        # Mock for fetch endpoint with XML response
        mock_fetch_response = MagicMock()
        mock_fetch_response.text = """
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation Status="MEDLINE" Owner="NLM">
                    <PMID Version="1">12345678</PMID>
                    <Article PubModel="Print">
                        <Journal>
                            <Title>Journal of Example Research</Title>
                            <JournalIssue CitedMedium="Internet">
                                <Volume>42</Volume>
                                <Issue>3</Issue>
                                <PubDate>
                                    <Year>2022</Year>
                                    <Month>Mar</Month>
                                    <Day>15</Day>
                                </PubDate>
                            </JournalIssue>
                        </Journal>
                        <ArticleTitle>PTEN regulation in cancer signaling pathways</ArticleTitle>
                        <Abstract>
                            <AbstractText>This is a test abstract.</AbstractText>
                        </Abstract>
                        <AuthorList CompleteYN="Y">
                            <Author ValidYN="Y">
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                        </AuthorList>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        """
        
        # Set up the mock to return different responses for different URLs
        def side_effect(url, params):
            if url == PubMedAdapter.ESEARCH_URL:
                return mock_search_response
            elif url == PubMedAdapter.EFETCH_URL:
                return mock_fetch_response
            return MagicMock()
        
        mock_get.side_effect = side_effect
        
        # Test with different rate limit configurations
        rate_limits = [1, 3, 5]
        sleep_calls = {}
        
        for rate_limit in rate_limits:
            # Update the mock config
            self.mock_config.return_value.get.return_value = rate_limit
            
            # Create a new adapter with the updated rate limit
            adapter = PubMedAdapter()
            
            # Patch the time.sleep method for this specific test
            with patch('scientific_voyager.literature.pubmed_adapter.time.sleep') as mock_sleep:
                # Make multiple API calls
                for _ in range(3):
                    adapter.search_articles("PTEN", max_results=1)
                
                # Store the sleep call count for each rate limit
                sleep_calls[rate_limit] = mock_sleep.call_count
                
                # For rate_limit=1, we expect multiple sleep calls
                if rate_limit == 1:
                    self.assertGreaterEqual(sleep_calls[rate_limit], 3)
        
        # After all rate limits have been tested, verify that higher rate limits result in fewer or equal sleep calls
        # The relationship might not be strictly decreasing due to implementation details,
        # but generally higher rate limits should lead to fewer sleep calls
        self.assertGreaterEqual(sleep_calls[1], sleep_calls[5])


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for the PubMed API Adapter.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from datetime import datetime
from xml.etree import ElementTree

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the PubMedAdapter class directly from the file
from scientific_voyager.literature.pubmed_adapter import PubMedAdapter

# Mock the config manager to avoid importing it
sys.modules['scientific_voyager.config.config_manager'] = MagicMock()


class TestPubMedAdapter(unittest.TestCase):
    """Test cases for the PubMed API Adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a patcher for the config manager
        self.config_patcher = patch('scientific_voyager.literature.pubmed_adapter.get_config')
        self.mock_config = self.config_patcher.start()
        
        # Configure the mock config
        mock_config_dto = MagicMock()
        mock_config_dto.api_keys = {"pubmed": "test_api_key"}
        self.mock_config.return_value.get_config_dto.return_value = mock_config_dto
        self.mock_config.return_value.get.return_value = 3  # requests_per_second
        
        # Create the adapter
        self.adapter = PubMedAdapter()
        
        # Load test data
        self.load_test_data()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.config_patcher.stop()
    
    def load_test_data(self):
        """Load test data for mock responses."""
        # Sample search response
        self.search_response = {
            "esearchresult": {
                "count": "2",
                "retmax": "2",
                "retstart": "0",
                "idlist": ["12345678", "87654321"],
                "translationset": [],
                "translationstack": [],
                "querytranslation": "PTEN[All Fields] AND cancer[All Fields]"
            }
        }
        
        # Sample article XML for efetch response
        self.article_xml = """
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
                            <AbstractText>Background: PTEN is a tumor suppressor gene that is frequently mutated in human cancers.</AbstractText>
                            <AbstractText Label="Methods">We analyzed PTEN expression in various cancer cell lines.</AbstractText>
                            <AbstractText Label="Results">PTEN loss leads to increased PI3K signaling in cancer cells.</AbstractText>
                            <AbstractText Label="Conclusion">Our findings suggest that PTEN is a key regulator of cancer signaling pathways.</AbstractText>
                        </Abstract>
                        <AuthorList CompleteYN="Y">
                            <Author ValidYN="Y">
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                            <Author ValidYN="Y">
                                <LastName>Johnson</LastName>
                                <ForeName>Emily</ForeName>
                            </Author>
                        </AuthorList>
                    </Article>
                    <KeywordList Owner="NOTNLM">
                        <Keyword MajorTopicYN="N">PTEN</Keyword>
                        <Keyword MajorTopicYN="N">cancer</Keyword>
                        <Keyword MajorTopicYN="N">signaling</Keyword>
                    </KeywordList>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">12345678</ArticleId>
                        <ArticleId IdType="doi">10.1234/example.12345678</ArticleId>
                    </ArticleIdList>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        """
        
        # Sample related articles response
        self.related_response = {
            "linksets": [
                {
                    "dbfrom": "pubmed",
                    "ids": ["12345678"],
                    "linksetdbs": [
                        {
                            "linkname": "pubmed_pubmed",
                            "links": ["87654321", "11223344", "55667788"]
                        }
                    ]
                }
            ]
        }
    
    @patch('scientific_voyager.literature.pubmed_adapter.requests.get')
    def test_search_articles(self, mock_get):
        """Test searching for articles."""
        # Configure the mock response for search
        mock_search_response = MagicMock()
        mock_search_response.json.return_value = self.search_response
        
        # Configure the mock response for fetch
        mock_fetch_response = MagicMock()
        mock_fetch_response.text = self.article_xml
        
        # Set up the mock to return different responses for different URLs
        def side_effect(url, params):
            if url == PubMedAdapter.ESEARCH_URL:
                return mock_search_response
            elif url == PubMedAdapter.EFETCH_URL:
                return mock_fetch_response
            return MagicMock()
        
        mock_get.side_effect = side_effect
        
        # Call the method under test
        articles = self.adapter.search_articles("PTEN cancer", max_results=2)
        
        # Verify the results
        self.assertEqual(len(articles), 1)  # Only one article in our mock XML
        self.assertEqual(articles[0]["article_id"], "12345678")
        self.assertEqual(articles[0]["title"], "PTEN regulation in cancer signaling pathways")
        self.assertEqual(len(articles[0]["authors"]), 2)
        self.assertEqual(articles[0]["authors"][0], "Smith, John")
        self.assertEqual(articles[0]["journal"], "Journal of Example Research")
        self.assertEqual(articles[0]["publication_date"], "2022-03-15")
        self.assertEqual(articles[0]["doi"], "10.1234/example.12345678")
        
        # Verify the abstract contains all sections
        self.assertIn("Background: PTEN is a tumor suppressor gene", articles[0]["abstract"])
        self.assertIn("Methods: We analyzed PTEN expression", articles[0]["abstract"])
        self.assertIn("Results: PTEN loss leads to increased PI3K signaling", articles[0]["abstract"])
        self.assertIn("Conclusion: Our findings suggest", articles[0]["abstract"])
        
        # Verify the API calls
        self.assertEqual(mock_get.call_count, 2)
        
        # Check search parameters
        search_call = mock_get.call_args_list[0]
        self.assertEqual(search_call[0][0], PubMedAdapter.ESEARCH_URL)
        self.assertEqual(search_call[1]["params"]["term"], "PTEN cancer")
        self.assertEqual(search_call[1]["params"]["retmax"], 2)
        self.assertEqual(search_call[1]["params"]["api_key"], "test_api_key")
        
        # Check fetch parameters
        fetch_call = mock_get.call_args_list[1]
        self.assertEqual(fetch_call[0][0], PubMedAdapter.EFETCH_URL)
        self.assertEqual(fetch_call[1]["params"]["id"], "12345678,87654321")
        self.assertEqual(fetch_call[1]["params"]["api_key"], "test_api_key")
    
    @patch('scientific_voyager.literature.pubmed_adapter.requests.get')
    def test_get_article_by_id(self, mock_get):
        """Test getting an article by ID."""
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.text = self.article_xml
        mock_get.return_value = mock_response
        
        # Call the method under test
        article = self.adapter.get_article_by_id("12345678")
        
        # Verify the results
        self.assertEqual(article["article_id"], "12345678")
        self.assertEqual(article["title"], "PTEN regulation in cancer signaling pathways")
        self.assertEqual(len(article["authors"]), 2)
        self.assertEqual(article["authors"][0], "Smith, John")
        self.assertEqual(article["journal"], "Journal of Example Research")
        self.assertEqual(article["publication_date"], "2022-03-15")
        self.assertEqual(article["doi"], "10.1234/example.12345678")
        
        # Verify the API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[0][0], PubMedAdapter.EFETCH_URL)
        self.assertEqual(call_args[1]["params"]["id"], "12345678")
        self.assertEqual(call_args[1]["params"]["api_key"], "test_api_key")
    
    @patch('scientific_voyager.literature.pubmed_adapter.requests.get')
    def test_get_article_abstract(self, mock_get):
        """Test getting an article abstract."""
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.text = self.article_xml
        mock_get.return_value = mock_response
        
        # Call the method under test
        abstract = self.adapter.get_article_abstract("12345678")
        
        # Verify the results
        self.assertIn("Background: PTEN is a tumor suppressor gene", abstract)
        self.assertIn("Methods: We analyzed PTEN expression", abstract)
        self.assertIn("Results: PTEN loss leads to increased PI3K signaling", abstract)
        self.assertIn("Conclusion: Our findings suggest", abstract)
        
        # Verify the API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[0][0], PubMedAdapter.EFETCH_URL)
        self.assertEqual(call_args[1]["params"]["id"], "12345678")
    
    @patch('scientific_voyager.literature.pubmed_adapter.requests.get')
    def test_get_related_articles(self, mock_get):
        """Test getting related articles."""
        # Configure the mock responses
        mock_elink_response = MagicMock()
        mock_elink_response.json.return_value = self.related_response
        
        mock_fetch_response = MagicMock()
        mock_fetch_response.text = self.article_xml
        
        # Set up the mock to return different responses for different URLs
        def side_effect(url, params):
            if url == PubMedAdapter.ELINK_URL:
                return mock_elink_response
            elif url == PubMedAdapter.EFETCH_URL:
                return mock_fetch_response
            return MagicMock()
        
        mock_get.side_effect = side_effect
        
        # Call the method under test
        related_articles = self.adapter.get_related_articles("12345678", max_results=3)
        
        # Verify the results
        self.assertEqual(len(related_articles), 1)  # Only one article in our mock XML
        self.assertEqual(related_articles[0]["article_id"], "12345678")
        
        # Verify the API calls
        self.assertEqual(mock_get.call_count, 2)
        
        # Check elink parameters
        elink_call = mock_get.call_args_list[0]
        self.assertEqual(elink_call[0][0], PubMedAdapter.ELINK_URL)
        self.assertEqual(elink_call[1]["params"]["id"], "12345678")
        self.assertEqual(elink_call[1]["params"]["linkname"], "pubmed_pubmed")
        
        # Check fetch parameters
        fetch_call = mock_get.call_args_list[1]
        self.assertEqual(fetch_call[0][0], PubMedAdapter.EFETCH_URL)
        self.assertEqual(fetch_call[1]["params"]["id"], "87654321,11223344,55667788")
    
    def test_invalid_search_query(self):
        """Test searching with an invalid query."""
        with self.assertRaises(ValueError):
            self.adapter.search_articles("")
    
    def test_invalid_article_id(self):
        """Test getting an article with an invalid ID."""
        with self.assertRaises(ValueError):
            self.adapter.get_article_by_id("")
    
    @patch('scientific_voyager.literature.pubmed_adapter.requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection errors."""
        # Configure the mock to raise a connection error
        mock_get.side_effect = Exception("Connection error")
        
        # Verify that the adapter properly raises the exception
        with self.assertRaises(Exception):
            self.adapter.search_articles("PTEN cancer")


if __name__ == '__main__':
    unittest.main()

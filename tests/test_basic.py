#!/usr/bin/env python3
"""
Basic tests for the Financial Reporting Tool
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class TestBasicImports(unittest.TestCase):
    """Test that all core modules can be imported"""
    
    def test_ai_summarizer_import(self):
        """Test AI summarizer module import"""
        try:
            from src.ai_summary.ai_summarizer import AISummarizer
            self.assertTrue(True, "AI summarizer imports successfully")
        except ImportError as e:
            self.fail(f"Failed to import AISummarizer: {e}")
    
    def test_dashboard_import(self):
        """Test dashboard module import"""
        try:
            from src.reporting.dashboard import create_dashboard
            self.assertTrue(True, "Dashboard imports successfully")
        except ImportError as e:
            self.fail(f"Failed to import dashboard: {e}")
    
    def test_pipeline_import(self):
        """Test pipeline module import"""
        try:
            from src.pipeline import FinancialReportingPipeline
            self.assertTrue(True, "Pipeline imports successfully")
        except ImportError as e:
            self.fail(f"Failed to import pipeline: {e}")
    
    def test_database_manager_import(self):
        """Test database manager import"""
        try:
            from src.storage.database_manager import EnhancedDatabaseManager
            self.assertTrue(True, "Database manager imports successfully")
        except ImportError as e:
            self.fail(f"Failed to import database manager: {e}")
    
    def test_config_import(self):
        """Test config module import"""
        try:
            from config.settings import DATABASE_URL
            self.assertTrue(True, "Config imports successfully")
        except ImportError as e:
            self.fail(f"Failed to import config: {e}")

class TestAISummarizer(unittest.TestCase):
    """Test AI summarizer functionality"""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_ai_summarizer_initialization(self):
        """Test AI summarizer can be initialized"""
        from src.ai_summary.ai_summarizer import AISummarizer
        
        # Test with mock API key
        summarizer = AISummarizer(provider='gemini', api_key='test-key')
        self.assertIsNotNone(summarizer)
        self.assertEqual(summarizer.provider, 'gemini')

class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality"""
    
    def test_database_manager_initialization(self):
        """Test database manager can be initialized"""
        from src.storage.database_manager import EnhancedDatabaseManager
        
        # Test with SQLite URL
        db_manager = EnhancedDatabaseManager('sqlite:///test.db')
        self.assertIsNotNone(db_manager)

if __name__ == '__main__':
    unittest.main()

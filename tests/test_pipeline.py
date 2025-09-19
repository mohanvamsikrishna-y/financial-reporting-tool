"""
Basic tests for the Financial Reporting Tool pipeline.
"""

import pytest
import pandas as pd
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.pipeline import FinancialReportingPipeline
from src.validation import DataValidator, DataTransformer
from config.settings import DATABASE_URL

class TestFinancialReportingPipeline:
    """Test cases for the main pipeline"""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        pipeline = FinancialReportingPipeline()
        assert pipeline is not None
        assert pipeline.db_manager is not None
        assert pipeline.data_loader is not None
        pipeline.close()
    
    def test_pipeline_status(self):
        """Test pipeline status check"""
        pipeline = FinancialReportingPipeline()
        status = pipeline.get_pipeline_status()
        assert 'status' in status
        assert 'timestamp' in status
        pipeline.close()

class TestDataValidator:
    """Test cases for data validation"""
    
    def test_validate_transactions(self):
        """Test transaction validation"""
        validator = DataValidator()
        
        # Create test data
        test_data = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'transaction_date': [datetime.now(), datetime.now()],
            'account_id': [1, 2],
            'amount': [100.0, 200.0],
            'transaction_type': ['Debit', 'Credit']
        })
        
        result = validator.validate_transactions(test_data)
        assert 'is_valid' in result
        assert 'data_quality_score' in result
    
    def test_validate_accounts(self):
        """Test account validation"""
        validator = DataValidator()
        
        # Create test data
        test_data = pd.DataFrame({
            'account_code': ['1001', '1002'],
            'account_name': ['Cash', 'Accounts Receivable'],
            'account_type': ['Asset', 'Asset']
        })
        
        result = validator.validate_accounts(test_data)
        assert 'is_valid' in result

class TestDataTransformer:
    """Test cases for data transformation"""
    
    def test_transform_transactions(self):
        """Test transaction transformation"""
        transformer = DataTransformer()
        
        # Create test data
        test_data = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002'],
            'transaction_date': ['2024-01-01', '2024-01-02'],
            'account_code': ['1001', '1002'],
            'amount': [100.0, 200.0],
            'transaction_type': ['Debit', 'Credit'],
            'currency': ['USD', 'USD']
        })
        
        result = transformer.transform_transactions(test_data)
        assert len(result) == len(test_data)
        assert 'amount_usd' in result.columns
        assert 'exchange_rate' in result.columns

if __name__ == '__main__':
    pytest.main([__file__])

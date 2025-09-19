"""
Data validation module for financial data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates financial data for quality and compliance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.validation_rules = self._load_validation_rules()
        self.validation_results = {}
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules from configuration"""
        return {
            'required_fields': ['transaction_id', 'transaction_date', 'account_id', 'amount', 'transaction_type'],
            'numeric_fields': ['amount'],
            'date_fields': ['transaction_date'],
            'string_fields': ['transaction_id', 'transaction_type'],
            'amount_range': (0.01, 1000000.00),
            'date_range': {
                'min': datetime.now() - timedelta(days=365*5),  # 5 years ago
                'max': datetime.now() + timedelta(days=30)      # 30 days in future
            },
            'transaction_types': ['Debit', 'Credit'],
            'account_types': ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense'],
            'currency_codes': ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        }
    
    def validate_transactions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate transaction data"""
        logger.info(f"Starting validation for {len(df)} transaction records")
        
        validation_result = {
            'is_valid': True,
            'total_records': len(df),
            'valid_records': 0,
            'invalid_records': 0,
            'errors': [],
            'warnings': [],
            'data_quality_score': 0.0
        }
        
        # Check for empty dataset
        if len(df) == 0:
            validation_result['errors'].append("Dataset is empty")
            validation_result['is_valid'] = False
            return validation_result
        
        # Validate required fields
        missing_fields = self._validate_required_fields(df)
        if missing_fields:
            validation_result['errors'].extend(missing_fields)
            validation_result['is_valid'] = False
        
        # Validate data types
        type_errors = self._validate_data_types(df)
        if type_errors:
            validation_result['errors'].extend(type_errors)
            validation_result['is_valid'] = False
        
        # Validate business rules
        business_errors = self._validate_business_rules(df)
        if business_errors:
            validation_result['errors'].extend(business_errors)
            validation_result['is_valid'] = False
        
        # Validate data ranges
        range_errors = self._validate_data_ranges(df)
        if range_errors:
            validation_result['warnings'].extend(range_errors)
        
        # Check for duplicates
        duplicate_errors = self._validate_duplicates(df)
        if duplicate_errors:
            validation_result['warnings'].extend(duplicate_errors)
        
        # Calculate data quality score
        validation_result['data_quality_score'] = self._calculate_quality_score(df, validation_result)
        
        # Count valid/invalid records
        validation_result['valid_records'] = len(df) - len(validation_result['errors'])
        validation_result['invalid_records'] = len(validation_result['errors'])
        
        logger.info(f"Validation completed. Quality score: {validation_result['data_quality_score']:.2f}")
        return validation_result
    
    def _validate_required_fields(self, df: pd.DataFrame) -> List[str]:
        """Validate that all required fields are present"""
        errors = []
        required_fields = self.validation_rules['required_fields']
        
        for field in required_fields:
            if field not in df.columns:
                errors.append(f"Required field '{field}' is missing")
        
        return errors
    
    def _validate_data_types(self, df: pd.DataFrame) -> List[str]:
        """Validate data types for each field"""
        errors = []
        
        # Validate numeric fields
        for field in self.validation_rules['numeric_fields']:
            if field in df.columns:
                if not pd.api.types.is_numeric_dtype(df[field]):
                    errors.append(f"Field '{field}' must be numeric")
                elif df[field].isnull().any():
                    errors.append(f"Field '{field}' contains null values")
        
        # Validate date fields
        for field in self.validation_rules['date_fields']:
            if field in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df[field]):
                    errors.append(f"Field '{field}' must be datetime")
                elif df[field].isnull().any():
                    errors.append(f"Field '{field}' contains null values")
        
        return errors
    
    def _validate_business_rules(self, df: pd.DataFrame) -> List[str]:
        """Validate business rules"""
        errors = []
        
        # Validate transaction types
        if 'transaction_type' in df.columns:
            invalid_types = df[~df['transaction_type'].isin(self.validation_rules['transaction_types'])]
            if not invalid_types.empty:
                errors.append(f"Invalid transaction types found: {invalid_types['transaction_type'].unique().tolist()}")
        
        # Validate transaction IDs format
        if 'transaction_id' in df.columns:
            invalid_ids = df[~df['transaction_id'].astype(str).str.match(r'^[A-Za-z0-9_-]+$')]
            if not invalid_ids.empty:
                errors.append(f"Invalid transaction ID format found in {len(invalid_ids)} records")
        
        return errors
    
    def _validate_data_ranges(self, df: pd.DataFrame) -> List[str]:
        """Validate data ranges"""
        warnings = []
        
        # Validate amount ranges
        if 'amount' in df.columns:
            min_amount, max_amount = self.validation_rules['amount_range']
            invalid_amounts = df[(df['amount'] < min_amount) | (df['amount'] > max_amount)]
            if not invalid_amounts.empty:
                warnings.append(f"{len(invalid_amounts)} records have amounts outside normal range")
        
        # Validate date ranges
        if 'transaction_date' in df.columns:
            min_date = self.validation_rules['date_range']['min']
            max_date = self.validation_rules['date_range']['max']
            # Convert to datetime if needed
            try:
                df_dates = pd.to_datetime(df['transaction_date'])
                invalid_dates = df[(df_dates < min_date) | (df_dates > max_date)]
                if not invalid_dates.empty:
                    warnings.append(f"{len(invalid_dates)} records have dates outside normal range")
            except Exception as e:
                warnings.append(f"Error validating date ranges: {str(e)}")
        
        return warnings
    
    def _validate_duplicates(self, df: pd.DataFrame) -> List[str]:
        """Check for duplicate records"""
        warnings = []
        
        if 'transaction_id' in df.columns:
            duplicates = df[df.duplicated(subset=['transaction_id'], keep=False)]
            if not duplicates.empty:
                warnings.append(f"Found {len(duplicates)} duplicate transaction IDs")
        
        return warnings
    
    def _calculate_quality_score(self, df: pd.DataFrame, validation_result: Dict[str, Any]) -> float:
        """Calculate data quality score (0-100)"""
        total_checks = len(df) * len(self.validation_rules['required_fields'])
        error_count = len(validation_result['errors'])
        warning_count = len(validation_result['warnings'])
        
        # Deduct points for errors and warnings
        score = 100.0
        score -= (error_count * 10)  # 10 points per error
        score -= (warning_count * 2)  # 2 points per warning
        
        return max(0.0, min(100.0, score))
    
    def validate_accounts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate account master data"""
        validation_result = {
            'is_valid': True,
            'total_records': len(df),
            'errors': [],
            'warnings': []
        }
        
        # Check for duplicate account codes
        if 'account_code' in df.columns:
            duplicates = df[df.duplicated(subset=['account_code'], keep=False)]
            if not duplicates.empty:
                validation_result['errors'].append(f"Found {len(duplicates)} duplicate account codes")
                validation_result['is_valid'] = False
        
        # Validate account types
        if 'account_type' in df.columns:
            invalid_types = df[~df['account_type'].isin(self.validation_rules['account_types'])]
            if not invalid_types.empty:
                validation_result['errors'].append(f"Invalid account types: {invalid_types['account_type'].unique().tolist()}")
                validation_result['is_valid'] = False
        
        return validation_result
    
    def validate_vendors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate vendor master data"""
        validation_result = {
            'is_valid': True,
            'total_records': len(df),
            'errors': [],
            'warnings': []
        }
        
        # Check for duplicate vendor codes
        if 'vendor_code' in df.columns:
            duplicates = df[df.duplicated(subset=['vendor_code'], keep=False)]
            if not duplicates.empty:
                validation_result['errors'].append(f"Found {len(duplicates)} duplicate vendor codes")
                validation_result['is_valid'] = False
        
        # Validate email format
        if 'contact_email' in df.columns:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            invalid_emails = df[df['contact_email'].notna() & ~df['contact_email'].str.match(email_pattern)]
            if not invalid_emails.empty:
                validation_result['warnings'].append(f"Found {len(invalid_emails)} invalid email formats")
        
        return validation_result

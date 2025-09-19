"""
CSV and Excel data ingestion module.
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CSVDataIngestion:
    """Handles data ingestion from CSV and Excel files"""
    
    def __init__(self, data_directory: str = 'sample_data'):
        self.data_directory = data_directory
        self.supported_formats = ['.csv', '.xlsx', '.xls']
    
    def get_available_files(self) -> List[str]:
        """Get list of available data files"""
        files = []
        if os.path.exists(self.data_directory):
            for file in os.listdir(self.data_directory):
                if any(file.lower().endswith(ext) for ext in self.supported_formats):
                    files.append(os.path.join(self.data_directory, file))
        return files
    
    def read_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Read data from CSV or Excel file"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                if sheet_name:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            logger.info(f"Successfully read {len(df)} rows from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def read_transactions(self, file_path: str) -> pd.DataFrame:
        """Read transaction data with standard column mapping"""
        df = self.read_file(file_path)
        
        # Standardize column names
        column_mapping = {
            'Transaction ID': 'transaction_id',
            'TransactionId': 'transaction_id',
            'ID': 'transaction_id',
            'Date': 'transaction_date',
            'Transaction Date': 'transaction_date',
            'Account': 'account_code',
            'Account Code': 'account_code',
            'Account Name': 'account_name',
            'Vendor': 'vendor_name',
            'Vendor Name': 'vendor_name',
            'Description': 'description',
            'Amount': 'amount',
            'Currency': 'currency',
            'Type': 'transaction_type',
            'Transaction Type': 'transaction_type',
            'Category': 'category',
            'Reference': 'reference_number',
            'Reference Number': 'reference_number'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Convert date column
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Ensure numeric columns
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        return df
    
    def read_accounts(self, file_path: str) -> pd.DataFrame:
        """Read account master data"""
        df = self.read_file(file_path)
        
        column_mapping = {
            'Account Code': 'account_code',
            'Code': 'account_code',
            'Account Name': 'account_name',
            'Name': 'account_name',
            'Type': 'account_type',
            'Account Type': 'account_type',
            'Parent Account': 'parent_account_code',
            'Parent Account Code': 'parent_account_code',
            'Active': 'is_active'
        }
        
        df = df.rename(columns=column_mapping)
        return df
    
    def read_vendors(self, file_path: str) -> pd.DataFrame:
        """Read vendor master data"""
        df = self.read_file(file_path)
        
        column_mapping = {
            'Vendor Code': 'vendor_code',
            'Code': 'vendor_code',
            'Vendor Name': 'vendor_name',
            'Name': 'vendor_name',
            'Type': 'vendor_type',
            'Vendor Type': 'vendor_type',
            'Email': 'contact_email',
            'Contact Email': 'contact_email',
            'Phone': 'contact_phone',
            'Contact Phone': 'contact_phone',
            'Address': 'address',
            'Active': 'is_active'
        }
        
        df = df.rename(columns=column_mapping)
        return df
    
    def validate_file_structure(self, df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
        """Validate file structure and return validation results"""
        validation_result = {
            'is_valid': True,
            'missing_columns': [],
            'data_quality_issues': [],
            'row_count': len(df)
        }
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_result['missing_columns'] = missing_columns
            validation_result['is_valid'] = False
        
        # Check for data quality issues
        if len(df) == 0:
            validation_result['data_quality_issues'].append("File is empty")
            validation_result['is_valid'] = False
        
        # Check for duplicate rows
        if df.duplicated().any():
            validation_result['data_quality_issues'].append(f"Found {df.duplicated().sum()} duplicate rows")
        
        # Check for missing values in critical columns
        for col in required_columns:
            if col in df.columns and df[col].isnull().any():
                missing_count = df[col].isnull().sum()
                validation_result['data_quality_issues'].append(f"Column '{col}' has {missing_count} missing values")
        
        return validation_result

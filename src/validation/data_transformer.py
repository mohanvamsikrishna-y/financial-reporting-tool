"""
Data transformation module for financial data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class DataTransformer:
    """Transforms and normalizes financial data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.exchange_rates = {}
        self.default_currency = self.config.get('default_currency', 'USD')
    
    def set_exchange_rates(self, exchange_rates_df: pd.DataFrame):
        """Set exchange rates for currency conversion"""
        if not exchange_rates_df.empty:
            self.exchange_rates = exchange_rates_df.set_index('currency')['rate_to_usd'].to_dict()
            logger.info(f"Loaded exchange rates for {len(self.exchange_rates)} currencies")
    
    def transform_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform transaction data"""
        logger.info(f"Transforming {len(df)} transaction records")
        
        # Create a copy to avoid modifying original data
        transformed_df = df.copy()
        
        # Standardize column names
        transformed_df = self._standardize_columns(transformed_df)
        
        # Clean and validate data
        transformed_df = self._clean_data(transformed_df)
        
        # Normalize currencies
        transformed_df = self._normalize_currencies(transformed_df)
        
        # Add calculated fields
        transformed_df = self._add_calculated_fields(transformed_df)
        
        # Categorize transactions
        transformed_df = self._categorize_transactions(transformed_df)
        
        logger.info("Transaction transformation completed")
        return transformed_df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and formats"""
        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # Standardize specific column names
        column_mapping = {
            'transactionid': 'transaction_id',
            'trans_date': 'transaction_date',
            'acct_code': 'account_code',
            'acct_name': 'account_name',
            'vend_name': 'vendor_name',
            'trans_type': 'transaction_type',
            'ref_num': 'reference_number'
        }
        
        df = df.rename(columns=column_mapping)
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data values"""
        # Clean string columns
        string_columns = ['transaction_id', 'description', 'reference_number', 'category']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
        
        # Clean transaction type
        if 'transaction_type' in df.columns:
            df['transaction_type'] = df['transaction_type'].str.strip().str.title()
            df['transaction_type'] = df['transaction_type'].replace({
                'DB': 'Debit',
                'CR': 'Credit',
                'DEBIT': 'Debit',
                'CREDIT': 'Credit'
            })
        
        # Clean currency codes
        if 'currency' in df.columns:
            df['currency'] = df['currency'].str.strip().str.upper()
            df['currency'] = df['currency'].fillna(self.default_currency)
        
        # Clean numeric columns
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df['amount'] = df['amount'].fillna(0)
        
        # Clean date columns
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        return df
    
    def _normalize_currencies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert all amounts to USD using exchange rates"""
        if 'currency' not in df.columns or 'amount' not in df.columns:
            return df
        
        # Add amount_usd column
        df['amount_usd'] = df['amount'].copy()
        
        # Convert non-USD amounts
        for currency, rate in self.exchange_rates.items():
            if currency != self.default_currency:
                mask = df['currency'] == currency
                df.loc[mask, 'amount_usd'] = df.loc[mask, 'amount'] * rate
        
        # Add exchange rate column
        df['exchange_rate'] = 1.0
        for currency, rate in self.exchange_rates.items():
            if currency != self.default_currency:
                mask = df['currency'] == currency
                df.loc[mask, 'exchange_rate'] = rate
        
        logger.info(f"Normalized currencies for {len(df)} records")
        return df
    
    def _add_calculated_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields to the dataset"""
        # Add month and year columns
        if 'transaction_date' in df.columns:
            df['transaction_month'] = df['transaction_date'].dt.to_period('M')
            df['transaction_year'] = df['transaction_date'].dt.year
            df['transaction_quarter'] = df['transaction_date'].dt.quarter
        
        # Add absolute amount for analysis
        if 'amount_usd' in df.columns:
            df['amount_abs'] = df['amount_usd'].abs()
        
        # Add transaction direction (positive for credits, negative for debits)
        if 'amount_usd' in df.columns and 'transaction_type' in df.columns:
            df['amount_signed'] = df['amount_usd'].copy()
            debit_mask = df['transaction_type'] == 'Debit'
            df.loc[debit_mask, 'amount_signed'] = -df.loc[debit_mask, 'amount_usd']
        
        return df
    
    def _categorize_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize transactions based on description and account"""
        if 'description' not in df.columns:
            return df
        
        # Define category mapping based on keywords
        category_keywords = {
            'Office Supplies': ['office', 'supplies', 'stationery', 'paper', 'pens'],
            'Travel': ['travel', 'hotel', 'flight', 'taxi', 'uber', 'lyft', 'mileage'],
            'Marketing': ['marketing', 'advertising', 'promotion', 'social media', 'campaign'],
            'Software': ['software', 'license', 'subscription', 'saas', 'cloud'],
            'Utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'utility'],
            'Rent': ['rent', 'lease', 'office space', 'warehouse'],
            'Professional Services': ['legal', 'accounting', 'consulting', 'audit', 'lawyer'],
            'Equipment': ['equipment', 'computer', 'laptop', 'printer', 'furniture'],
            'Insurance': ['insurance', 'premium', 'coverage'],
            'Training': ['training', 'course', 'education', 'conference', 'seminar']
        }
        
        # Apply categorization
        df['auto_category'] = 'Other'
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                mask = df['description'].str.contains(keyword, case=False, na=False)
                df.loc[mask, 'auto_category'] = category
        
        # Use existing category if available, otherwise use auto-categorized
        if 'category' in df.columns:
            df['final_category'] = df['category'].fillna(df['auto_category'])
        else:
            df['final_category'] = df['auto_category']
        
        return df
    
    def transform_accounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform account master data"""
        logger.info(f"Transforming {len(df)} account records")
        
        transformed_df = df.copy()
        
        # Standardize column names
        transformed_df = self._standardize_columns(transformed_df)
        
        # Clean account codes
        if 'account_code' in transformed_df.columns:
            transformed_df['account_code'] = transformed_df['account_code'].astype(str).str.strip().str.upper()
        
        # Clean account names
        if 'account_name' in transformed_df.columns:
            transformed_df['account_name'] = transformed_df['account_name'].astype(str).str.strip().str.title()
        
        # Clean account types
        if 'account_type' in transformed_df.columns:
            transformed_df['account_type'] = transformed_df['account_type'].str.strip().str.title()
        
        # Set default values
        transformed_df['is_active'] = transformed_df.get('is_active', 'Y')
        
        logger.info("Account transformation completed")
        return transformed_df
    
    def transform_vendors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform vendor master data"""
        logger.info(f"Transforming {len(df)} vendor records")
        
        transformed_df = df.copy()
        
        # Standardize column names
        transformed_df = self._standardize_columns(transformed_df)
        
        # Clean vendor codes
        if 'vendor_code' in transformed_df.columns:
            transformed_df['vendor_code'] = transformed_df['vendor_code'].astype(str).str.strip().str.upper()
        
        # Clean vendor names
        if 'vendor_name' in transformed_df.columns:
            transformed_df['vendor_name'] = transformed_df['vendor_name'].astype(str).str.strip().str.title()
        
        # Clean email addresses
        if 'contact_email' in transformed_df.columns:
            transformed_df['contact_email'] = transformed_df['contact_email'].astype(str).str.strip().str.lower()
        
        # Set default values
        transformed_df['is_active'] = transformed_df.get('is_active', 'Y')
        transformed_df['vendor_type'] = transformed_df.get('vendor_type', 'Supplier')
        
        logger.info("Vendor transformation completed")
        return transformed_df
    
    def aggregate_data(self, df: pd.DataFrame, group_by: List[str], agg_functions: Dict[str, str]) -> pd.DataFrame:
        """Aggregate data by specified columns"""
        logger.info(f"Aggregating data by {group_by}")
        
        aggregated_df = df.groupby(group_by).agg(agg_functions).reset_index()
        
        # Flatten column names
        aggregated_df.columns = ['_'.join(col).strip() if col[1] else col[0] for col in aggregated_df.columns.values]
        
        logger.info(f"Aggregation completed, {len(aggregated_df)} groups created")
        return aggregated_df

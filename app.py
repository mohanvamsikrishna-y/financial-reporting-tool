#!/usr/bin/env python3
"""
Streamlit app entry point for cloud deployment
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Initialize database and create sample data
from src.storage.database_manager import EnhancedDatabaseManager
from config.settings import DATABASE_URL
import pandas as pd
from datetime import datetime, timedelta
import random

def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        # Initialize database
        db_manager = EnhancedDatabaseManager(DATABASE_URL)
        db_manager.create_tables()
        
        # Check if data already exists
        data_summary = db_manager.get_data_summary()
        if data_summary.get('transactions', 0) > 0:
            return  # Data already exists
        
        # Create sample data
        create_sample_data(db_manager)
        
    except Exception as e:
        print(f"Error initializing database: {e}")

def create_sample_data(db_manager):
    """Create sample financial data"""
    try:
        # Sample accounts
        accounts_data = {
            'account_code': ['1001', '1002', '2001', '2002', '3001', '4001', '4002', '5001', '5002', '5003'],
            'account_name': ['Cash', 'Accounts Receivable', 'Accounts Payable', 'Accrued Expenses', 'Retained Earnings', 
                           'Sales Revenue', 'Service Revenue', 'Office Supplies', 'Travel Expenses', 'Marketing Expenses'],
            'account_type': ['Asset', 'Asset', 'Liability', 'Liability', 'Equity', 'Revenue', 'Revenue', 
                           'Expense', 'Expense', 'Expense'],
            'is_active': ['Y'] * 10
        }
        
        accounts_df = pd.DataFrame(accounts_data)
        db_manager.load_accounts(accounts_df)
        
        # Sample vendors
        vendors_data = {
            'vendor_code': ['V001', 'V002', 'V003', 'V004', 'V005'],
            'vendor_name': ['Office Depot', 'Delta Airlines', 'Google Ads', 'Amazon Web Services', 'Local Restaurant'],
            'vendor_type': ['Supplier', 'Travel', 'Marketing', 'Technology', 'Meals'],
            'contact_email': ['orders@officedepot.com', 'business@delta.com', 'support@google.com', 'support@aws.com', 'info@restaurant.com'],
            'is_active': ['Y'] * 5
        }
        
        vendors_df = pd.DataFrame(vendors_data)
        db_manager.load_vendors(vendors_df)
        
        # Sample transactions
        transactions_data = []
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(100):
            transaction_id = f"TXN{str(i+1).zfill(6)}"
            transaction_date = start_date + timedelta(days=random.randint(0, 90))
            
            # Random account and vendor
            account_code = random.choice(accounts_data['account_code'])
            vendor_code = random.choice(vendors_data['vendor_code']) if random.random() > 0.3 else None
            
            # Random amount and type
            amount = round(random.uniform(10, 5000), 2)
            transaction_type = random.choice(['Debit', 'Credit'])
            
            # Random description and category
            descriptions = ['Office supplies purchase', 'Business travel', 'Marketing campaign', 'Software license', 'Client meeting']
            categories = ['Office Supplies', 'Travel', 'Marketing', 'Software', 'Meals']
            
            description = random.choice(descriptions)
            category = random.choice(categories)
            
            transactions_data.append({
                'transaction_id': transaction_id,
                'transaction_date': transaction_date.strftime('%Y-%m-%d'),
                'account_code': account_code,
                'vendor_code': vendor_code,
                'description': description,
                'amount': amount,
                'currency': 'USD',
                'transaction_type': transaction_type,
                'category': category,
                'reference_number': f"REF{random.randint(1000, 9999)}"
            })
        
        transactions_df = pd.DataFrame(transactions_data)
        db_manager.load_transactions(transactions_df)
        
        print("Sample data created successfully")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

# Initialize database before running dashboard
initialize_database()

# Import and run the dashboard
from src.reporting.dashboard import run_dashboard

if __name__ == "__main__":
    run_dashboard()
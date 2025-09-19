"""
Configuration settings for the Financial Reporting Tool.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', 'free')  # Use free tier by default

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///financial_data.db')

# File Paths
SAMPLE_DATA_DIR = 'sample_data'
OUTPUT_DIR = 'outputs'
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
DASHBOARD_DIR = os.path.join(OUTPUT_DIR, 'dashboard')

# Report Configuration
REPORT_TYPES = {
    'P&L': 'Profit and Loss Statement',
    'EXPENSE_BREAKDOWN': 'Expense Breakdown by Category',
    'VENDOR_ANALYSIS': 'Vendor Analysis Report',
    'COMPLIANCE_LOG': 'Compliance and Audit Log'
}

# Currency Configuration
DEFAULT_CURRENCY = 'USD'
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']

# Exchange Rate API Configuration
EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'
EXCHANGE_RATE_UPDATE_FREQUENCY = 'daily'  # daily, weekly, monthly

# AI Summary Configuration
AI_SUMMARY_MODEL = 'gpt-3.5-turbo'
AI_SUMMARY_MAX_TOKENS = 500
AI_SUMMARY_TEMPERATURE = 0.7

# Scheduling Configuration
AUTO_REFRESH_ENABLED = True
REFRESH_SCHEDULE = 'daily'  # daily, weekly, monthly
REFRESH_TIME = '06:00'  # 6 AM

# Email Configuration (Optional)
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
NOTIFICATION_EMAILS = os.getenv('NOTIFICATION_EMAILS', '').split(',')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(OUTPUT_DIR, 'logs', 'financial_reporting.log')

# Validation Rules
MIN_TRANSACTION_AMOUNT = 0.01
MAX_TRANSACTION_AMOUNT = 1000000.00
REQUIRED_FIELDS = ['transaction_id', 'transaction_date', 'account_id', 'amount', 'transaction_type']

# Data Quality Thresholds
MAX_MISSING_DATA_PERCENTAGE = 5.0  # Maximum 5% missing data allowed
MIN_RECORDS_FOR_REPORT = 10  # Minimum records required to generate a report

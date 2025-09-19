"""
Data ingestion module for the Financial Reporting Tool.
Handles data extraction from various sources: CSV, Excel, APIs, and databases.
"""

from .csv_ingestion import CSVDataIngestion
from .api_ingestion import APIDataIngestion
from .database_ingestion import DatabaseDataIngestion

__all__ = ['CSVDataIngestion', 'APIDataIngestion', 'DatabaseDataIngestion']

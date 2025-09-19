import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from sqlalchemy import create_engine
import os

logger = logging.getLogger(__name__)

class RealDataConnector:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session = requests.Session()
        
    def connect_quickbooks(self, client_id: str, client_secret: str, 
                          company_id: str, access_token: str) -> Dict[str, Any]:
        """Connect to QuickBooks Online API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            # Get company info
            company_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/companyinfo/{company_id}"
            response = self.session.get(company_url, headers=headers)
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'provider': 'quickbooks',
                    'company_id': company_id,
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'QuickBooks API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"QuickBooks connection error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def connect_xero(self, client_id: str, client_secret: str, 
                    tenant_id: str, access_token: str) -> Dict[str, Any]:
        """Connect to Xero API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Xero-tenant-id': tenant_id,
                'Accept': 'application/json'
            }
            
            # Get organisation info
            org_url = "https://api.xero.com/api.xro/2.0/Organisation"
            response = self.session.get(org_url, headers=headers)
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'provider': 'xero',
                    'tenant_id': tenant_id,
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Xero API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Xero connection error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def connect_mysql(self, host: str, port: int, database: str, 
                     username: str, password: str) -> Dict[str, Any]:
        """Connect to MySQL database"""
        try:
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(connection_string)
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            
            return {
                'status': 'success',
                'provider': 'mysql',
                'connection_string': connection_string,
                'engine': engine
            }
            
        except Exception as e:
            logger.error(f"MySQL connection error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def connect_postgresql(self, host: str, port: int, database: str, 
                          username: str, password: str) -> Dict[str, Any]:
        """Connect to PostgreSQL database"""
        try:
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(connection_string)
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            
            return {
                'status': 'success',
                'provider': 'postgresql',
                'connection_string': connection_string,
                'engine': engine
            }
            
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def connect_salesforce(self, username: str, password: str, 
                          security_token: str, domain: str = 'login') -> Dict[str, Any]:
        """Connect to Salesforce API"""
        try:
            auth_url = f"https://{domain}.salesforce.com/services/oauth2/token"
            auth_data = {
                'grant_type': 'password',
                'client_id': self.config.get('salesforce_client_id', ''),
                'client_secret': self.config.get('salesforce_client_secret', ''),
                'username': username,
                'password': password + security_token
            }
            
            response = self.session.post(auth_url, data=auth_data)
            
            if response.status_code == 200:
                auth_response = response.json()
                return {
                    'status': 'success',
                    'provider': 'salesforce',
                    'access_token': auth_response.get('access_token'),
                    'instance_url': auth_response.get('instance_url')
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Salesforce authentication error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Salesforce connection error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def connect_google_sheets(self, credentials_file: str, 
                             spreadsheet_id: str) -> Dict[str, Any]:
        """Connect to Google Sheets API"""
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            credentials = Credentials.from_service_account_file(
                credentials_file, scopes=scopes
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            # Test connection
            sheet = service.spreadsheets()
            result = sheet.get(spreadsheetId=spreadsheet_id).execute()
            
            return {
                'status': 'success',
                'provider': 'google_sheets',
                'spreadsheet_id': spreadsheet_id,
                'service': service
            }
            
        except Exception as e:
            logger.error(f"Google Sheets connection error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def connect_excel_file(self, file_path: str) -> Dict[str, Any]:
        """Connect to Excel file"""
        try:
            if not os.path.exists(file_path):
                return {'status': 'error', 'message': 'File not found'}
            
            # Read Excel file to test
            df = pd.read_excel(file_path, nrows=1)
            
            return {
                'status': 'success',
                'provider': 'excel',
                'file_path': file_path,
                'columns': df.columns.tolist()
            }
            
        except Exception as e:
            logger.error(f"Excel file connection error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_data_from_source(self, connection: Dict[str, Any], 
                           data_type: str = 'transactions') -> pd.DataFrame:
        """Extract data from connected source"""
        try:
            provider = connection.get('provider')
            
            if provider == 'quickbooks':
                return self._get_quickbooks_data(connection, data_type)
            elif provider == 'xero':
                return self._get_xero_data(connection, data_type)
            elif provider in ['mysql', 'postgresql']:
                return self._get_database_data(connection, data_type)
            elif provider == 'salesforce':
                return self._get_salesforce_data(connection, data_type)
            elif provider == 'google_sheets':
                return self._get_google_sheets_data(connection, data_type)
            elif provider == 'excel':
                return self._get_excel_data(connection, data_type)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error getting data from {connection.get('provider')}: {str(e)}")
            return pd.DataFrame()
    
    def _get_quickbooks_data(self, connection: Dict[str, Any], data_type: str) -> pd.DataFrame:
        """Extract data from QuickBooks"""
        # Implementation for QuickBooks data extraction
        return pd.DataFrame()
    
    def _get_xero_data(self, connection: Dict[str, Any], data_type: str) -> pd.DataFrame:
        """Extract data from Xero"""
        # Implementation for Xero data extraction
        return pd.DataFrame()
    
    def _get_database_data(self, connection: Dict[str, Any], data_type: str) -> pd.DataFrame:
        """Extract data from database"""
        engine = connection.get('engine')
        if not engine:
            return pd.DataFrame()
        
        # Define queries based on data type
        queries = {
            'transactions': "SELECT * FROM transactions WHERE transaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
            'accounts': "SELECT * FROM accounts WHERE is_active = 1",
            'vendors': "SELECT * FROM vendors WHERE is_active = 1"
        }
        
        query = queries.get(data_type, queries['transactions'])
        
        try:
            return pd.read_sql(query, engine)
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            return pd.DataFrame()
    
    def _get_salesforce_data(self, connection: Dict[str, Any], data_type: str) -> pd.DataFrame:
        """Extract data from Salesforce"""
        # Implementation for Salesforce data extraction
        return pd.DataFrame()
    
    def _get_google_sheets_data(self, connection: Dict[str, Any], data_type: str) -> pd.DataFrame:
        """Extract data from Google Sheets"""
        service = connection.get('service')
        spreadsheet_id = connection.get('spreadsheet_id')
        
        if not service or not spreadsheet_id:
            return pd.DataFrame()
        
        # Define sheet ranges based on data type
        ranges = {
            'transactions': 'Transactions!A:Z',
            'accounts': 'Accounts!A:Z',
            'vendors': 'Vendors!A:Z'
        }
        
        range_name = ranges.get(data_type, ranges['transactions'])
        
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            return df
            
        except Exception as e:
            logger.error(f"Google Sheets data extraction error: {str(e)}")
            return pd.DataFrame()
    
    def _get_excel_data(self, connection: Dict[str, Any], data_type: str) -> pd.DataFrame:
        """Extract data from Excel file"""
        file_path = connection.get('file_path')
        if not file_path:
            return pd.DataFrame()
        
        # Define sheet names based on data type
        sheet_names = {
            'transactions': 'Transactions',
            'accounts': 'Accounts',
            'vendors': 'Vendors'
        }
        
        sheet_name = sheet_names.get(data_type, 'Sheet1')
        
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Excel data extraction error: {str(e)}")
            return pd.DataFrame()

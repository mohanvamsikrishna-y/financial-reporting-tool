"""
Database data ingestion module.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class DatabaseDataIngestion:
    """Handles data ingestion from external databases"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # Convert to DataFrame
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                logger.info(f"Query executed successfully, returned {len(df)} rows")
                return df
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """Get table schema information"""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = :table_name
        ORDER BY ordinal_position
        """
        
        try:
            return self.execute_query(query, {'table_name': table_name})
        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {str(e)}")
            return pd.DataFrame()
    
    def get_table_data(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Get data from a specific table"""
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query)
    
    def get_transaction_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Get transaction data with optional date filtering"""
        query = """
        SELECT 
            transaction_id,
            transaction_date,
            account_code,
            account_name,
            vendor_name,
            description,
            amount,
            currency,
            transaction_type,
            category,
            reference_number
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        LEFT JOIN vendors v ON t.vendor_id = v.id
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND transaction_date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND transaction_date <= :end_date"
            params['end_date'] = end_date
        
        query += " ORDER BY transaction_date DESC"
        
        return self.execute_query(query, params)
    
    def get_account_balances(self, as_of_date: Optional[str] = None) -> pd.DataFrame:
        """Get account balances as of a specific date"""
        if as_of_date is None:
            as_of_date = "CURRENT_DATE"
        
        query = f"""
        SELECT 
            a.account_code,
            a.account_name,
            a.account_type,
            COALESCE(SUM(
                CASE 
                    WHEN t.transaction_type = 'Debit' THEN t.amount_usd
                    WHEN t.transaction_type = 'Credit' THEN -t.amount_usd
                    ELSE 0
                END
            ), 0) as balance
        FROM accounts a
        LEFT JOIN transactions t ON a.id = t.account_id 
            AND t.transaction_date <= {as_of_date}
        WHERE a.is_active = 'Y'
        GROUP BY a.id, a.account_code, a.account_name, a.account_type
        ORDER BY a.account_type, a.account_code
        """
        
        return self.execute_query(query)
    
    def close_connection(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

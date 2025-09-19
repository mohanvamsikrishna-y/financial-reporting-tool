"""
Data loader module for querying and retrieving data from the database.
"""

import pandas as pd
from sqlalchemy import text
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from .database_manager import EnhancedDatabaseManager

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles data retrieval and querying from the database"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
    
    def get_transactions(self, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None,
                        account_codes: Optional[List[str]] = None,
                        vendor_codes: Optional[List[str]] = None,
                        transaction_types: Optional[List[str]] = None) -> pd.DataFrame:
        """Get transaction data with optional filters"""
        
        query = """
        SELECT 
            t.id,
            t.transaction_id,
            t.transaction_date,
            a.account_code,
            a.account_name,
            a.account_type,
            v.vendor_code,
            v.vendor_name,
            t.description,
            t.amount,
            t.currency,
            t.exchange_rate,
            t.amount_usd,
            t.transaction_type,
            t.category,
            t.reference_number,
            t.created_at
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        LEFT JOIN vendors v ON t.vendor_id = v.id
        WHERE 1=1
        """
        
        params = {}
        
        if start_date:
            query += " AND t.transaction_date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND t.transaction_date <= :end_date"
            params['end_date'] = end_date
        
        if account_codes:
            placeholders = ','.join([f':account_code_{i}' for i in range(len(account_codes))])
            query += f" AND a.account_code IN ({placeholders})"
            for i, code in enumerate(account_codes):
                params[f'account_code_{i}'] = code
        
        if vendor_codes:
            placeholders = ','.join([f':vendor_code_{i}' for i in range(len(vendor_codes))])
            query += f" AND v.vendor_code IN ({placeholders})"
            for i, code in enumerate(vendor_codes):
                params[f'vendor_code_{i}'] = code
        
        if transaction_types:
            placeholders = ','.join([f':transaction_type_{i}' for i in range(len(transaction_types))])
            query += f" AND t.transaction_type IN ({placeholders})"
            for i, t_type in enumerate(transaction_types):
                params[f'transaction_type_{i}'] = t_type
        
        query += " ORDER BY t.transaction_date DESC, t.id DESC"
        
        session = self.db_manager.get_session()
        try:
            result = session.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Retrieved {len(df)} transaction records")
            return df
        except Exception as e:
            logger.error(f"Error retrieving transactions: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_profit_loss_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get Profit & Loss data for the specified period"""
        
        query = """
        SELECT 
            a.account_type,
            a.account_code,
            a.account_name,
            SUM(CASE 
                WHEN t.transaction_type = 'Credit' THEN t.amount_usd
                WHEN t.transaction_type = 'Debit' THEN -t.amount_usd
                ELSE 0
            END) as net_amount
        FROM accounts a
        LEFT JOIN transactions t ON a.id = t.account_id 
            AND t.transaction_date >= :start_date 
            AND t.transaction_date <= :end_date
        WHERE a.account_type IN ('Revenue', 'Expense')
        GROUP BY a.id, a.account_type, a.account_code, a.account_name
        HAVING SUM(CASE 
            WHEN t.transaction_type = 'Credit' THEN t.amount_usd
            WHEN t.transaction_type = 'Debit' THEN -t.amount_usd
            ELSE 0
        END) != 0
        ORDER BY a.account_type, a.account_code
        """
        
        session = self.db_manager.get_session()
        try:
            result = session.execute(text(query), {
                'start_date': start_date,
                'end_date': end_date
            })
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Retrieved P&L data for {len(df)} accounts")
            return df
        except Exception as e:
            logger.error(f"Error retrieving P&L data: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_expense_breakdown(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get expense breakdown by category"""
        
        query = """
        SELECT 
            COALESCE(t.category, 'Uncategorized') as category,
            COUNT(*) as transaction_count,
            SUM(t.amount_usd) as total_amount,
            AVG(t.amount_usd) as avg_amount,
            MIN(t.amount_usd) as min_amount,
            MAX(t.amount_usd) as max_amount
        FROM transactions t
        INNER JOIN accounts a ON t.account_id = a.id
        WHERE a.account_type = 'Expense'
            AND t.transaction_date >= :start_date
            AND t.transaction_date <= :end_date
        GROUP BY COALESCE(t.category, 'Uncategorized')
        ORDER BY total_amount DESC
        """
        
        session = self.db_manager.get_session()
        try:
            result = session.execute(text(query), {
                'start_date': start_date,
                'end_date': end_date
            })
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Retrieved expense breakdown for {len(df)} categories")
            return df
        except Exception as e:
            logger.error(f"Error retrieving expense breakdown: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_vendor_analysis(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get vendor analysis data"""
        
        query = """
        SELECT 
            v.vendor_code,
            v.vendor_name,
            v.vendor_type,
            COUNT(t.id) as transaction_count,
            SUM(t.amount_usd) as total_amount,
            AVG(t.amount_usd) as avg_amount,
            MIN(t.transaction_date) as first_transaction,
            MAX(t.transaction_date) as last_transaction
        FROM vendors v
        INNER JOIN transactions t ON v.id = t.vendor_id
        WHERE t.transaction_date >= :start_date
            AND t.transaction_date <= :end_date
        GROUP BY v.id, v.vendor_code, v.vendor_name, v.vendor_type
        ORDER BY total_amount DESC
        """
        
        session = self.db_manager.get_session()
        try:
            result = session.execute(text(query), {
                'start_date': start_date,
                'end_date': end_date
            })
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Retrieved vendor analysis for {len(df)} vendors")
            return df
        except Exception as e:
            logger.error(f"Error retrieving vendor analysis: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_monthly_trends(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get monthly trend data"""
        
        query = """
        SELECT 
            DATE_TRUNC('month', t.transaction_date) as month,
            a.account_type,
            SUM(CASE 
                WHEN t.transaction_type = 'Credit' THEN t.amount_usd
                WHEN t.transaction_type = 'Debit' THEN -t.amount_usd
                ELSE 0
            END) as net_amount
        FROM transactions t
        INNER JOIN accounts a ON t.account_id = a.id
        WHERE t.transaction_date >= :start_date
            AND t.transaction_date <= :end_date
        GROUP BY DATE_TRUNC('month', t.transaction_date), a.account_type
        ORDER BY month, a.account_type
        """
        
        session = self.db_manager.get_session()
        try:
            result = session.execute(text(query), {
                'start_date': start_date,
                'end_date': end_date
            })
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Retrieved monthly trends for {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error retrieving monthly trends: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_account_balances(self, as_of_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get account balances as of a specific date"""
        
        if as_of_date is None:
            as_of_date = datetime.now()
        
        query = """
        SELECT 
            a.account_code,
            a.account_name,
            a.account_type,
            COALESCE(SUM(
                CASE 
                    WHEN t.transaction_type = 'Credit' THEN t.amount_usd
                    WHEN t.transaction_type = 'Debit' THEN -t.amount_usd
                    ELSE 0
                END
            ), 0) as balance
        FROM accounts a
        LEFT JOIN transactions t ON a.id = t.account_id 
            AND t.transaction_date <= :as_of_date
        WHERE a.is_active = 'Y'
        GROUP BY a.id, a.account_code, a.account_name, a.account_type
        ORDER BY a.account_type, a.account_code
        """
        
        session = self.db_manager.get_session()
        try:
            result = session.execute(text(query), {'as_of_date': as_of_date})
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Retrieved account balances for {len(df)} accounts")
            return df
        except Exception as e:
            logger.error(f"Error retrieving account balances: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_compliance_log(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get compliance and audit log data"""
        
        query = """
        SELECT 
            t.transaction_id,
            t.transaction_date,
            a.account_code,
            a.account_name,
            v.vendor_name,
            t.description,
            t.amount_usd,
            t.transaction_type,
            t.category,
            t.reference_number,
            t.created_at,
            t.updated_at
        FROM transactions t
        INNER JOIN accounts a ON t.account_id = a.id
        LEFT JOIN vendors v ON t.vendor_id = v.id
        WHERE t.transaction_date >= :start_date
            AND t.transaction_date <= :end_date
        ORDER BY t.transaction_date DESC, t.created_at DESC
        """
        
        session = self.db_manager.get_session()
        try:
            result = session.execute(text(query), {
                'start_date': start_date,
                'end_date': end_date
            })
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            logger.info(f"Retrieved compliance log with {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error retrieving compliance log: {str(e)}")
            raise
        finally:
            session.close()

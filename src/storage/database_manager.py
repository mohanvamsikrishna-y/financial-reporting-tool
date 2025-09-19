"""
Database management module for the Financial Reporting Tool.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import os

from config.database import Base, Account, Vendor, Transaction, ExchangeRate, ReportLog, DatabaseManager

logger = logging.getLogger(__name__)

class EnhancedDatabaseManager(DatabaseManager):
    """Enhanced database manager with additional functionality"""
    
    def __init__(self, database_url: str = None):
        super().__init__(database_url)
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = ['outputs', 'outputs/reports', 'outputs/logs', 'outputs/dashboard']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_accounts(self, accounts_df: pd.DataFrame) -> Dict[str, Any]:
        """Load account master data"""
        logger.info(f"Loading {len(accounts_df)} account records")
        
        session = self.get_session()
        try:
            loaded_count = 0
            updated_count = 0
            errors = []
            
            for _, row in accounts_df.iterrows():
                try:
                    # Check if account already exists
                    existing_account = session.query(Account).filter(
                        Account.account_code == row['account_code']
                    ).first()
                    
                    if existing_account:
                        # Update existing account
                        existing_account.account_name = row['account_name']
                        existing_account.account_type = row['account_type']
                        existing_account.is_active = row.get('is_active', 'Y')
                        existing_account.updated_at = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new account
                        account = Account(
                            account_code=row['account_code'],
                            account_name=row['account_name'],
                            account_type=row['account_type'],
                            is_active=row.get('is_active', 'Y')
                        )
                        session.add(account)
                        loaded_count += 1
                    
                except Exception as e:
                    error_msg = f"Error processing account {row.get('account_code', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            session.commit()
            
            result = {
                'loaded_count': loaded_count,
                'updated_count': updated_count,
                'error_count': len(errors),
                'errors': errors
            }
            
            logger.info(f"Account loading completed: {loaded_count} new, {updated_count} updated, {len(errors)} errors")
            return result
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading accounts: {str(e)}")
            raise
        finally:
            session.close()
    
    def load_vendors(self, vendors_df: pd.DataFrame) -> Dict[str, Any]:
        """Load vendor master data"""
        logger.info(f"Loading {len(vendors_df)} vendor records")
        
        session = self.get_session()
        try:
            loaded_count = 0
            updated_count = 0
            errors = []
            
            for _, row in vendors_df.iterrows():
                try:
                    # Check if vendor already exists
                    existing_vendor = session.query(Vendor).filter(
                        Vendor.vendor_code == row['vendor_code']
                    ).first()
                    
                    if existing_vendor:
                        # Update existing vendor
                        existing_vendor.vendor_name = row['vendor_name']
                        existing_vendor.vendor_type = row.get('vendor_type', 'Supplier')
                        existing_vendor.contact_email = row.get('contact_email')
                        existing_vendor.contact_phone = row.get('contact_phone')
                        existing_vendor.address = row.get('address')
                        existing_vendor.is_active = row.get('is_active', 'Y')
                        existing_vendor.updated_at = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new vendor
                        vendor = Vendor(
                            vendor_code=row['vendor_code'],
                            vendor_name=row['vendor_name'],
                            vendor_type=row.get('vendor_type', 'Supplier'),
                            contact_email=row.get('contact_email'),
                            contact_phone=row.get('contact_phone'),
                            address=row.get('address'),
                            is_active=row.get('is_active', 'Y')
                        )
                        session.add(vendor)
                        loaded_count += 1
                    
                except Exception as e:
                    error_msg = f"Error processing vendor {row.get('vendor_code', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            session.commit()
            
            result = {
                'loaded_count': loaded_count,
                'updated_count': updated_count,
                'error_count': len(errors),
                'errors': errors
            }
            
            logger.info(f"Vendor loading completed: {loaded_count} new, {updated_count} updated, {len(errors)} errors")
            return result
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading vendors: {str(e)}")
            raise
        finally:
            session.close()
    
    def load_transactions(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Load transaction data"""
        logger.info(f"Loading {len(transactions_df)} transaction records")
        
        session = self.get_session()
        try:
            loaded_count = 0
            updated_count = 0
            errors = []
            
            for _, row in transactions_df.iterrows():
                try:
                    # Get account ID
                    account = session.query(Account).filter(
                        Account.account_code == row['account_code']
                    ).first()
                    
                    if not account:
                        errors.append(f"Account not found for code: {row['account_code']}")
                        continue
                    
                    # Get vendor ID if vendor_code is provided
                    vendor_id = None
                    if 'vendor_code' in row and pd.notna(row['vendor_code']):
                        vendor = session.query(Vendor).filter(
                            Vendor.vendor_code == row['vendor_code']
                        ).first()
                        if vendor:
                            vendor_id = vendor.id
                    
                    # Check if transaction already exists
                    existing_transaction = session.query(Transaction).filter(
                        Transaction.transaction_id == row['transaction_id']
                    ).first()
                    
                    if existing_transaction:
                        # Update existing transaction
                        existing_transaction.transaction_date = row['transaction_date']
                        existing_transaction.account_id = account.id
                        existing_transaction.vendor_id = vendor_id
                        existing_transaction.description = row.get('description')
                        existing_transaction.amount = row['amount']
                        existing_transaction.currency = row.get('currency', 'USD')
                        existing_transaction.exchange_rate = row.get('exchange_rate', 1.0)
                        existing_transaction.amount_usd = row.get('amount_usd', row['amount'])
                        existing_transaction.transaction_type = row['transaction_type']
                        existing_transaction.category = row.get('final_category') or row.get('category')
                        existing_transaction.reference_number = row.get('reference_number')
                        existing_transaction.updated_at = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new transaction
                        transaction = Transaction(
                            transaction_id=row['transaction_id'],
                            transaction_date=row['transaction_date'],
                            account_id=account.id,
                            vendor_id=vendor_id,
                            description=row.get('description'),
                            amount=row['amount'],
                            currency=row.get('currency', 'USD'),
                            exchange_rate=row.get('exchange_rate', 1.0),
                            amount_usd=row.get('amount_usd', row['amount']),
                            transaction_type=row['transaction_type'],
                            category=row.get('final_category') or row.get('category'),
                            reference_number=row.get('reference_number')
                        )
                        session.add(transaction)
                        loaded_count += 1
                    
                except Exception as e:
                    error_msg = f"Error processing transaction {row.get('transaction_id', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            session.commit()
            
            result = {
                'loaded_count': loaded_count,
                'updated_count': updated_count,
                'error_count': len(errors),
                'errors': errors
            }
            
            logger.info(f"Transaction loading completed: {loaded_count} new, {updated_count} updated, {len(errors)} errors")
            return result
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading transactions: {str(e)}")
            raise
        finally:
            session.close()
    
    def load_exchange_rates(self, rates_df: pd.DataFrame) -> Dict[str, Any]:
        """Load exchange rate data"""
        logger.info(f"Loading {len(rates_df)} exchange rate records")
        
        session = self.get_session()
        try:
            loaded_count = 0
            errors = []
            
            for _, row in rates_df.iterrows():
                try:
                    # Check if rate already exists for this date and currency
                    existing_rate = session.query(ExchangeRate).filter(
                        ExchangeRate.currency == row['currency'],
                        ExchangeRate.rate_date == row['rate_date']
                    ).first()
                    
                    if not existing_rate:
                        rate = ExchangeRate(
                            currency=row['currency'],
                            rate_to_usd=row['rate_to_usd'],
                            rate_date=row['rate_date'],
                            source=row.get('source', 'API')
                        )
                        session.add(rate)
                        loaded_count += 1
                    
                except Exception as e:
                    error_msg = f"Error processing exchange rate for {row.get('currency', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            session.commit()
            
            result = {
                'loaded_count': loaded_count,
                'error_count': len(errors),
                'errors': errors
            }
            
            logger.info(f"Exchange rate loading completed: {loaded_count} new, {len(errors)} errors")
            return result
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading exchange rates: {str(e)}")
            raise
        finally:
            session.close()
    
    def log_report_generation(self, report_type: str, report_period: str, file_path: str, 
                            status: str = 'SUCCESS', error_message: str = None, record_count: int = 0):
        """Log report generation activity"""
        session = self.get_session()
        try:
            log_entry = ReportLog(
                report_type=report_type,
                report_period=report_period,
                file_path=file_path,
                status=status,
                error_message=error_message,
                record_count=record_count
            )
            session.add(log_entry)
            session.commit()
            logger.info(f"Report generation logged: {report_type} - {status}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging report generation: {str(e)}")
        finally:
            session.close()
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of data in the database"""
        session = self.get_session()
        try:
            summary = {
                'accounts': session.query(Account).count(),
                'vendors': session.query(Vendor).count(),
                'transactions': session.query(Transaction).count(),
                'exchange_rates': session.query(ExchangeRate).count(),
                'report_logs': session.query(ReportLog).count()
            }
            
            # Get date range of transactions
            if summary['transactions'] > 0:
                min_date = session.query(Transaction.transaction_date).order_by(Transaction.transaction_date.asc()).first()[0]
                max_date = session.query(Transaction.transaction_date).order_by(Transaction.transaction_date.desc()).first()[0]
                summary['transaction_date_range'] = {
                    'min_date': min_date,
                    'max_date': max_date
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting data summary: {str(e)}")
            return {}
        finally:
            session.close()

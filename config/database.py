"""
Database configuration and schema definitions for the Financial Reporting Tool.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Account(Base):
    """Account master table"""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    account_code = Column(String(20), unique=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    parent_account_id = Column(Integer, ForeignKey('accounts.id'))
    is_active = Column(String(1), default='Y')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_account = relationship("Account", remote_side=[id])
    transactions = relationship("Transaction", back_populates="account")

class Vendor(Base):
    """Vendor master table"""
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True)
    vendor_code = Column(String(20), unique=True, nullable=False)
    vendor_name = Column(String(100), nullable=False)
    vendor_type = Column(String(50))  # Supplier, Customer, Service Provider
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    address = Column(Text)
    is_active = Column(String(1), default='Y')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="vendor")

class Transaction(Base):
    """Transaction details table"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(50), unique=True, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    description = Column(Text)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    exchange_rate = Column(Float, default=1.0)
    amount_usd = Column(Float, nullable=False)  # Normalized amount in USD
    transaction_type = Column(String(20), nullable=False)  # Debit, Credit
    category = Column(String(50))  # Office Supplies, Travel, Marketing, etc.
    reference_number = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    vendor = relationship("Vendor", back_populates="transactions")

class ExchangeRate(Base):
    """Exchange rates table"""
    __tablename__ = 'exchange_rates'
    
    id = Column(Integer, primary_key=True)
    currency = Column(String(3), nullable=False)
    rate_to_usd = Column(Float, nullable=False)
    rate_date = Column(DateTime, nullable=False)
    source = Column(String(50))  # API, Manual, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportLog(Base):
    """Report generation log"""
    __tablename__ = 'report_logs'
    
    id = Column(Integer, primary_key=True)
    report_type = Column(String(50), nullable=False)  # P&L, Expense Breakdown, etc.
    report_period = Column(String(20), nullable=False)  # 2024-01, 2024-Q1, etc.
    generated_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(200))
    status = Column(String(20), default='SUCCESS')  # SUCCESS, FAILED, PARTIAL
    error_message = Column(Text)
    record_count = Column(Integer)

class DatabaseManager:
    """Database connection and management"""
    
    def __init__(self, database_url=None):
        if database_url is None:
            # Default to SQLite for development
            database_url = "sqlite:///financial_data.db"
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        print("Database tables created successfully!")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def close_connection(self):
        """Close database connection"""
        self.engine.dispose()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///financial_data.db')

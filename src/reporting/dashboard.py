"""
Streamlit dashboard for the Financial Reporting Tool.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional
from .ai_chat import create_ai_chat_interface

logger = logging.getLogger(__name__)

def create_dashboard(data_loader, db_manager):
    """Create the main Streamlit dashboard"""
    
    st.set_page_config(
        page_title="Financial Reporting Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📊 Financial Reporting Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📅 Report Period")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        
        # Report type selector
        st.header("📋 Report Types")
        report_types = st.multiselect(
            "Select Reports to Display",
            ["P&L", "Expense Breakdown", "Vendor Analysis", "Compliance Log", "AI Assistant"],
            default=["P&L", "Expense Breakdown"]
        )
        
        # Account filter
        st.header("🔍 Filters")
        account_types = st.multiselect(
            "Account Types",
            ["Asset", "Liability", "Equity", "Revenue", "Expense"],
            default=["Revenue", "Expense"]
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
        
        # AI Assistant info
        if "AI Assistant" in report_types:
            st.markdown("---")
            st.markdown("**🤖 AI Assistant**")
            st.markdown("Ask questions about your financial data and get instant AI-powered insights using Google Gemini.")
    
    # Convert dates to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Get data summary
    data_summary = db_manager.get_data_summary()
    
    # Main content
    if not report_types:
        st.warning("Please select at least one report type from the sidebar.")
        return
    
    # Overview metrics
    st.header("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Accounts",
            value=f"{data_summary.get('accounts', 0):,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Vendors",
            value=f"{data_summary.get('vendors', 0):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Transactions",
            value=f"{data_summary.get('transactions', 0):,}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Report Period",
            value=f"{(end_date - start_date).days} days",
            delta=None
        )
    
    st.divider()
    
    # Generate reports based on selection
    if "P&L" in report_types:
        display_profit_loss(data_loader, start_datetime, end_datetime)
    
    if "Expense Breakdown" in report_types:
        display_expense_breakdown(data_loader, start_datetime, end_datetime)
    
    if "Vendor Analysis" in report_types:
        display_vendor_analysis(data_loader, start_datetime, end_datetime)
    
    if "Compliance Log" in report_types:
        display_compliance_log(data_loader, start_datetime, end_datetime)
    
    if "AI Assistant" in report_types:
        create_ai_chat_interface(data_loader, db_manager)
    
    # Footer
    st.divider()
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | "
        f"Financial Reporting Tool v1.0"
        f"</div>",
        unsafe_allow_html=True
    )

def display_profit_loss(data_loader, start_datetime, end_datetime):
    """Display Profit & Loss section"""
    st.header("💰 Profit & Loss Statement")
    
    try:
        pnl_data = data_loader.get_profit_loss_data(start_datetime, end_datetime)
        
        if pnl_data.empty:
            st.warning("No P&L data available for the selected period.")
            return
        
        # Calculate totals
        revenue_data = pnl_data[pnl_data['account_type'] == 'Revenue']
        expense_data = pnl_data[pnl_data['account_type'] == 'Expense']
        
        revenue_total = revenue_data['net_amount'].sum()
        expense_total = expense_data['net_amount'].sum()
        net_income = revenue_total - expense_total
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Revenue",
                value=f"${revenue_total:,.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Expenses",
                value=f"${expense_total:,.2f}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Net Income",
                value=f"${net_income:,.2f}",
                delta=None,
                delta_color="normal" if net_income >= 0 else "inverse"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue vs Expenses pie chart
            if revenue_total > 0 or expense_total > 0:
                fig_pie = px.pie(
                    values=[revenue_total, expense_total],
                    names=['Revenue', 'Expenses'],
                    title="Revenue vs Expenses",
                    color_discrete_sequence=['#2E8B57', '#DC143C']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # P&L by account type
            if not pnl_data.empty:
                fig_bar = px.bar(
                    pnl_data,
                    x='account_name',
                    y='net_amount',
                    color='account_type',
                    title="P&L by Account",
                    labels={'net_amount': 'Amount (USD)', 'account_name': 'Account Name'}
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Data table
        st.subheader("📋 Detailed P&L Data")
        st.dataframe(
            pnl_data,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error loading P&L data: {str(e)}")
        logger.error(f"Error loading P&L data: {str(e)}")

def display_expense_breakdown(data_loader, start_datetime, end_datetime):
    """Display Expense Breakdown section"""
    st.header("💸 Expense Breakdown")
    
    try:
        expense_data = data_loader.get_expense_breakdown(start_datetime, end_datetime)
        
        if expense_data.empty:
            st.warning("No expense data available for the selected period.")
            return
        
        # Summary metrics
        total_expenses = expense_data['total_amount'].sum()
        total_transactions = expense_data['transaction_count'].sum()
        avg_transaction = total_expenses / total_transactions if total_transactions > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Expenses",
                value=f"${total_expenses:,.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Transactions",
                value=f"{total_transactions:,}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Average Transaction",
                value=f"${avg_transaction:,.2f}",
                delta=None
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Expense breakdown pie chart
            fig_pie = px.pie(
                expense_data,
                values='total_amount',
                names='category',
                title="Expenses by Category"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Expense breakdown bar chart
            fig_bar = px.bar(
                expense_data,
                x='category',
                y='total_amount',
                title="Expenses by Category",
                labels={'total_amount': 'Amount (USD)', 'category': 'Category'}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Data table
        st.subheader("📋 Detailed Expense Data")
        st.dataframe(
            expense_data,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error loading expense data: {str(e)}")
        logger.error(f"Error loading expense data: {str(e)}")

def display_vendor_analysis(data_loader, start_datetime, end_datetime):
    """Display Vendor Analysis section"""
    st.header("🏢 Vendor Analysis")
    
    try:
        vendor_data = data_loader.get_vendor_analysis(start_datetime, end_datetime)
        
        if vendor_data.empty:
            st.warning("No vendor data available for the selected period.")
            return
        
        # Summary metrics
        total_amount = vendor_data['total_amount'].sum()
        total_vendors = len(vendor_data)
        avg_vendor_amount = total_amount / total_vendors if total_vendors > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Amount",
                value=f"${total_amount:,.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Vendors",
                value=f"{total_vendors:,}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Average per Vendor",
                value=f"${avg_vendor_amount:,.2f}",
                delta=None
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top vendors bar chart
            top_vendors = vendor_data.head(10)
            fig_bar = px.bar(
                top_vendors,
                x='vendor_name',
                y='total_amount',
                title="Top 10 Vendors by Spending",
                labels={'total_amount': 'Amount (USD)', 'vendor_name': 'Vendor Name'}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Vendor type distribution
            vendor_type_data = vendor_data.groupby('vendor_type')['total_amount'].sum().reset_index()
            fig_pie = px.pie(
                vendor_type_data,
                values='total_amount',
                names='vendor_type',
                title="Spending by Vendor Type"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Data table
        st.subheader("📋 Detailed Vendor Data")
        st.dataframe(
            vendor_data,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error loading vendor data: {str(e)}")
        logger.error(f"Error loading vendor data: {str(e)}")

def display_compliance_log(data_loader, start_datetime, end_datetime):
    """Display Compliance Log section"""
    st.header("🔍 Compliance & Audit Log")
    
    try:
        compliance_data = data_loader.get_compliance_log(start_datetime, end_datetime)
        
        if compliance_data.empty:
            st.warning("No compliance data available for the selected period.")
            return
        
        # Summary metrics
        total_amount = compliance_data['amount_usd'].sum()
        total_transactions = len(compliance_data)
        avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Amount",
                value=f"${total_amount:,.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Transactions",
                value=f"{total_transactions:,}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Average Transaction",
                value=f"${avg_transaction:,.2f}",
                delta=None
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction type distribution
            transaction_type_data = compliance_data['transaction_type'].value_counts().reset_index()
            transaction_type_data.columns = ['transaction_type', 'count']
            fig_pie = px.pie(
                transaction_type_data,
                values='count',
                names='transaction_type',
                title="Transaction Types"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Daily transaction volume
            daily_data = compliance_data.groupby(compliance_data['transaction_date'].dt.date)['amount_usd'].sum().reset_index()
            daily_data.columns = ['date', 'amount']
            fig_line = px.line(
                daily_data,
                x='date',
                y='amount',
                title="Daily Transaction Volume",
                labels={'amount': 'Amount (USD)', 'date': 'Date'}
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Data table
        st.subheader("📋 Transaction Audit Log")
        st.dataframe(
            compliance_data,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error loading compliance data: {str(e)}")
        logger.error(f"Error loading compliance data: {str(e)}")

def run_dashboard():
    """Run the Streamlit dashboard"""
    import sys
    import os
    
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)
    
    from src.storage.database_manager import EnhancedDatabaseManager
    from src.storage.data_loader import DataLoader
    from config.settings import DATABASE_URL
    
    # Initialize database and data loader
    db_manager = EnhancedDatabaseManager(DATABASE_URL)
    data_loader = DataLoader(db_manager)
    
    # Create and run dashboard
    create_dashboard(data_loader, db_manager)

if __name__ == '__main__':
    run_dashboard()
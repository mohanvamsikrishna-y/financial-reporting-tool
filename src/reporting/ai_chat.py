import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from src.ai_summary.ai_summarizer import AISummarizer

logger = logging.getLogger(__name__)

class FinancialAIChat:
    def __init__(self, data_loader, db_manager):
        self.data_loader = data_loader
        self.db_manager = db_manager
        self.ai_summarizer = AISummarizer(provider='gemini')
        
    def process_query(self, query: str, context_data: Dict[str, Any] = None) -> str:
        """Process user query and return AI response"""
        try:
            if not self.ai_summarizer.api_key:
                return "AI chat is not available. Please configure your Gemini API key."
            
            # Prepare context from current data
            if context_data is None:
                context_data = self._get_current_context()
            
            # Create prompt for financial query
            prompt = self._create_financial_prompt(query, context_data)
            
            # Get AI response
            response = self.ai_summarizer._call_gemini(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"Sorry, I encountered an error processing your query: {str(e)}"
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current financial context for AI"""
        try:
            # Get recent data summary
            data_summary = self.db_manager.get_data_summary()
            
            # Get recent P&L data
            end_date = datetime.now()
            start_date = datetime(end_date.year, end_date.month, 1)
            
            pnl_data = self.data_loader.get_profit_loss_data(start_date, end_date)
            expense_data = self.data_loader.get_expense_breakdown(start_date, end_date)
            vendor_data = self.data_loader.get_vendor_analysis(start_date, end_date)
            
            return {
                'data_summary': data_summary,
                'pnl_data': pnl_data,
                'expense_data': expense_data,
                'vendor_data': vendor_data,
                'period': f"{start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}"
            }
            
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return {}
    
    def _create_financial_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Create prompt for financial AI query"""
        
        # Basic context
        data_summary = context.get('data_summary', {})
        pnl_data = context.get('pnl_data', pd.DataFrame())
        expense_data = context.get('expense_data', pd.DataFrame())
        vendor_data = context.get('vendor_data', pd.DataFrame())
        period = context.get('period', 'current period')
        
        # Calculate key metrics
        revenue_total = 0
        expense_total = 0
        net_income = 0
        
        if not pnl_data.empty:
            revenue_data = pnl_data[pnl_data['account_type'] == 'Revenue']
            expense_data_pnl = pnl_data[pnl_data['account_type'] == 'Expense']
            revenue_total = revenue_data['net_amount'].sum()
            expense_total = expense_data_pnl['net_amount'].sum()
            net_income = revenue_total - expense_total
        
        # Top expenses
        top_expense = "N/A"
        top_expense_amount = 0
        if not expense_data.empty:
            top_expense = expense_data.iloc[0]['category']
            top_expense_amount = expense_data.iloc[0]['total_amount']
        
        # Top vendor
        top_vendor = "N/A"
        top_vendor_amount = 0
        if not vendor_data.empty:
            top_vendor = vendor_data.iloc[0]['vendor_name']
            top_vendor_amount = vendor_data.iloc[0]['total_amount']
        
        prompt = f"""
        You are a financial analyst AI assistant. Answer the user's question about their financial data.
        
        Current Financial Context ({period}):
        - Total Revenue: ${revenue_total:,.2f}
        - Total Expenses: ${expense_total:,.2f}
        - Net Income: ${net_income:,.2f}
        - Top Expense Category: {top_expense} (${top_expense_amount:,.2f})
        - Top Vendor: {top_vendor} (${top_vendor_amount:,.2f})
        - Total Accounts: {data_summary.get('accounts', 0)}
        - Total Transactions: {data_summary.get('transactions', 0)}
        - Total Vendors: {data_summary.get('vendors', 0)}
        
        User Question: {query}
        
        Please provide a helpful, professional response about their financial data. 
        Be specific and reference the actual numbers when relevant.
        Keep your response concise but informative.
        """
        
        return prompt

def create_ai_chat_interface(data_loader, db_manager):
    """Create AI chat interface for the dashboard"""
    
    st.header("🤖 AI Financial Assistant")
    st.markdown("Ask questions about your financial data and get AI-powered insights.")
    
    # Initialize chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize AI chat
    if "ai_chat" not in st.session_state:
        st.session_state.ai_chat = FinancialAIChat(data_loader, db_manager)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your financial data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your financial data..."):
                response = st.session_state.ai_chat.process_query(prompt)
                st.markdown(response)
        
        # Add AI response
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Quick action buttons
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 What's my profit margin?"):
            query = "What is my profit margin and how is it trending?"
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("Analyzing..."):
                response = st.session_state.ai_chat.process_query(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("💸 Where am I spending most?"):
            query = "What are my top expense categories and where should I focus cost reduction?"
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("Analyzing..."):
                response = st.session_state.ai_chat.process_query(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("🏢 Who are my top vendors?"):
            query = "Who are my top vendors by spending and what should I know about them?"
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("Analyzing..."):
                response = st.session_state.ai_chat.process_query(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

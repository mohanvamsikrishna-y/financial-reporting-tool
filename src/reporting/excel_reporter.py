"""
Excel reporting module for financial reports.
"""

import pandas as pd
import xlsxwriter
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ExcelReporter:
    """Generates Excel reports for financial data"""
    
    def __init__(self, output_dir: str = 'outputs/reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_profit_loss_report(self, pnl_data: pd.DataFrame, 
                                 period: str, 
                                 output_filename: Optional[str] = None) -> str:
        """Create Profit & Loss statement in Excel format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"P&L_Report_{period}_{timestamp}.xlsx"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#366092',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0',
                'border': 1
            })
            
            # Create P&L worksheet
            pnl_df = self._format_pnl_data(pnl_data)
            pnl_df.to_excel(writer, sheet_name='Profit & Loss', index=False)
            
            worksheet = writer.sheets['Profit & Loss']
            
            # Apply formatting
            worksheet.set_column('A:A', 20)  # Account Code
            worksheet.set_column('B:B', 30)  # Account Name
            worksheet.set_column('C:C', 15)  # Account Type
            worksheet.set_column('D:D', 15, currency_format)  # Net Amount
            
            # Add header formatting
            for col_num, value in enumerate(pnl_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Add summary section
            self._add_summary_section(worksheet, pnl_data, 5, workbook)
            
            # Add charts
            self._add_pnl_chart(workbook, worksheet, pnl_data)
        
        logger.info(f"P&L report created: {file_path}")
        return file_path
    
    def create_expense_breakdown_report(self, expense_data: pd.DataFrame,
                                      period: str,
                                      output_filename: Optional[str] = None) -> str:
        """Create expense breakdown report in Excel format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Expense_Breakdown_{period}_{timestamp}.xlsx"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#70AD47',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0',
                'border': 1
            })
            
            # Create expense breakdown worksheet
            expense_df = self._format_expense_data(expense_data)
            expense_df.to_excel(writer, sheet_name='Expense Breakdown', index=False)
            
            worksheet = writer.sheets['Expense Breakdown']
            
            # Apply formatting
            worksheet.set_column('A:A', 25)  # Category
            worksheet.set_column('B:B', 15, number_format)  # Transaction Count
            worksheet.set_column('C:C', 15, currency_format)  # Total Amount
            worksheet.set_column('D:D', 15, currency_format)  # Average Amount
            worksheet.set_column('E:E', 15, currency_format)  # Min Amount
            worksheet.set_column('F:F', 15, currency_format)  # Max Amount
            
            # Add header formatting
            for col_num, value in enumerate(expense_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Add summary section
            self._add_expense_summary(worksheet, expense_data, 5, workbook)
            
            # Add charts
            self._add_expense_chart(workbook, worksheet, expense_data)
        
        logger.info(f"Expense breakdown report created: {file_path}")
        return file_path
    
    def create_vendor_analysis_report(self, vendor_data: pd.DataFrame,
                                    period: str,
                                    output_filename: Optional[str] = None) -> str:
        """Create vendor analysis report in Excel format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Vendor_Analysis_{period}_{timestamp}.xlsx"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#C55A11',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'num_format': 'mm/dd/yyyy',
                'border': 1
            })
            
            # Create vendor analysis worksheet
            vendor_df = self._format_vendor_data(vendor_data)
            vendor_df.to_excel(writer, sheet_name='Vendor Analysis', index=False)
            
            worksheet = writer.sheets['Vendor Analysis']
            
            # Apply formatting
            worksheet.set_column('A:A', 15)  # Vendor Code
            worksheet.set_column('B:B', 30)  # Vendor Name
            worksheet.set_column('C:C', 20)  # Vendor Type
            worksheet.set_column('D:D', 15, number_format)  # Transaction Count
            worksheet.set_column('E:E', 15, currency_format)  # Total Amount
            worksheet.set_column('F:F', 15, currency_format)  # Average Amount
            worksheet.set_column('G:G', 15, date_format)  # First Transaction
            worksheet.set_column('H:H', 15, date_format)  # Last Transaction
            
            # Add header formatting
            for col_num, value in enumerate(vendor_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Add summary section
            self._add_vendor_summary(worksheet, vendor_data, 5, workbook)
            
            # Add charts
            self._add_vendor_chart(workbook, worksheet, vendor_data)
        
        logger.info(f"Vendor analysis report created: {file_path}")
        return file_path
    
    def create_compliance_report(self, compliance_data: pd.DataFrame,
                               period: str,
                               output_filename: Optional[str] = None) -> str:
        """Create compliance and audit report in Excel format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Compliance_Report_{period}_{timestamp}.xlsx"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#7030A0',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'num_format': 'mm/dd/yyyy hh:mm:ss',
                'border': 1
            })
            
            # Create compliance worksheet
            compliance_df = self._format_compliance_data(compliance_data)
            compliance_df.to_excel(writer, sheet_name='Compliance Log', index=False)
            
            worksheet = writer.sheets['Compliance Log']
            
            # Apply formatting
            worksheet.set_column('A:A', 20)  # Transaction ID
            worksheet.set_column('B:B', 15, date_format)  # Transaction Date
            worksheet.set_column('C:C', 15)  # Account Code
            worksheet.set_column('D:D', 25)  # Account Name
            worksheet.set_column('E:E', 25)  # Vendor Name
            worksheet.set_column('F:F', 40)  # Description
            worksheet.set_column('G:G', 15, currency_format)  # Amount USD
            worksheet.set_column('H:H', 15)  # Transaction Type
            worksheet.set_column('I:I', 20)  # Category
            worksheet.set_column('J:J', 20)  # Reference Number
            worksheet.set_column('K:K', 15, date_format)  # Created At
            worksheet.set_column('L:L', 15, date_format)  # Updated At
            
            # Add header formatting
            for col_num, value in enumerate(compliance_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Add summary section
            self._add_compliance_summary(worksheet, compliance_data, 5, workbook)
        
        logger.info(f"Compliance report created: {file_path}")
        return file_path
    
    def _format_pnl_data(self, pnl_data: pd.DataFrame) -> pd.DataFrame:
        """Format P&L data for Excel output"""
        formatted_df = pnl_data.copy()
        
        # Rename columns for better display
        column_mapping = {
            'account_code': 'Account Code',
            'account_name': 'Account Name',
            'account_type': 'Account Type',
            'net_amount': 'Net Amount (USD)'
        }
        
        formatted_df = formatted_df.rename(columns=column_mapping)
        
        # Sort by account type and code
        formatted_df = formatted_df.sort_values(['Account Type', 'Account Code'])
        
        return formatted_df
    
    def _format_expense_data(self, expense_data: pd.DataFrame) -> pd.DataFrame:
        """Format expense data for Excel output"""
        formatted_df = expense_data.copy()
        
        # Rename columns for better display
        column_mapping = {
            'category': 'Category',
            'transaction_count': 'Transaction Count',
            'total_amount': 'Total Amount (USD)',
            'avg_amount': 'Average Amount (USD)',
            'min_amount': 'Min Amount (USD)',
            'max_amount': 'Max Amount (USD)'
        }
        
        formatted_df = formatted_df.rename(columns=column_mapping)
        
        # Sort by total amount descending
        formatted_df = formatted_df.sort_values('Total Amount (USD)', ascending=False)
        
        return formatted_df
    
    def _format_vendor_data(self, vendor_data: pd.DataFrame) -> pd.DataFrame:
        """Format vendor data for Excel output"""
        formatted_df = vendor_data.copy()
        
        # Rename columns for better display
        column_mapping = {
            'vendor_code': 'Vendor Code',
            'vendor_name': 'Vendor Name',
            'vendor_type': 'Vendor Type',
            'transaction_count': 'Transaction Count',
            'total_amount': 'Total Amount (USD)',
            'avg_amount': 'Average Amount (USD)',
            'first_transaction': 'First Transaction',
            'last_transaction': 'Last Transaction'
        }
        
        formatted_df = formatted_df.rename(columns=column_mapping)
        
        # Sort by total amount descending
        formatted_df = formatted_df.sort_values('Total Amount (USD)', ascending=False)
        
        return formatted_df
    
    def _format_compliance_data(self, compliance_data: pd.DataFrame) -> pd.DataFrame:
        """Format compliance data for Excel output"""
        formatted_df = compliance_data.copy()
        
        # Rename columns for better display
        column_mapping = {
            'transaction_id': 'Transaction ID',
            'transaction_date': 'Transaction Date',
            'account_code': 'Account Code',
            'account_name': 'Account Name',
            'vendor_name': 'Vendor Name',
            'description': 'Description',
            'amount_usd': 'Amount (USD)',
            'transaction_type': 'Transaction Type',
            'category': 'Category',
            'reference_number': 'Reference Number',
            'created_at': 'Created At',
            'updated_at': 'Updated At'
        }
        
        formatted_df = formatted_df.rename(columns=column_mapping)
        
        return formatted_df
    
    def _add_summary_section(self, worksheet, pnl_data: pd.DataFrame, start_row: int, workbook=None):
        """Add summary section to P&L worksheet"""
        # Calculate totals
        revenue_total = pnl_data[pnl_data['account_type'] == 'Revenue']['net_amount'].sum()
        expense_total = pnl_data[pnl_data['account_type'] == 'Expense']['net_amount'].sum()
        net_income = revenue_total - expense_total
        
        # Add summary
        summary_row = start_row + 2
        bold_format = workbook.add_format({'bold': True}) if workbook else None
        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': True}) if workbook else None
        number_format = workbook.add_format({'num_format': '#,##0', 'bold': True}) if workbook else None
        
        worksheet.write(summary_row, 0, 'SUMMARY', bold_format)
        worksheet.write(summary_row + 1, 0, 'Total Revenue:', bold_format)
        worksheet.write(summary_row + 1, 3, revenue_total, currency_format)
        worksheet.write(summary_row + 2, 0, 'Total Expenses:', bold_format)
        worksheet.write(summary_row + 2, 3, expense_total, currency_format)
        worksheet.write(summary_row + 3, 0, 'Net Income:', bold_format)
        worksheet.write(summary_row + 3, 3, net_income, currency_format)
    
    def _add_expense_summary(self, worksheet, expense_data: pd.DataFrame, start_row: int, workbook=None):
        """Add summary section to expense worksheet"""
        total_amount = expense_data['total_amount'].sum()
        total_transactions = expense_data['transaction_count'].sum()
        
        summary_row = start_row + 2
        bold_format = workbook.add_format({'bold': True}) if workbook else None
        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': True}) if workbook else None
        number_format = workbook.add_format({'num_format': '#,##0', 'bold': True}) if workbook else None
        
        worksheet.write(summary_row, 0, 'SUMMARY', bold_format)
        worksheet.write(summary_row + 1, 0, 'Total Expenses:', bold_format)
        worksheet.write(summary_row + 1, 2, total_amount, currency_format)
        worksheet.write(summary_row + 2, 0, 'Total Transactions:', bold_format)
        worksheet.write(summary_row + 2, 1, total_transactions, number_format)
    
    def _add_vendor_summary(self, worksheet, vendor_data: pd.DataFrame, start_row: int, workbook=None):
        """Add summary section to vendor worksheet"""
        total_amount = vendor_data['total_amount'].sum()
        total_vendors = len(vendor_data)
        
        summary_row = start_row + 2
        bold_format = workbook.add_format({'bold': True}) if workbook else None
        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': True}) if workbook else None
        number_format = workbook.add_format({'num_format': '#,##0', 'bold': True}) if workbook else None
        
        worksheet.write(summary_row, 0, 'SUMMARY', bold_format)
        worksheet.write(summary_row + 1, 0, 'Total Amount:', bold_format)
        worksheet.write(summary_row + 1, 4, total_amount, currency_format)
        worksheet.write(summary_row + 2, 0, 'Total Vendors:', bold_format)
        worksheet.write(summary_row + 2, 4, total_vendors, number_format)
    
    def _add_compliance_summary(self, worksheet, compliance_data: pd.DataFrame, start_row: int, workbook=None):
        """Add summary section to compliance worksheet"""
        total_amount = compliance_data['amount_usd'].sum()
        total_transactions = len(compliance_data)
        
        summary_row = start_row + 2
        bold_format = workbook.add_format({'bold': True}) if workbook else None
        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': True}) if workbook else None
        number_format = workbook.add_format({'num_format': '#,##0', 'bold': True}) if workbook else None
        
        worksheet.write(summary_row, 0, 'SUMMARY', bold_format)
        worksheet.write(summary_row + 1, 0, 'Total Amount:', bold_format)
        worksheet.write(summary_row + 1, 6, total_amount, currency_format)
        worksheet.write(summary_row + 2, 0, 'Total Transactions:', bold_format)
        worksheet.write(summary_row + 2, 6, total_transactions, number_format)
    
    def _add_pnl_chart(self, workbook, worksheet, pnl_data: pd.DataFrame):
        """Add P&L chart to worksheet"""
        # Create a pie chart for revenue vs expenses
        revenue_data = pnl_data[pnl_data['account_type'] == 'Revenue']['net_amount'].sum()
        expense_data = pnl_data[pnl_data['account_type'] == 'Expense']['net_amount'].sum()
        
        if revenue_data > 0 or expense_data > 0:
            chart = workbook.add_chart({'type': 'pie'})
            chart.add_series({
                'name': 'P&L Breakdown',
                'categories': ['Revenue', 'Expenses'],
                'values': [revenue_data, expense_data],
            })
            chart.set_title({'name': 'Revenue vs Expenses'})
            chart.set_size({'width': 400, 'height': 300})
            worksheet.insert_chart('F2', chart)
    
    def _add_expense_chart(self, workbook, worksheet, expense_data: pd.DataFrame):
        """Add expense breakdown chart to worksheet"""
        if len(expense_data) > 0:
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': 'Expense by Category',
                'categories': ['Expense Breakdown', expense_data['category'].tolist()],
                'values': ['Expense Breakdown', expense_data['total_amount'].tolist()],
            })
            chart.set_title({'name': 'Expense Breakdown by Category'})
            chart.set_x_axis({'name': 'Category'})
            chart.set_y_axis({'name': 'Amount (USD)'})
            chart.set_size({'width': 500, 'height': 300})
            worksheet.insert_chart('H2', chart)
    
    def _add_vendor_chart(self, workbook, worksheet, vendor_data: pd.DataFrame):
        """Add vendor analysis chart to worksheet"""
        if len(vendor_data) > 0:
            # Show top 10 vendors
            top_vendors = vendor_data.head(10)
            chart = workbook.add_chart({'type': 'bar'})
            chart.add_series({
                'name': 'Vendor Spending',
                'categories': ['Vendor Analysis', top_vendors['vendor_name'].tolist()],
                'values': ['Vendor Analysis', top_vendors['total_amount'].tolist()],
            })
            chart.set_title({'name': 'Top 10 Vendors by Spending'})
            chart.set_x_axis({'name': 'Vendor'})
            chart.set_y_axis({'name': 'Amount (USD)'})
            chart.set_size({'width': 600, 'height': 400})
            worksheet.insert_chart('J2', chart)

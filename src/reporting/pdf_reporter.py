"""
PDF reporting module for financial reports.
"""

import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class PDFReporter:
    """Generates PDF reports for financial data"""
    
    def __init__(self, output_dir: str = 'outputs/reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='SummaryText',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.darkgreen
        ))
    
    def create_profit_loss_report(self, pnl_data: pd.DataFrame,
                                 period: str,
                                 output_filename: Optional[str] = None) -> str:
        """Create Profit & Loss statement in PDF format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"P&L_Report_{period}_{timestamp}.pdf"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("Profit & Loss Statement", self.styles['CustomTitle']))
        story.append(Paragraph(f"Period: {period}", self.styles['CustomNormal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                              self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Revenue Section
        revenue_data = pnl_data[pnl_data['account_type'] == 'Revenue']
        if not revenue_data.empty:
            story.append(Paragraph("REVENUE", self.styles['CustomHeading']))
            story.append(self._create_pnl_table(revenue_data))
            story.append(Spacer(1, 12))
        
        # Expense Section
        expense_data = pnl_data[pnl_data['account_type'] == 'Expense']
        if not expense_data.empty:
            story.append(Paragraph("EXPENSES", self.styles['CustomHeading']))
            story.append(self._create_pnl_table(expense_data))
            story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("SUMMARY", self.styles['CustomHeading']))
        summary_data = self._calculate_pnl_summary(pnl_data)
        story.append(self._create_summary_table(summary_data))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"P&L PDF report created: {file_path}")
        return file_path
    
    def create_expense_breakdown_report(self, expense_data: pd.DataFrame,
                                      period: str,
                                      output_filename: Optional[str] = None) -> str:
        """Create expense breakdown report in PDF format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Expense_Breakdown_{period}_{timestamp}.pdf"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("Expense Breakdown Report", self.styles['CustomTitle']))
        story.append(Paragraph(f"Period: {period}", self.styles['CustomNormal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                              self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Expense breakdown table
        story.append(Paragraph("EXPENSE BREAKDOWN BY CATEGORY", self.styles['CustomHeading']))
        story.append(self._create_expense_table(expense_data))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("SUMMARY", self.styles['CustomHeading']))
        summary_data = self._calculate_expense_summary(expense_data)
        story.append(self._create_summary_table(summary_data))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Expense breakdown PDF report created: {file_path}")
        return file_path
    
    def create_vendor_analysis_report(self, vendor_data: pd.DataFrame,
                                    period: str,
                                    output_filename: Optional[str] = None) -> str:
        """Create vendor analysis report in PDF format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Vendor_Analysis_{period}_{timestamp}.pdf"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("Vendor Analysis Report", self.styles['CustomTitle']))
        story.append(Paragraph(f"Period: {period}", self.styles['CustomNormal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                              self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Vendor analysis table
        story.append(Paragraph("VENDOR ANALYSIS", self.styles['CustomHeading']))
        story.append(self._create_vendor_table(vendor_data))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("SUMMARY", self.styles['CustomHeading']))
        summary_data = self._calculate_vendor_summary(vendor_data)
        story.append(self._create_summary_table(summary_data))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Vendor analysis PDF report created: {file_path}")
        return file_path
    
    def create_compliance_report(self, compliance_data: pd.DataFrame,
                               period: str,
                               output_filename: Optional[str] = None) -> str:
        """Create compliance and audit report in PDF format"""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Compliance_Report_{period}_{timestamp}.pdf"
        
        file_path = os.path.join(self.output_dir, output_filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("Compliance and Audit Report", self.styles['CustomTitle']))
        story.append(Paragraph(f"Period: {period}", self.styles['CustomNormal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                              self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Compliance data table
        story.append(Paragraph("TRANSACTION AUDIT LOG", self.styles['CustomHeading']))
        story.append(self._create_compliance_table(compliance_data))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("SUMMARY", self.styles['CustomHeading']))
        summary_data = self._calculate_compliance_summary(compliance_data)
        story.append(self._create_summary_table(summary_data))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Compliance PDF report created: {file_path}")
        return file_path
    
    def _create_pnl_table(self, data: pd.DataFrame) -> Table:
        """Create P&L table"""
        table_data = [['Account Code', 'Account Name', 'Amount (USD)']]
        
        for _, row in data.iterrows():
            table_data.append([
                row['account_code'],
                row['account_name'],
                f"${row['net_amount']:,.2f}"
            ])
        
        table = Table(table_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_expense_table(self, data: pd.DataFrame) -> Table:
        """Create expense breakdown table"""
        table_data = [['Category', 'Transactions', 'Total Amount', 'Average Amount']]
        
        for _, row in data.iterrows():
            table_data.append([
                row['category'],
                str(int(row['transaction_count'])),
                f"${row['total_amount']:,.2f}",
                f"${row['avg_amount']:,.2f}"
            ])
        
        table = Table(table_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_vendor_table(self, data: pd.DataFrame) -> Table:
        """Create vendor analysis table"""
        table_data = [['Vendor Code', 'Vendor Name', 'Transactions', 'Total Amount', 'Average Amount']]
        
        for _, row in data.iterrows():
            table_data.append([
                row['vendor_code'],
                row['vendor_name'][:30] + '...' if len(row['vendor_name']) > 30 else row['vendor_name'],
                str(int(row['transaction_count'])),
                f"${row['total_amount']:,.2f}",
                f"${row['avg_amount']:,.2f}"
            ])
        
        table = Table(table_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_compliance_table(self, data: pd.DataFrame) -> Table:
        """Create compliance table"""
        table_data = [['Transaction ID', 'Date', 'Account', 'Amount', 'Type', 'Category']]
        
        for _, row in data.head(20).iterrows():  # Limit to first 20 rows for PDF
            table_data.append([
                row['transaction_id'][:15] + '...' if len(row['transaction_id']) > 15 else row['transaction_id'],
                row['transaction_date'].strftime('%m/%d/%Y'),
                row['account_code'],
                f"${row['amount_usd']:,.2f}",
                row['transaction_type'],
                row['category'][:15] + '...' if len(str(row['category'])) > 15 else str(row['category'])
            ])
        
        table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_summary_table(self, summary_data: List[List[str]]) -> Table:
        """Create summary table"""
        table = Table(summary_data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _calculate_pnl_summary(self, pnl_data: pd.DataFrame) -> List[List[str]]:
        """Calculate P&L summary data"""
        revenue_total = pnl_data[pnl_data['account_type'] == 'Revenue']['net_amount'].sum()
        expense_total = pnl_data[pnl_data['account_type'] == 'Expense']['net_amount'].sum()
        net_income = revenue_total - expense_total
        
        return [
            ['Total Revenue:', f"${revenue_total:,.2f}"],
            ['Total Expenses:', f"${expense_total:,.2f}"],
            ['Net Income:', f"${net_income:,.2f}"]
        ]
    
    def _calculate_expense_summary(self, expense_data: pd.DataFrame) -> List[List[str]]:
        """Calculate expense summary data"""
        total_amount = expense_data['total_amount'].sum()
        total_transactions = expense_data['transaction_count'].sum()
        avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
        
        return [
            ['Total Expenses:', f"${total_amount:,.2f}"],
            ['Total Transactions:', f"{total_transactions:,}"],
            ['Average Transaction:', f"${avg_transaction:,.2f}"]
        ]
    
    def _calculate_vendor_summary(self, vendor_data: pd.DataFrame) -> List[List[str]]:
        """Calculate vendor summary data"""
        total_amount = vendor_data['total_amount'].sum()
        total_vendors = len(vendor_data)
        avg_vendor_amount = total_amount / total_vendors if total_vendors > 0 else 0
        
        return [
            ['Total Amount:', f"${total_amount:,.2f}"],
            ['Total Vendors:', f"{total_vendors:,}"],
            ['Average per Vendor:', f"${avg_vendor_amount:,.2f}"]
        ]
    
    def _calculate_compliance_summary(self, compliance_data: pd.DataFrame) -> List[List[str]]:
        """Calculate compliance summary data"""
        total_amount = compliance_data['amount_usd'].sum()
        total_transactions = len(compliance_data)
        avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
        
        return [
            ['Total Amount:', f"${total_amount:,.2f}"],
            ['Total Transactions:', f"{total_transactions:,}"],
            ['Average Transaction:', f"${avg_transaction:,.2f}"]
        ]

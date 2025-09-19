"""
Main pipeline for the Financial Reporting Tool.
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from config.database import DatabaseManager
from config.settings import *
from src.data_ingestion import CSVDataIngestion, APIDataIngestion
from src.validation import DataValidator, DataTransformer
from src.storage import EnhancedDatabaseManager, DataLoader
from src.reporting import ExcelReporter, PDFReporter
from src.ai_summary import AISummarizer

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FinancialReportingPipeline:
    """Main pipeline for financial reporting and analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.db_manager = None
        self.data_loader = None
        self.excel_reporter = None
        self.pdf_reporter = None
        self.ai_summarizer = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all pipeline components"""
        try:
            # Initialize database
            self.db_manager = EnhancedDatabaseManager(DATABASE_URL)
            self.db_manager.create_tables()
            
            # Initialize data loader
            self.data_loader = DataLoader(self.db_manager)
            
            # Initialize reporters
            self.excel_reporter = ExcelReporter(REPORTS_DIR)
            self.pdf_reporter = PDFReporter(REPORTS_DIR)
            
            # Initialize AI summarizer with Gemini (free)
            self.ai_summarizer = AISummarizer(provider='gemini')
            
            logger.info("Pipeline components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing pipeline components: {str(e)}")
            raise
    
    def run_full_pipeline(self, 
                         data_files: Optional[List[str]] = None,
                         period: Optional[str] = None,
                         generate_ai_summary: bool = True) -> Dict[str, Any]:
        """Run the complete financial reporting pipeline"""
        
        logger.info("Starting full financial reporting pipeline")
        
        try:
            # Step 1: Data Ingestion
            logger.info("Step 1: Data Ingestion")
            ingestion_results = self._run_data_ingestion(data_files)
            
            # Step 2: Data Validation and Transformation
            logger.info("Step 2: Data Validation and Transformation")
            validation_results = self._run_validation_and_transformation()
            
            # Step 3: Generate Reports
            logger.info("Step 3: Generate Reports")
            report_results = self._generate_reports(period)
            
            # Step 4: Generate AI Summary
            ai_summary_results = {}
            if generate_ai_summary and self.ai_summarizer.api_key:
                logger.info("Step 4: Generate AI Summary")
                ai_summary_results = self._generate_ai_summary(period)
            else:
                logger.info("Skipping AI summary generation (API key not available)")
            
            # Step 5: Log Results
            logger.info("Step 5: Log Results")
            self._log_pipeline_results(ingestion_results, validation_results, report_results, ai_summary_results)
            
            pipeline_results = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'ingestion_results': ingestion_results,
                'validation_results': validation_results,
                'report_results': report_results,
                'ai_summary_results': ai_summary_results
            }
            
            logger.info("Full pipeline completed successfully")
            return pipeline_results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _run_data_ingestion(self, data_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run data ingestion from various sources"""
        
        ingestion_results = {
            'csv_files_processed': 0,
            'api_data_fetched': False,
            'exchange_rates_updated': False,
            'errors': []
        }
        
        try:
            # CSV Data Ingestion
            csv_ingestion = CSVDataIngestion(SAMPLE_DATA_DIR)
            
            if data_files:
                files_to_process = data_files
            else:
                files_to_process = csv_ingestion.get_available_files()
            
            for file_path in files_to_process:
                try:
                    logger.info(f"Processing file: {file_path}")
                    
                    # Determine file type and process accordingly
                    if 'transaction' in file_path.lower():
                        df = csv_ingestion.read_transactions(file_path)
                        result = self.db_manager.load_transactions(df)
                    elif 'account' in file_path.lower():
                        df = csv_ingestion.read_accounts(file_path)
                        result = self.db_manager.load_accounts(df)
                    elif 'vendor' in file_path.lower():
                        df = csv_ingestion.read_vendors(file_path)
                        result = self.db_manager.load_vendors(df)
                    else:
                        logger.warning(f"Unknown file type: {file_path}")
                        continue
                    
                    ingestion_results['csv_files_processed'] += 1
                    logger.info(f"Successfully processed {file_path}")
                    
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    ingestion_results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            # API Data Ingestion
            try:
                api_ingestion = APIDataIngestion(EXCHANGE_RATE_API_KEY)
                exchange_rates_df = api_ingestion.get_exchange_rates()
                
                if not exchange_rates_df.empty:
                    result = self.db_manager.load_exchange_rates(exchange_rates_df)
                    ingestion_results['api_data_fetched'] = True
                    ingestion_results['exchange_rates_updated'] = True
                    logger.info("Exchange rates updated successfully")
                
            except Exception as e:
                error_msg = f"Error fetching exchange rates: {str(e)}"
                ingestion_results['errors'].append(error_msg)
                logger.error(error_msg)
            
            return ingestion_results
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {str(e)}")
            ingestion_results['errors'].append(str(e))
            return ingestion_results
    
    def _run_validation_and_transformation(self) -> Dict[str, Any]:
        """Run data validation and transformation"""
        
        validation_results = {
            'transactions_validated': False,
            'accounts_validated': False,
            'vendors_validated': False,
            'data_quality_score': 0.0,
            'errors': []
        }
        
        try:
            # Get data from database for validation
            transactions_df = self.data_loader.get_transactions()
            
            if not transactions_df.empty:
                # Validate transactions
                validator = DataValidator()
                validation_result = validator.validate_transactions(transactions_df)
                validation_results['transactions_validated'] = validation_result['is_valid']
                validation_results['data_quality_score'] = validation_result['data_quality_score']
                
                if not validation_result['is_valid']:
                    validation_results['errors'].extend(validation_result['errors'])
                
                logger.info(f"Transaction validation completed. Quality score: {validation_result['data_quality_score']:.2f}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            validation_results['errors'].append(str(e))
            return validation_results
    
    def _generate_reports(self, period: Optional[str] = None) -> Dict[str, Any]:
        """Generate all financial reports"""
        
        if period is None:
            period = datetime.now().strftime("%Y-%m")
        
        # Calculate date range for the period
        start_date = datetime.strptime(period, "%Y-%m").replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1) - timedelta(days=1)
        
        report_results = {
            'period': period,
            'excel_reports': [],
            'pdf_reports': [],
            'errors': []
        }
        
        try:
            # Generate P&L Report
            try:
                pnl_data = self.data_loader.get_profit_loss_data(start_date, end_date)
                if not pnl_data.empty:
                    excel_path = self.excel_reporter.create_profit_loss_report(pnl_data, period)
                    pdf_path = self.pdf_reporter.create_profit_loss_report(pnl_data, period)
                    report_results['excel_reports'].append(excel_path)
                    report_results['pdf_reports'].append(pdf_path)
                    logger.info("P&L report generated successfully")
            except Exception as e:
                error_msg = f"Error generating P&L report: {str(e)}"
                report_results['errors'].append(error_msg)
                logger.error(error_msg)
            
            # Generate Expense Breakdown Report
            try:
                expense_data = self.data_loader.get_expense_breakdown(start_date, end_date)
                if not expense_data.empty:
                    excel_path = self.excel_reporter.create_expense_breakdown_report(expense_data, period)
                    pdf_path = self.pdf_reporter.create_expense_breakdown_report(expense_data, period)
                    report_results['excel_reports'].append(excel_path)
                    report_results['pdf_reports'].append(pdf_path)
                    logger.info("Expense breakdown report generated successfully")
            except Exception as e:
                error_msg = f"Error generating expense breakdown report: {str(e)}"
                report_results['errors'].append(error_msg)
                logger.error(error_msg)
            
            # Generate Vendor Analysis Report
            try:
                vendor_data = self.data_loader.get_vendor_analysis(start_date, end_date)
                if not vendor_data.empty:
                    excel_path = self.excel_reporter.create_vendor_analysis_report(vendor_data, period)
                    pdf_path = self.pdf_reporter.create_vendor_analysis_report(vendor_data, period)
                    report_results['excel_reports'].append(excel_path)
                    report_results['pdf_reports'].append(pdf_path)
                    logger.info("Vendor analysis report generated successfully")
            except Exception as e:
                error_msg = f"Error generating vendor analysis report: {str(e)}"
                report_results['errors'].append(error_msg)
                logger.error(error_msg)
            
            # Generate Compliance Report
            try:
                compliance_data = self.data_loader.get_compliance_log(start_date, end_date)
                if not compliance_data.empty:
                    excel_path = self.excel_reporter.create_compliance_report(compliance_data, period)
                    pdf_path = self.pdf_reporter.create_compliance_report(compliance_data, period)
                    report_results['excel_reports'].append(excel_path)
                    report_results['pdf_reports'].append(pdf_path)
                    logger.info("Compliance report generated successfully")
            except Exception as e:
                error_msg = f"Error generating compliance report: {str(e)}"
                report_results['errors'].append(error_msg)
                logger.error(error_msg)
            
            return report_results
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            report_results['errors'].append(str(e))
            return report_results
    
    def _generate_ai_summary(self, period: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI-powered executive summary"""
        
        if period is None:
            period = datetime.now().strftime("%Y-%m")
        
        # Calculate date range for the period
        start_date = datetime.strptime(period, "%Y-%m").replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1) - timedelta(days=1)
        
        ai_summary_results = {
            'period': period,
            'summary_files': [],
            'errors': []
        }
        
        try:
            # Get data for AI analysis
            pnl_data = self.data_loader.get_profit_loss_data(start_date, end_date)
            expense_data = self.data_loader.get_expense_breakdown(start_date, end_date)
            vendor_data = self.data_loader.get_vendor_analysis(start_date, end_date)
            
            # Generate executive summary
            summary_result = self.ai_summarizer.generate_executive_summary(
                pnl_data, expense_data, vendor_data, period
            )
            
            if summary_result['status'] == 'success':
                # Save summary to file
                summary_file = self.ai_summarizer.save_summary_to_file(summary_result)
                ai_summary_results['summary_files'].append(summary_file)
                logger.info("AI executive summary generated successfully")
            
            # Generate risk analysis
            risk_result = self.ai_summarizer.generate_risk_analysis(
                pnl_data, expense_data, vendor_data, period
            )
            
            if risk_result['status'] == 'success':
                # Save risk analysis to file
                risk_file = self.ai_summarizer.save_summary_to_file(risk_result, filename=f"Risk_Analysis_{period}.txt")
                ai_summary_results['summary_files'].append(risk_file)
                logger.info("AI risk analysis generated successfully")
            
            return ai_summary_results
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {str(e)}")
            ai_summary_results['errors'].append(str(e))
            return ai_summary_results
    
    def _log_pipeline_results(self, ingestion_results: Dict[str, Any], 
                            validation_results: Dict[str, Any],
                            report_results: Dict[str, Any],
                            ai_summary_results: Dict[str, Any]):
        """Log pipeline results to database"""
        
        try:
            # Log report generation
            for excel_report in report_results.get('excel_reports', []):
                self.db_manager.log_report_generation(
                    report_type='Excel Report',
                    report_period=report_results.get('period', 'Unknown'),
                    file_path=excel_report,
                    status='SUCCESS',
                    record_count=0
                )
            
            for pdf_report in report_results.get('pdf_reports', []):
                self.db_manager.log_report_generation(
                    report_type='PDF Report',
                    report_period=report_results.get('period', 'Unknown'),
                    file_path=pdf_report,
                    status='SUCCESS',
                    record_count=0
                )
            
            # Log AI summary generation
            for summary_file in ai_summary_results.get('summary_files', []):
                self.db_manager.log_report_generation(
                    report_type='AI Summary',
                    report_period=ai_summary_results.get('period', 'Unknown'),
                    file_path=summary_file,
                    status='SUCCESS',
                    record_count=0
                )
            
            logger.info("Pipeline results logged to database")
            
        except Exception as e:
            logger.error(f"Error logging pipeline results: {str(e)}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        
        try:
            data_summary = self.db_manager.get_data_summary()
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'database_connected': True,
                'data_summary': data_summary,
                'ai_available': self.ai_summarizer.api_key is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def close(self):
        """Close pipeline and cleanup resources"""
        try:
            if self.db_manager:
                self.db_manager.close_connection()
            logger.info("Pipeline closed successfully")
        except Exception as e:
            logger.error(f"Error closing pipeline: {str(e)}")

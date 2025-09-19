#!/usr/bin/env python3
"""
Financial Reporting & Analysis Platform
"""

import argparse
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from config.settings import *
from src.pipeline import FinancialReportingPipeline
from src.automation import AutomationManager
from src.reporting.dashboard import run_dashboard

def setup_logging():
    """Setup logging configuration"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

def run_pipeline(data_files: Optional[List[str]] = None, 
                period: Optional[str] = None,
                generate_ai_summary: bool = True):
    """Run the financial reporting pipeline"""
    
    print("🚀 Starting Financial Reporting Pipeline...")
    
    try:
        # Initialize pipeline
        pipeline = FinancialReportingPipeline()
        
        # Run pipeline
        results = pipeline.run_full_pipeline(
            data_files=data_files,
            period=period,
            generate_ai_summary=generate_ai_summary
        )
        
        # Display results
        if results['status'] == 'success':
            print("✅ Pipeline completed successfully!")
            
            # Display report files
            report_results = results.get('report_results', {})
            if report_results.get('excel_reports'):
                print("\n📊 Excel Reports Generated:")
                for report in report_results['excel_reports']:
                    print(f"  - {report}")
            
            if report_results.get('pdf_reports'):
                print("\n📄 PDF Reports Generated:")
                for report in report_results['pdf_reports']:
                    print(f"  - {report}")
            
            # Display AI summaries
            ai_results = results.get('ai_summary_results', {})
            if ai_results.get('summary_files'):
                print("\n🤖 AI Summaries Generated:")
                for summary in ai_results['summary_files']:
                    print(f"  - {summary}")
            
            print(f"\n📁 All reports saved to: {REPORTS_DIR}")
            
        else:
            print(f"❌ Pipeline failed: {results.get('error', 'Unknown error')}")
            return 1
        
        # Close pipeline
        pipeline.close()
        return 0
        
    except Exception as e:
        print(f"❌ Error running pipeline: {str(e)}")
        return 1

def run_dashboard_mode():
    """Run the Streamlit dashboard"""
    print("🌐 Starting Financial Reporting Dashboard...")
    print("Dashboard will open in your default web browser.")
    print("Press Ctrl+C to stop the dashboard.")
    
    try:
        run_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {str(e)}")
        return 1
    
    return 0

def run_automation_mode():
    """Run the automation scheduler"""
    print("⏰ Starting Automation Scheduler...")
    print(f"Schedule: {REFRESH_SCHEDULE} at {REFRESH_TIME}")
    print("Press Ctrl+C to stop the scheduler.")
    
    try:
        # Initialize pipeline and automation
        pipeline = FinancialReportingPipeline()
        automation = AutomationManager(pipeline)
        
        # Start scheduler
        automation.start_scheduler()
        
        # Keep running until interrupted
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n👋 Stopping automation scheduler...")
        automation.stop_scheduler()
        pipeline.close()
        print("✅ Automation stopped successfully")
    except Exception as e:
        print(f"❌ Error running automation: {str(e)}")
        return 1
    
    return 0

def create_sample_data():
    """Create sample data for testing"""
    print("📝 Creating sample data...")
    
    try:
        import pandas as pd
        from datetime import datetime, timedelta
        import random
        
        # Create sample accounts
        accounts_data = {
            'account_code': ['1001', '1002', '2001', '2002', '3001', '4001', '4002', '5001', '5002', '5003'],
            'account_name': ['Cash', 'Accounts Receivable', 'Accounts Payable', 'Accrued Expenses', 'Retained Earnings', 
                           'Sales Revenue', 'Service Revenue', 'Office Supplies', 'Travel Expenses', 'Marketing Expenses'],
            'account_type': ['Asset', 'Asset', 'Liability', 'Liability', 'Equity', 'Revenue', 'Revenue', 
                           'Expense', 'Expense', 'Expense'],
            'is_active': ['Y'] * 10
        }
        
        accounts_df = pd.DataFrame(accounts_data)
        accounts_df.to_csv(os.path.join(SAMPLE_DATA_DIR, 'accounts.csv'), index=False)
        
        # Create sample vendors
        vendors_data = {
            'vendor_code': ['V001', 'V002', 'V003', 'V004', 'V005'],
            'vendor_name': ['Office Depot', 'Delta Airlines', 'Google Ads', 'Amazon Web Services', 'Local Restaurant'],
            'vendor_type': ['Supplier', 'Travel', 'Marketing', 'Technology', 'Meals'],
            'contact_email': ['orders@officedepot.com', 'business@delta.com', 'support@google.com', 'support@aws.com', 'info@restaurant.com'],
            'is_active': ['Y'] * 5
        }
        
        vendors_df = pd.DataFrame(vendors_data)
        vendors_df.to_csv(os.path.join(SAMPLE_DATA_DIR, 'vendors.csv'), index=False)
        
        # Create sample transactions
        transactions_data = []
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(100):
            transaction_id = f"TXN{str(i+1).zfill(6)}"
            transaction_date = start_date + timedelta(days=random.randint(0, 90))
            
            # Random account and vendor
            account_code = random.choice(accounts_data['account_code'])
            vendor_code = random.choice(vendors_data['vendor_code']) if random.random() > 0.3 else None
            
            # Random amount and type
            amount = round(random.uniform(10, 5000), 2)
            transaction_type = random.choice(['Debit', 'Credit'])
            
            # Random description and category
            descriptions = ['Office supplies purchase', 'Business travel', 'Marketing campaign', 'Software license', 'Client meeting']
            categories = ['Office Supplies', 'Travel', 'Marketing', 'Software', 'Meals']
            
            description = random.choice(descriptions)
            category = random.choice(categories)
            
            transactions_data.append({
                'transaction_id': transaction_id,
                'transaction_date': transaction_date.strftime('%Y-%m-%d'),
                'account_code': account_code,
                'vendor_code': vendor_code,
                'description': description,
                'amount': amount,
                'currency': 'USD',
                'transaction_type': transaction_type,
                'category': category,
                'reference_number': f"REF{random.randint(1000, 9999)}"
            })
        
        transactions_df = pd.DataFrame(transactions_data)
        transactions_df.to_csv(os.path.join(SAMPLE_DATA_DIR, 'transactions.csv'), index=False)
        
        print(f"✅ Sample data created in {SAMPLE_DATA_DIR}")
        print("  - accounts.csv: 10 sample accounts")
        print("  - vendors.csv: 5 sample vendors")
        print("  - transactions.csv: 100 sample transactions")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        return 1

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Smart Financial Reporting & Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run                           # Run pipeline with sample data
  python main.py run --period 2024-01         # Run pipeline for specific period
  python main.py dashboard                     # Start web dashboard
  python main.py automation                    # Start automation scheduler
  python main.py create-sample-data           # Create sample data files
        """
    )
    
    parser.add_argument('command', choices=['run', 'dashboard', 'automation', 'create-sample-data'],
                       help='Command to execute')
    parser.add_argument('--data-files', nargs='+', help='Specific data files to process')
    parser.add_argument('--period', help='Report period (YYYY-MM format)')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI summary generation')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        global LOG_LEVEL
        LOG_LEVEL = 'DEBUG'
    
    setup_logging()
    
    # Create necessary directories
    os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Execute command
    if args.command == 'run':
        return run_pipeline(
            data_files=args.data_files,
            period=args.period,
            generate_ai_summary=not args.no_ai
        )
    
    elif args.command == 'dashboard':
        return run_dashboard_mode()
    
    elif args.command == 'automation':
        return run_automation_mode()
    
    elif args.command == 'create-sample-data':
        return create_sample_data()
    
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())

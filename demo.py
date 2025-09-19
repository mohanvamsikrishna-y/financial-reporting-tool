#!/usr/bin/env python3
"""
Demo script for the Financial Reporting Tool.
This script demonstrates the key features of the tool.
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def print_banner():
    """Print welcome banner"""
    print("=" * 80)
    print("🚀 SMART FINANCIAL REPORTING & ANALYSIS TOOL - DEMO")
    print("=" * 80)
    print("This demo will showcase the key features of the tool:")
    print("• Data ingestion from multiple sources")
    print("• Data validation and transformation")
    print("• Comprehensive financial reporting")
    print("• AI-powered executive summaries")
    print("• Interactive dashboard")
    print("• Automation and scheduling")
    print("=" * 80)
    print()

def run_demo():
    """Run the complete demo"""
    
    print_banner()
    
    try:
        # Step 1: Create sample data
        print("📝 STEP 1: Creating sample data...")
        os.system("python main.py create-sample-data")
        print("✅ Sample data created successfully!")
        print()
        
        # Step 2: Run the pipeline
        print("🔄 STEP 2: Running the financial reporting pipeline...")
        print("This will:")
        print("  - Load sample data into the database")
        print("  - Validate and transform the data")
        print("  - Generate Excel and PDF reports")
        print("  - Create AI-powered executive summaries")
        print()
        
        # Run pipeline (skip AI if no API key)
        result = os.system("python main.py run --no-ai")
        if result == 0:
            print("✅ Pipeline completed successfully!")
        else:
            print("⚠️  Pipeline completed with warnings (AI features may be disabled)")
        print()
        
        # Step 3: Show generated files
        print("📁 STEP 3: Generated files:")
        reports_dir = "outputs/reports"
        if os.path.exists(reports_dir):
            files = os.listdir(reports_dir)
            if files:
                for file in sorted(files):
                    file_path = os.path.join(reports_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"  📄 {file} ({file_size:,} bytes)")
            else:
                print("  No files found in reports directory")
        else:
            print("  Reports directory not found")
        print()
        
        # Step 4: Show database status
        print("🗄️  STEP 4: Database status:")
        try:
            from src.pipeline import FinancialReportingPipeline
            pipeline = FinancialReportingPipeline()
            status = pipeline.get_pipeline_status()
            
            if status['status'] == 'healthy':
                data_summary = status.get('data_summary', {})
                print(f"  ✅ Database: Connected")
                print(f"  📊 Accounts: {data_summary.get('accounts', 0)}")
                print(f"  🏢 Vendors: {data_summary.get('vendors', 0)}")
                print(f"  💰 Transactions: {data_summary.get('transactions', 0)}")
                print(f"  🤖 AI Available: {'Yes' if status.get('ai_available') else 'No'}")
            else:
                print(f"  ❌ Database: {status.get('error', 'Unknown error')}")
            
            pipeline.close()
        except Exception as e:
            print(f"  ❌ Error checking database: {str(e)}")
        print()
        
        # Step 5: Instructions for next steps
        print("🎯 NEXT STEPS:")
        print("1. View the interactive dashboard:")
        print("   python main.py dashboard")
        print("   Then open http://localhost:8501 in your browser")
        print()
        print("2. Start the automation scheduler:")
        print("   python main.py automation")
        print()
        print("3. Run with AI summaries (requires OpenAI API key):")
        print("   python main.py run")
        print()
        print("4. Run for a specific period:")
        print("   python main.py run --period 2024-01")
        print()
        
        # Step 6: Configuration tips
        print("⚙️  CONFIGURATION TIPS:")
        print("• Copy env.example to .env and configure your settings")
        print("• Add your OpenAI API key for AI-powered summaries")
        print("• Configure email settings for automated notifications")
        print("• Set up PostgreSQL for production use")
        print()
        
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("Check the outputs/reports directory for generated files.")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        print("=" * 80)
    except Exception as e:
        print(f"\n\n❌ Demo failed: {str(e)}")
        print("Check the logs for more details.")
        print("=" * 80)

if __name__ == '__main__':
    run_demo()

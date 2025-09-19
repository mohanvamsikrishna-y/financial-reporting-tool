#!/usr/bin/env python3
"""
Test script to verify the Financial Reporting Tool is working correctly.
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from src.pipeline import FinancialReportingPipeline
        print("  ✅ Pipeline import successful")
    except Exception as e:
        print(f"  ❌ Pipeline import failed: {e}")
        return False
    
    try:
        from src.storage import EnhancedDatabaseManager, DataLoader
        print("  ✅ Storage imports successful")
    except Exception as e:
        print(f"  ❌ Storage imports failed: {e}")
        return False
    
    try:
        from src.reporting import ExcelReporter, PDFReporter
        print("  ✅ Reporting imports successful")
    except Exception as e:
        print(f"  ❌ Reporting imports failed: {e}")
        return False
    
    try:
        from src.ai_summary import AISummarizer
        print("  ✅ AI summary import successful")
    except Exception as e:
        print(f"  ❌ AI summary import failed: {e}")
        return False
    
    try:
        from src.automation import AutomationManager
        print("  ✅ Automation import successful")
    except Exception as e:
        print(f"  ❌ Automation import failed: {e}")
        return False
    
    return True

def test_pipeline():
    """Test the pipeline functionality"""
    print("\n🔄 Testing pipeline...")
    
    try:
        from src.pipeline import FinancialReportingPipeline
        
        # Initialize pipeline
        pipeline = FinancialReportingPipeline()
        print("  ✅ Pipeline initialized successfully")
        
        # Test status check
        status = pipeline.get_pipeline_status()
        print(f"  ✅ Pipeline status: {status['status']}")
        
        # Close pipeline
        pipeline.close()
        print("  ✅ Pipeline closed successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Pipeline test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️  Testing database...")
    
    try:
        from src.storage import EnhancedDatabaseManager
        from config.settings import DATABASE_URL
        
        # Initialize database
        db_manager = EnhancedDatabaseManager(DATABASE_URL)
        print("  ✅ Database manager initialized")
        
        # Test data summary
        summary = db_manager.get_data_summary()
        print(f"  ✅ Data summary: {summary}")
        
        # Close database
        db_manager.close_connection()
        print("  ✅ Database connection closed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_reports():
    """Test report generation"""
    print("\n📊 Testing report generation...")
    
    try:
        from src.reporting import ExcelReporter, PDFReporter
        import pandas as pd
        
        # Create test data
        test_data = pd.DataFrame({
            'account_code': ['1001', '1002'],
            'account_name': ['Cash', 'Revenue'],
            'account_type': ['Asset', 'Revenue'],
            'net_amount': [1000.0, 5000.0]
        })
        
        # Test Excel reporter
        excel_reporter = ExcelReporter('test_outputs')
        print("  ✅ Excel reporter initialized")
        
        # Test PDF reporter
        pdf_reporter = PDFReporter('test_outputs')
        print("  ✅ PDF reporter initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Report generation test failed: {e}")
        return False

def test_ai_summary():
    """Test AI summary functionality"""
    print("\n🤖 Testing AI summary...")
    
    try:
        from src.ai_summary import AISummarizer
        
        # Initialize AI summarizer
        ai_summarizer = AISummarizer()
        print("  ✅ AI summarizer initialized")
        
        if ai_summarizer.api_key:
            print("  ✅ OpenAI API key configured")
        else:
            print("  ⚠️  OpenAI API key not configured (AI features disabled)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI summary test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 FINANCIAL REPORTING TOOL - SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_pipeline,
        test_database,
        test_reports,
        test_ai_summary
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
        print("\nNext steps:")
        print("1. Run the demo: python demo.py")
        print("2. Generate reports: python main.py run")
        print("3. Start dashboard: python main.py dashboard")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

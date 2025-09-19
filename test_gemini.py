#!/usr/bin/env python3
"""
Test script for Gemini AI integration in Financial Reporting Tool
"""

import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_gemini_integration():
    """Test Gemini AI integration"""
    print("🧪 Testing Gemini AI Integration")
    print("=" * 40)
    
    try:
        from src.ai_summary.ai_summarizer import AISummarizer
        
        # Check if Gemini API key is available
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            print("📝 Please add your Gemini API key to .env file:")
            print("   GEMINI_API_KEY=your_gemini_api_key_here")
            return False
        
        print("✅ Gemini API key found")
        
        # Initialize Gemini summarizer
        print("🔧 Initializing Gemini AI summarizer...")
        summarizer = AISummarizer(provider='gemini')
        
        if not summarizer.api_key:
            print("❌ Failed to initialize Gemini API")
            return False
        
        print("✅ Gemini AI summarizer initialized successfully")
        
        # Create test data
        print("📊 Creating test financial data...")
        pnl_data = pd.DataFrame({
            'account_code': ['4001', '4002', '5001', '5002'],
            'account_name': ['Sales Revenue', 'Service Revenue', 'Office Supplies', 'Travel Expenses'],
            'account_type': ['Revenue', 'Revenue', 'Expense', 'Expense'],
            'net_amount': [50000.0, 25000.0, -5000.0, -3000.0]
        })
        
        expense_data = pd.DataFrame({
            'category': ['Office Supplies', 'Travel', 'Marketing'],
            'total_amount': [5000.0, 3000.0, 2000.0]
        })
        
        vendor_data = pd.DataFrame({
            'vendor_name': ['Office Depot', 'Delta Airlines', 'Google Ads'],
            'total_amount': [3000.0, 2000.0, 1500.0]
        })
        
        print("✅ Test data created")
        
        # Test executive summary generation
        print("🤖 Testing executive summary generation...")
        result = summarizer.generate_executive_summary(
            pnl_data, expense_data, vendor_data, "2024-01"
        )
        
        if result['status'] == 'success':
            print("✅ Executive summary generated successfully!")
            print(f"📝 Provider: {result.get('provider', 'unknown')}")
            print(f"🤖 Model: {result.get('model_used', 'unknown')}")
            print(f"📊 Data points: {result.get('data_points', 0)}")
            print("\n📄 Summary preview:")
            print("-" * 30)
            print(result['summary'][:200] + "..." if len(result['summary']) > 200 else result['summary'])
            print("-" * 30)
        else:
            print(f"❌ Executive summary failed: {result['summary']}")
            return False
        
        # Test risk analysis
        print("\n🔍 Testing risk analysis...")
        risk_result = summarizer.generate_risk_analysis(
            pnl_data, expense_data, vendor_data, "2024-01"
        )
        
        if risk_result['status'] == 'success':
            print("✅ Risk analysis generated successfully!")
            print(f"📝 Provider: {risk_result.get('provider', 'unknown')}")
        else:
            print(f"❌ Risk analysis failed: {risk_result['analysis']}")
        
        print("\n🎉 Gemini integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Please install required packages:")
        print("   pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Gemini AI Integration Test")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Creating from env.example...")
        if os.path.exists('env.example'):
            import shutil
            shutil.copy('env.example', '.env')
            print("✅ .env file created. Please add your Gemini API key.")
        else:
            print("❌ env.example file not found.")
            return 1
    
    success = test_gemini_integration()
    
    if success:
        print("\n✅ All tests passed! Gemini integration is working.")
        print("\n📋 Next steps:")
        print("1. Add your Gemini API key to .env file")
        print("2. Run the main pipeline: python main.py run")
        print("3. The AI summaries will now use Gemini instead of OpenAI")
        return 0
    else:
        print("\n❌ Tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Setup script for the Financial Reporting Tool.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "sample_data",
        "outputs",
        "outputs/reports",
        "outputs/logs",
        "outputs/dashboard"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ Created: {directory}")
    
    return True

def setup_environment():
    """Setup environment configuration"""
    print("⚙️  Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("  ✅ Created .env file from template")
        print("  📝 Please edit .env file with your configuration")
    elif env_file.exists():
        print("  ✅ .env file already exists")
    else:
        print("  ⚠️  No env.example file found")
    
    return True

def run_tests():
    """Run basic tests"""
    print("🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        print("✅ Tests passed successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Some tests failed, but setup can continue")
        return True
    except FileNotFoundError:
        print("⚠️  pytest not found, skipping tests")
        return True

def main():
    """Main setup function"""
    print("🚀 FINANCIAL REPORTING TOOL - SETUP")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run the demo: python demo.py")
    print("3. Or start the dashboard: python main.py dashboard")
    print("4. Or run the pipeline: python main.py run")
    print("=" * 50)

if __name__ == '__main__':
    main()

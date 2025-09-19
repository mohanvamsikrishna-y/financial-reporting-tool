#!/usr/bin/env python3
"""
Deployment helper script for Streamlit Cloud
"""

import os
import subprocess
import sys

def check_git():
    """Check if git is initialized"""
    if not os.path.exists('.git'):
        print("Initializing git repository...")
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git repository initialized")
    else:
        print("✅ Git repository already exists")

def check_files():
    """Check if required files exist"""
    required_files = ['app.py', 'requirements.txt', '.streamlit/config.toml']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def setup_git():
    """Setup git for deployment"""
    print("Setting up git for deployment...")
    
    # Add all files
    subprocess.run(['git', 'add', '.'], check=True)
    print("✅ Files added to git")
    
    # Check if there are changes to commit
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.run(['git', 'commit', '-m', 'Deploy to Streamlit Cloud'], check=True)
        print("✅ Changes committed")
    else:
        print("✅ No changes to commit")

def main():
    """Main deployment setup"""
    print("🚀 Setting up for Streamlit Cloud deployment...")
    print("=" * 50)
    
    # Check git
    check_git()
    
    # Check files
    if not check_files():
        print("❌ Please ensure all required files are present")
        return
    
    # Setup git
    setup_git()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Push to GitHub:")
    print("   git remote add origin https://github.com/yourusername/financial-reporting-tool.git")
    print("   git push -u origin main")
    print("\n2. Deploy to Streamlit Cloud:")
    print("   - Go to https://share.streamlit.io")
    print("   - Sign in with GitHub")
    print("   - Click 'New app'")
    print("   - Select your repository")
    print("   - Set main file: app.py")
    print("   - Add GEMINI_API_KEY in secrets")
    print("   - Click 'Deploy'")
    print("\n3. Your app will be live at: https://your-app-name.streamlit.app")

if __name__ == "__main__":
    main()

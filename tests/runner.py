#!/usr/bin/env python3
"""
Simple test runner for the Compliance Document Service
Runs the most important integration tests
"""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run the test suite"""
    print("🚀 Running Compliance Document Service Tests")
    print("=" * 60)
    
    # Check if test files exist
    test_files_dir = Path("test_files")
    if not test_files_dir.exists():
        print("❌ Test files directory not found!")
        print("   Please ensure the 'test_files' directory exists with PDF test files.")
        return False
    
    pdf_files = list(test_files_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF test files found!")
        print("   Please add PDF files to the 'test_files' directory.")
        return False
    
    print(f"✅ Found {len(pdf_files)} test PDF files:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    
    # Check if required packages are installed
    try:
        import pytest
        import fastapi
        import httpx
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Please install test dependencies: pip install -r requirements.txt")
        return False
    
    # Run the tests
    print("\n🧪 Running integration tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_integration.py", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_quick_test():
    """Run a quick manual test of the API"""
    print("\n🔍 Running quick API test...")
    
    try:
        import requests
        import time
        
        # Start the server in background (if not already running)
        print("   Starting server...")
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", "127.0.0.1", "--port", "8002"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8002/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get("http://127.0.0.1:8002/", timeout=5)
        if response.status_code == 200 and "Compliance Document Checker" in response.text:
            print("   ✅ Web interface accessible")
        else:
            print(f"   ❌ Web interface failed: {response.status_code}")
            return False
        
        # Test with a sample PDF file
        test_files_dir = Path("test_files")
        if test_files_dir.exists():
            pdf_files = list(test_files_dir.glob("*.pdf"))
            if pdf_files:
                pdf_file = pdf_files[0]
                with open(pdf_file, "rb") as f:
                    files = {"files": (pdf_file.name, f, "application/pdf")}
                    response = requests.post("http://127.0.0.1:8002/check-docs", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if "results" in data and len(data["results"]) > 0:
                        print(f"   ✅ PDF processing successful: {data['results'][0]['doc_type']}")
                    else:
                        print("   ❌ PDF processing returned no results")
                        return False
                else:
                    print(f"   ❌ PDF processing failed: {response.status_code}")
                    return False
        
        # Stop the server
        server_process.terminate()
        server_process.wait()
        
        print("   ✅ Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Quick test failed: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = run_quick_test()
    else:
        success = run_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("   The Compliance Document Service is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        print("   Please check the errors above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
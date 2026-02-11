"""
Test Backend Connection
Verifies that the client can reach the backend server
Run this BEFORE building the exe to ensure backend is accessible
"""
import requests
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

def test_connection():
    """Test backend server connection"""
    print("\n" + "="*60)
    print("🔌 ParentEye Backend Connection Test")
    print("="*60)
    
    print(f"\n📍 Backend URL: {BACKEND_URL}")
    print("-"*60)
    
    tests = [
        ("Basic Connection", f"{BACKEND_URL}/"),
        ("API Status", f"{BACKEND_URL}/api/status"),
        ("Device Registration", f"{BACKEND_URL}/api/devices"),
    ]
    
    all_passed = True
    
    for test_name, url in tests:
        try:
            print(f"\n🔍 Testing {test_name}...", end=" ")
            response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 401, 404]:  # 401/404 is OK if backend is responding
                print(f"✅ OK (Status: {response.status_code})")
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ FAILED - Cannot connect")
            all_passed = False
        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Timeout (server not responding)")
            all_passed = False
        except Exception as e:
            print(f"❌ FAILED - {type(e).__name__}: {e}")
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ Backend is REACHABLE")
        print("\n✓ You can proceed to build the EXE")
        print("  Run: build_exe.bat")
        return True
    else:
        print("❌ Backend is NOT REACHABLE")
        print("\n⚠️  Fix these issues first:")
        print("  1. Check if backend server is running")
        print("  2. Verify BACKEND_URL in .env is correct")
        print("  3. Check firewall settings")
        print("  4. Check network connectivity")
        print("\nDEBUG:")
        print(f"  • Backend: {BACKEND_URL}")
        print(f"  • Try in browser: {BACKEND_URL}")
        print(f"  • Or from command line: curl {BACKEND_URL}")
        return False

def main():
    """Main function"""
    success = test_connection()
    
    print("\n")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

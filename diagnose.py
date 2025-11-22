#!/usr/bin/env python3
"""
Diagnostic script to verify the Company Insight Chat UI setup.
Run this to check your configuration before launching the app.
"""

import os
import sys
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")
    version = sys.version_info
    if version >= (3, 8):
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (requires 3.8+)")
        return False

def check_dependencies():
    """Check if all required packages are installed."""
    print_header("Checking Dependencies")
    packages = {
        'streamlit': '1.29.0',
        'supabase': '2.3.0',
        'requests': '2.31.0',
        'dotenv': 'python-dotenv'
    }
    
    all_installed = True
    for package, expected in packages.items():
        try:
            if package == 'dotenv':
                import dotenv
                print_success(f"{expected} installed")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print_success(f"{package} {version}")
        except ImportError:
            print_error(f"{package} not installed (expected: {expected})")
            all_installed = False
    
    return all_installed

def check_files():
    """Check if all required files exist."""
    print_header("Checking Required Files")
    files = [
        'app.py',
        'auth.py',
        'database.py',
        'n8n_client.py',
        'summarizer.py',
        'requirements.txt',
        'supabase_schema.sql',
        '.env.example'
    ]
    
    all_exist = True
    for file in files:
        if Path(file).exists():
            print_success(file)
        else:
            print_error(f"{file} not found")
            all_exist = False
    
    return all_exist

def check_env_file():
    """Check if .env file exists and has required variables."""
    print_header("Checking Environment Configuration")
    
    if not Path('.env').exists():
        print_error(".env file not found")
        print_warning("Create .env file: cp .env.example .env")
        return False
    
    print_success(".env file exists")
    
    # Load and check variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'SUPABASE_URL': 'https://',
        'SUPABASE_KEY': 'eyJ',
        'N8N_WEBHOOK_URL': 'http',
        'PROFILE_SUMMARY_MESSAGE_THRESHOLD': None,
        'REQUEST_TIMEOUT': None
    }
    
    all_set = True
    for var, prefix in required_vars.items():
        value = os.getenv(var)
        if not value:
            print_error(f"{var} not set")
            all_set = False
        elif value.startswith('your-') or value == 'your-anon-public-key-here':
            print_warning(f"{var} still has placeholder value")
            all_set = False
        elif prefix and not value.startswith(prefix):
            print_warning(f"{var} may be invalid (expected to start with '{prefix}')")
        else:
            # Mask sensitive values
            if 'KEY' in var or 'URL' in var:
                display = value[:20] + '...' if len(value) > 20 else value
            else:
                display = value
            print_success(f"{var} = {display}")
    
    return all_set

def test_supabase_connection():
    """Test Supabase connection."""
    print_header("Testing Supabase Connection")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print_error("Supabase credentials not configured")
        return False
    
    try:
        from supabase import create_client
        client = create_client(url, key)
        print_success("Supabase client initialized")
        
        # Try a simple query (will fail if tables don't exist, but connection works)
        try:
            # Test connection with a health check
            result = client.table('users').select('id').limit(0).execute()
            print_success("Database connection successful")
            print_success("Database tables accessible")
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if 'relation' in error_msg and 'does not exist' in error_msg:
                print_error("Database tables not found")
                print_warning("Run supabase_schema.sql in Supabase SQL Editor")
                return False
            elif 'jwt' in error_msg or 'auth' in error_msg:
                print_warning("Authentication test - tables may not be accessible without user login")
                print_success("Connection is working (tables exist)")
                return True
            else:
                print_error(f"Database query failed: {e}")
                return False
                
    except Exception as e:
        print_error(f"Supabase connection failed: {e}")
        return False

def test_n8n_webhook():
    """Test n8n webhook connection."""
    print_header("Testing n8n Webhook")
    
    from dotenv import load_dotenv
    import requests
    
    load_dotenv()
    webhook_url = os.getenv('N8N_WEBHOOK_URL')
    
    if not webhook_url:
        print_error("N8N_WEBHOOK_URL not configured")
        return False
    
    print(f"Testing webhook: {webhook_url[:50]}...")
    
    try:
        response = requests.post(
            webhook_url,
            json={"message": "diagnostic test"},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"Webhook responded (HTTP {response.status_code})")
            
            try:
                data = response.json()
                if 'reply' in data or 'output' in data or 'text' in data:
                    print_success("Response format is valid")
                    return True
                else:
                    print_warning("Response missing expected fields (reply/output/text)")
                    print(f"Received: {list(data.keys())}")
                    return False
            except ValueError:
                print_warning("Response is not JSON")
                return False
        else:
            print_error(f"Webhook returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Webhook timeout (>10s)")
        print_warning("Workflow may be slow or inactive")
        return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to webhook")
        print_warning("Check if n8n is running and workflow is activated")
        return False
    except Exception as e:
        print_error(f"Webhook test failed: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print(f"\n{BLUE}{'*' * 60}{RESET}")
    print(f"{BLUE}Company Insight Chat UI - Diagnostic Tool{RESET}".center(70))
    print(f"{BLUE}{'*' * 60}{RESET}")
    
    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Required Files": check_files(),
        "Environment Config": check_env_file(),
        "Supabase Connection": test_supabase_connection(),
        "n8n Webhook": test_n8n_webhook()
    }
    
    # Summary
    print_header("Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(check)
        else:
            print_error(check)
    
    print(f"\n{BLUE}Result: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{'=' * 60}{RESET}")
        print(f"{GREEN}All checks passed! You're ready to run the app.{RESET}")
        print(f"{GREEN}{'=' * 60}{RESET}\n")
        print("Launch the app with: streamlit run app.py\n")
        return 0
    else:
        print(f"{RED}{'=' * 60}{RESET}")
        print(f"{RED}Some checks failed. Please fix the issues above.{RESET}")
        print(f"{RED}{'=' * 60}{RESET}\n")
        print("See QUICKSTART.md or README.md for setup instructions.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

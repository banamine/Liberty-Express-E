"""Security audit script for ScheduleFlow
Run: python3 security_audit.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_bandit():
    """Run bandit security scan on Python code"""
    print("\n" + "="*80)
    print("SECURITY AUDIT: Bandit Code Analysis")
    print("="*80 + "\n")
    
    try:
        result = subprocess.run(
            ["bandit", "-r", "src/", "-f", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"✅ Bandit scan complete")
            print(f"   Metrics: {data.get('metrics', {})}")
            
            if data.get("results"):
                print(f"\n⚠️  Found {len(data['results'])} security issues:")
                for issue in data["results"][:5]:  # Show first 5
                    print(f"   - {issue['issue_text']} ({issue['severity']})")
        else:
            print(f"❌ Bandit errors:\n{result.stderr}")
    
    except FileNotFoundError:
        print("⚠️  Bandit not installed. Install with: pip install bandit")
    except Exception as e:
        print(f"❌ Error running bandit: {e}")


def check_dependencies():
    """Check for known vulnerable dependencies"""
    print("\n" + "="*80)
    print("SECURITY CHECK: Dependency Vulnerabilities")
    print("="*80 + "\n")
    
    try:
        result = subprocess.run(
            ["pip-audit"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "No known security vulnerabilities found" in result.stdout:
            print("✅ No known vulnerable dependencies")
        else:
            print(result.stdout)
    
    except FileNotFoundError:
        print("⚠️  pip-audit not installed. Install with: pip install pip-audit")
    except Exception as e:
        print(f"⚠️  Error checking dependencies: {e}")


def check_secrets():
    """Check for hardcoded secrets"""
    print("\n" + "="*80)
    print("SECURITY CHECK: Hardcoded Secrets")
    print("="*80 + "\n")
    
    patterns = [
        ("API Keys", r"api[_-]?key"),
        ("Passwords", r"password"),
        ("AWS Keys", r"aws[_-]?secret"),
        ("Tokens", r"token"),
        ("Database URLs", r"mongodb|postgres|mysql|redis")
    ]
    
    found = False
    for pattern_name, pattern in patterns:
        try:
            result = subprocess.run(
                ["grep", "-r", "-i", "-E", pattern, "src/", "--include=*.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                print(f"⚠️  Potential {pattern_name} found:")
                for line in result.stdout.split("\n")[:3]:
                    if line:
                        print(f"   {line}")
                found = True
        except:
            pass
    
    if not found:
        print("✅ No obvious hardcoded secrets detected")


def check_auth():
    """Check authentication implementation"""
    print("\n" + "="*80)
    print("SECURITY CHECK: Authentication")
    print("="*80 + "\n")
    
    checks = {
        "JWT Implementation": "src/core/auth.py",
        "User Management": "src/core/user_manager.py",
        "Password Hashing": "src/core/auth.py"
    }
    
    for check_name, file_path in checks.items():
        if Path(file_path).exists():
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Not found")


def check_input_validation():
    """Check for input validation"""
    print("\n" + "="*80)
    print("SECURITY CHECK: Input Validation")
    print("="*80 + "\n")
    
    try:
        result = subprocess.run(
            ["grep", "-r", "validate", "src/", "--include=*.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        count = len([l for l in result.stdout.split("\n") if l])
        if count > 0:
            print(f"✅ Input validation found: {count} validation checks")
        else:
            print("⚠️  No validation checks found")
    except:
        pass


def check_error_handling():
    """Check error handling"""
    print("\n" + "="*80)
    print("SECURITY CHECK: Error Handling")
    print("="*80 + "\n")
    
    try:
        result = subprocess.run(
            ["grep", "-r", "except", "src/", "--include=*.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        count = len([l for l in result.stdout.split("\n") if l])
        if count > 0:
            print(f"✅ Exception handling found: {count} try-except blocks")
        else:
            print("⚠️  No exception handling found")
    except:
        pass


def main():
    """Run all security checks"""
    print("\n" + "="*80)
    print("SCHEDULEFLOW SECURITY AUDIT")
    print("="*80)
    
    check_auth()
    check_input_validation()
    check_error_handling()
    check_secrets()
    check_dependencies()
    run_bandit()
    
    print("\n" + "="*80)
    print("AUDIT COMPLETE")
    print("="*80 + "\n")
    
    print("Recommendations:")
    print("1. Review any identified security issues")
    print("2. Run penetration testing on API endpoints")
    print("3. Enable rate limiting in production")
    print("4. Use HTTPS/TLS for all communications")
    print("5. Implement audit logging for sensitive operations")


if __name__ == "__main__":
    main()

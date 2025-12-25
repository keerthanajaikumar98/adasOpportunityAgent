"""Quick test to verify setup before Git."""

import os
from dotenv import load_dotenv

print("=" * 60)
print("ADAS Agent - Setup Verification")
print("=" * 60)

# Test 1: Check if .env file exists
print("\n1. Checking for .env file...")
if os.path.exists('.env'):
    print("   ✅ .env file found")
else:
    print("   ❌ .env file NOT found - create it from .env.example")
    exit(1)

# Test 2: Load environment variables
print("\n2. Loading environment variables...")
load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print(f"   ✅ API key loaded (starts with: {api_key[:15]}...)")
else:
    print("   ❌ API key NOT loaded - check your .env file")
    exit(1)

# Test 3: Check model setting
model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
print(f"\n3. Model setting: {model}")
print("   ✅ Model configured")

print("\n" + "=" * 60)
print("Environment setup looks good! ✅")
print("=" * 60)
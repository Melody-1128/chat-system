#!/usr/bin/env python3
"""
Verification script for DeepSeek chatbot integration.
Run this to check if all dependencies and configurations are correct.
"""

import os
import sys


def check_python_version():
    """Check if Python version is 3.7+"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python 3.7+ required")
        return False
    return True


def check_tkinter():
    """Check if Tkinter is available"""
    try:
        import tkinter
        print("✓ Tkinter is available")
        return True
    except ImportError:
        print("✗ Tkinter is NOT available")
        print("  Install with: python3 -m pip install tk")
        return False


def check_openai_sdk():
    """Check if OpenAI SDK is installed"""
    try:
        import openai
        print(f"✓ OpenAI SDK is installed (version {openai.__version__})")
        return True
    except ImportError:
        print("✗ OpenAI SDK is NOT installed")
        print("  Install with: pip install openai")
        return False


def check_deepseek_api_key():
    """Check if DEEPSEEK_API_KEY is set"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        # Show first few chars, hide the rest
        masked_key = api_key[:10] + "*" * (len(api_key) - 20) + api_key[-10:]
        print(f"✓ DEEPSEEK_API_KEY is set: {masked_key}")
        return True
    else:
        print("✗ DEEPSEEK_API_KEY environment variable is NOT set")
        print("  Set with: export DEEPSEEK_API_KEY='your_api_key'")
        return False


def check_chat_files():
    """Check if required chat files exist"""
    files_to_check = [
        "chat_gui_client.py",
        "chat_server.py",
        "chat_utils.py",
        "deepseek_bot.py",
    ]
    all_exist = True
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"✓ {filename} exists")
        else:
            print(f"✗ {filename} NOT found")
            all_exist = False
    return all_exist


def test_deepseek_api_connection():
    """Test connection to DeepSeek API"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("⚠ Skipping API test (no API key)")
            return False
        
        print("⏳ Testing DeepSeek API connection...")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        
        print(f"✓ DeepSeek API connection successful")
        print(f"  Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"✗ DeepSeek API test failed: {str(e)}")
        return False


def test_chatbot_class():
    """Test if chatbot class can be instantiated"""
    try:
        from deepseek_bot import DeepSeekChatBot
        
        print("⏳ Testing DeepSeekChatBot class...")
        
        # Check if API key is set
        if not os.getenv("DEEPSEEK_API_KEY"):
            print("⚠ Cannot test chatbot (no API key set)")
            return False
        
        bot = DeepSeekChatBot(personality="friendly")
        print("✓ DeepSeekChatBot initialized successfully")
        print(f"  Current personality: {bot.get_personality()}")
        print(f"  Available personalities: {bot.get_available_personalities()}")
        return True
        
    except Exception as e:
        print(f"✗ DeepSeekChatBot test failed: {str(e)}")
        return False


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("DeepSeek Chatbot Integration - Verification Script")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Tkinter", check_tkinter),
        ("OpenAI SDK", check_openai_sdk),
        ("DeepSeek API Key", check_deepseek_api_key),
        ("Chat Files", check_chat_files),
        ("API Connection", test_deepseek_api_connection),
        ("Chatbot Class", test_chatbot_class),
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n[{name}]")
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Error during check: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! Ready to use the chatbot.")
        print("\nNext steps:")
        print("1. Terminal 1: python3 chat_server.py")
        print("2. Terminal 2: python3 chat_gui_client.py")
        print("3. Type '@bot What is Python?' to test the chatbot")
        return 0
    else:
        print("\n✗ Some checks failed. Fix the issues above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

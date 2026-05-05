#!/usr/bin/env python3
"""
Quick start example for testing the chatbot integration.
This script demonstrates how to use the chatbot directly.
"""

import os
import sys

# Add the project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from deepseek_bot import DeepSeekChatBot


def main():
    print("=" * 60)
    print("DeepSeek Chatbot - Quick Start Example")
    print("=" * 60)
    print()
    
    # Check if API key is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("ERROR: DEEPSEEK_API_KEY environment variable is not set!")
        print("Set it with: export DEEPSEEK_API_KEY='your_api_key'")
        return 1
    
    print("Initializing chatbot...")
    try:
        bot = DeepSeekChatBot(personality="friendly")
        print(f"✓ Chatbot initialized with personality: {bot.get_personality()}")
    except Exception as e:
        print(f"✗ Failed to initialize chatbot: {e}")
        return 1
    
    print()
    print("Available personalities:", bot.get_available_personalities())
    print()
    print("Chat examples (type 'quit' to exit):")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Check for personality change command
            if user_input.startswith("/personality "):
                personality = user_input.replace("/personality ", "").strip()
                try:
                    bot.set_personality(personality)
                    bot.reset_history()
                    print(f"✓ Personality changed to: {personality}")
                    continue
                except ValueError as e:
                    print(f"✗ {e}")
                    continue
            
            # Get chatbot response
            print("Chatbot: ", end="", flush=True)
            response = bot.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
DeepSeek Chatbot Module

Provides a chatbot class that uses OpenAI-compatible API for DeepSeek.
Supports conversation history, personality system, and context awareness.
"""

import os
from openai import OpenAI

# Default system prompts for different personalities
PERSONALITY_PROMPTS = {
    "friendly": """You are a friendly and warm AI assistant. Be casual, supportive, and approachable in your responses. 
Use simple language and show genuine interest in the user's questions. Add a touch of humor when appropriate.""",
    
    "professional": """You are a professional and knowledgeable AI assistant. Provide concise, formal, and technically accurate responses.
Focus on clarity and precision. Use proper terminology and structure your answers logically.""",
    
    "funny": """You are a humorous and witty AI assistant. Make your responses entertaining while still being helpful.
Use appropriate jokes, puns, or light-hearted comments. Keep it fun but never inappropriate."""
}


class DeepSeekChatBot:
    """
    DeepSeek chatbot using OpenAI-compatible API.
    
    Supports:
    - Conversation history for context awareness
    - Multiple personalities (friendly, professional, funny)
    - Graceful error handling
    """
    
    def __init__(self, personality="friendly"):
        """
        Initialize the chatbot.
        
        Args:
            personality (str): One of "friendly", "professional", or "funny"
        
        Raises:
            ValueError: If API key is missing or personality is invalid
        """
        # Load API key from environment
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        
        # Initialize OpenAI client with DeepSeek API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Set personality and initialize conversation history
        self.personality = personality
        self.conversation_history = []  # Stores messages for context awareness
        self.max_history = 10  # Keep last 10 turns to avoid extremely long prompts
        
        if personality not in PERSONALITY_PROMPTS:
            raise ValueError(f"Unknown personality: {personality}. Choose from: {list(PERSONALITY_PROMPTS.keys())}")
    
    def set_personality(self, personality):
        """
        Change the chatbot's personality.
        
        Args:
            personality (str): One of "friendly", "professional", or "funny"
        
        Raises:
            ValueError: If personality is invalid
        """
        if personality not in PERSONALITY_PROMPTS:
            raise ValueError(f"Unknown personality: {personality}. Choose from: {list(PERSONALITY_PROMPTS.keys())}")
        self.personality = personality
    
    def chat(self, user_message):
        """
        Send a message to the chatbot and get a response.
        
        This method maintains conversation history for context awareness.
        Previous turns are included in the API call to provide context.
        
        Args:
            user_message (str): The user's message
        
        Returns:
            str: The chatbot's response, or an error message on failure
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Build messages list with system prompt + history
            messages = [
                {
                    "role": "system",
                    "content": PERSONALITY_PROMPTS[self.personality]
                }
            ]
            
            # Add conversation history (limit to last N turns)
            # Each turn is user + assistant, so max_history messages
            start_idx = max(0, len(self.conversation_history) - self.max_history)
            messages.extend(self.conversation_history[start_idx:])
            
            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract and store assistant response
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        
        except ValueError as e:
            # Handle API key or model errors
            return f"Chatbot error: {str(e)}"
        except Exception as e:
            # Handle API connection or other errors
            return f"Chatbot error: {str(e)}"
    
    def reset_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_personality(self):
        """Get the current personality."""
        return self.personality
    
    def get_available_personalities(self):
        """Get list of available personalities."""
        return list(PERSONALITY_PROMPTS.keys())

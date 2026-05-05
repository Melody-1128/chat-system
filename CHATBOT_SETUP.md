# DeepSeek Chatbot Integration - Setup & Usage Guide

## Overview

This integration adds a DeepSeek AI chatbot feature to the existing socket-based GUI chat system. The chatbot supports:
- **Direct chatbot interaction**: Type `@bot` to chat with the AI
- **Context awareness**: Conversation history is maintained during the session
- **Multiple personalities**: Switch between friendly, professional, and funny modes
- **Group chat participation**: Bot responds when mentioned with `@bot` or `@chatbot`
- **Non-blocking**: API calls run in background threads to keep GUI responsive

## Files Modified/Created

### New Files
- **`deepseek_bot.py`**: DeepSeek chatbot class with personality system and conversation history

### Modified Files
- **`chat_gui_client.py`**: Integrated chatbot UI and message routing

## Prerequisites

1. **Python 3.7+** with Tkinter
2. **OpenAI Python SDK** (version 1.0+)
3. **DeepSeek API key** from https://platform.deepseek.com

## Installation

### Step 1: Install Dependencies

```bash
pip install openai
```

### Step 2: Set Up DeepSeek API Key

Get your API key from [DeepSeek Platform](https://platform.deepseek.com), then set it as an environment variable:

**On macOS/Linux:**
```bash
export DEEPSEEK_API_KEY="your_api_key_here"
```

**On Windows (Command Prompt):**
```cmd
set DEEPSEEK_API_KEY=your_api_key_here
```

**On Windows (PowerShell):**
```powershell
$env:DEEPSEEK_API_KEY="your_api_key_here"
```

**Persistent setup (Optional):**
Add to your shell profile (~/.bash_profile, ~/.zshrc, etc.):
```bash
export DEEPSEEK_API_KEY="your_api_key_here"
```

## Running the System

### Terminal 1: Start the Server
```bash
cd /Users/zhangmojia/Desktop/icds/unit\ project/UP3
python3 chat_server.py
```

### Terminal 2: Start Client 1
```bash
cd /Users/zhangmojia/Desktop/icds/unit\ project/UP3
python3 chat_gui_client.py --host 127.0.0.1 --port 1112
```

### Terminal 3: Start Client 2 (Optional, for group chat)
```bash
cd /Users/zhangmojia/Desktop/icds/unit\ project/UP3
python3 chat_gui_client.py --host 127.0.0.1 --port 1112
```

## How to Use the Chatbot

### A. Basic Chatbot Chat (Direct)

1. **Login** with a username (e.g., "Melody")
2. **In the message input box**, type:
   ```
   @bot What is socket programming?
   ```
3. **Press Enter** or click **Send**
4. The chatbot will respond with an answer

**Example:**
```
Melody: @bot What is socket programming?
Chatbot: Socket programming is a way of connecting two nodes on a network...
```

### B. Change Personality

1. **Locate the "Personality" selector** (bottom right area of the chat window)
2. **Select one of:**
   - `friendly` - Warm, casual, supportive tone
   - `professional` - Concise, formal, technical
   - `funny` - Humorous but helpful

3. The chatbot personality changes immediately for subsequent messages
4. **Note**: Changing personality resets the conversation history

**Example:**
```
Personality changed to: professional
Melody: @bot What is machine learning?
Chatbot: Machine learning is a subset of artificial intelligence that enables...
```

### C. Context Awareness (Conversation History)

The chatbot remembers previous turns within the current session:

**Example:**
```
Melody: @bot My favorite programming language is Python.
Chatbot: That's great! Python is known for its clean syntax and versatility...

Melody: @bot What language did I say I like?
Chatbot: You mentioned that your favorite programming language is Python!
```

**How it works:**
- Each conversation is stored in memory
- The last 10 user/assistant turns are sent with each API call for context
- Closing and reopening the client clears history
- Changing personality resets history

### D. Group Chat with Bot Mentions

When connected to a chat group with other clients:

1. **Connect to another user** as usual
2. **Type a message mentioning the bot**:
   ```
   Hey everyone, @bot can you explain recursion?
   ```
3. **The bot will:**
   - Display the message normally in the group chat
   - Generate and display a response locally in your GUI

**Note**: The bot response appears in your client. To share with other users, you could mention the response in follow-up messages.

## Personality System

### Friendly Mode
- Warm and supportive tone
- Uses simple language
- Shows genuine interest
- Adds light humor when appropriate

### Professional Mode
- Formal and technical
- Concise and precise
- Uses proper terminology
- Logically structured responses

### Funny Mode
- Witty and entertaining
- Includes appropriate jokes/puns
- Still helpful and accurate
- Keeps a playful tone

## Error Handling

### Missing API Key
If you see this message:
```
Chatbot: DeepSeek API key is missing. Please set DEEPSEEK_API_KEY.
```

**Solution:** Set the environment variable as shown in the "Installation" section.

### API Connection Errors
If you see:
```
Chatbot: Chatbot error: Connection failed
```

**Solutions:**
- Check internet connection
- Verify API key is correct and active
- Check if DeepSeek API is operational at https://platform.deepseek.com

### GUI Freezing
The chatbot uses background threads, so the GUI should never freeze. If it does:
- Kill the process and restart
- Check terminal for error messages
- Report the issue

## Code Architecture

### deepseek_bot.py
```
DeepSeekChatBot class:
├── __init__(personality="friendly")
│   ├── Load API key from environment
│   ├── Initialize OpenAI client (DeepSeek endpoint)
│   └── Set up conversation history
├── chat(user_message)
│   ├── Add message to history
│   ├── Call DeepSeek API with context
│   └── Return response
├── set_personality(personality)
│   └── Change personality system prompt
├── reset_history()
│   └── Clear conversation memory
└── get_personality() / get_available_personalities()
```

### chat_gui_client.py Changes
```
ChatGUI class additions:
├── Attributes:
│   ├── self.chatbot: DeepSeekChatBot instance
│   ├── self.bot_responses: Queue for bot thread responses
│   ├── self.personality_var: Current personality selection
│   └── self.bot_initialized: API key validation flag
├── UI Elements:
│   ├── Personality combobox selector
│   └── Instruction label ("Type '@bot' to chat with AI")
├── Methods:
│   ├── initialize_chatbot(): Setup on startup
│   ├── on_personality_changed(): Handle personality selection
│   ├── process_bot_request(): Background thread function
│   ├── process_bot_responses(): Process thread results
│   └── send_message(): Enhanced with @bot detection
```

## Message Flow Diagram

### Direct Bot Chat
```
User types "@bot question" 
    → send_message() detects @bot prefix
    → Display: "[Username] @bot question"
    → Create background thread
    → process_bot_request() calls chatbot.chat()
    → Response returned to bot_responses queue
    → process_bot_responses() displays: "Chatbot: answer"
```

### Group Chat with Bot Mention
```
User types "message @bot context"
    → send_message() detects @bot in message
    → Send through socket to other clients
    → Display locally: "[Username] message @bot context"
    → Extract mention text "context"
    → Create background thread
    → Display bot response locally: "Chatbot: answer"
    → Other clients see the original message but not bot response
```

## Testing Checklist

### Basic Functionality
- [ ] Login successfully
- [ ] Type `@bot What is Python?`
- [ ] Chatbot responds
- [ ] GUI doesn't freeze during API call

### Context Awareness
- [ ] User: `@bot My name is Alice`
- [ ] Chatbot: "Nice to meet you, Alice..."
- [ ] User: `@bot What is my name?`
- [ ] Chatbot: "Your name is Alice"

### Personality Switching
- [ ] Select "friendly" → Type `@bot hello`
- [ ] Select "professional" → Type same question
- [ ] Compare responses (different tones)
- [ ] Verify history resets when changing personality

### Group Chat
- [ ] Start 2 clients (User1, User2)
- [ ] User1 connects to User2
- [ ] User1: `@bot What is networking?`
- [ ] Verify bot response appears in User1's chat
- [ ] Verify User2 sees the original message but not bot response

### Error Handling
- [ ] Unset API key, try `@bot hello`
- [ ] Should show: "API key is missing..."
- [ ] Set API key correctly, should work again

## Troubleshooting

### Bot doesn't respond
**Check:**
1. Is DEEPSEEK_API_KEY set? → `echo $DEEPSEEK_API_KEY`
2. Is the API key valid? → Test at https://platform.deepseek.com
3. Check internet connection
4. Look for error messages in terminal

### Wrong personality applied
- Changing personality automatically resets history
- Make sure you selected from dropdown, not typed manually

### GUI elements not visible
- Resize the chat window to make sure bot_frame is visible
- Check that all UI elements are in the right grid positions

### Message starts with @bot but bot doesn't respond
- Make sure there's actual content after @bot
- Example: `@bot ` (with space only) won't work
- Use: `@bot hello` (with actual question/message)

## Advanced: Customization

### Change Max Conversation History
Edit `deepseek_bot.py`:
```python
self.max_history = 10  # Change this number
# 10 means keep last 10 user-assistant turns
```

### Add New Personality
Edit `deepseek_bot.py` in the `PERSONALITY_PROMPTS` dictionary:
```python
PERSONALITY_PROMPTS = {
    "your_personality": "Your system prompt here..."
}
```

Then update the combobox in `chat_gui_client.py`:
```python
values=["friendly", "professional", "funny", "your_personality"]
```

### Modify Bot Response Display
In `chat_gui_client.py`, change the format in `process_bot_responses()`:
```python
self.append_log(f"🤖 Bot says: {response.get('message', '')}")  # Different prefix
```

## API Rate Limits

DeepSeek API has usage limits. Check your account at:
https://platform.deepseek.com/usage

Each message costs tokens. The system sends conversation history, so longer conversations cost more.

## Security Notes

- **Never commit API keys** to version control
- API key is only used locally in the background thread
- Conversation history is not sent to any external service except DeepSeek
- DeepSeek privacy policy: https://www.deepseek.com/privacy-policy

## Support

For issues with:
- **DeepSeek API**: https://platform.deepseek.com/support
- **Python OpenAI SDK**: https://github.com/openai/openai-python
- **Chat system**: Review original chat_server.py and chat_utils.py documentation

---

**Last Updated:** May 5, 2026  
**System:** UP3 Chat with DeepSeek Integration  
**Version:** 1.0

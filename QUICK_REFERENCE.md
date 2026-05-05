# 🤖 DeepSeek Chatbot Integration - Quick Reference Card

## 📦 Installation (One-time)

```bash
# 1. Install Python dependency
pip install openai

# 2. Set API key (replace with your actual key)
export DEEPSEEK_API_KEY="sk_..."

# 3. Verify setup
python3 verify_setup.py
```

---

## 🚀 Running (Every Session)

### Terminal 1: Server
```bash
python3 chat_server.py
```

### Terminal 2: Client 1
```bash
python3 chat_gui_client.py
```

### Terminal 3+: Additional Clients (Optional)
```bash
python3 chat_gui_client.py
```

---

## 💬 Using the Chatbot

### Direct Chat with Bot
```
Type in input box: @bot What is Python?
Press Enter

Result:
[YourName] @bot What is Python?
Chatbot: Python is a high-level programming language...
```

### Change Personality
1. Look for "Personality:" dropdown (bottom of chat window)
2. Select: friendly, professional, or funny
3. Type your next `@bot` message

**Important**: Changing personality resets conversation history

### Context Awareness
```
Turn 1:
You: @bot My name is Alice
Bot: Nice to meet you, Alice!

Turn 2:
You: @bot What's my name?
Bot: Your name is Alice!
```

### Group Chat (Multiple Users)
```
User1 types: Hey @bot explain recursion
Result:
- Message sent to other users
- Bot response appears in User1's chat only
- Other users see the message but not the bot response
```

---

## 🔧 Keyboard Shortcuts

| Action | Input |
|--------|-------|
| Send message | Enter or Click Send |
| Clear message | CMD+A then Delete |
| Exit GUI | CMD+Q or Close window |

---

## ⚙️ Chatbot Commands

In the GUI, you can use:
- `@bot question` - Ask the chatbot
- `@chatbot question` - Alternative trigger (same effect)
- Personality selector - Change tone

---

## 🐛 Troubleshooting

### "Chatbot: DeepSeek API key is missing"
```bash
export DEEPSEEK_API_KEY="your_key_here"
```

### "Chatbot error: Connection failed"
- Check internet connection
- Verify API key is valid at https://platform.deepseek.com
- Check if DeepSeek API is online

### GUI freezes during API call
- This shouldn't happen (uses threading)
- Force quit: CMD+Q or kill the process

### Bot doesn't respond to @bot
- Make sure there's text after `@bot`
- Bad: `@bot ` (space only)
- Good: `@bot hello` (has content)

### Wrong personality applied
- Dropdown shows current setting
- Make sure you selected from dropdown
- Personality changes reset history

---

## 📊 API Usage

### Free Tier Limits
- Check at: https://platform.deepseek.com/usage
- Each message costs tokens
- History adds to token count

### Cost Optimization
- Keep `max_history` reasonable (default: 10 turns)
- Long conversations cost more
- Change personality to reset history if needed

---

## 🎯 Personality Quick Reference

### Friendly
```
You: @bot What is AI?
Bot: Hey! AI is super cool - it's like giving computers 
the ability to think and learn, kind of like how we do! 
Pretty neat, right? 😊
```

### Professional
```
You: @bot What is AI?
Bot: Artificial Intelligence (AI) refers to computer systems 
designed to perform tasks that typically require human intelligence. 
This includes learning, problem-solving, and pattern recognition.
```

### Funny
```
You: @bot What is AI?
Bot: AI is like teaching computers to think - though they 
think a LOT faster than we do! Some say AI is the future, 
but honestly, it's also probably judging us for asking it 
silly questions. 🤖
```

---

## 📁 Project Structure

```
UP3/
├── chat_server.py          # Main server
├── chat_gui_client.py      # GUI client (MODIFIED)
├── chat_utils.py           # Utilities
├── deepseek_bot.py         # NEW: Chatbot class
├── CHATBOT_SETUP.md        # Full setup guide
├── verify_setup.py         # Dependency checker
├── chatbot_demo.py         # Command-line demo
└── IMPLEMENTATION_SUMMARY.md
```

---

## 🧪 Quick Test

After setup, test with:
```python
python3 chatbot_demo.py
```

Try commands:
```
You: Hi there!
You: /personality professional
You: Tell me about Python
You: quit
```

---

## 🔐 Security Tips

- ✅ API key in environment only
- ✅ Never commit API key to git
- ✅ Don't share API key
- ✅ Conversation history is local
- ✅ Use HTTPS (built-in with DeepSeek SDK)

---

## 📞 Quick Support

| Issue | Solution |
|-------|----------|
| API key not found | `export DEEPSEEK_API_KEY="..."` |
| OpenAI SDK missing | `pip install openai` |
| Can't import tkinter | Python GUI framework (built-in on most systems) |
| Bot slow to respond | Normal - API call takes time, check network |
| GUI unresponsive | Should use threads - restart client if frozen |

---

## 🎓 Learning Resources

- **DeepSeek Docs**: https://platform.deepseek.com
- **OpenAI SDK**: https://github.com/openai/openai-python
- **Socket Programming**: See chat_server.py & chat_utils.py
- **Threading in Python**: Python docs on threading module

---

## 📝 Session Notes

- Personality selector is at bottom right
- Tip label says "Type '@bot' to chat with AI"
- Each client gets independent conversation history
- Closing client clears history (fresh start on reopen)

---

## ✅ Status Checklist

- [ ] `pip install openai` completed
- [ ] `DEEPSEEK_API_KEY` environment variable set
- [ ] `python3 verify_setup.py` passes all checks
- [ ] Server running in Terminal 1
- [ ] Client running in Terminal 2
- [ ] Can type `@bot` messages
- [ ] Bot responds correctly
- [ ] Personality selector works
- [ ] Context awareness working

---

**Quick Start Time**: ~5 minutes  
**First Working Chatbot**: ~2 minutes after API key setup  
**Enjoy!** 🎉

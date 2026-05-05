# 🧪 DeepSeek Chatbot Integration - Comprehensive Test Plan

## Pre-Test Checklist

- [ ] Python 3.7+ installed
- [ ] `pip install openai` completed
- [ ] `DEEPSEEK_API_KEY` environment variable set
- [ ] All project files in place
- [ ] `python3 verify_setup.py` passes

---

## Test Suite 1: Setup Verification

### Test 1.1: Verify Dependencies
```bash
cd /Users/zhangmojia/Desktop/icds/unit\ project/UP3
python3 verify_setup.py
```

**Expected Result:**
```
✓ Python version: 3.x.x
✓ Tkinter is available
✓ OpenAI SDK is installed
✓ DEEPSEEK_API_KEY is set: sk_...****...
✓ Chat files exist: chat_gui_client.py, chat_server.py, etc.
✓ DeepSeek API connection successful
✓ DeepSeekChatBot initialized successfully

Passed: 7/7
✓ All checks passed! Ready to use the chatbot.
```

**Status:** ✅ / ❌

---

## Test Suite 2: Command-Line Chatbot Demo

### Test 2.1: Run Chatbot Demo
```bash
python3 chatbot_demo.py
```

**Interactions:**
```
You: Hi there!
[Chatbot responds with greeting]

You: My name is TestUser
[Chatbot acknowledges]

You: What's my name?
[Chatbot: Your name is TestUser]

You: /personality professional
[Should show: ✓ Personality changed to: professional]

You: Hi there again
[Chatbot responds in professional tone]

You: quit
```

**Expected Results:**
- [ ] Each message gets a response
- [ ] Responses are relevant
- [ ] Personality changes are applied
- [ ] Context is maintained
- [ ] No errors or crashes

**Status:** ✅ / ❌

---

## Test Suite 3: Basic GUI Functionality

### Test 3.1: Start Server
```bash
# Terminal 1
python3 chat_server.py
```

**Expected Output:**
```
server started...
```

**Status:** ✅ / ❌

### Test 3.2: Start Client
```bash
# Terminal 2
python3 chat_gui_client.py
```

**Expected:**
- GUI window opens with title "UP3 Chat Client"
- Server IP: 127.0.0.1
- Port: 1112
- Username field empty
- All buttons disabled (grayed out)

**Status:** ✅ / ❌

### Test 3.3: Login
1. Enter username: "TestUser"
2. Click "Login"

**Expected:**
- Status changes to "Logged in as TestUser"
- Refresh button enabled
- Message input box enabled
- "Connect to User" button enabled
- Chat log shows: "Logged in as TestUser" message

**Status:** ✅ / ❌

---

## Test Suite 4: Basic Chatbot Functionality

### Test 4.1: Direct Bot Chat - Simple Question
1. In message input, type: `@bot What is Python?`
2. Press Enter

**Expected in Chat Log:**
```
Logged in as TestUser
...
[TestUser] @bot What is Python?
Chatbot: Python is a high-level programming language known for...
```

**Pass Criteria:**
- [x] Message appears with [TestUser] prefix
- [x] Bot response appears with "Chatbot:" prefix
- [x] Response is relevant to question
- [x] GUI doesn't freeze during API call

**Status:** ✅ / ❌

### Test 4.2: Empty Bot Message
1. Type: `@bot `
2. Press Enter

**Expected:**
```
[Bot] Please provide a message after @bot
```

**Status:** ✅ / ❌

### Test 4.3: Multiple Questions
```
Type: @bot What is a variable?
Wait for response...
Type: @bot What about functions?
Wait for response...
```

**Expected:**
- [ ] Both questions answered
- [ ] No crashes
- [ ] No duplicate responses

**Status:** ✅ / ❌

---

## Test Suite 5: Context Awareness

### Test 5.1: Conversation History
```
Interaction 1:
Type: @bot My favorite color is blue
Wait for response

Interaction 2:
Type: @bot What is my favorite color?
Wait for response
```

**Expected:**
- First response acknowledges blue
- Second response correctly states: "Your favorite color is blue"
- Chatbot remembers context

**Failure Indicators:**
- Bot says "I don't know your favorite color" ❌
- Bot gives random response ❌
- Bot says something unrelated ❌

**Status:** ✅ / ❌

### Test 5.2: Multiple Turns
```
Turn 1: @bot I'm learning about APIs
Turn 2: @bot How do they work?
Turn 3: @bot Can you give me examples?
```

**Expected:**
- Each response builds on previous context
- Chatbot mentions APIs in Turn 2 and 3
- Conversation flows naturally

**Status:** ✅ / ❌

### Test 5.3: History Persistence
```
Do 5+ message exchanges
```

**Expected:**
- All previous exchanges remembered
- Context includes information from early messages
- Response quality maintains high level

**Status:** ✅ / ❌

---

## Test Suite 6: Personality System

### Test 6.1: Friendly Personality (Default)
1. Verify personality dropdown shows "friendly"
2. Type: `@bot What makes a good friend?`

**Expected:**
- Warm, supportive tone
- Uses phrases like "I think...", "That's great...", etc.
- Maybe includes light emoji or casual language

**Example Response:**
```
"What a wonderful question! A good friend is someone 
who listens, cares, and is there for you no matter what..."
```

**Status:** ✅ / ❌

### Test 6.2: Switch to Professional
1. Click personality dropdown
2. Select "professional"
3. Wait for message: "[Bot] Personality changed to: professional"
4. Type: `@bot What makes a good friend?`

**Expected:**
- Formal, concise tone
- Technical or structured language
- No casual phrases or emojis

**Example Response:**
```
"A good friend demonstrates the following characteristics: 
reliability, trustworthiness, active listening, and mutual support. 
These qualities form the basis of meaningful interpersonal relationships."
```

**Verify:**
- [ ] History cleared (personality change notification appears)
- [ ] New response is in professional tone
- [ ] Response is different from friendly version

**Status:** ✅ / ❌

### Test 6.3: Switch to Funny
1. Click personality dropdown
2. Select "funny"
3. Type: `@bot What makes a good friend?`

**Expected:**
- Witty, humorous tone
- Includes jokes or puns
- Still helpful and accurate

**Example Response:**
```
"Well, a good friend is basically someone who laughs at 
your jokes even when they're terrible, remembers your 
favorite snack, and doesn't hold it against you when 
you're weird at 2 AM! 😄"
```

**Status:** ✅ / ❌

### Test 6.4: History Reset on Personality Change
1. Ask a question: `@bot My name is Alice`
2. Bot responds with name
3. Change personality to professional
4. Ask: `@bot What's my name?`

**Expected:**
```
Chatbot: I don't have information about your name 
in our current conversation.
```

(Because history was reset)

**Status:** ✅ / ❌

---

## Test Suite 7: Group Chat with Bot Mention

### Test 7.1: Start Second Client
```bash
# Terminal 3
python3 chat_gui_client.py
```

Enter different username (e.g., "OtherUser")

**Status:** ✅ / ❌

### Test 7.2: Client 1 Connects to Client 2
**Client 1 (TestUser):**
1. Refresh user list
2. Select "OtherUser"
3. Click "Connect To User"

**Expected in Client 1:**
```
Connected to OtherUser
```

**Expected in Client 2:**
```
OtherUser connected to your chat group
```

**Status:** ✅ / ❌

### Test 7.3: Normal Group Message
**Client 1:**
Type: `Hello from Client 1`

**Expected in Client 1:**
```
[TestUser] Hello from Client 1
```

**Expected in Client 2:**
```
[TestUser] Hello from Client 1
```

**Status:** ✅ / ❌

### Test 7.4: Bot Mention in Group
**Client 1:**
Type: `Hey @bot, what is networking?`

**Expected in Client 1:**
```
[TestUser] Hey @bot, what is networking?
Chatbot: Networking is the practice of connecting computers...
```

**Expected in Client 2:**
```
[TestUser] Hey @bot, what is networking?
(No bot response - only sees original message)
```

**Status:** ✅ / ❌

### Test 7.5: Alternative Bot Mention
**Client 1:**
Type: `@chatbot explain variables`

**Expected:**
- Works same as `@bot`
- Bot responds locally
- Message sent to Client 2

**Status:** ✅ / ❌

---

## Test Suite 8: Error Handling

### Test 8.1: Missing API Key
```bash
# In new terminal, unset key
unset DEEPSEEK_API_KEY

# Restart client
python3 chat_gui_client.py
```

Then try: `@bot hello`

**Expected Error:**
```
Chatbot: DeepSeek API key is missing. 
Please set DEEPSEEK_API_KEY environment variable.
```

**Status:** ✅ / ❌

### Test 8.2: Invalid API Key
```bash
export DEEPSEEK_API_KEY="invalid_key_123"
python3 chat_gui_client.py
```

Try: `@bot hello`

**Expected Error:**
```
Chatbot: Chatbot error: Incorrect API key provided...
```

**Status:** ✅ / ❌

### Test 8.3: API Connection Error
1. Disconnect internet (or use invalid base URL temporarily)
2. Try: `@bot hello`

**Expected:**
```
Chatbot error: Connection failed...
```

(But GUI should remain responsive)

**Status:** ✅ / ❌

### Test 8.4: GUI Non-Responsiveness
During API call (while waiting for bot response):
- Try to type in message box
- Try to click buttons
- Try to interact with GUI

**Expected:**
- All interactions remain responsive
- No freezing or lag
- Can type while waiting

**Status:** ✅ / ❌

---

## Test Suite 9: UI Integration

### Test 9.1: Personality Selector Visibility
1. Look at bottom of chat window
2. Verify you can see:
   - [ ] "Personality:" label
   - [ ] Dropdown with "friendly", "professional", "funny"
   - [ ] Tip label: "💡 Tip: Type '@bot' to chat with AI"

**Status:** ✅ / ❌

### Test 9.2: Personality Selector Functionality
1. Click dropdown
2. Select different options
3. Verify selection changes

**Status:** ✅ / ❌

### Test 9.3: Original Features Preserved
Verify that original functionality still works:
- [ ] Login/Logout
- [ ] User list refresh
- [ ] Connect to user
- [ ] Leave chat group
- [ ] Send normal messages (without @bot)
- [ ] Receive messages from other clients
- [ ] Display formatting

**Status:** ✅ / ❌

---

## Test Suite 10: Performance & Stability

### Test 10.1: Long Conversation
1. Send 10+ bot messages
2. Keep changing personality
3. Test rapid messages

**Expected:**
- No memory leaks (gradually gets slower)
- No crashes
- Consistent response quality
- All messages processed correctly

**Status:** ✅ / ❌

### Test 10.2: Rapid Personality Changes
1. Rapidly click through personality options
2. Send bot message between each change

**Expected:**
- No crashes
- No duplicate responses
- Each personality applied correctly

**Status:** ✅ / ❌

### Test 10.3: Multiple Clients Stability
1. Run 3-4 clients simultaneously
2. Send multiple bot messages
3. Have different personalities in different clients

**Expected:**
- All clients remain stable
- No cross-contamination between clients
- Each client independent

**Status:** ✅ / ❌

---

## Test Suite 11: Edge Cases

### Test 11.1: Very Long Message
Type: `@bot ` + (very long question, 500+ characters)

**Expected:**
- Message processed
- Response generated
- No truncation

**Status:** ✅ / ❌

### Test 11.2: Special Characters
Type: `@bot What's the meaning of "hello" and 'world'?`

**Expected:**
- Special chars handled correctly
- Response makes sense
- No encoding errors

**Status:** ✅ / ❌

### Test 11.3: Emojis in Question
Type: `@bot What is 🚀 and 🤖?`

**Expected:**
- Emojis processed
- Response acknowledges them
- No crashes

**Status:** ✅ / ❌

### Test 11.4: Multiple Mentions
Type: `@bot hello @bot goodbye`

**Expected:**
- Processed as single message
- Bot response to full text
- Not treated as multiple messages

**Status:** ✅ / ❌

---

## Final Validation

### Checklist for Deployment

- [ ] **Syntax**: No Python errors
- [ ] **Dependencies**: OpenAI SDK installed
- [ ] **Configuration**: API key set correctly
- [ ] **Server**: Starts without errors
- [ ] **Client**: GUI loads correctly
- [ ] **Login**: Authentication works
- [ ] **Chatbot**: Responds to @bot messages
- [ ] **Context**: Remembers history
- [ ] **Personalities**: All three work correctly
- [ ] **Group Chat**: Bot mentions work
- [ ] **Errors**: Gracefully handled
- [ ] **GUI**: Responsive, no freezing
- [ ] **Features**: Original chat functionality preserved
- [ ] **UI**: New elements visible and functional

**Overall Status**: ✅ Ready / ⚠️ Needs Work / ❌ Not Ready

---

## Test Session Log

```
Start Time: ________
End Time: ________
Tester: ________
Environment: macOS / Python 3.x

Test Results:
- Suite 1 (Setup): ___/11 tests passed
- Suite 2 (Demo): ___/4 tests passed
- Suite 3 (GUI): ___/3 tests passed
- Suite 4 (Basic): ___/3 tests passed
- Suite 5 (Context): ___/3 tests passed
- Suite 6 (Personality): ___/4 tests passed
- Suite 7 (Group): ___/5 tests passed
- Suite 8 (Errors): ___/4 tests passed
- Suite 9 (UI): ___/3 tests passed
- Suite 10 (Performance): ___/3 tests passed
- Suite 11 (Edge Cases): ___/4 tests passed

Total: ___/48 tests passed

Issues Found:
[List any failures with descriptions]

Recommendations:
[Any improvements or notes]

Sign-off: ________ Date: ________
```

---

## Quick Reference During Testing

| Command | Purpose |
|---------|---------|
| `python3 verify_setup.py` | Check dependencies |
| `python3 chatbot_demo.py` | Test chatbot CLI |
| `python3 chat_server.py` | Start server |
| `python3 chat_gui_client.py` | Start client |
| `export DEEPSEEK_API_KEY="..."` | Set API key |
| `echo $DEEPSEEK_API_KEY` | Check API key set |

---

**Test Plan Version**: 1.0  
**Last Updated**: May 5, 2026  
**Status**: Ready for execution

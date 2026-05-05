# UP3 Chat Project

A Python socket-based chat system with a Tkinter GUI client and a forwarding server. This project supports multi-user chat, file transfer, emoji input, chatbot integration, local NLP tools, sentiment analysis, Tic-Tac-Toe game, and two-person video calls.

## Features

- **Multi-user chat** with login and presence list
- **Server-based forwarding** for chat groups
- **Graphical Tkinter client** with message history and controls
- **Emoji picker** for quick emoji insertion
- **File transfer** with click-to-open received files
- **Time / Who buttons** to show system time and online users
- **Search local history** for previous chat lines
- **DeepSeek chatbot support** via `@bot` or `@chatbot`
- **Local NLP tools**:
  - `/summary` → local summary of recent chat
  - `/keywords` → local keyword extraction
- **Sentiment analysis** on outgoing user messages
- **Tic-Tac-Toe game** between two selected users using `Start Game`
- **Two-person video call** with invite/accept/end flow

## Files

- `chat_server.py` — main chat server
- `chat_gui_client.py` — Tkinter GUI client with chat, file, game, NLP, sentiment, and video features
- `deepseek_bot.py` — DeepSeek API wrapper
- `chat_utils.py` — socket framing utilities and protocol helpers
- `chat_group.py` — chat group membership logic
- `video_server.py` — video frame relay server

## Requirements

- Python 3
- `openai` Python package (DeepSeek-compatible SDK)
- `opencv-python` (for video calls)
- `Pillow` (for video display)
- `numpy` (for video processing)
- `DEEPSEEK_API_KEY` environment variable set before running the client

## Setup

1. Install required Python packages:

```bash
pip3 install openai opencv-python Pillow numpy
```

2. Set the DeepSeek API key:

```bash
export DEEPSEEK_API_KEY="your_api_key"
```

3. Run the servers:

```bash
python3 chat_server.py &
python3 video_server.py &
```

4. Launch one or more clients:

```bash
python3 chat_gui_client.py
```

## How to Use

### Login and connect
1. Start the client.
2. Enter server IP and port.
3. Enter a username.
4. Click **Login**.
5. Refresh the online list and choose a target user.
6. Click **Connect To User** to join a chat group.

### Chat
- Type a message and press **Send** or Enter.
- Regular messages are broadcast to the chat group.
- Messages are displayed once per client.

### Emoji
- Click **Emoji** to open the emoji picker.
- Select an emoji to insert it into the message box.

### File transfer
- Click **Send File** to choose a local file.
- The file is sent as a `FILE|...` message.
- Receivers save files to `./received_files/`.
- Click the blue filename in chat to open it.

### Time and Who
- Click **Time** to display the current time.
- Click **Who** to display all users in the current chat group.

### Search history
- Click **Search** and enter a keyword.
- The client searches recent local chat history and displays matches.

### Chatbot
- Type `@bot` or `@chatbot` in a message.
- The message is forwarded to the group and processed locally for bot reply.

### NLP commands
- `/summary` produces a local summary of the last 5 normal messages.
- `/keywords` produces a local keyword list from the last 5 normal messages.
- NLP output is shown only in the client that requested it.

### Sentiment analysis
- Every normal outgoing message is analyzed with DeepSeek.
- The sent message is tagged with:
  - `😊 [Positive]`
  - `😐 [Neutral]`
  - `😡 [Negative]`
- The sentiment-labeled message is broadcast to all users.

### Tic-Tac-Toe game
1. Select another online user and connect.
2. Click **Start Game**.
3. The selected opponent receives an invite and opens the game window.
4. X starts first, and players alternate turns.
5. The game only affects the two participants.

### Video Call
1. Select another online user and connect.
2. Click **Video Call**.
3. The selected opponent receives an invite and can accept or decline.
4. When accepted, both users see each other's video.
5. Click **End Call** to stop the video call.

## Notes

- The chat server forwards control messages; video frames are relayed by a separate server.
- Video uses OpenCV for capture and JPEG encoding.
- Duplicate incoming messages are filtered with unique `message_id` values.


## Development

If you want to extend the project:
- add new NLP commands in `chat_gui_client.py`
- improve game UI in the `TicTacToeGame` class
- update server logic in `chat_server.py` only for routing, not game rules

---

Enjoy the chat project!

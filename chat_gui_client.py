import argparse
import base64
import datetime
import json
import os
import platform
import queue
import socket
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import simpledialog
from tkinter import ttk

from chat_utils import CHAT_PORT, myrecv, mysend
from deepseek_bot import DeepSeekChatBot


class TicTacToeGame:
    def __init__(self, parent_gui, opponent, is_initiator):
        self.parent_gui = parent_gui
        self.opponent = opponent
        self.is_initiator = is_initiator
        self.symbol = 'X' if is_initiator else 'O'
        self.opponent_symbol = 'O' if is_initiator else 'X'
        self.my_turn = is_initiator
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.game_over = False

        self.window = tk.Toplevel(parent_gui.root)
        self.window.title(f"Tic-Tac-Toe vs {opponent}")
        self.window.geometry("300x350")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.status_label = ttk.Label(self.window, text=f"You are {self.symbol}. {'Your turn.' if self.my_turn else 'Waiting for opponent.'}")
        self.status_label.pack(pady=10)

        self.frame = ttk.Frame(self.window)
        self.frame.pack()

        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = ttk.Button(self.frame, text='', command=lambda r=i, c=j: self.make_move(r, c))
                self.buttons[i][j].grid(row=i, column=j, ipadx=20, ipady=20)

        self.reset_button = ttk.Button(self.window, text="Reset Game", command=self.reset_game_from_button)
        self.reset_button.pack(pady=10)

    def make_move(self, row, col):
        if self.game_over or not self.my_turn or self.board[row][col] != '':
            return
        self.board[row][col] = self.symbol
        self.buttons[row][col].config(text=self.symbol, state=tk.DISABLED)
        self.my_turn = False
        self.update_status()
        print("[GAME DEBUG] local move:", row, col, self.symbol)
        self.parent_gui.send_game_message("MOVE", row, col, self.symbol)
        self.check_game_end()

    def apply_remote_move(self, row, col, symbol):
        self.board[row][col] = symbol
        self.buttons[row][col].config(text=symbol, state=tk.DISABLED)
        self.my_turn = True
        self.update_status()
        self.check_game_end()

    def update_status(self):
        if self.game_over:
            return
        if self.my_turn:
            self.status_label.config(text=f"You are {self.symbol}. Your turn.")
        else:
            self.status_label.config(text=f"You are {self.symbol}. Waiting for opponent.")

    def check_game_end(self):
        winner = self.check_winner()
        if winner:
            self.game_over = True
            if winner == self.symbol:
                self.status_label.config(text="You win!")
                self.parent_gui.send_game_message("RESULT", "win")
            else:
                self.status_label.config(text="You lose!")
                self.parent_gui.send_game_message("RESULT", "lose")
            self.disable_buttons()
        elif all(self.board[i][j] != '' for i in range(3) for j in range(3)):
            self.game_over = True
            self.status_label.config(text="Draw!")
            self.parent_gui.send_game_message("RESULT", "draw")
            self.disable_buttons()

    def check_winner(self):
        # Check rows
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != '':
                return self.board[i][0]
        # Check columns
        for j in range(3):
            if self.board[0][j] == self.board[1][j] == self.board[2][j] != '':
                return self.board[0][j]
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        return None

    def reset_board_only(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.my_turn = self.is_initiator
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text='', state=tk.NORMAL)
        self.update_status()

    def reset_game_from_button(self):
        self.reset_board_only()
        self.parent_gui.send_game_message("RESET")

    def disable_buttons(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state=tk.DISABLED)

    def on_close(self):
        self.parent_gui.game = None
        self.window.destroy()


class ChatGUI:
    def __init__(self, root, default_host, default_port):
        self.root = root
        self.root.title("UP3 Chat Client")
        self.root.geometry("920x600")

        self.default_host = default_host
        self.default_port = default_port

        self.sock = None
        self.receiver_thread = None
        self.running = False
        self.logged_in = False
        self.name = ""
        self.connected_peer = ""
        self.incoming = queue.Queue()
        
        # Chatbot-related attributes
        self.chatbot = None
        self.bot_responses = queue.Queue()  # Queue for bot responses from background thread
        self.personality_var = tk.StringVar(value="friendly")
        self.bot_initialized = False
        self.initialize_chatbot()  # Try to initialize on startup

        # Emoji, file, and search state
        self.history = []
        self.file_links = {}
        self.next_file_tag_id = 1

        self.game = None  # TicTacToeGame instance

        self.host_var = tk.StringVar(value=self.default_host)
        self.port_var = tk.StringVar(value=str(self.default_port))
        self.name_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Not connected")

        self._build_ui()
        self._set_logged_in(False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.process_incoming)
        self.root.after(100, self.process_bot_responses)

    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        top = ttk.Frame(self.root, padding=12)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        for col in range(7):
            top.columnconfigure(col, weight=1 if col in (1, 3, 5) else 0)

        ttk.Label(top, text="Server IP").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.host_var, width=18).grid(row=0, column=1, sticky="ew", padx=(6, 12))

        ttk.Label(top, text="Port").grid(row=0, column=2, sticky="w")
        ttk.Entry(top, textvariable=self.port_var, width=8).grid(row=0, column=3, sticky="ew", padx=(6, 12))

        ttk.Label(top, text="Username").grid(row=0, column=4, sticky="w")
        ttk.Entry(top, textvariable=self.name_var, width=16).grid(row=0, column=5, sticky="ew", padx=(6, 12))

        self.login_button = ttk.Button(top, text="Login", command=self.login)
        self.login_button.grid(row=0, column=6, sticky="ew")

        left = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        left.grid(row=1, column=0, sticky="ns")
        left.rowconfigure(2, weight=1)

        ttk.Label(left, text="Online Users").grid(row=0, column=0, sticky="w")
        self.refresh_button = ttk.Button(left, text="Refresh", command=self.request_user_list)
        self.refresh_button.grid(row=0, column=1, sticky="e", padx=(8, 0))

        self.user_list = tk.Listbox(left, height=18, exportselection=False)
        self.user_list.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(8, 12))
        self.user_list.bind("<<ListboxSelect>>", self.use_selected_user)

        ttk.Label(left, text="Chat Target").grid(row=3, column=0, sticky="w")
        ttk.Entry(left, textvariable=self.target_var).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 10))

        self.connect_button = ttk.Button(left, text="Connect To User", command=self.connect_to_target)
        self.connect_button.grid(row=5, column=0, columnspan=2, sticky="ew")

        self.disconnect_button = ttk.Button(left, text="Leave Chat Group", command=self.leave_chat_group)
        self.disconnect_button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        right = ttk.Frame(self.root, padding=(0, 0, 12, 12))
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        ttk.Label(right, textvariable=self.status_var).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.chat_log = scrolledtext.ScrolledText(right, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_log.grid(row=1, column=0, sticky="nsew")

        bottom = ttk.Frame(right)
        bottom.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)

        self.message_entry = ttk.Entry(bottom, textvariable=self.message_var)
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.message_entry.bind("<Return>", self.send_message)

        self.emoji_button = ttk.Button(bottom, text="Emoji", command=self.open_emoji_popup)
        self.emoji_button.grid(row=0, column=1, sticky="ew", padx=(0, 4))

        self.file_button = ttk.Button(bottom, text="Send File", command=self.send_file)
        self.file_button.grid(row=0, column=2, sticky="ew", padx=(0, 4))

        self.time_button = ttk.Button(bottom, text="Time", command=self.display_time)
        self.time_button.grid(row=0, column=3, sticky="ew", padx=(0, 4))

        self.who_button = ttk.Button(bottom, text="Who", command=self.display_online_users)
        self.who_button.grid(row=0, column=4, sticky="ew", padx=(0, 4))

        self.search_button = ttk.Button(bottom, text="Search", command=self.search_history)
        self.search_button.grid(row=0, column=5, sticky="ew", padx=(0, 4))

        self.send_button = ttk.Button(bottom, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=6, sticky="ew")

        self.start_game_button = ttk.Button(bottom, text="Start Game", command=self.start_game)
        self.start_game_button.grid(row=0, column=7, sticky="ew")

        for col in range(8):
            bottom.columnconfigure(col, weight=1 if col == 0 else 0)
        
        # Chatbot UI elements
        bot_frame = ttk.Frame(right)
        bot_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        bot_frame.columnconfigure(1, weight=1)
        
        ttk.Label(bot_frame, text="Personality:", foreground="gray").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.personality_combo = ttk.Combobox(
            bot_frame, 
            textvariable=self.personality_var, 
            values=["friendly", "professional", "funny"], 
            state="readonly",
            width=12
        )
        self.personality_combo.grid(row=0, column=1, sticky="w", padx=(0, 12))
        self.personality_combo.bind("<<ComboboxSelected>>", self.on_personality_changed)
        
        ttk.Label(bot_frame, text="💡 Tip: Type '@bot' to chat with AI", foreground="gray").grid(row=0, column=2, sticky="e")

    def _set_logged_in(self, logged_in):
        state = tk.NORMAL if logged_in else tk.DISABLED
        self.logged_in = logged_in
        self.refresh_button.config(state=state)
        self.connect_button.config(state=state)
        self.disconnect_button.config(state=state)
        self.message_entry.config(state=state)
        self.send_button.config(state=state)

    def append_log(self, text):
        self.history.append(text)
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, text.rstrip() + "\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def append_file_message(self, sender, filename, filepath):
        """
        Display a received file message with a clickable tag.

        Args:
            sender (str): sender name to display
            filename (str): file name
            filepath (str): local path where the file is saved
        """
        display_text = f"[File] {sender} sent: "
        self.history.append(display_text + filename)

        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, display_text)
        start_index = self.chat_log.index(tk.END)
        self.chat_log.insert(tk.END, filename)
        end_index = self.chat_log.index(tk.END)
        tag_name = f"file_{self.next_file_tag_id}"
        self.next_file_tag_id += 1

        self.chat_log.tag_add(tag_name, start_index, end_index)
        self.chat_log.tag_configure(tag_name, foreground="blue", underline=1)
        self.chat_log.tag_bind(tag_name, "<Button-1>", lambda e, p=filepath: self.open_file(p))
        self.file_links[tag_name] = filepath
        self.chat_log.insert(tk.END, "\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def open_emoji_popup(self):
        """
        Show an emoji picker popup and insert the selected emoji at the cursor.
        """
        emojis = ["😀", "😂", "👍", "❤️", "🎉", "😭", "😎"]
        popup = tk.Toplevel(self.root)
        popup.title("Choose Emoji")
        popup.geometry("260x80")
        popup.resizable(False, False)

        def add_emoji(emoji):
            self.insert_emoji(emoji)
            popup.destroy()

        for idx, emoji in enumerate(emojis):
            button = ttk.Button(popup, text=emoji, command=lambda e=emoji: add_emoji(e))
            button.grid(row=0, column=idx, padx=3, pady=10)

    def insert_emoji(self, emoji):
        """
        Insert the selected emoji into the message input at the current cursor position.
        """
        index = self.message_entry.index(tk.INSERT)
        current = self.message_var.get()
        new_text = current[:index] + emoji + current[index:]
        self.message_var.set(new_text)
        self.message_entry.icursor(index + len(emoji))

    def open_emoji_popup(self):
        """
        Show an emoji picker popup and insert the selected emoji at the cursor.
        """
        emojis = ["😀", "😂", "👍", "❤️", "🎉", "😭", "😎"]
        popup = tk.Toplevel(self.root)
        popup.title("Choose Emoji")
        popup.geometry("260x80")
        popup.resizable(False, False)

        def add_emoji(emoji):
            self.insert_emoji(emoji)
            popup.destroy()

        for idx, emoji in enumerate(emojis):
            button = ttk.Button(popup, text=emoji, command=lambda e=emoji: add_emoji(e))
            button.grid(row=0, column=idx, padx=3, pady=10)

    def insert_emoji(self, emoji):
        """
        Insert the selected emoji into the message input at the current cursor position.
        """
        index = self.message_entry.index(tk.INSERT)
        current = self.message_var.get()
        new_text = current[:index] + emoji + current[index:]
        self.message_var.set(new_text)
        self.message_entry.icursor(index + len(emoji))

    def open_file(self, filepath):
        """
        Open a file using the operating system default application.
        """
        if not os.path.exists(filepath):
            self.append_log(f"[System] File not found: {filepath}")
            return

        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", filepath], check=False)
            elif platform.system() == "Windows":
                os.startfile(filepath)
            else:
                subprocess.run(["xdg-open", filepath], check=False)
        except Exception as exc:
            self.append_log(f"[System] Could not open file: {exc}")

    def display_time(self):
        """
        Display the current local time in the chat log.
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.append_log(f"[System] Current time: {now}")

    def display_online_users(self):
        """
        Display the current online users from the user list.
        """
        users = [self.user_list.get(i) for i in range(self.user_list.size())]
        display = ", ".join(users) if users else "No users online"
        self.append_log(f"[System] Online users: {display}")

    def search_history(self):
        """
        Prompt for a keyword and search the local chat history.
        """
        keyword = simpledialog.askstring("Search", "Enter keyword:")
        if not keyword:
            return

        results = [msg for msg in self.history if keyword.lower() in msg.lower()]
        self.append_log(f"[Search] Found {len(results)} results for \"{keyword}\"")
        for msg in results:
            self.append_log(f"[Search] {msg}")

    def start_game(self):
        """
        Start a Tic-Tac-Toe game with the selected target user.
        """
        if not self.logged_in or self.sock is None:
            messagebox.showerror("Error", "Please login and select a connected user before starting a game.")
            return
        target = self.target_var.get().strip()
        if not target:
            messagebox.showerror("Error", "Please select a user to start a game")
            return
        users = self.user_list.get(0, tk.END)
        if target not in users:
            messagebox.showerror("Error", "Selected user is not online")
            return
        if target == self.name:
            messagebox.showerror("Error", "You cannot play against yourself")
            return
        if self.game is not None:
            messagebox.showerror("Error", "You are already in a game")
            return
        self.send_game_message("INVITE")
        # Open game window for initiator
        self.game = TicTacToeGame(self, target, True)

    def send_game_message(self, action, *args):
        """
        Send a game message to the target user.
        """
        if self.sock is None:
            print("Not connected to server")
            return
        target = self.target_var.get().strip()
        payload_message = "|".join(["GAME", action, self.name, target] + [str(arg) for arg in args])
        print("[GAME DEBUG] sending:", payload_message)
        payload = {"action": "exchange", "from": f"[{self.name}]", "message": payload_message}
        print("[GAME DEBUG] send_game_message payload:", payload)
        self.send_json(payload)

    def handle_game_message(self, message):
        """
        Handle incoming game messages.
        """
        parts = message.split("|")
        print("[GAME DEBUG] parsed game message:", parts)
        if len(parts) < 4:
            return
        action = parts[1]
        sender = parts[2]
        target = parts[3]
        if self.name not in [sender, target]:
            return  # Ignore if not involved
        if action == "INVITE":
            if self.game is None:
                self.game = TicTacToeGame(self, sender, False)
        elif action == "MOVE":
            if sender == self.name:
                return
            if self.game and len(parts) >= 7:
                row = int(parts[4])
                col = int(parts[5])
                symbol = parts[6]
                self.game.apply_remote_move(row, col, symbol)
        elif action == "RESET":
            if self.game:
                self.game.reset_board_only()
        elif action == "RESULT":
            pass

    def login(self):
        if self.logged_in:
            return

        host = self.host_var.get().strip()
        name = self.name_var.get().strip()
        if not host or not name:
            messagebox.showwarning("Missing info", "Please enter both server IP and username.")
            return

        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showwarning("Invalid port", "Port must be an integer.")
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            mysend(sock, json.dumps({"action": "login", "name": name}))
            response = json.loads(myrecv(sock))
        except Exception as exc:
            sock.close()
            messagebox.showerror("Login failed", f"Could not connect to server:\n{exc}")
            return

        if response.get("status") != "ok":
            sock.close()
            messagebox.showerror("Login failed", "Username already in use or server rejected the login.")
            return

        self.sock = sock
        self.name = name
        self.running = True
        self.receiver_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.receiver_thread.start()

        self._set_logged_in(True)
        self.login_button.config(state=tk.DISABLED)
        self.status_var.set(f"Logged in as {self.name}")
        self.append_log(f"Logged in as {self.name}.")
        self.append_log("Pick an online user and click 'Connect To User' to start chatting.")
        self.request_user_list()

    def receive_loop(self):
        try:
            while self.running and self.sock is not None:
                msg = myrecv(self.sock)
                if not msg:
                    self.incoming.put({"action": "_system", "kind": "closed"})
                    break
                try:
                    self.incoming.put(json.loads(msg))
                except json.JSONDecodeError:
                    self.incoming.put({"action": "_system", "kind": "bad_message", "raw": msg})
        except OSError:
            self.incoming.put({"action": "_system", "kind": "closed"})

    def process_incoming(self):
        while not self.incoming.empty():
            msg = self.incoming.get()
            action = msg.get("action")

            if action == "list":
                self.update_user_list(msg.get("users", []))
            elif action == "connect":
                if msg.get("status") == "success":
                    target = self.target_var.get().strip()
                    if target:
                        self.connected_peer = target
                        self.status_var.set(f"Chatting with {self.connected_peer}")
                        self.append_log(f"Connected to {self.connected_peer}.")
                elif msg.get("status") == "request":
                    self.connected_peer = msg.get("from", "")
                    self.status_var.set(f"Chatting with {self.connected_peer}")
                    self.append_log(f"{self.connected_peer} connected to your chat group.")
                elif msg.get("status") == "self":
                    self.append_log("You cannot connect to yourself.")
                elif msg.get("status") == "no-user":
                    self.append_log("That user is not online.")
            elif action == "exchange":
                message_text = msg.get("message", "")
                if message_text.startswith("GAME|"):
                    self.handle_game_message(message_text)
                    continue
                if message_text.startswith("FILE|"):
                    self.handle_file_message(message_text)
                    continue
                self.append_log(f'{msg.get("from", "[peer]")} {message_text}')
            elif action == "disconnect":
                self.connected_peer = ""
                self.status_var.set(f"Logged in as {self.name}")
                self.append_log(msg.get("msg", "You left the chat group."))
            elif action == "_system":
                self.append_log("Connection closed.")
                self.cleanup_connection()
            elif action == "time":
                self.append_log(f'Server time: {msg.get("results", "")}')
            elif action == "search":
                result = msg.get("results", "").strip() or "No search result."
                self.append_log(result)
            elif action == "poem":
                result = msg.get("results", "").strip() or "Poem not found."
                self.append_log(result)

        self.root.after(100, self.process_incoming)

    def update_user_list(self, users):
        self.user_list.delete(0, tk.END)
        for user in users:
            if user != self.name:
                self.user_list.insert(tk.END, user)

    def use_selected_user(self, _event):
        selection = self.user_list.curselection()
        if selection:
            self.target_var.set(self.user_list.get(selection[0]))

    def send_file(self):
        """
        Open a file dialog, encode the selected file in base64, and send it over the socket.
        """
        if self.sock is None:
            return
        if not self.connected_peer:
            messagebox.showwarning("Not chatting", "Connect to someone before sending a file.")
            return

        filename = filedialog.askopenfilename()
        if not filename:
            return

        try:
            filesize = os.path.getsize(filename)
            if filesize > 5 * 1024 * 1024:
                messagebox.showerror("File too large", "File must be smaller than 5MB.")
                return

            with open(filename, "rb") as f:
                file_data = f.read()
            encoded = base64.b64encode(file_data).decode("utf-8")
            sender = self.name
            basename = os.path.basename(filename)
            packet = f"FILE|{sender}|{basename}|{encoded}"
            self.send_json({"action": "exchange", "from": f"[{self.name}]", "message": packet})
            self.append_file_message(sender, basename, filename)
        except Exception as exc:
            messagebox.showerror("File send error", f"Could not send file: {exc}")

    def _unique_received_filepath(self, filename):
        """Generate a unique filepath for received files."""
        os.makedirs("received_files", exist_ok=True)
        base = os.path.basename(filename)
        target = os.path.join("received_files", base)
        name, ext = os.path.splitext(base)
        counter = 1
        while os.path.exists(target):
            target = os.path.join("received_files", f"{name}_{counter}{ext}")
            counter += 1
        return target

    def handle_file_message(self, message_text):
        """
        Parse a FILE| message and save the incoming file locally.
        """
        try:
            parts = message_text.split("|", 3)
            if len(parts) != 4:
                raise ValueError("Invalid file message format")
            _, sender, filename, encoded_data = parts
            filename = os.path.basename(filename)
            filepath = self._unique_received_filepath(filename)
            file_bytes = base64.b64decode(encoded_data)
            with open(filepath, "wb") as f:
                f.write(file_bytes)
            print("[FILE DEBUG] received FILE message:", filename)
            print("[FILE DEBUG] saved to:", filepath)
            self.append_file_message(sender, filename, filepath)
        except Exception as exc:
            messagebox.showerror("File receive error", f"Could not receive file: {exc}")
            print("[FILE DEBUG] failed to receive file:", exc)

    def request_user_list(self):
        if self.sock is None:
            return
        self.send_json({"action": "list"})

    def connect_to_target(self):
        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("No target", "Choose or type a username first.")
            return
        self.send_json({"action": "connect", "target": target})

    def leave_chat_group(self):
        if self.sock is None:
            return
        self.send_json({"action": "disconnect"})
        self.connected_peer = ""
        self.status_var.set(f"Logged in as {self.name}")
        self.append_log("You left the current chat group.")

    def send_json(self, payload):
        try:
            mysend(self.sock, json.dumps(payload))
        except OSError as exc:
            self.append_log(f"Send failed: {exc}")
            self.cleanup_connection()

    def cleanup_connection(self):
        self.running = False
        self.connected_peer = ""
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None
        self._set_logged_in(False)
        self.login_button.config(state=tk.NORMAL)
        self.status_var.set("Not connected")

    def on_close(self):
        if self.game:
            self.game.on_close()
        self.cleanup_connection()
        self.root.destroy()

    def initialize_chatbot(self):
        """
        Initialize the chatbot on startup.
        Show error if API key is missing.
        """
        try:
            self.chatbot = DeepSeekChatBot(personality="friendly")
            self.bot_initialized = True
        except ValueError as e:
            # API key missing - this will be shown when user tries to use @bot
            self.bot_initialized = False

    def on_personality_changed(self, _event=None):
        """
        Handle personality selector change.
        Update chatbot personality and reset conversation history.
        """
        if self.chatbot:
            new_personality = self.personality_var.get()
            try:
                self.chatbot.set_personality(new_personality)
                self.chatbot.reset_history()
                self.append_log(f"[Bot] Personality changed to: {new_personality}")
            except ValueError as e:
                self.append_log(f"[Bot] Error: {str(e)}")

    def process_bot_request(self, user_message):
        """
        Process a bot request in a background thread to avoid blocking the GUI.
        
        Args:
            user_message (str): The message to send to the chatbot
        """
        if not self.bot_initialized:
            self.bot_responses.put({
                "status": "error",
                "message": "DeepSeek API key is missing. Please set DEEPSEEK_API_KEY environment variable."
            })
            return
        
        try:
            # Call the chatbot
            response = self.chatbot.chat(user_message)
            self.bot_responses.put({
                "status": "success",
                "message": response
            })
        except Exception as e:
            self.bot_responses.put({
                "status": "error",
                "message": f"Chatbot error: {str(e)}"
            })

    def process_bot_responses(self):
        """
        Process responses from the bot background thread.
        Display bot responses in the chat log and forward them through the socket.
        """
        while not self.bot_responses.empty():
            response = self.bot_responses.get()
            if response.get("status") == "success":
                bot_message = response.get('message', '')
                self.append_log(f"Chatbot: {bot_message}")
                if self.sock is not None and self.connected_peer:
                    self.send_json({
                        "action": "exchange",
                        "from": "Chatbot:",
                        "message": bot_message
                    })
            elif response.get("status") == "error":
                self.append_log(f"Chatbot: {response.get('message', 'Unknown error')}")

        self.root.after(100, self.process_bot_responses)

    def send_message(self, _event=None):
        """
        Send a message. Detect @bot and @chatbot mentions.
        Forward the original message through the socket, then call DeepSeek locally
        for bot replies only on the sender side.
        """
        if self.sock is None:
            return

        text = self.message_var.get().strip()
        if not text:
            return

        if not self.connected_peer:
            messagebox.showwarning("Not chatting", "Connect to someone before sending a message.")
            return

        if "@bot" in text.lower() or "@chatbot" in text.lower():
            # Forward the original @bot message to the server so peers see it.
            self.send_json({"action": "exchange", "from": f"[{self.name}]", "message": text})
            self.append_log(f"[{self.name}] {text}")
            self.message_var.set("")

            mention_text = text.replace("@bot", "").replace("@chatbot", "").strip()
            if mention_text:
                bot_thread = threading.Thread(
                    target=self.process_bot_request,
                    args=(mention_text,),
                    daemon=True
                )
                bot_thread.start()
            return

        # Normal user message (not targeting the bot)
        self.send_json({"action": "exchange", "from": f"[{self.name}]", "message": text})
        self.append_log(f"[{self.name}] {text}")
        self.message_var.set("")
def main():
    parser = argparse.ArgumentParser(description="UP3 GUI chat client")
    parser.add_argument("--host", default="127.0.0.1", help="Server IP address")
    parser.add_argument("--port", type=int, default=CHAT_PORT, help="Server port")
    args = parser.parse_args()

    root = tk.Tk()
    app = ChatGUI(root, args.host, args.port)
    root.mainloop()


if __name__ == "__main__":
    main()

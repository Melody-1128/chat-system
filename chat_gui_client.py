import argparse
import json
import queue
import socket
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk

from chat_utils import CHAT_PORT, myrecv, mysend
from deepseek_bot import DeepSeekChatBot


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

        self.send_button = ttk.Button(bottom, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, sticky="ew")
        
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
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, text.rstrip() + "\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

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
                self.append_log(f'{msg.get("from", "[peer]")} {msg.get("message", "")}')
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

    def send_message(self, _event=None):
        if self.sock is None:
            return

        text = self.message_var.get().strip()
        if not text:
            return
        
        # Check if message is for the chatbot (starts with @bot)
        if text.lower().startswith("@bot"):
            # Extract the actual message (remove @bot prefix)
            user_message = text[4:].strip()
            if not user_message:
                self.append_log("[Bot] Please provide a message after @bot")
                self.message_var.set("")
                return
            
            # Display user message
            self.append_log(f"[{self.name}] @bot {user_message}")
            self.message_var.set("")
            
            # Process bot request in a background thread (non-blocking)
            bot_thread = threading.Thread(
                target=self.process_bot_request,
                args=(user_message,),
                daemon=True
            )
            bot_thread.start()
            return
        
        # Check for group chat mentions - if message contains @bot or @chatbot
        if "@bot" in text.lower() or "@chatbot" in text.lower():
            # Send message through socket first
            if not self.connected_peer:
                messagebox.showwarning("Not chatting", "Connect to someone before sending a message.")
                return
            
            self.send_json({"action": "exchange", "from": f"[{self.name}]", "message": text})
            self.append_log(f"[{self.name}] {text}")
            self.message_var.set("")
            
            # Extract mention text for bot processing
            mention_text = text.replace("@bot", "").replace("@chatbot", "").strip()
            if mention_text:
                # Process bot response in background thread (non-blocking)
                bot_thread = threading.Thread(
                    target=self.process_bot_request,
                    args=(mention_text,),
                    daemon=True
                )
                bot_thread.start()
            return
        
        # Normal message (not for bot)
        if not self.connected_peer:
            messagebox.showwarning("Not chatting", "Connect to someone before sending a message.")
            return

        self.send_json({"action": "exchange", "from": f"[{self.name}]", "message": text})
        self.append_log(f"[{self.name}] {text}")
        self.message_var.set("")

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
        Display bot responses in the chat log.
        """
        while not self.bot_responses.empty():
            response = self.bot_responses.get()
            if response.get("status") == "success":
                self.append_log(f"Chatbot: {response.get('message', '')}")
            elif response.get("status") == "error":
                self.append_log(f"Chatbot: {response.get('message', 'Unknown error')}")
        
        self.root.after(100, self.process_bot_responses)

    def send_message(self, _event=None):
        """
        Send a message. Detect @bot prefix to route to chatbot.
        If message starts with @bot, send to chatbot in background thread.
        Otherwise send through normal socket chat.
        """
        if self.sock is None:
            return

        text = self.message_var.get().strip()
        if not text:
            return
        
        # Check if message is for the chatbot (starts with @bot)
        if text.lower().startswith("@bot"):
            # Extract the actual message (remove @bot prefix)
            user_message = text[4:].strip()
            if not user_message:
                self.append_log("[Bot] Please provide a message after @bot")
                self.message_var.set("")
                return
            
            # Display user message
            self.append_log(f"[{self.name}] @bot {user_message}")
            self.message_var.set("")
            
            # Process bot request in a background thread (non-blocking)
            bot_thread = threading.Thread(
                target=self.process_bot_request,
                args=(user_message,),
                daemon=True
            )
            bot_thread.start()
            return
        
        # Check for group chat mentions - if message contains @bot or @chatbot
        if "@bot" in text.lower() or "@chatbot" in text.lower():
            # Send message through socket first
            if not self.connected_peer:
                messagebox.showwarning("Not chatting", "Connect to someone before sending a message.")
                return
            
            self.send_json({"action": "exchange", "from": f"[{self.name}]", "message": text})
            self.append_log(f"[{self.name}] {text}")
            self.message_var.set("")
            
            # Extract mention text for bot processing
            mention_text = text.replace("@bot", "").replace("@chatbot", "").strip()
            if mention_text:
                # Process bot response in background thread (non-blocking)
                bot_thread = threading.Thread(
                    target=self.process_bot_request,
                    args=(mention_text,),
                    daemon=True
                )
                bot_thread.start()
            return
        
        # Normal message (not for bot)
        if not self.connected_peer:
            messagebox.showwarning("Not chatting", "Connect to someone before sending a message.")
            return

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

import tkinter as tk
from tkinter import Canvas, Scrollbar, filedialog
import threading
import time
import sys
from pathlib import Path

# Ensure local modules resolve when the app is launched from another directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chatbot import NovaChatbot
from speech import SpeechManager
from config import (  # type: ignore[reportMissingImports]
    APP_NAME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BG_COLOR,
    CHAT_BG,
    BOT_BUBBLE,
    USER_BUBBLE,
    TEXT_COLOR,
    SECONDARY_TEXT,
    INPUT_BG,
    ACCENT_COLOR,
    BOT_NAME
)


class NovaApp:

    def __init__(self, root):

        self.root = root

        self.root.title(APP_NAME)
        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(700, 500)
        self.root.configure(bg=BG_COLOR)

        # Chatbot and speech engines
        self.chatbot = NovaChatbot()
        self.speech = SpeechManager()

        # Prevent multiple voice recordings
        self.is_listening = False
        self.response_generation = 0

        # Build GUI
        self.create_header()
        self.create_chat_area()
        self.create_input_area()

        # Welcome message
        self.root.after(
            500,
            lambda: self.add_bot_message(
                "Hello! 👋 I'm Nova, your AI assistant. "
                "How can I help you today?"
            )
        )

    # ==================================================
    # HEADER
    # ==================================================

    def create_header(self):

        header = tk.Frame(
            self.root,
            bg=BG_COLOR,
            height=75
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        icon = tk.Label(
            header,
            text="🤖",
            font=("Segoe UI Emoji", 30),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )

        icon.pack(
            side="left",
            padx=(25, 10)
        )

        title_frame = tk.Frame(
            header,
            bg=BG_COLOR
        )

        title_frame.pack(
            side="left"
        )

        title = tk.Label(
            title_frame,
            text=BOT_NAME,
            font=("Segoe UI", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )

        title.pack(
            anchor="w"
        )

        status = tk.Label(
            title_frame,
            text="● Online • Rule-Based AI",
            font=("Segoe UI", 9),
            bg=BG_COLOR,
            fg="#22c55e"
        )

        status.pack(
            anchor="w"
        )

        load_button = tk.Button(
            header,
            text="Load Dataset",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_COLOR,
            fg="#0f172a",
            activebackground=ACCENT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.load_dataset
        )

        load_button.pack(
            side="right",
            padx=25
        )

    def load_dataset(self):

        file_path = filedialog.askopenfilename(
            title="Select dataset",
            filetypes=[
                ("Excel or CSV files", "*.xlsx *.csv"),
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        self.chatbot.analyzer = __import__(
            "data_analyzer",
            fromlist=["DataAnalyzer"]
        ).DataAnalyzer(file_path)

        if self.chatbot.analyzer.is_loaded():
            self.add_bot_message(
                "Dataset loaded successfully. You can ask me about it now."
            )
        else:
            self.add_bot_message(
                "I couldn't load that dataset. Please select a valid Excel or CSV file."
            )

    # ==================================================
    # CHAT AREA
    # ==================================================

    def create_chat_area(self):

        container = tk.Frame(
            self.root,
            bg=CHAT_BG
        )

        container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 10)
        )

        self.canvas = Canvas(
            container,
            bg=CHAT_BG,
            highlightthickness=0
        )

        self.scrollbar = Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.chat_frame = tk.Frame(
            self.canvas,
            bg=CHAT_BG
        )

        self.chat_window = self.canvas.create_window(
            (0, 0),
            window=self.chat_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.chat_frame.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_chat_frame
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

    def update_scroll_region(self, event=None):

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

        self.canvas.after(
            50,
            lambda: self.canvas.yview_moveto(1.0)
        )

    def resize_chat_frame(self, event):

        self.canvas.itemconfig(
            self.chat_window,
            width=event.width
        )

    def on_mousewheel(self, event):

        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # ==================================================
    # INPUT AREA
    # ==================================================

    def create_input_area(self):

        bottom = tk.Frame(
            self.root,
            bg=BG_COLOR
        )

        bottom.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        input_container = tk.Frame(
            bottom,
            bg=INPUT_BG
        )

        input_container.pack(
            fill="x"
        )

        self.message_entry = tk.Entry(
            input_container,
            font=("Segoe UI", 12),
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            bd=0
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(15, 5),
            pady=14
        )

        self.message_entry.bind(
            "<Return>",
            self.on_enter
        )

        self.mic_button = tk.Button(
            input_container,
            text="🎤",
            font=("Segoe UI Emoji", 16),
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            activebackground=INPUT_BG,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.start_voice_input
        )

        self.mic_button.pack(
            side="left",
            padx=5
        )

        send_button = tk.Button(
            input_container,
            text="➤",
            font=("Segoe UI", 18, "bold"),
            bg=ACCENT_COLOR,
            fg="#0f172a",
            activebackground=ACCENT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=3,
            command=self.send_message
        )

        send_button.pack(
            side="right",
            padx=5,
            pady=5
        )

    # ==================================================
    # USER MESSAGE
    # ==================================================

    def add_user_message(self, message):

        row = tk.Frame(
            self.chat_frame,
            bg=CHAT_BG
        )

        row.pack(
            fill="x",
            padx=15,
            pady=8
        )

        bubble = tk.Label(
            row,
            text=message,
            font=("Segoe UI", 11),
            bg=USER_BUBBLE,
            fg="white",
            padx=15,
            pady=10,
            wraplength=550,
            justify="left"
        )

        bubble.pack(
            side="right",
            anchor="e"
        )

        name = tk.Label(
            row,
            text="You 👤",
            font=("Segoe UI", 8),
            bg=CHAT_BG,
            fg=SECONDARY_TEXT
        )

        name.pack(
            side="right",
            padx=(0, 10),
            anchor="e"
        )

        self.scroll_to_bottom()

    # ==================================================
    # BOT MESSAGE
    # ==================================================

    def add_bot_message(self, message):

        row = tk.Frame(
            self.chat_frame,
            bg=CHAT_BG
        )

        row.pack(
            fill="x",
            padx=15,
            pady=8
        )

        avatar = tk.Label(
            row,
            text="🤖",
            font=("Segoe UI Emoji", 18),
            bg=CHAT_BG,
            fg=TEXT_COLOR
        )

        avatar.pack(
            side="left",
            anchor="n",
            padx=(0, 8)
        )

        bubble = tk.Label(
            row,
            text=message,
            font=("Segoe UI", 11),
            bg=BOT_BUBBLE,
            fg=TEXT_COLOR,
            padx=15,
            pady=10,
            wraplength=550,
            justify="left"
        )

        bubble.pack(
            side="left",
            anchor="w"
        )

        self.scroll_to_bottom()

    # ==================================================
    # SCROLL
    # ==================================================

    def scroll_to_bottom(self):

        self.root.after(
            50,
            lambda: self.canvas.yview_moveto(1.0)
        )

    # ==================================================
    # TYPING INDICATOR
    # ==================================================

    def show_typing(self):

        if hasattr(self, "typing_label"):

            try:
                self.typing_label.destroy()
            except tk.TclError:
                pass

        self.typing_label = tk.Label(
            self.chat_frame,
            text="🤖 Nova is typing...",
            font=("Segoe UI", 9, "italic"),
            bg=CHAT_BG,
            fg=SECONDARY_TEXT
        )

        self.typing_label.pack(
            anchor="w",
            padx=55,
            pady=5
        )

        self.scroll_to_bottom()

    def hide_typing(self):

        if hasattr(self, "typing_label"):

            try:
                self.typing_label.destroy()
            except tk.TclError:
                pass

            del self.typing_label

    # ==================================================
    # SEND MESSAGE
    # ==================================================

    def send_message(self):

        message = self.message_entry.get().strip()

        if not message:
            return

        self.response_generation += 1
        self.speech.stop_speaking()
        response_generation = self.response_generation

        self.message_entry.delete(
            0,
            tk.END
        )

        self.add_user_message(
            message
        )

        # Process response in background
        thread = threading.Thread(
            target=self.process_message,
            args=(message, response_generation),
            daemon=True
        )

        thread.start()

    # ==================================================
    # PROCESS TEXT MESSAGE
    # ==================================================

    def process_message(self, message, response_generation):

        if response_generation != self.response_generation:
            return

        self.root.after(
            0,
            self.show_typing
        )

        time.sleep(0.5)

        if response_generation != self.response_generation:
            return

        response = self.chatbot.get_response(
            message
        )

        if response_generation != self.response_generation:
            return

        self.root.after(
            0,
            self.hide_typing
        )

        self.root.after(
            0,
            lambda: self.add_bot_message(response)
        )

        # Add response to TTS queue
        self.speech.speak(response)

    # ==================================================
    # ENTER KEY
    # ==================================================

    def on_enter(self, event):

        self.send_message()

    # ==================================================
    # VOICE INPUT
    # ==================================================

    def start_voice_input(self):

        # Don't allow multiple recordings
        if self.is_listening:
            return

        self.is_listening = True

        self.mic_button.config(
            text="🔴",
            state="disabled"
        )

        self.add_bot_message(
            "🎤 Listening... Please speak now."
        )

        thread = threading.Thread(
            target=self.process_voice,
            daemon=True
        )

        thread.start()

def process_voice(self):

    try:

        text = self.speech.listen()

        if text:

            self.root.after(
                0,
                lambda: self.add_user_message(text)
            )

            response = self.chatbot.get_response(
                text
            )

            self.root.after(
                0,
                lambda: self.add_bot_message(response)
            )

            # Add response to TTS queue
            self.speech.speak(response)

        else:

            self.root.after(
                0,
                lambda: self.add_bot_message(
                    "Sorry, I couldn't understand you. "
                    "Please try again. 🎤"
                )
            )

    finally:

        self.is_listening = False

        self.root.after(
            0,
            lambda: self.mic_button.config(
                text="🎤",
                state="normal"
            )
        )

# ======================================================
# START APPLICATION
# ======================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = NovaApp(root)

    root.mainloop()
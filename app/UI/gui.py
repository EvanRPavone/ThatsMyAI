# app/UI/gui.py

import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel,
    QListWidget, QListWidgetItem, QSplitter, QMessageBox
)
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt

from app.chat_engine import ChatEngine
from app.UI.setup_form import SetupForm
from app.session_history import SessionHistory


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = ChatEngine()
        self.history = SessionHistory()

        self.setWindowTitle("ThatsMyAI")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Session List Panel
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.load_selected_session)
        self.splitter.addWidget(self.session_list)

        self.button_panel = QVBoxLayout()
        self.new_btn = QPushButton("➕ New Session")
        self.new_btn.clicked.connect(self.start_new_session)
        self.delete_btn = QPushButton("🗑️ Delete Session")
        self.delete_btn.clicked.connect(self.delete_session)
        self.button_panel.addWidget(self.new_btn)
        self.button_panel.addWidget(self.delete_btn)

        btn_container = QWidget()
        btn_container.setLayout(self.button_panel)
        self.splitter.addWidget(btn_container)

        # Chat Area
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_container.setLayout(self.chat_layout)
        self.splitter.addWidget(self.chat_container)

        self.title_label = QLabel("ThatsMyAI")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chat_layout.addWidget(self.title_label)

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_log)

        self.input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self.handle_send)
        self.input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_send)
        self.input_layout.addWidget(self.send_button)
        self.chat_layout.addLayout(self.input_layout)

        self.export_button = QPushButton("Export Summary")
        self.export_button.clicked.connect(self.handle_export)
        self.chat_layout.addWidget(self.export_button)

        self.personality_buttons = QHBoxLayout()
        self.view_button = QPushButton("🧠 View Personality")
        self.view_button.clicked.connect(self.handle_view_personality)
        self.personality_buttons.addWidget(self.view_button)

        self.regen_button = QPushButton("♻️ Regenerate Personality")
        self.regen_button.clicked.connect(self.handle_regen_personality)
        self.personality_buttons.addWidget(self.regen_button)
        self.chat_layout.addLayout(self.personality_buttons)

        self.load_session_list()
        self.refresh_chat()

    def handle_send(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        # Show user's message
        self.append_message("You", user_input)

        # Get AI response
        response = self.engine.send_message(user_input)
        self.append_message("AI", response)

        # Refresh session list if this is a newly named session
        if (
            self.engine.prompt_count == 2 and
            self.engine.session_name not in [
                self.session_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.session_list.count())
            ]
        ):
            self.load_session_list()

        # Clear input field
        self.input_field.clear()

    def append_message(self, sender, content):
        self.chat_log.append(f"<b>{sender}:</b>")
        self.chat_log.append(f"{content}")
        self.chat_log.append("")  # Add spacing
        self.chat_log.moveCursor(QTextCursor.MoveOperation.End)

    def handle_export(self):
        new_title = self.engine.generate_session_title()
        if new_title:
            self.engine.session_name = new_title
            self.setWindowTitle(f"ThatsMyAI – {self.engine.session_name}")
            result = self.engine.send_message("export_summary")
            self.append_message("System", result)

    def handle_view_personality(self):
        result = self.engine.send_message("get_personality")
        self.append_message("Personality", result)

    def handle_regen_personality(self):
        result = self.engine.send_message("regen_personality")
        self.append_message("Updated Personality", result)

    def load_session_list(self):
        self.session_list.clear()
        sessions = self.history.list_sessions()
        for session in sessions:
            item = QListWidgetItem(session["title"])
            item.setData(Qt.ItemDataRole.UserRole, session["title"])
            self.session_list.addItem(item)

    def load_selected_session(self, item):
        selected_name = item.data(Qt.ItemDataRole.UserRole)
        self.engine = ChatEngine(session_name=selected_name)
        self.refresh_chat()

    def refresh_chat(self):
        self.chat_log.clear()
        self.setWindowTitle(f"ThatsMyAI – {self.engine.session_name}")
        for msg in self.engine.messages:
            if not isinstance(msg, dict):
                continue
            if "role" not in msg or "content" not in msg:
                continue
            role = "You" if msg["role"] == "user" else "AI"
            self.append_message(role, msg["content"])

    def start_new_session(self):
        self.engine = ChatEngine()
        self.chat_log.clear()
        self.setWindowTitle("ThatsMyAI – New Session")
        self.load_session_list()

    def delete_session(self):
        item = self.session_list.currentItem()
        if not item:
            QMessageBox.information(self, "No Selection", "Select a session to delete.")
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete session '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.history.delete_session(name)
            self.load_session_list()
            self.start_new_session()


def run_gui():
    app = QApplication(sys.argv)
    main_window = None

    def launch_chat():
        nonlocal main_window
        main_window = MainWindow()
        main_window.show()

    if not os.path.exists("config/user_config.json"):
        setup = SetupForm(on_complete_callback=launch_chat)
        setup.show()
    else:
        launch_chat()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()

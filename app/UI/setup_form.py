from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import os
import json

class SetupForm(QWidget):
    def __init__(self, on_complete_callback):
        super().__init__()
        self.setWindowTitle("Setup Your AI")
        self.on_complete = on_complete_callback

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.goals_input = QLineEdit()
        self.tone_input = QLineEdit()

        layout.addWidget(QLabel("What's your name?"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("How old are you? (optional)"))
        layout.addWidget(self.age_input)
        layout.addWidget(QLabel("What are your goals? (comma-separated)"))
        layout.addWidget(self.goals_input)
        layout.addWidget(QLabel("Preferred tone(s)? (comma-separated)"))
        layout.addWidget(self.tone_input)

        submit_btn = QPushButton("Start Using Your AI")
        submit_btn.clicked.connect(self.save_and_start)
        layout.addWidget(submit_btn)

        self.setLayout(layout)

    def save_and_start(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        goals = [g.strip() for g in self.goals_input.text().split(",") if g.strip()]
        tone = [t.strip() for t in self.tone_input.text().split(",") if t.strip()]

        if not name or not goals or not tone:
            QMessageBox.warning(self, "Missing Info", "Please fill in name, goals, and tone.")
            return

        config = {
            "name": name,
            "age": age,
            "goals": goals,
            "tone": tone
        }

        os.makedirs("config", exist_ok=True)
        with open("config/user_config.json", "w") as f:
            json.dump(config, f, indent=2)

        # generate personality
        personality = (
            f"You are a personal AI assistant for {name}. "
            f"You speak with a tone that is {', '.join(tone)}. "
            f"Their goals include: {', '.join(goals)}. "
            f"Be proactive, insightful, and reflect the user's style when responding."
        )

        with open("config/personality.json", "w") as f:
            json.dump({"profile": personality}, f, indent=2)

        QMessageBox.information(self, "All Set", "Your AI is ready!")
        self.on_complete()
        self.hide()

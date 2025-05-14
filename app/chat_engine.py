import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import json
import glob

class ChatEngine:
    def __init__(self, session_name=None):
        self.chat_initialized = False
        self.prompt_count = 0
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
    
        # Points to the memory folder
        self.memory_dir = os.path.join("memory")
        os.makedirs(self.memory_dir, exist_ok=True)
    
        # Start with user-defined personality
        system_message = {
            "role": "system",
            "content": self._load_user_profile()
        }
        self.messages = [system_message] + self._load_context_from_all_sessions(limit=25)
        # a unique name for the chat session
        if session_name:
            self.session_name = session_name
        else:
            self.session_name = "session_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # the full file path like memory/session_2025-04-10_15-30-22.json
        self.memory_file = os.path.join(self.memory_dir, f"{self.session_name}.json")
        # holds the ongoing chat history in memory
        self.config_path = os.path.join("config", "personality.json")
        self.messages = self._load_memory()
        self.session_start = datetime.now()
        if not self.messages:
            # Start with the system personality
            self.messages = [{"role": "system", "content": self._load_personality()}]

            # Add context from old sessions
            self.messages += self._load_context_from_all_sessions(limit=25)
    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[⚠️] Failed to load memory: {e}")
        return []

    def _save_memory(self):
        try:
            # Filter valid messages only
            save_data = [
                msg for msg in self.messages
                if isinstance(msg, dict) and "role" in msg and "content" in msg
            ]

            # Add tooltip summary as metadata (but NOT part of self.messages)
            if self.chat_initialized:
                tooltip = self.generate_tooltip_summary()
                metadata = {"tooltip_summary": tooltip}
                save_data.insert(0, metadata)

            with open(self.memory_file, "w") as f:
                json.dump(save_data, f, indent=2)

        except Exception as e:
            print(f"[❌] Failed to save memory: {e}")

    def send_message(self, user_input):
        # 🔹 Handle special commands
        command = user_input.lower()
        if command == "get_personality":
            return f"[🧠 Personality]\n{self._load_personality()}"
        if command == "regen_personality":
            result = self._rebuild_personality()
            return f"[🧠 Personality Regenerated]\n{result}"
        if command == "export_summary":
            summary = self.summarize_session()
            try:
                from .pdf_exporter import PDFExporter
                pdf = PDFExporter(self.session_name, summary)
                path = pdf.export()
                return f"[Summary PDF Generated]\nSaved to: {path}"
            except Exception as e:
                return f"Failed to export PDF: {e}"

        # 🔹 Append user's message
        self.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        self.prompt_count += 1

        try:
            # 🔹 Send only valid messages to OpenAI
            valid_messages = [
                m for m in self.messages
                if isinstance(m, dict) and "role" in m and "content" in m
            ]

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=valid_messages
            )

            reply = response.choices[0].message.content.strip()
            self.messages.append({
                "role": "assistant",
                "content": reply,
                "timestamp": datetime.now().isoformat()
            })

            # 🔹 Generate a real session title after 2 messages
            if self.prompt_count == 2 and self.session_name.startswith("session_"):
                new_title = self.generate_session_title()
                if new_title:
                    date = datetime.now().strftime("%Y-%m-%d")
                    final_name = f"{date}__{new_title}"
                    old_path = self.memory_file
                    self.session_name = final_name
                    self.memory_file = os.path.join(self.memory_dir, f"{final_name}.json")
                    if os.path.exists(old_path):
                        os.rename(old_path, self.memory_file)

            self._save_memory()
            return reply

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "Sorry, something went wrong when trying to talk to OpenAI."


    def _load_personality(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                return data.get("profile","You are a helpful assistant")
            except Exception as e:
                print(f"[⚠️] Failed to load personality: {e}")
        return "You are a helpful assistant."

    def _rebuild_personality(self):
        all_files = glob.glob(os.path.join(self.memory_dir, "*.json"))
        all_messages = []

        for file in all_files:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                for msg in data:
                    if msg["role"] in ["user", "assistant"]:
                        all_messages.append(msg)
            except Exception as e:
                print(f"[⚠️] Skipping {file}: {e}")

        all_messages = all_messages[-50:]
        if not all_messages:
            return "No memory found."

        all_messages.append({
            "role": "user",
            "content": (
                "Based on this message history, generate a new personality description for this assistant. "
                "Make it natural, aligned with how it usually talks, and reflect its behavior. Just return the personality."
            )
        })

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=all_messages
            )
            new_profile = response.choices[0].message.content.strip()

            with open(self.config_path, "w") as f:
                json.dump({"profile": new_profile}, f, indent=2)

            return new_profile

        except Exception as e:
            return f"Failed to regenerate personality: {e}"

    def _load_context_from_all_sessions(self,limit=25):
        all_files = glob.glob(os.path.join(self.memory_dir, "*.json"))
        all_context = []
    
        for file in all_files:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    for msg in data:
                        if msg["role"] in ["user","assistant"]:
                            all_context.append(msg)
            except Exception as e:
                print(f"[⚠️] Skipping corrupt memory file {file}: {e}")
        return all_context[-limit:]

    def summarize_session(self):
        try:
            summary_prompt = (
                "Generate a clean, helpful session summary using the structure below. Include only real content actually discussed in the session.\n\n"
                "1. Overview – TL;DR summary of what was covered. Bullet points or a short paragraph.\n\n"
                "2. Full Summary – Paragraph-style explanation of the chat flow. Mention if code or projects were discussed.\n\n"
                "3. Key Concepts – Bullet list of the Python topics, tools, or ideas that were talked about.\n\n"
                "4. Code Snippets – Include real code from the session only here. Add comments if there are multiple examples.\n\n"
                "5. Next Steps – Include anything the user mentioned they’d like to do, even casually. For example, if they said 'next steps would be…' or 'I want to…', treat that as a valid future action.\n\n"
                "Skip sections only if they are 100% irrelevant. Do not invent content, but do not overlook user intent either."
            )



            session_messages = [
                msg for msg in self.messages
                if msg["role"] in ["user", "assistant"]
                and datetime.fromisoformat(msg.get("timestamp", "1900-01-01")) >= self.session_start
            ]

            session_messages.append({
                "role": "user",
                "content": summary_prompt
            })

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=session_messages
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"[❌] Failed to generate summary: {e}"

    def generate_session_title(self):
        try:
            title_prompt = (
                "Based on this conversation, suggest a short and descriptive session title (1–4 words max). "
                "Make it filename-safe: no quotes, slashes, colons, or emojis. Use lowercase and underscores. "
                "Examples: python_loops, brewing_basics, ai_personality_reset"
            )

            session_messages = [
                msg for msg in self.messages
                if msg["role"] in ["user", "assistant"]
                and datetime.fromisoformat(msg.get("timestamp", "1900-01-01")) >= self.session_start
            ]

            session_messages.append({"role": "user", "content": title_prompt})

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=session_messages
            )

            return response.choices[0].message.content.strip().replace(" ", "_")

        except Exception as e:
            return None

    def generate_tooltip_summary(self):
        try:
            quick_prompt = (
                "In one sentence, describe what this chat session is about. "
                "Keep it short, clear, and without quotes or emojis."
            )
            messages = [
                msg for msg in self.messages
                if msg["role"] in ["user", "assistant"]
                and datetime.fromisoformat(msg.get("timestamp", "1900-01-01")) >= self.session_start
            ]
            messages.append({"role": "user", "content": quick_prompt})

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return "No summary available."

    def _load_user_profile(self):
        path = os.path.join("config", "user_config.json")
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    name = data.get("name", "the user")
                    tone = data.get("tone", "friendly")
                    goals = data.get("goals", "")
                    return (
                        f"You are a personal AI assistant for {name}. "
                        f"Your tone should be {tone}. "
                        f"Their goals include: {goals}."
                    )
            except Exception as e:
                print(f"[⚠️] Failed to load user profile: {e}")
        return "You are a helpful AI assistant."

    def _save_memory(self):
        try:
            data = self.messages.copy()
            if self.chat_initialized and not any(m.get("tooltip_summary") for m in data):
                tooltip = self.generate_tooltip_summary()
                data.insert(0, {"tooltip_summary": tooltip})

            with open(self.memory_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[❌] Failed to save memory: {e}")
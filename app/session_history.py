import os
import json
from datetime import datetime

class SessionHistory:
    def __init__(self, memory_dir="memory"):
        self.memory_dir = memory_dir

    def list_sessions(self):
        sessions = []
        if not os.path.exists(self.memory_dir):
            return sessions

        for filename in os.listdir(self.memory_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.memory_dir, filename)
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        created = os.path.getctime(path)

                        # Find tooltip summary if present
                        tooltip = ""
                        for msg in data:
                            if "tooltip_summary" in msg:
                                tooltip = msg["tooltip_summary"]
                                break

                        sessions.append({
                            "title": filename.replace(".json", ""),
                            "path": path,
                            "created": datetime.fromtimestamp(created),
                            "tooltip": tooltip
                        })
                except Exception as e:
                    print(f"[⚠️] Skipping {filename}: {e}")

        # Sort newest to oldest
        return sorted(sessions, key=lambda x: x["created"], reverse=True)

    def delete_session(self, session_name):
        file_path = os.path.join(self.memory_dir, f"{session_name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

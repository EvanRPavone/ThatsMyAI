import os
import glob
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = os.path.join("memory")
CONFIG_PATH = os.path.join("config", "personality.json")

def gather_all_messages():
    all_files = glob.glob(os.path.join(MEMORY_DIR, "*.json"))
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
    
    return all_messages[-50:]  # only most recent 50 to avoid overload

def regenerate_personality():
    print("🧠 Rebuilding personality from memory...")

    history = gather_all_messages()
    if not history:
        print("No memory found.")
        return

    history.append({
        "role": "user",
        "content": (
            "Based on all the messages in this chat history, generate a new personality description "
            "for this AI assistant. It should be natural, consistent, and based on how the AI usually acts. "
            "Respond with only the personality description."
        )
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=history
        )

        new_profile = response.choices[0].message.content.strip()
        print("✅ Personality rebuilt!\n")

        with open(CONFIG_PATH, "w") as f:
            json.dump({"profile": new_profile}, f, indent=2)
        
        print(f"Personality saved to {CONFIG_PATH}")

    except Exception as e:
        print(f"[❌] Error generating personality: {e}")

if __name__ == "__main__":
    regenerate_personality()

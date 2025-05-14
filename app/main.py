# app/main.py

from .chat_engine import ChatEngine

def run_chat():
    ai = ChatEngine()
    print(f"\nSession: {ai.session_name}")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        reply = ai.send_message(user_input)
        print(f"AI: {reply}\n")

if __name__ == "__main__":
    run_chat()

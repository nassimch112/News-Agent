import json
import os
from typing import List, Dict, Any

class Memory:
    def __init__(self, storage_file: str = "memory.json"):
        self.storage_file = storage_file
        self.messages: List[Dict[str, Any]] = []
        self.load_from_file()

    def add_message(self, role: str, content: str):
        """
        Adds a message to the memory.
        role: 'user' or 'model' (to match Gemini API expectations)
        content: The text content of the message.
        """
        self.messages.append({"role": role, "parts": [content]})
        self.save_to_file()

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Returns the full conversation history.
        """
        return self.messages

    def clear(self):
        self.messages = []
        self.save_to_file()

    def save_to_file(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.messages, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save memory: {e}")

    def load_from_file(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.messages = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load memory: {e}")

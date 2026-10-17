import os
import json
import logging

class StateManager:
    """
    Manages session persistence, model context memory, and project 
    tracking states to prevent context drift during model swaps.
    """
    def __init__(self, state_file_path):
        self.state_file = state_file_path
        self.default_state = {
            "active_compute_tier": "LITE",
            "current_project_dir": None,
            "active_model_context": {},
            "conversation_history": []
        }
        self.current_state = self.load_state()

    def load_state(self):
        """Loads persistent session state or initializes clean tracking defaults."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"StateManager failed to parse state file, resetting: {e}")
        return dict(self.default_state)

    def save_state(self):
        """Commits active memory state directly to local disk layout safely."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.current_state, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"StateManager write operations failed: {e}")
            return False

    def update_metric(self, key, value):
        """Safely injects a new key-value tracker into the state cache."""
        self.current_state[key] = value
        self.save_state()

    def append_chat_history(self, role, content, localized_model):
        """
        Maintains chronological chat threads, tagging which model handled 
        the turn to allow context alignment during backend routing shifts.
        """
        chat_turn = {
            "role": role,
            "content": content,
            "processed_by": localized_model
        }
        self.current_state["conversation_history"].append(chat_turn)
        # Prevent memory expansion blowout by capping short-term context rolling memory at 30 turns
        if len(self.current_state["conversation_history"]) > 30:
            self.current_state["conversation_history"].pop(0)
        self.save_state()

    def flush_history(self):
        """Clears volatile conversation threads during project shifts or shutdowns."""
        self.current_state["conversation_history"] = []
        self.save_state()

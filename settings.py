import json
import os

SETTINGS_FILE = "user_settings.json"

DEFAULT_SETTINGS = {
    "theme": "Dark",              # Dark, Light, System
    "color_theme": "blue",        # blue, green, dark-blue
    "output_folder": "output",
    "model_dir": "models",
    "last_input_file": ""
}

class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS
        self.load_settings()

    def load_settings(self):
        """Loads settings from JSON file, creates one if missing."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    loaded = json.load(f)
                    # Update defaults with loaded values (prevents crashes if keys are missing)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            self.save_settings()

    def save_settings(self):
        """Saves current settings to JSON file."""
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
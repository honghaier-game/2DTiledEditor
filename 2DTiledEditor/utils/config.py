import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                return json.load(file)
        else:
            return {
                "recent_files": [],
                "window_size": {"width": 800, "height": 600},
                "window_position": {"x": 100, "y": 100},
                "layout_settings": {},
                "last_map_file": None,
                "language": "en"  # 默认语言设置为英文
            }

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)

    def update_recent_files(self, file_path):
        if file_path in self.config["recent_files"]:
            self.config["recent_files"].remove(file_path)
        self.config["recent_files"].insert(0, file_path)
        if len(self.config["recent_files"]) > 5:
            self.config["recent_files"] = self.config["recent_files"][:5]
        self.save_config()

    def get_recent_files(self):
        return self.config["recent_files"]

    def save_window_size(self, width, height):
        self.config["window_size"]["width"] = width
        self.config["window_size"]["height"] = height
        self.save_config()

    def get_window_size(self):
        return self.config["window_size"]

    def save_window_position(self, x, y):
        self.config["window_position"]["x"] = x
        self.config["window_position"]["y"] = y
        self.save_config()

    def get_window_position(self):
        return self.config["window_position"]

    def save_layout_settings(self, settings):
        self.config["layout_settings"] = settings
        self.save_config()

    def get_layout_settings(self):
        return self.config["layout_settings"]

    def get_last_map_file(self):
        return self.config.get("last_map_file")

    def set_last_map_file(self, file_path):
        self.config["last_map_file"] = file_path
        self.save_config()

    def get_language(self):
        return self.config.get("language", "en")

    def set_language(self, language):
        self.config["language"] = language
        self.save_config()

import logging
from PySide6 import QtCore

AICODEPREP_GUI_VERSION = "1.0"

DEFAULT_PRESETS = [
    ("Debug", "Can you help me debug this code?"),
    ("Security check", "Can you analyze this code for any security issues?"),
    ("Agent Prompt", "Write a prompt for my AI coding agent. Split the tasks into sub-tasks with enough detail to guide the agent. The agent might not be very smart but you can guide it along using plain English and find / replace style text, include just enough details to guide the agent and include some of the 'whys' about why we are doing what we are doing, to help guide it along. Enclose the entire agent prompt in one big code tag for easy copy and paste. "),
    ("Best Practices", "Please analyze this code for: Error handling, Edge cases, Performance optimization, Best practices, Please do not unnecessarily remove any comments or code. Generate the code with clear comments explaining the logic."),
    ("Please review for", "Code quality and adherence to best practices, Potential bugs or edge cases, Performance optimizations, Readability and maintainability, Security concerns. Suggest improvements and explain your reasoning for each suggestion"),
    ("Cline, Roo Code Prompt", "Write a prompt for Cline, an AI coding agent, to make the necessary changes. Enclose the entire Cline prompt in one single code tag for easy copy and paste. Cline likes search and replace blocks with just plain language with a little bit of explanations about why we are doing things to help guide the agent.")
]


class GlobalPresetManager:
    PRESET_SCHEMA_VERSION = 1

    def __init__(self):
        try:
            self.settings = QtCore.QSettings("aicodeprep-gui", "ButtonPresets")
            self._ensure_default_presets()
        except Exception as e:
            logging.error(f"Failed to initialize global preset manager: {e}")
            self.settings = None

    def _ensure_default_presets(self):
        try:
            if not self.settings:
                return

            self.settings.beginGroup("internal")
            last_version = self.settings.value("preset_version", 0, type=int)
            self.settings.endGroup()

            if last_version >= self.PRESET_SCHEMA_VERSION:
                return

            logging.info(
                f"Updating default button presets (schema version {last_version} -> {self.PRESET_SCHEMA_VERSION})")

            self.settings.beginGroup("presets")
            for label, text in DEFAULT_PRESETS:
                self.settings.setValue(label, text)
            self.settings.endGroup()

            self.settings.beginGroup("internal")
            self.settings.setValue(
                "preset_version", self.PRESET_SCHEMA_VERSION)
            self.settings.endGroup()

            logging.info("Default button presets updated successfully.")
        except Exception as e:
            logging.error(f"Failed to update default presets: {e}")

    def get_all_presets(self):
        try:
            if not self.settings:
                return []
            presets = []
            self.settings.beginGroup("presets")
            for key in self.settings.childKeys():
                presets.append((key, self.settings.value(key, "")))
            self.settings.endGroup()
            return presets
        except Exception as e:
            logging.error(f"Failed to get presets: {e}")
            return []

    def add_preset(self, label, text):
        try:
            if not self.settings or not label.strip() or not text.strip():
                return False
            self.settings.beginGroup("presets")
            self.settings.setValue(label.strip(), text.strip())
            self.settings.endGroup()
            return True
        except Exception as e:
            logging.error(f"Failed to add preset '{label}': {e}")
            return False

    def delete_preset(self, label):
        try:
            if not self.settings or not label.strip():
                return False
            self.settings.beginGroup("presets")
            self.settings.remove(label.strip())
            self.settings.endGroup()
            return True
        except Exception as e:
            logging.error(f"Failed to delete preset '{label}': {e}")
            return False


global_preset_manager = GlobalPresetManager()

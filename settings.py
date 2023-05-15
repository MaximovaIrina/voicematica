import json
import os
from template_message import EXAMPLE_AUDIO

from typing import Dict

class VoiceMaticaSettings:
    def __init__(self):
        self.voice = "dmitry"
        self.speed = 1
        self.tone = 0
        self.atmosphere = "auto"
        self.audio_title = ""
        self.key_to_name = {
            "dmitry": "Дмитрий",
            "ksenia": "Ксения",
            "viktor": "Виктор",
            "anna": "Анна",
            "lofi": "lofi hip hop",
            "vestern": "Вестерн",
            "guitar": "Гитара",
            "vostok": "Восток",
            "auto": "Автоматическая",
            "empty": "Без атмосферы"
        }
        self.is_last_feedback = False
        self.update_id = set()

    def _save(self):
        data = {}
        for k, v in USERS_SETTINGS.items():
            data[k] = {
               "voice": v.voice,
               "speed": v.speed,
               "tone": v.tone,
               "atmosphere": v.atmosphere,
               "audio_title": v.audio_title,
               "is_last_feedback": v.is_last_feedback,
               "update_id": list(v.update_id),
            }
        with open("USERS_SETTINGS.json", "w") as f:
            json.dump(data, f)

    @staticmethod
    def load_users_settings():
        if os.path.exists("USERS_SETTINGS.json"):
            with open("USERS_SETTINGS.json", "r") as f:
                data = json.load(f)
            for k, v in data.items():
                vs = VoiceMaticaSettings()
                vs.voice = v["voice"]
                vs.speed = v["speed"]
                vs.tone = v["tone"]
                vs.atmosphere = v["atmosphere"]
                vs.audio_title = v["audio_title"]
                vs.is_last_feedback = v["is_last_feedback"]
                vs.update_id = set(v["update_id"])
                USERS_SETTINGS[k] = vs


    def update(self, setting_str, value_str):
        if setting_str == "voice":
            self.voice = value_str
            self.audio_title = f"Тестовая фраза голосом {self.key_to_name[self.voice]}"
            txt = f"Голос '{self.key_to_name[self.voice]}' установлен 💫\n"
        elif setting_str == "atmosphere":
            self.atmosphere = value_str
            self.audio_title = f"Тестовая фраза c '{self.key_to_name[self.atmosphere]}'"
            txt = f"Атмосфера {self.key_to_name[self.atmosphere]} установлена 💫\n"
        elif setting_str == "speed":
            self.speed = float(value_str)
            self.audio_title = f"Тестовая фраза на скорости x{self.speed}"
            txt = f"Скорость x{self.speed} установлена 💫\n"
        elif setting_str == "tone":
            self.tone = float(value_str)
            self.audio_title = f"Тестовая фраза c высотой {self.tone}"
            txt = f"Высота тона {self.tone} установлена 💫\n"
        self._save()
        return txt + EXAMPLE_AUDIO

    def __str__(self):
        return f"""Текущие настройки: \n🎤 голос: {self.key_to_name[self.voice]}\n🏎️ скорость: {self.speed}\n🎵 тональность: {self.tone}\n✨ атмосфера: {self.key_to_name[self.atmosphere]}"""

USERS_SETTINGS = {}

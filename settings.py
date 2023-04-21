from template_message import EXAMPLE_AUDIO

USERS_SETTINGS = {}    
    
class VoiceMaticaSettings:
    def __init__(self):
        self.users_map = {}
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
        
    def update(self, setting_str, value_str):
        if setting_str == "voice":
            self.voice = value_str
            self.audio_title = f"Тестовая фраза голосом {self.key_to_name[self.voice]}"
            txt = f"Голос '{self.key_to_name[self.voice]}' установлен.\n"
        elif setting_str == "atmosphere":
            self.atmosphere = value_str
            self.audio_title = f"Тестовая фраза c '{self.key_to_name[self.atmosphere]}'"
            txt = f"Атмосфера {self.key_to_name[self.atmosphere]} установлена.\n"
        elif setting_str == "speed":
            self.speed = float(value_str)
            self.audio_title = f"Тестовая фраза на скорости x{self.speed}"
            txt = f"Скорость x{self.speed} установлена.\n"
        elif setting_str == "tone":
            self.tone = float(value_str)
            self.audio_title = f"Тестовая фраза c высотой {self.tone}"
            txt = f"Высота тона {self.tone} установлена.\n"
        return txt + EXAMPLE_AUDIO
            
    def __str__(self):
        return f"""Settings: \t\nvoice - {self.voice} \t\nspeed - {self.speed} \t\ntone - {self.tone} \t\natmosphere - {self.atmosphere}"""
    
    
import os
from typing import Union
from multiprocessing import Process, Value
import multiprocessing
from typing import List, Tuple
from gpt_requests import GET_ATMOSPHERE, GET_NUM_WORDS, GET_TITLE
from template_message import BIG_MESSAGE, SMALL_MESSAGE
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import torch
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm
from nltk.tokenize import sent_tokenize
import re
from ssml_builder.core import Speech
import openai
from librosa.effects import pitch_shift, time_stretch
from transliterate import translit
import re
import roman
from num2words import num2words

from settings import VoiceMaticaSettings
from utils import PRONUNCIATION_DICT, SHORTCUTS, SPEAKER_MAP
from vm_token import GPT_TOKEN

openai.api_key = GPT_TOKEN


class VoiceMatica:
    NUM_SYMBOLS_PER_MINUT = 1500
    SR = 44100

    def __init__(self):
        self.text_max_size = 600
        self.atmosphere_volume = 0.15
        self.atmo_range_procentage = 0.15
        self.promo_time = 5

        self.tts_model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts", language="ru", speaker="v3_1_ru")

        tags_tokenizer = AutoTokenizer.from_pretrained(
            "xlm-roberta-large-finetuned-conll03-english")
        tags_model = AutoModelForTokenClassification.from_pretrained(
            "xlm-roberta-large-finetuned-conll03-english")
        self.tag_classifier = pipeline(
            "ner", model=tags_model, tokenizer=tags_tokenizer)

    def _update_volume_on_the_boards(self, audio: np.ndarray) -> np.ndarray:
        ic_dec_part_size = int(self.promo_time * self.SR * 3/4)
        increase_scale = np.linspace(0, 1, ic_dec_part_size)
        audio[:ic_dec_part_size] *= increase_scale
        audio[len(audio) - ic_dec_part_size:] *= increase_scale[::-1]
        return audio

    def _split_text(self, text: str) -> List[str]:
        texts = []
        while len(text) > self.text_max_size:
            last_dot_index = max(
                text[:self.text_max_size].rfind(stop) for stop in ".?!") + 1
            texts.append(text[:last_dot_index])
            text = text[last_dot_index:]
        texts.append(text)
        return texts

    def _made_title(self, text: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user",
                       "content": GET_TITLE.format(text)}],
            temperature=0,
        )
        title = response.choices[0].message.content
        title = self._decode_english_words(title)
        return title

    @staticmethod
    def _get_atmosphere_response(text, result):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": GET_ATMOSPHERE.format(text)}],
            temperature=0,
        )
        result.put(response.choices[0].message.content)

    def _get_atmosphere(
            self,
            text: str,
            atmosphere: str) -> Tuple[Union[multiprocessing.Process, None],
                                      Union[multiprocessing.Value, str]]:
        if atmosphere != "auto":
            return None, atmosphere
        atmosphere = multiprocessing.Queue()
        process = Process(
            target=self._get_atmosphere_response,
            args=(text, atmosphere)
        )
        process.start()
        return process, atmosphere

    def _replace_roman_numbers(self, text):
        pattern = re.compile(r'\b[IVXLCDM]+\b')
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                number = roman.fromRoman(match)
                text = text.replace(match, str(number))
            except roman.InvalidRomanNumeralError:
                pass
        return text

    def _decode_shortcuts(self, text: str) -> str:
        for shortcut, full_version in SHORTCUTS.items():
            text = text.replace(shortcut, full_version)
        return text

    def _decode_english_words(self, text: str) -> str:
        english_words = re.findall(r'\b[a-zA-Z]+\b', text)
        for word in set(english_words):
            word_translit = translit(word, 'ru')
            text = text.replace(word, word_translit)
        return text

    def _preprocess_whole_text(self, text: str) -> Tuple[str]:
        text = self._decode_shortcuts(text)
        print("TEXT _decode_shortcuts")
        print(text)
        # text = self._replace_roman_numbers(text)
        # print("PART TEXT _replace_roman_numbers")
        print(text)
        text = self._decode_english_words(text)
        return text

    def _to_ssml(self, text: str, idx: int, length: int, title: Union[str, None]) -> str:
        speech = Speech()
        # Add title
        if idx == 0:
            if self.promo_time:
                speech.add_text(f"""<break time=\"{self.promo_time}s\"/>""")
            if title:
                speech.add_text(f"""Всем привет! {title}."<break time="500ms"/> Начинаем... <break time="1500ms"/>""")

        for t in text.split("\n"):
            # Pause between sentences
            t = "".join([sent + "<break time=\"300ms\"/>" for sent in sent_tokenize(t, language="russian")])
            # t = t.replace(",", ",<break time=\"150ms\"/>")
            t = t.replace(",", ",<break time=\"30ms\"/>")
            # Pause when sequence occurs
            t = t.replace(":", "<break time=\"100ms\"/>")
            # t = t.replace("/", "<break time=\"500ms\"/>")
            # Pause for brackets
            t = t.replace("пункт)", "пункт)<break time=\"500ms\"/>")
            t = t.replace("пункт.", "пункт.<break time=\"500ms\"/>")
            t = t.replace("(", "<break time=\"75ms\"/>")
            t = t.replace(")", "<break time=\"75ms\"/>")
            # Pause for paragraph
            speech.p(t)

        # Add goodbye message
        if idx == length - 1:
            speech.add_text(f"""<break time=\"{self.promo_time}s\"/>""")
            if title:
                speech.add_text("<break time=\"2s\"/> Вы прослушали сообщение до конца! Так держать <break time=\"200ms\"/> и до новых встреч.")

        return speech.speak()

    def _decode_abbreviations(self, text: str) -> str:
        text_without_accents = re.sub('[́]', '', text)
        tags = self.tag_classifier(text_without_accents)
        tags = [t for t in tags
                if t["entity"].split("-")[-1] in ["ORG", "LOC", "MISC"]]

        if len(tags):
            abbreviations = []
            curr_word_start = tags[0]["start"]
            curr_word_end = tags[0]["end"]
            curr_word_tag = tags[0]["entity"]
            for id in range(1, len(tags)):
                if tags[id]["word"] == "_":
                    continue
                if curr_word_tag == tags[id]["entity"] and \
                        curr_word_end == tags[id]["start"]:
                    curr_word_end = tags[id]["end"]
                else:
                    abbreviations.append(text[curr_word_start:curr_word_end])
                    curr_word_start = tags[id]["start"]
                    curr_word_end = tags[id]["end"]
                    curr_word_tag = tags[id]["entity"]

            abbreviations.append(text[curr_word_start:curr_word_end])
            abbreviations = [a for a in abbreviations if a.isupper() and len(a) > 1]

            print("abbreviations", abbreviations)
            for abbr in set(abbreviations):
                abbr_pronounce = ""
                for c in abbr:
                    if c in PRONUNCIATION_DICT:
                        abbr_pronounce += PRONUNCIATION_DICT[c]
                    else:
                        abbr_pronounce += " "
                text = text.replace(abbr, abbr_pronounce)
        return text

    def _decode_nums(self, text: str) -> str:
        if len(re.findall(r'\d+', text)) == 0:
            return text

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": GET_NUM_WORDS.format(text)}],
            temperature=0,
        )
        text = response.choices[0].message.content
        lost_nums = set(re.findall(r'\d+', text))
        if len(lost_nums) != 0:
            for n in lost_nums:
                text = text.replace(n, num2words(n, lang="ru"))
        return text

    def _preprocess_part_text(self, text: str) -> str:
        text = self._decode_nums(text)
        print("PART TEXT DECODED NUMS")
        print(text)
        text = self._decode_abbreviations(text)
        return text

    def _get_audio_with_atmosphere(
            self,
            audio: np.ndarray,
            process: Union[multiprocessing.context.Process, None],
            atmosphere: Union[multiprocessing.queues.Queue, None]) -> np.ndarray:
        if atmosphere == "empty":
            return audio

        if isinstance(process, multiprocessing.context.Process):
            process = process.join()
            atmosphere = atmosphere.get()
            atmosphere = atmosphere.lower()

        atmosphere_file = "neutral.wav"
        print("atmosphere:", atmosphere)
        for atmo in os.listdir("atmospheres/"):
            if atmo.split(".")[0] in atmosphere:
                atmosphere_file = atmo
                break

        atmosphere, _ = sf.read(f"atmospheres/{atmosphere_file}")

        if len(atmosphere) < len(audio):
            n_repeats = int(np.ceil(len(audio) / len(atmosphere)))
            atmosphere = np.array([list(atmosphere) * n_repeats])[0]

        atmosphere = atmosphere[:len(audio)]
        atmosphere = self._update_volume_on_the_boards(atmosphere)
        atmosphere *= self.atmosphere_volume * np.max(audio)
        audio += atmosphere
        return audio

    def _tts(self, text: str, voice: str, title: str) -> np.ndarray:
        print("TEXT")
        print(text)
        texts = self._split_text(text) \
            if len(text) > self.text_max_size else [text, ]
        audio = []
        idx = 0

        for text in tqdm(texts):
            print("PART TEXT")
            print(text)
            text = self._preprocess_part_text(text)
            print("PART TEXT TO SSML")
            print(text)
            text = self._to_ssml(text, idx, len(texts), title)
            print("PART TEXT FINISH")
            print(text)
            sub_audio = self.tts_model.apply_tts(
                ssml_text=text,
                speaker=SPEAKER_MAP[voice],
                sample_rate=48000,
                put_accent=True,
                put_yo=True)
            audio.extend(list(sub_audio.numpy()))
            idx += 1

        audio = np.array(audio, dtype=np.float32)
        audio = librosa.resample(audio, orig_sr=48000, target_sr=self.SR)
        return audio

    def _set_promo_time(self, text: str, title: str):
        if title is None:
            self.promo_time = 0
        else:
            self.promo_time = int(np.ceil(min((len(text) / 100), 5)))
        print("self.promo_time ", self.promo_time, title is None, title)

    @torch.no_grad()
    def __call__(self, text: str, settings: VoiceMaticaSettings) -> np.ndarray:
        print("TEXT SRC")
        print(text)
        title = self._made_title(text) if len(text) > 500 else None
        self._set_promo_time(text, title)
        text = self._preprocess_whole_text(text)
        print("TEXT _preprocess_whole_text")
        print(text)
        process, atmosphere = self._get_atmosphere(text, settings.atmosphere)

        audio = self._tts(text, settings.voice, title)

        if settings.tone != 0:
            audio = pitch_shift(y=audio, sr=self.SR, n_steps=settings.tone)

        if settings.speed != 1:
            audio = time_stretch(y=audio, rate=settings.speed)

        audio = self._get_audio_with_atmosphere(audio, process, atmosphere)
        return audio

    @torch.no_grad()
    def get_example(self, text: str, settings: VoiceMaticaSettings) -> np.ndarray:
        self._set_promo_time(text, None)

        ssml_text = self._to_ssml(text, 0, 1, title=None)
        print(ssml_text)
        audio = self.tts_model.apply_tts(
                ssml_text=ssml_text,
                speaker=SPEAKER_MAP[settings.voice],
                sample_rate=48000,
                put_accent=True,
                put_yo=True)
        audio = librosa.resample(audio.numpy(), orig_sr=48000, target_sr=self.SR)

        if settings.tone != 0:
            audio = pitch_shift(y=audio, sr=self.SR, n_steps=settings.tone)

        if settings.speed != 1:
            audio = time_stretch(y=audio, rate=settings.speed)

        atmosphere = settings.atmosphere
        if atmosphere == "auto":
            atmosphere = "neutral"

        audio = self._get_audio_with_atmosphere(audio,
                                                process=None,
                                                atmosphere=atmosphere)
        return audio


if __name__ == "__main__":
    vm = VoiceMatica()

    for v in ["dmitry", "ksenia", "viktor", "anna"]:
        # for a in ["lofi", "vestern", "guitar", "vostok", "auto", "empty"]:
        for a in ["auto", "vestern", "guitar", "vostok", "lofi", "empty"]:
            for t in [0., -0.5, 0.5, -1., 1., -2, 2.]:
                for s in [1, 0.85, 0.90, 0.95, 1.15, 1.25, 1.5]:
                    settings = VoiceMaticaSettings()
                    settings.update("voice", v)
                    settings.update("speed", str(s))
                    settings.update("tone", str(t))
                    settings.update("atmosphere", a)
                    sf.write(f"outputs_big/{v}v_{a}a_{s}s_{t}t.wav",
                             vm(SMALL_MESSAGE, settings),
                             vm.SR)
                    raise

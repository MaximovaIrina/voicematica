from template_message import BIG_MESSAGE, SMALL_MESSAGE
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM, AutoModelForTokenClassification
from transformers import pipeline
import torch
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm
import re
from num2words import num2words
from ssml_builder.core import Speech
import nltk
from nltk.tokenize import sent_tokenize


from settings import VoiceMaticaSettings

class VoiceMatica:

    def __init__(self):
        self.sr = 44100
        
        self.tts_model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="ru",
            speaker="v3_1_ru")
        self.speaker_map = {
            "dmitry": "eugene", 
            "ksenia": "xenia", 
            "viktor": "aidar", 
            "anna": "kseniya"
        }

        self.atmo_procentage=0.25
        self.atmo_range_procentage=0.15
        
        self.atmo_tokenizer = AutoTokenizer.from_pretrained("Tatyana/rubert-base-cased-sentiment-new")
        self.atmo_model = AutoModelForSequenceClassification.from_pretrained("Tatyana/rubert-base-cased-sentiment-new")
        self.emotions = ["neutral", "positive", "negative"]
        
        self.pronunciation_dict = {
            'А': 'а',
            'Б': 'бэ',
            'В': 'вэ',
            'Г': 'гэ',
            'Д': 'дэ',
            'Е': 'е',
            'Ё': 'ё',
            'Ж': 'жэ',
            'З': 'зэ',
            'И': 'и',
            'Й': 'и краткое',
            'К': 'кэ',
            'Л': 'эл',
            'М': 'эм',
            'Н': 'эн',
            'О': 'о',
            'П': 'пэ',
            'Р': 'эр',
            'С': 'эс',
            'Т': 'тэ',
            'У': 'у',
            'Ф': 'эф',
            'Х': 'ха',
            'Ц': 'цэ',
            'Ч': 'чэ',
            'Ш': 'ша',
            'Щ': 'ща',
            'Ъ': 'твёрдый знак',
            'Ы': 'ы',
            'Ь': 'мягкий знак',
            'Э': 'э',
            'Ю': 'ю',
            'Я': 'я'
        }
        self.shorters = {
            "т.е."           : "то есть", 
            "т.к."           : "так как", 
            "т.д."           : "и так далее", 
            "т.н."           : "так называемый", 
            "т.п."           : "и тому подобное", 
            "напр."          : "например", 
            "и пр."          : "и прочее", 
            "и др."          : "и другое", 
            "и т.д."         : "и так далее", 
            "и т.п."         : "и так далее, и прочее", 
            "в т.ч."         : "в том числе", 
            "вкл."           : "включая", 
            "см."            : "смотри", 
        }
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        
        self.title_tokenizer = AutoTokenizer.from_pretrained("csebuetnlp/mT5_multilingual_XLSum")
        self.title_model = AutoModelForSeq2SeqLM.from_pretrained("csebuetnlp/mT5_multilingual_XLSum")
        
        self.tags_tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
        self.tags_model = AutoModelForTokenClassification.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
        self.tag_classifier = pipeline("ner", model=self.tags_model, tokenizer=self.tags_tokenizer)
    
    def _update_volume_on_the_boards(self, audio, begin=True, end=True):
        lenght = len(audio)
        ic_dec_part_size = int(self.atmo_range_procentage * lenght)
        increase_scale = np.linspace(0, 1, ic_dec_part_size)
        if begin:
            audio[:ic_dec_part_size] *= increase_scale
        if end:
            audio[lenght - ic_dec_part_size:] *= increase_scale[::-1]
        return audio

    def _split_text(self, text):
        texts = []
        while len(text) > 999:
            last_dot_index = max(text[:1000].rfind('.'), text[:1000].rfind('?'), text[:1000].rfind('!'))
            texts.append(text[:last_dot_index])
            text = text[last_dot_index:]
        texts.append(text)
        return texts
    
    def _made_title(self, text):
        WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

        input_ids = self.title_tokenizer(
            [WHITESPACE_HANDLER(text)],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512
        )["input_ids"]

        output_ids = self.title_model.generate(
            input_ids=input_ids,
            max_length=30,
            no_repeat_ngram_size=2,
            num_beams=4
        )[0]

        summary = self.title_tokenizer.decode(
            output_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )
        return summary

    
    def _num_to_word(self, text: str) -> str:
        numbers = set(re.findall(r'\d+\.\d+|\d+', text))
        for num in sorted(numbers, key=lambda x: len(x), reverse=True):
            num_digit = float(num) if "." in num else int(num)
            text = text.replace(num, num2words(num_digit, lang="ru"))
        text = text.replace("тысяч", "т+ысяч")
        return text


    def _decode_shortcuts(self, text: str) -> str:
        for shortcut, full_version in self.shorters.items():
            text = text.replace(shortcut, full_version)
        return text


    def _preprocess_whole_text(self, text: str, forwarded: str = None):
        text = self._num_to_word(text)
        text = self._decode_shortcuts(text)
            
        if forwarded is None:
            text = f"Дорогой слушатель. Сейчас вы прослушаете подкаст: \"{self._made_title(text)}\". Начинаем...\n\n" + text
        else:
            text = f"Дорогой слушатель. Сейчас вы прослушаете сообщение пересалнное от {forwarded}. Начинаем...\n\n" + text
        text += "\n <break time=\"300ms\"/> Конец! <break time=\"300ms\"/>"
        return text
        
    def _to_ssml(self, text: str):
        speech = Speech()
        for t in text.split("\n"):
            t = t.replace("/n", "")

            id = 0
            position = t.find("\"")
            while position != -1:
                old_len = len(t)
                if id % 2 == 0:
                    t = t[:position] + "<break time=\"250ms\"/><prosody pitch=\"high\">" + t[position + 1:]
                else:
                    t = t[:position] + "</prosody><break time=\"500ms\"/>" + t[position + 1:]
                diff = len(t) - old_len 
                id += 1
                position = t.find("\"", position + diff)

            t = "".join(["<s>" + sent + "</s>" for sent in sent_tokenize(t)])
            speech.p(t)
        return speech.speak()
        

    def _preprocess_part_text(self, text: str) -> str:
        tags = self.tag_classifier(text)
        tags = [t for t in tags if t["entity"].split("-")[-1] in ["ORG", "LOC", "MISC"]]
        if len(tags):
            abbreviations = []
            curr_word_start = tags[0]["start"]
            curr_word_end = tags[0]["end"]
            curr_word_tag = tags[0]["entity"]
            for id in range(1, len(tags)):
                if curr_word_tag == tags[id]["entity"] and curr_word_end == tags[id]["start"]:
                    curr_word_end = tags[id]["end"]
                else: 
                    abbreviations.append(text[curr_word_start:curr_word_end])
                    curr_word_start = tags[id]["start"]
                    curr_word_end = tags[id]["end"]
                    curr_word_tag = tags[id]["entity"]
            
            abbreviations.append(text[curr_word_start:curr_word_end])
            abbreviations = [a for a in abbreviations if a.isupper()]

            for abbr in set(abbreviations):
                abbr_pronounce = ""
                for c in abbr:
                    abbr_pronounce += self.pronunciation_dict[c]
                text = text.replace(abbr, abbr_pronounce)
        return text 


    def __call__(self, text: str, settings: VoiceMaticaSettings, forwarded: str = None):
        text = self._preprocess_whole_text(text, forwarded)
        with torch.no_grad():
            if len(text) > 850:
                texts = self._split_text(text)
                audio = []
                for text in tqdm(texts):
                    text = self._preprocess_part_text(text)
                    sub_audio = self.tts_model.apply_tts(ssml_text=self._to_ssml(text),
                                speaker=self.speaker_map[settings.voice],
                                sample_rate=48000,
                                put_accent=True,
                                put_yo=True).numpy()
                    audio.extend(list(sub_audio))
                audio = np.array(audio, dtype=float)
            else:
                text = self._preprocess_part_text(text)
                audio = self.tts_model.apply_tts(ssml_text=self._to_ssml(text),
                                speaker=self.speaker_map[settings.voice],
                                sample_rate=48000,
                                put_accent=True,
                                put_yo=True).numpy()
            
            audio = librosa.resample(audio, orig_sr=48000, target_sr=self.sr)
        
            
            if settings.tone != 0:
                audio = librosa.effects.pitch_shift(y=audio, sr=self.sr, n_steps=settings.tone)
            
            
            if settings.speed != 1:
                audio = librosa.effects.time_stretch(y=audio, rate=settings.speed)


            if settings.atmosphere != "empty":
                atmosphere = settings.atmosphere
                if atmosphere == "auto":
                    ids = self.atmo_tokenizer([text, ])["input_ids"]
                    emotion = self.atmo_model(torch.tensor(ids)).logits.softmax(-1)[0].numpy()
                    emotion_id = np.argmax(emotion) 
                    atmosphere = self.emotions[emotion_id]
                
                atmosphere, sr = sf.read(f"atmospheres/{atmosphere}.wav")
                if len(atmosphere.shape) > 1:
                    atmosphere = atmosphere[:, 0]
                assert sr == self.sr, f"{sr} != {self.sr}"
                
                if len(atmosphere) < len(audio):
                    atmosphere = self._update_volume_on_the_boards(atmosphere)
                    n_repeats = int(len(audio) / len(atmosphere)) + 1
                    atmosphere = np.array([ list(atmosphere) * n_repeats ])[0]
                    
                atmosphere = atmosphere[:len(audio)]
                atmosphere = self._update_volume_on_the_boards(atmosphere, begin=False)
                atmosphere *= self.atmo_procentage * np.max(audio)
                audio += atmosphere
                
            return audio
        

if __name__ == "__main__":
    vm = VoiceMatica()
    
    for voice in ["dmitry", "ksenia", "viktor", "anna"]:
        for atmo in ["lofi", "vestern", "guitar", "vostok", "auto", "empty"]:
            for tone in [0., -0.5, 0.5, -1., 1., -2, 2.]:
                for speed in [1, 0.85, 0.90, 0.95, 1.15, 1.25, 1.5]:
                    settings = VoiceMaticaSettings()
                    settings.update("voice", voice)
                    settings.update("speed", str(speed))
                    settings.update("tone", str(tone))
                    settings.update("atmosphere", atmo)
                    # sf.write(f"outputs/small_{voice}v_{atmo}a_{speed}s_{tone}t.wav", 
                    #          vm(SMALL_MESSAGE, settings), 
                    #          vm.sr)
                    sf.write(f"outputs_big/small_{voice}v_{atmo}a_{speed}s_{tone}t.wav", 
                             vm(BIG_MESSAGE, settings), 
                             vm.sr)
                raise
            
            
# * add pauses for , 
# * joia audio without volume
# * increase volume
# * change speed (slower)
# * 1) - пауза для () 
import os
import re
from flask import Flask
from flask import request
from flask import Response
import requests
import emoji
import soundfile as sf

from VoiceMatica import VoiceMatica

TOKEN = "5523151975:AAHPQpIYJ7OfQ5P9pqfQURQ89uqLjhVZFMk"
LANGUAGE = "ru"
app = Flask(__name__)
chat_to_prompt_file = {}
chat_to_is_setup = {}
if LANGUAGE == "ru":
    MODEL = VoiceMaticaRu()
    DEFAULT_VOICE = "prompts/female.pt"
    DEFAULT_TEXT = "Привет мир!"
    VOICE_CHOICE = {"ic_male": "Мужской голос",
                    "ic_female": "Женский голос", "ic_custom": "Установить свой вариант"}
    BUILTIN_VOICE_CHOICE = "{} успешно установлен.\n" \
                           "Он будет использован для дальнейшей озвучки.\n" \
                           "Пример звучания фразы 'Привет мир!':"
    CUSTOM_VOICE_CHOICE = "Вы выбрали свой вариант озвучки.\n" \
                          "Запишите голосове сообщение с нужным голосом длительностью не менее 3х секунд. " \
                          "Для улучшения качества речь должна быть на русском языке."
    FAIL_VOICE_SETUP = "Я не могу использовать это сообщение в качестве образца голоса.\n" \
                       "Процесс настройки голоса сброшен."
    LONG_VOICE_SETUP = "Аудио должно длится не менее 3х секунд.\n" \
                       "Процесс настройки голоса сброшен."
    NEXT_MSG_FORWARDED_FROM = "Сообщение переслано от {}.\n"
    EMPTY_MESSAGE = "Я не могу озучить сообщение без текста"


def parse_text_message(message):
    print("text message-->", message)
    print("text message keys-->", message.keys())
    message = message['message']
    chat_id = message['chat']['id']

    txt = ""
    if "forward_sender_name" in message:  # Forwarded message
        txt = NEXT_MSG_FORWARDED_FROM.format(message['forward_sender_name'])
    elif "forward_from" in message:  # Forwarded message
        txt = NEXT_MSG_FORWARDED_FROM.format(
            message['forward_from']['first_name'])
    elif "forward_from_chat" in message:  # Forwarded from chat message
        txt = NEXT_MSG_FORWARDED_FROM.format(
            message['forward_from_chat']['title'])

    succeed = None
    if "text" in message:  # Simple message
        txt += message['text']
        succeed = True
    elif "caption" in message:  # Message with file
        txt += message['caption']
        succeed = True

    txt = emoji.replace_emoji(txt)
    txt = re.compile(
        r'https?://\S+|www\.\S+').sub(', here is the link attached,', txt)
    if len(txt) == 0:
        txt = EMPTY_MESSAGE
        succeed = False

    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt, succeed


def parse_inlinebutton_message(message):
    print("menu message-->", message)
    print("menu message keys-->", message.keys())
    chat_id = message["callback_query"]["message"]["chat"]["id"]
    txt = message["callback_query"]["data"]
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt


def parse_message(message):
    txt = ""
    chat_id = None
    is_inline_buttom = False
    succeed = False
    if "edited_message" in message:
        txt = ""
        chat_id = message["edited_message"]["chat"]["id"]
        succeed = False
    elif "message" in message:
        chat_id, txt, succeed = parse_text_message(message)
    else:
        chat_id, txt = parse_inlinebutton_message(message)
        is_inline_buttom = True

    if chat_id in chat_to_is_setup:
        is_inline_buttom = False
        if ("message" in message) and ("voice" in message["message"]):
            if message["message"]["voice"]["duration"] > 3:
                file_id = message["message"]["voice"]["file_id"]
                extension = message["message"]["voice"]["mime_type"].split(
                    "/")[-1]
                file = f"prompts/{chat_id}.{extension}"
                tel_get_file(file_id, file)
                chat_to_prompt_file[chat_id] = file
                print(f"chat_to_prompt_file = {chat_to_prompt_file}")
                tel_send_message(
                    chat_id, BUILTIN_VOICE_CHOICE.format("custom"))
                txt = DEFAULT_TEXT
                succeed = True
            else:
                txt += LONG_VOICE_SETUP
                succeed = False
        else:
            txt += FAIL_VOICE_SETUP
            succeed = False
        chat_to_is_setup.pop(chat_id, None)

    return chat_id, txt, is_inline_buttom, succeed


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()

        chat_id, txt, is_inline_buttom, succeed = parse_message(msg)
        if is_inline_buttom:
            voice = txt[3:]
            if voice in ["male", "female"]:
                chat_to_prompt_file[chat_id] = f"prompts/{voice}.pt"
                tel_send_message(
                    chat_id, BUILTIN_VOICE_CHOICE.format(VOICE_CHOICE[txt]))
                speech = MODEL(DEFAULT_TEXT, chat_to_prompt_file[chat_id])
                file = f"outputs/{chat_id}.wav"
                sf.write(file, speech, 16000)
                tel_send_audio(chat_id, file, DEFAULT_TEXT)
                os.remove(file)
            else:
                tel_send_message(chat_id,  CUSTOM_VOICE_CHOICE)
                chat_to_is_setup[chat_id] = True
        else:
            if txt == "/voice":
                tel_send_inlinebutton(chat_id)
            elif succeed:
                prompt_file = DEFAULT_VOICE
                if chat_id in chat_to_prompt_file:
                    prompt_file = chat_to_prompt_file[chat_id]
                print("chat_to_prompt_file: ", chat_to_prompt_file)
                print("prompt_file: ", prompt_file)
                speech = MODEL(txt, prompt_file)
                file = f"outputs/{chat_id}.wav"
                sf.write(file, speech, 16000)
                tel_send_audio(chat_id, file, txt)
                # os.remove(file)
            else:
                tel_send_message(chat_id, txt)

        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


def tel_send_audio(chat_id, file, title):
    url = f'https://api.telegram.org/bot{TOKEN}/sendAudio'
    payload = {
        'chat_id': chat_id,
        'title': title,
        'parse_mode': 'HTML'
    }
    with open(file, 'rb') as audio:
        files = {'audio': audio.read()}
    r = requests.post(url, data=payload, files=files).json()
    return r


def tel_send_inlinebutton(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': 'Select a preferred voice:',
        'reply_markup': {
            "inline_keyboard": [[
                {
                    "text": "ic_male",
                    "callback_data": VOICE_CHOICE["ic_male"]
                },
                {
                    "text": "ic_female",
                    "callback_data": VOICE_CHOICE["ic_female"]
                }],
                [{
                    "text": "ic_custom",
                    "callback_data": VOICE_CHOICE["ic_custom"]
                }],
            ]
        }
    }
    r = requests.post(url, json=payload)
    return r


def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    r = requests.post(url, json=payload)
    return r


def tel_get_file(file_id, path):
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
    file_path = response["result"]["file_path"]
    audio_file = requests.get(
        f"https://api.telegram.org/file/bot{TOKEN}/{file_path}")
    with open(path, "wb") as f:
        f.write(audio_file.content)


if __name__ == '__main__':
    app.run(debug=True)

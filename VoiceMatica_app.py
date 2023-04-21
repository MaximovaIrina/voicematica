import re
from flask import Flask
from flask import request
from flask import Response
import emoji
from send import send_message, send_settings_voice, send_settings_speed, send_settings_tone, send_settings_atmosphere, send_audio
from settings import USERS_SETTINGS, VoiceMaticaSettings

from template_message import START_MSG


app = Flask(__name__)
chat_to_prompt_file = {}
chat_to_is_setup = {}
MODEL = None
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
    txt = re.compile(r'https?://\S+|www\.\S+').sub(', here is the link attached,', txt)
    if len(txt) == 0:
        txt = EMPTY_MESSAGE
        succeed = False

    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt, succeed


def parse_settings_message(message):
    chat_id = message["callback_query"]["message"]["chat"]["id"]
    txt = message["callback_query"]["data"]
    value, setting = txt.split("_")[1:]
    txt = USERS_SETTINGS[chat_id].update(setting, value)
    print(f"Update user-{chat_id} settings -->", USERS_SETTINGS[chat_id])
    return chat_id, txt


def parse_message(message):
    print("message_key->", message.keys())
    if "edited_message" in message:
        txt = ""
        chat_id = message["edited_message"]["chat"]["id"]
        succeed = False
        is_inline_buttom = False
    elif "message" in message:
        chat_id, txt, succeed = parse_text_message(message)
        is_inline_buttom = False
    elif "callback_query" in message:
        chat_id, txt = parse_settings_message(message)
        succeed = True
        is_inline_buttom = True
    else:
        raise "unknown error"
    return chat_id, txt, succeed, is_inline_buttom


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()

        # try:
        chat_id, txt, succeed, is_inline_buttom = parse_message(msg)
        # except:
        #     print("ERROR")
        #     return Response('ok', status=200)
        
        if chat_id not in USERS_SETTINGS:
            USERS_SETTINGS[chat_id] = VoiceMaticaSettings()
            print("USERS_SETTINGS -->", USERS_SETTINGS)
            
        if is_inline_buttom:
            send_message(chat_id, txt)
            send_audio(chat_id, "prompts/test.wav", USERS_SETTINGS[chat_id].audio_title)
            return Response('ok', status=200)
        
        if txt == "/start":
            send_message(chat_id, START_MSG)
        elif txt == "/voice":
            send_settings_voice(chat_id)
        elif txt == "/speed":
            send_settings_speed(chat_id)
        elif txt == "/tonality":
            send_settings_tone(chat_id)
        elif txt == "/atmosphere":
            send_settings_atmosphere(chat_id)
        else:
            send_message(chat_id, START_MSG)
        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


if __name__ == '__main__':
    app.run(debug=True)


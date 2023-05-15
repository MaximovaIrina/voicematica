from datetime import date
import json
import os
import re
from flask import Flask
from flask import request
from flask import Response
import emoji
import traceback
import logging

import numpy as np
from VoiceMatica import VoiceMatica
from send import (
    send_message,
    send_settings_voice,
    send_settings_speed,
    send_settings_tone,
    send_settings_atmosphere,
    send_audio,
    send_voice
)
from settings import USERS_SETTINGS, VoiceMaticaSettings

from template_message import (
    EXAMPLE_AUDIO_TEXT,
    FEEDBACK_MSG,
    FEEDBACK_RECEIVED_MSG,
    INTERNAL_ERROR_MSG,
    START_MSG,
    START_PROCESS,
    EMPTY_MESSAGE
)


logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

app = Flask(__name__)
chat_to_prompt_file = {}
chat_to_is_setup = {}
MODEL = VoiceMatica()
DEFAULT_VOICE = "prompts/female.pt"
DEFAULT_TEXT = "Привет мир!"

NEXT_MSG_FORWARDED_FROM = "Сообщение переслано от {}.\n"


def replace_links(txt, message):
    offset = 0
    template = ', здесь прикреплена ссылка,'
    if "entities" in message:
        for entity in message["entities"]:
            if entity["type"] in "text_link":
                start = entity["offset"] + offset
                url_len = entity["length"]
                if len(re.findall(r'https?://\S+|www\.\S+', txt[start:start+url_len])) == 0:
                    txt = txt[:start+url_len] + template + txt[start+url_len:]
                    offset += len(template)
                else:
                    txt = txt[:start] + template + txt[start+url_len:]
                    offset += len(template) - url_len
    if "caption_entities" in message:
        for entity in message["caption_entities"]:
            if entity["type"] == "text_link":
                start = entity["offset"] + offset
                url_len = entity["length"]
                if len(re.findall(r'https?://\S+|www\.\S+', txt[start:start+url_len])) == 0:
                    txt = txt[:start+url_len] + template + txt[start+url_len:]
                    offset += len(template)
                else:
                    txt = txt[:start] + template + txt[start+url_len:]
                    offset += len(template) - url_len
    return txt


def parse_text_message(message):
    print("text message-->", message)
    print("text message keys-->", message.keys())
    message = message['message']
    chat_id = message['chat']['id']

    txt = ""
    # if "forward_sender_name" in message:  # Forwarded message
    #     txt = NEXT_MSG_FORWARDED_FROM.format(message['forward_sender_name'])
    # elif "forward_from" in message:  # Forwarded message
    #     txt = NEXT_MSG_FORWARDED_FROM.format(message['forward_from']['first_name'])
    # elif "forward_from_chat" in message:  # Forwarded from chat message
    #     txt = NEXT_MSG_FORWARDED_FROM.format(message['forward_from_chat']['title'])

    if "text" in message:  # Simple message
        txt += message['text']
    elif "caption" in message:  # Message with file
        txt += message['caption']

    if txt in ["/current_settings", "/voice", "/speed", "/tonality", "/atmosphere", "/feedback", "/start"]:
        print("txt-->", txt)
        return chat_id, txt, True

    txt = replace_links(txt, message)

    txt = emoji.replace_emoji(txt)
    txt = re.compile(r'https?://\S+|www\.\S+').sub(', здесь прикреплена ссылка,', txt)
    # txt = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+').sub(', здесь прикреплена ссылка,', txt)

    do_voice = True
    if len(txt.split(" ")) < 5:
        txt = EMPTY_MESSAGE
        do_voice = False

    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt, do_voice


def parse_settings_message(message):
    chat_id = message["callback_query"]["message"]["chat"]["id"]
    txt = message["callback_query"]["data"]
    value, setting = txt.split("_")[1:]
    txt = USERS_SETTINGS[chat_id].update(setting, value)
    print(f"Update user-{chat_id} settings -->", USERS_SETTINGS[chat_id])
    return chat_id, txt


def parse_message(message):
    print("message_key->", message.keys())
    update_id = message["update_id"]
    if "edited_message" in message:
        txt = ""
        chat_id = message["edited_message"]["chat"]["id"]
        do_voice = False
        is_inline_buttom = False
    elif "message" in message:
        chat_id, txt, do_voice = parse_text_message(message)
        is_inline_buttom = False
    elif "callback_query" in message:
        chat_id, txt = parse_settings_message(message)
        do_voice = True
        is_inline_buttom = True
    else:
        raise "unknown error"
    return chat_id, txt, do_voice, is_inline_buttom, update_id


def build_and_send_voice(chat_id, txt):
    audio = MODEL(txt, USERS_SETTINGS[chat_id])
    send_voice(chat_id, audio)


def _collect_usage_statistic(chat_id):
    n_msg = 0
    day = date.today()
    file = f"usage/{chat_id}_{day}.txt"
    if os.path.exists(file):
        with open(file, "r") as f:
            n_msg = int(f.read())
    with open(file, "w") as f:
        f.write(str(n_msg + 1))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        with open("last_receive_message.json", "w", encoding='utf8') as f:
            json.dump(msg, f, ensure_ascii=False)

        chat_id, txt, do_voice, is_inline_buttom, update_id = parse_message(msg)
        try:
            if chat_id not in USERS_SETTINGS:
                USERS_SETTINGS[chat_id] = VoiceMaticaSettings()
                print("USERS_SETTINGS -->", USERS_SETTINGS)

            if USERS_SETTINGS[chat_id].is_last_feedback:
                with open(f"feedback/{chat_id}_{int(np.random.rand()*100)}.json", "w", encoding='utf8') as f:
                    json.dump(msg, f, ensure_ascii=False)
                USERS_SETTINGS[chat_id].is_last_feedback = False
                send_message(chat_id, FEEDBACK_RECEIVED_MSG)
                return Response('ok', status=200)

            if update_id in USERS_SETTINGS[chat_id].update_id:
                return Response('ok', status=200)
            else:
                USERS_SETTINGS[chat_id].update_id.add(update_id)

            if is_inline_buttom:
                send_message(chat_id, txt)
                audio = MODEL.get_example(EXAMPLE_AUDIO_TEXT, USERS_SETTINGS[chat_id])
                send_audio(chat_id, audio, USERS_SETTINGS[chat_id].audio_title)
                return Response('ok', status=200)

            if not do_voice:
                send_message(chat_id, txt)
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
            elif txt == "/current_settings":
                send_message(chat_id, str(USERS_SETTINGS[chat_id]))
            elif txt == "/feedback":
                send_message(chat_id, FEEDBACK_MSG)
                USERS_SETTINGS[chat_id].is_last_feedback = True
            else:
                send_message(
                    chat_id,
                    START_PROCESS.format(
                        len(txt) / MODEL.NUM_SYMBOLS_PER_MINUT + 0.15
                    )
                )
                build_and_send_voice(chat_id, txt)
                _collect_usage_statistic(chat_id)
                return Response('ok', status=200)
        except Exception:
            logging.error("INTERNAL_PARSE_ERROR:\n")
            logging.error(traceback.format_exc())
            with open(f"errors/{len(os.listdir('errors'))}.json", "w", encoding='utf8') as f:
                json.dump(msg, f, ensure_ascii=False)
            send_message(chat_id, INTERNAL_ERROR_MSG)
        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


if __name__ == '__main__':
    VoiceMaticaSettings.load_users_settings()
    app.run(debug=True, port=5002)

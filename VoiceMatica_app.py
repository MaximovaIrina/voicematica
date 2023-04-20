# import re
# from flask import Flask
# from flask import request
# from flask import Response
# import emoji
# from send import send_message

# from template_message import START_MSG


# app = Flask(__name__)
# chat_to_prompt_file = {}
# chat_to_is_setup = {}
# MODEL = None
# DEFAULT_VOICE = "prompts/female.pt"
# DEFAULT_TEXT = "Привет мир!"
# VOICE_CHOICE = {"ic_male": "Мужской голос",
#                 "ic_female": "Женский голос", "ic_custom": "Установить свой вариант"}
# BUILTIN_VOICE_CHOICE = "{} успешно установлен.\n" \
#     "Он будет использован для дальнейшей озвучки.\n" \
#     "Пример звучания фразы 'Привет мир!':"
# CUSTOM_VOICE_CHOICE = "Вы выбрали свой вариант озвучки.\n" \
#     "Запишите голосове сообщение с нужным голосом длительностью не менее 3х секунд. " \
#     "Для улучшения качества речь должна быть на русском языке."
# FAIL_VOICE_SETUP = "Я не могу использовать это сообщение в качестве образца голоса.\n" \
#     "Процесс настройки голоса сброшен."
# LONG_VOICE_SETUP = "Аудио должно длится не менее 3х секунд.\n" \
#     "Процесс настройки голоса сброшен."
# NEXT_MSG_FORWARDED_FROM = "Сообщение переслано от {}.\n"
# EMPTY_MESSAGE = "Я не могу озучить сообщение без текста"


# def parse_text_message(message):
#     print("text message-->", message)
#     print("text message keys-->", message.keys())
#     message = message['message']
#     chat_id = message['chat']['id']

#     txt = ""
#     if "forward_sender_name" in message:  # Forwarded message
#         txt = NEXT_MSG_FORWARDED_FROM.format(message['forward_sender_name'])
#     elif "forward_from" in message:  # Forwarded message
#         txt = NEXT_MSG_FORWARDED_FROM.format(
#             message['forward_from']['first_name'])
#     elif "forward_from_chat" in message:  # Forwarded from chat message
#         txt = NEXT_MSG_FORWARDED_FROM.format(
#             message['forward_from_chat']['title'])

#     succeed = None
#     if "text" in message:  # Simple message
#         txt += message['text']
#         succeed = True
#     elif "caption" in message:  # Message with file
#         txt += message['caption']
#         succeed = True

#     txt = emoji.replace_emoji(txt)
#     txt = re.compile(
#         r'https?://\S+|www\.\S+').sub(', here is the link attached,', txt)
#     if len(txt) == 0:
#         txt = EMPTY_MESSAGE
#         succeed = False

#     print("chat_id-->", chat_id)
#     print("txt-->", txt)
#     return chat_id, txt, succeed


# def parse_inlinebutton_message(message):
#     print("menu message-->", message)
#     print("menu message keys-->", message.keys())
#     chat_id = message["callback_query"]["message"]["chat"]["id"]
#     txt = message["callback_query"]["data"]
#     print("chat_id-->", chat_id)
#     print("txt-->", txt)
#     return chat_id, txt


# def parse_message(message):
#     if "edited_message" in message:
#         txt = ""
#         chat_id = message["edited_message"]["chat"]["id"]
#         is_inline_buttom = False
#         succeed = False
#     elif "message" in message:
#         chat_id, txt, succeed = parse_text_message(message)
#         is_inline_buttom = False
#     else:
#         chat_id, txt = parse_inlinebutton_message(message)
#         succeed = True
#         is_inline_buttom = True
#     return chat_id, txt, is_inline_buttom, succeed


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     print("Start")
#     if request.method == 'POST':
#         msg = request.get_json()

#         chat_id, txt, is_inline_buttom, succeed = parse_message(msg)
#         if txt == "/start":
#             send_message(chat_id, START_MSG)
#         else:
#             raise "unimplemented"
#         return Response('ok', status=200)
#     else:
#         return "<h1>Welcome!</h1>"


# if __name__ == '__main__':
#     app.run(debug=True, port=5002)

from flask import Flask
from flask import request
from flask import Response
import requests

TOKEN = "<Your Bot Token>"
app = Flask(__name__)


def parse_message(message):
    print("message-->", message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt


def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    r = requests.post(url, json=payload)
    return r


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()

        chat_id, txt = parse_message(msg)
        if txt == "hi":
            tel_send_message(chat_id, "Hello!!")
        else:
            tel_send_message(chat_id, 'from webhook')

        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


if __name__ == '__main__':
    app.run(debug=True,  port=5002)

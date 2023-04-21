import requests

from vm_token import TOKEN


def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    r = requests.post(url, json=payload)
    return r


def send_settings_voice(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': 'Выберите голос озвучки:',
        'reply_markup': {
            "inline_keyboard": [[
                {
                    "callback_data": "ic_dmitry_voice",
                    "text": "Дмитрий"
                },
                {
                    "callback_data": "ic_ksenia_voice",
                    "text": "Ксения"
                }],[
                {
                    "callback_data": "ic_viktor_voice",
                    "text": "Виктор"
                },
                {
                    "callback_data": "ic_anna_voice",
                    "text": "Анна"
                }],
            ]
        }
    }
    r = requests.post(url, json=payload)
    return r


def send_settings_speed(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': 'Выберите скорость озвучки:',
        'reply_markup': {
            "inline_keyboard": [[
                {
                    "callback_data": "ic_0.5_speed",
                    "text": "x0.5"
                },
                {
                    "callback_data": "ic_0.75_speed",
                    "text": "x0.75"
                },
                {
                    "callback_data": "ic_0.85_speed",
                    "text": "x0.85"
                },
                {
                    "callback_data": "ic_0.90_speed",
                    "text": "x0.90"
                },
                {
                    "callback_data": "ic_0.95_speed",
                    "text": "x0.95"
                }],[
                {
                    "callback_data": "ic_1.0_speed",
                    "text": "Обычная"
                },],[
                {
                    "callback_data": "ic_1.05_speed",
                    "text": "x1.25"
                },
                {
                    "callback_data": "ic_1.15_speed",
                    "text": "x1.25"
                },
                {
                    "callback_data": "ic_1.25_speed",
                    "text": "x1.25"
                },
                {
                    "callback_data": "ic_1.5_speed",
                    "text": "x1.5"
                },
                {
                    "callback_data": "ic_1.75_speed",
                    "text": "x1.75"
                },
                {
                    "callback_data": "ic_2_speed",
                    "text": "x2"
                },
            ]]
        }
    }
    r = requests.post(url, json=payload)
    return r

def send_settings_tone(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': 'Выберите высоту тона озвучки:',
        'reply_markup': {
            "inline_keyboard": [[
                {
                    "callback_data": "ic_-0.5_tone",
                    "text": "-0.5"
                },
                {
                    "callback_data": "ic_-1_tone",
                    "text": "-1.0"
                },
                {
                    "callback_data": "ic_-2_tone",
                    "text": "-2"
                }],[
                {
                    "callback_data": "ic_0_tone",
                    "text": "Обычный"
                },],[
                {
                    "callback_data": "ic_+0.5_tone",
                    "text": "+0.5"
                },
                {
                    "callback_data": "ic_+1_tone",
                    "text": "+1.0"
                },
                {
                    "callback_data": "ic_+2_tone",
                    "text": "+2.0"
                },
            ]]
        }
    }
    r = requests.post(url, json=payload)
    return r


def send_settings_atmosphere(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': 'Выберите атмосферу подкаста:',
        'reply_markup': {
            "inline_keyboard": [[
                {
                    "callback_data": "ic_lofi_atmosphere",
                    "text": "lofi hip hop"
                },
                {
                    "callback_data": "ic_vestern_atmosphere",
                    "text": "Вестерн"
                }],[
                {
                    "callback_data": "ic_guitar_atmosphere",
                    "text": "Гитара"
                },
                {
                    "callback_data": "ic_vostok_atmosphere",
                    "text": "Восток"
                }],[
                {
                    "callback_data": "ic_auto_atmosphere",
                    "text": "Автоматическая"
                },
                {
                    "callback_data": "ic_empty_atmosphere",
                    "text": "Без атмосферы"
                },
            ]]
        }
    }
    r = requests.post(url, json=payload)
    return r


def send_audio(chat_id, file, title):
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
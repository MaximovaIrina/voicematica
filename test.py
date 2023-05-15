# # -*- coding: utf-8 -*-
import re
import openai

from vm_token import GPT_TOKEN

openai.api_key = GPT_TOKEN

import time



# # txt = """
# # Методичка-вопросник рассерженного патриота. (Сборник вопросов к представителям власти и пропагандонам-охранителям, по которым хотелось бы получить конкретные прямые и честные ответы, с вытекающими орг-выводами).

# # I. Вопросы "исторические":

# # 1) В две тысячи четырнадцатом году власть укро-хунты висела на волоске, вся Новороссия - глядя на Крым - с надеждой ждала Россию. Но Кремль сначала отказался от ввода миротворческих сил в Донбасс, а потом первым в мире признал легитимность избрания Порошенко.

# # (Настроение: negative)
# # """
# # a = "negative"
# # # print(txt.replace(f"(Настроение: {a})", ""))
# # # print(re.findall("\(Настроение: positive|neutral|negative)", txt)[0][0] == f"(Настроение: {a})")
# # predicted_atmosphere = re.findall("\(Настроение: (positive|neutral|negative)\)", txt)[0]
# # print(txt.replace(f"(Настроение: {predicted_atmosphere})", ""))
# # raise

# # text = "В две́ ты́сячи четы́рнадцатом го́ду я встре́тил ва́шу ма́му пе́рвый раз"
# # text_without_accents = ""
# # i = 0
# # while i < len(text) - 1:
# #     print(i)
# #     if text[i+1] == "́":
# #         text_without_accents += "+" + text[i]
# #         i += 1
# #     else:
# #         text_without_accents += text[i]
# #     i += 1
# # # text_with_plus = re.sub('[́]', '+', text)

# # print(text_without_accents)
# # raise



# # def generate_prompt(text : str):
# #     return [
# #         {"role": "user", "content": """Перепеши текст, расставляя ударения и замения числа и даты в тексте на нужные слова. Слова в верхнем регистре оставь без изменений. Обрати внимаение на правильность окончаний в словах. В конце скажи общее настроение сообщения(positive/neutral/negative).
# #         Текст: 1) В 2014 я встетрил вашу маму 1й раз в ВС ЛДПР.
# #         Переписанный текст: Первый пункт) В две ты́сячи четы́рнадцатом го́ду я встре́тил ва́шу ма́му пе́рвый раз в ВСУ ЛДПР. (Настроение: positive)
# #         Текст: {}
# #         Переписанный текст:""".format(text)}
# #     ]


# # text = """1) В 2014-м году власть укро-хунты висела на волоске ВСУ ВСУ ВСУ, вся Новороссия - глядя на Крым - с надеждой ждала Россию. 2) Но Кремль сначала отказался от ввода миротворческих сил в Донбасс, а потом первым в мире признал легитимность избрания Порошенко. В результате 8-летней \"минской тягомотины\" власти так называемый \"украина\" создали боеспособную армию, подавили протестное движение, промыли мозги значительной части населения и к 2022 году оказались в состоянии противостоять ВС РФ на поле боя. КТО отвечает за стратегически -провальные решения, за которые сейчас Россия расплачивается тысячами жизней и десятками тысяч калек? Кто понёс или должен понести наказание за данный кретинизм и/или прямое вредительство?"""

# # start = time.time()
# # completion = openai.ChatCompletion.create(
# #   model="gpt-3.5-turbo",
# #   messages=generate_prompt(text),
# #   temperature=0,
# # )

# # print(completion.choices[0].message.content)
# # print(time.time() - start)

# # "positive/neutral/negative. Напиши супер короткий  заголовок о сожержании текcта и о его настроении."
# start = time.time()
# completion = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo",
#   messages=[{"role": "user", "content": """Напиши супер короткий  заголовок о сожержании текcта. Твой ответ должен соответвовать шаблону: "Сегодня мы поговорим о <три-четыре слова о тексте>". Методичка-вопросник рассерженного патриота. (Сборник вопросов к представителям власти и пропагандонам-охранителям, по которым хотелось-бы получить конкретные прямые и честные ответы, с вытекающими орг-выводами).

# I. Вопросы "исторические":

# 1) В 2014-м году власть укро-хунты висела на волоске, вся Новороссия - глядя на Крым - с надеждой ждала Россию. Но Кремль сначала отказался от ввода миротворческих сил в Донбасс, а потом первым в мире признал легитимность избрания Порошенко. В результате 8-летней "минской тягомотины" власти т.н. "украина" создали боеспособную армию, подавили протестное движение, промыли мозги значительной части населения и к 2022 году оказались в состоянии противостоять ВС РФ на поле боя. КТО отвечает за стратегически -провальные решения, за которые сейчас Россия расплачивается тысячами жизней и десятками тысяч калек? Кто понёс или должен понести наказание за данный кретинизм и/или прямое вредительство?"""},],
#   temperature=0,
# )

# print(completion.choices[0].message.content)
# print(time.time() - start)


# start = time.time()
# completion = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo",
#   messages=[{"role": "user", "content": """Какое настроение в этом тектсе? Варианты ответа: positive/neutral/negative. Напиши только ответ.
# Методичка-вопросник рассерженного патриота. (Сборник вопросов к представителям власти и пропагандонам-охранителям, по которым хотелось-бы получить конкретные прямые и честные ответы, с вытекающими орг-выводами).

# I. Вопросы "исторические":

# 1) В 2014-м году власть укро-хунты висела на волоске, вся Новороссия - глядя на Крым - с надеждой ждала Россию. Но Кремль сначала отказался от ввода миротворческих сил в Донбасс, а потом первым в мире признал легитимность избрания Порошенко. В результате 8-летней "минской тягомотины" власти т.н. "украина" создали боеспособную армию, подавили протестное движение, промыли мозги значительной части населения и к 2022 году оказались в состоянии противостоять ВС РФ на поле боя. КТО отвечает за стратегически -провальные решения, за которые сейчас Россия расплачивается тысячами жизней и десятками тысяч калек? Кто понёс или должен понести наказание за данный кретинизм и/или прямое вредительство?"""},],
#   temperature=0,
# )

# print(completion.choices[0].message.content)
# print(time.time() - start)


# start = time.time()
# completion = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo",
#   # messages=[{"role": "user", "content": """Перепиши текст, заменяя числа и даты на слова. Числа которые соответвуют номеру пунтка перепиши со словом \"пункт\" (например "1) Купить продудкты" == "Первый пункт) Купить продукты"). Слова в верхнем регистре оставь без изменений.
#   # Методичка-вопросник рассерженного патриота. (Сборник вопросов к представителям власти и пропагандонам-охранителям, по которым хотелось-бы получить конкретные прямые и честные ответы, с вытекающими орг-выводами).\n\nI. Вопросы "исторические":\n\n1) В 2014-м году власть укро-хунты висела на волоске, вся Новороссия - глядя на Крым - с надеждой ждала Россию. Но Кремль сначала отказался от ввода миротворческих сил в Донбасс, а потом первым в мире признал легитимность избрания Порошенко."""},],
#   messages=[{"role": "user", "content": """Перепеши текст заменяя числа и даты на нужные слова. Слова в верхнем регистре оставь без изменений. Числа которые соответвуют номеру пунтка перепиши со словом \"пункт\". Обрати внимаение на правильность окончаний в словах.
#         Текст: 1) В 2014 я встетрил вашу маму 1й раз в ВС ЛДПР.
#         Переписанный текст: Первый пункт) В две тысячи четырнадцатом году я встретил вашу маму первый раз в ВСУ ЛДПР.
#         Текст: Методичка-вопросник рассерженного патриота. (Сборник вопросов к представителям власти и пропагандонам-охранителям, по которым хотелось-бы получить конкретные прямые и честные ответы, с вытекающими орг-выводами).\n\nI. Вопросы "исторические":\n\n1) В 2014-м году власть укро-хунты висела на волоске, вся Новороссия - глядя на Крым - с надеждой ждала Россию. Но Кремль сначала отказался от ввода миротворческих сил в Донбасс, а потом первым в мире признал легитимность избрания Порошенко.
#         Переписанный текст:"""}],
#   temperature=0,
# )

# print(completion.choices[0].message.content)
# print(time.time() - start)
txt = """Про накопительные счета

C 25 апреля 2023 года мы увеличиваем ставку по накопительному счету «На ежедневный остаток»:

🔸До 6% на сумму до 150 000 ₽ для всех клиентов;

🔸До 6% на сумму до 1 000 000 ₽ для клиентов с пакетами «Премиальный» и «Премиальный 5»;

🔸На остаток выше будет действовать ставка 0,01%.

Открыть можно не более одного накопительного счета, а ранее открытые счета с 25 апреля будут обслуживаться по новым условиям автоматически.

Больше подробностей тут."""

start = time.time()
completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  # messages=[{"role": "user", "content": """Перепиши текст, заменяя числа и даты на слова. Числа которые соответвуют номеру пунтка перепиши со словом \"пункт\" (например "1) Купить продудкты" == "Первый пункт) Купить продукты"). Слова в верхнем регистре оставь без изменений.
  # Методичка-вопросник рассерженного патриота. (Сборник вопросов к представителям власти и пропагандонам-охранителям, по которым хотелось-бы получить конкретные прямые и честные ответы, с вытекающими орг-выводами).\n\nI. Вопросы "исторические":\n\n1) В 2014-м году власть укро-хунты висела на волоске, вся Новороссия - глядя на Крым - с надеждой ждала Россию. Но Кремль сначала отказался от ввода миротворческих сил в Донбасс, а потом первым в мире признал легитимность избрания Порошенко."""},],
  messages=[{"role": "user", "content": f"""Перепеши текст заменяя числа и даты на нужные слова. Все остальное оставь без изменений. Числа которые соответвуют номеру пунтка перепиши со словом \"пункт\". Обрати внимаение на правильность окончаний в словах.
        Текст: 1) В 2014 я встетрил вашу маму 1й раз в ВСУ "ЛДПР 5", вероятность была 0.01.
        Переписанный текст: Первый пункт) В две тысячи четырнадцатом году я встретил вашу маму первый раз в ВСУ "ЛДПР пять", веротяность была одна сотая процента.
        Текст: {txt}.
        Переписанный текст:"""}],
  temperature=0,
)

print(completion.choices[0].message.content)
print(time.time() - start)

import os

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from email.message import EmailMessage
import smtplib
import random
import json
import re

from dotenv import load_dotenv

load_dotenv()


def make_city(city):
    city = re.split(' |-|_', city)
    return ' '.join(city), '-'.join(city), '_'.join(city), ''.join(city)


def get_city(cities, used_cities):
    city = random.choice(cities)
    if set(filter(lambda x: x.startswith(city[0]), used_cities)) == {item.lower() for item in
                                                                     cities}:
        return None
    while not check_city(city.lower(), used_cities, inv=True):
        city = random.choice(cities)
    return city


def check_city(city, cities, inv=False):
    cities = [item.lower() for item in cities]
    if inv:
        if city not in cities:
            return True
    else:
        if city in cities:
            return True
    return False


def check_ending(city: str):
    city = city.upper()
    try:
        if city.endswith('Ь'):
            return city.rstrip('Ь')[-1]
        if city.endswith('Ъ'):
            return city.rstrip('Ъ')[-1]
        if city.endswith('Ы'):
            return 'Ы', city.rstrip('Ы')[-1]
        if city.endswith('Ё'):
            return 'Е'
        else:
            return city[-1]
    except IndexError:
        return 'ERROR'


# def send_letter(all_data, text):
#
#     email = os.environ.get('email')
#     password = os.environ.get('password')
#
#     msg = EmailMessage()
#     msg['Subject'] = 'Ошибки в city_bot'
#     msg['FROM'] = email
#     msg['TO'] = email
#
#     message = f"Комментарий пользователя:\n\n{text}\n\n"
#     msg.set_content(message)
#
#     attachments = [os.path.join(os.path.dirname(__file__), 'users.json'),
#                    os.path.join(os.path.dirname(__file__), 'meta_user.json')]
#     for path in attachments:
#         with open(path, mode='r', encoding='UTF-8') as file:
#             data = file.read()
#             name = path.split("\\")[-1]
#
#             msg.add_attachment(data, filename=name)
#             smtpserver = smtplib.SMTP("smtp.gmail.com", 465)
#             smtpserver.ehlo()
#             smtpserver.starttls()
#             smtpserver.ehlo()
#             smtpserver.login('vkcitybot@gmail.com', 'asdfSS123')
#             smtpserver.send_message(msg)


def main():
    letters = list('АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЭЮЯ')

    with open('cities.json', encoding='UTF-8', mode='r') as all_cities:
        my_cities = json.load(all_cities)
    with open('rules.txt', encoding='UTF-8', mode='r') as rules:
        rules = ''.join(rules.readlines())
    with open('users.json', encoding='UTF-8', mode='r') as data_to_read:
        data = json.load(data_to_read)
    with open('phrases.json', encoding='UTF-8', mode='r') as templates:
        phrases = json.load(templates)

    vk_session = vk_api.VkApi(token=os.environ.get('token'))

    longpoll = VkBotLongPoll(vk_session, os.environ.get('num'))

    start_keyboard = VkKeyboard(one_time=True)
    start_keyboard.add_button('Начать', color=VkKeyboardColor.POSITIVE)
    start_keyboard.add_button('Правила', color=VkKeyboardColor.DEFAULT)

    stop_keyboard = VkKeyboard(one_time=True)
    stop_keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    stop_keyboard.add_button('Правила', color=VkKeyboardColor.DEFAULT)
    stop_keyboard.add_button('Ошибка?', color=VkKeyboardColor.DEFAULT)

    yes_no_keyboard = VkKeyboard(one_time=True)
    yes_no_keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
    yes_no_keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)

    curr_keyboard = start_keyboard

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            message = event.obj.message['text']
            user_id = event.obj.message['from_id']
            user = str(user_id)
            at_first = False
            # print(event)
            # print('Новое сообщение:')
            # print('Для меня от:', event.obj.message['from_id'])
            # print('Текст:', event.obj.message['text'])
            if user not in data:
                data[user] = {'IsGameStarted': False, 'UsedCities': [], "LastLetter": [],
                              "Disappointed": False}
                at_first = True

            game = data[user]

            if game['Disappointed'] != 'no':
                if game['Disappointed'] == 'yes':
                    if 'да' in message.lower():
                        game['Disappointed'] = 'very'
                        vk.messages.send(user_id=user_id,
                                         message=random.choice(phrases["listen"]),
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        game['Disappointed'] = 'no'
                        vk.messages.send(user_id=user_id,
                                         message=random.choice(phrases["errors"]["short"]),
                                         random_id=random.randint(0, 2 ** 64))
                        vk.messages.send(user_id=user_id,
                                         message=f'''
                                         {random.choice(phrases["letter"])}
                                         P.S. Вам на {"/".join(game["LastLetter"])}
                                         ''',
                                         random_id=random.randint(0, 2 ** 64),
                                         keyboard=stop_keyboard.get_keyboard())
                        vk.messages.send(user_id=168831681,
                                         message="Ошибка:\n\n{}\n\n{}\n\nКомментарий пользователя отсутствует".format(
                                             {user: game}, data),
                                         random_id=random.randint(0, 2 ** 64))

                elif game['Disappointed'] == 'very':
                    game['Disappointed'] = 'no'
                    vk.messages.send(user_id=user_id,
                                     message=random.choice(phrases["errors"]["long"]),
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user_id,
                                     message=f'''
                                     {random.choice(phrases["letter"])}
                                     P.S. Вам на {"/".join(game["LastLetter"])}
                                     ''',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=stop_keyboard.get_keyboard())
                    vk.messages.send(user_id=168831681,
                                     message="Ошибка:\n\n{}\n\n{}\n\nКомментарий пользователя:\n\n{}".format(
                                         {user: game}, data, message),
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=stop_keyboard.get_keyboard())

            elif message.lower() == 'начать':
                if not game["IsGameStarted"]:
                    if at_first:
                        vk.messages.send(user_id=user_id,
                                         message=random.choice(phrases["rejoin"]),
                                         random_id=random.randint(0, 2 ** 64),
                                         keyboard=curr_keyboard.get_keyboard())
                    my_city = random.choice(my_cities[random.choice(letters)])
                    last_letter = list(check_ending(my_city))

                    game["IsGameStarted"] = True
                    game["UsedCities"].append(my_city.lower())
                    game["LastLetter"] = last_letter

                    curr_keyboard = stop_keyboard
                    vk.messages.send(user_id=user_id,
                                     message=f'{my_city} — Вам на {"/".join(game["LastLetter"])}',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=curr_keyboard.get_keyboard())
                else:
                    vk.messages.send(user_id=user_id,
                                     message=random.choice(phrases["late_start"]),
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=curr_keyboard.get_keyboard())

            elif message.lower() == 'сдаться':
                if game["IsGameStarted"]:
                    curr_keyboard = start_keyboard
                    vk.messages.send(user_id=user_id,
                                     message=f'''
                                     {random.choice(phrases["loose"])}
                                     Вы назвали {len(game["UsedCities"]) // 2} городов
                                     ''',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=curr_keyboard.get_keyboard())
                    game = {'IsGameStarted': False, 'UsedCities': [], "LastLetter": [],
                            "Disappointed": "no"}
                else:
                    vk.messages.send(user_id=user_id,
                                     message=random.choice(phrases["not_yet"]),
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=curr_keyboard.get_keyboard())

            elif message.lower() == 'правила':
                vk.messages.send(user_id=user_id,
                                 message=f'{rules}',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=curr_keyboard.get_keyboard())

            elif 'ошибка' in message.lower():
                game['Disappointed'] = "yes"
                vk.messages.send(user_id=user_id,
                                 message='''
                                 Разработчик получит уведомление об ошибке
                                 Желаете отправить сообщение для наилучшего понимания проблемы и её скорейшего решения?
                                 ''',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=yes_no_keyboard.get_keyboard())

            else:
                if game["IsGameStarted"]:
                    curr_keyboard = stop_keyboard
                    message = message.lower()
                    if message[0].upper() in game["LastLetter"]:
                        if check_city(city=message, cities=my_cities[message[0].upper()]):
                            if check_city(city=message, cities=game["UsedCities"], inv=True):

                                game["UsedCities"].append(message)
                                last_letter = list(check_ending(message))
                                my_city = get_city(my_cities[random.choice(last_letter)],
                                                   game["UsedCities"])
                                if my_city:
                                    last_letter = list(check_ending(my_city))

                                    game["UsedCities"].append(my_city.lower())
                                    game["LastLetter"] = last_letter
                                    vk.messages.send(user_id=user_id,
                                                     message=f'{my_city} — Вам на {"/".join(game["LastLetter"])}',
                                                     random_id=random.randint(0, 2 ** 64),
                                                     keyboard=curr_keyboard.get_keyboard())
                                else:
                                    curr_keyboard = start_keyboard
                                    vk.messages.send(user_id=user_id,
                                                     message=f'''
                                                     {random.choice(phrases["endgame"])}
                                                     {len(game["UsedCities"]) // 2} названных Вами городов — это достойно
                                                     Спасибо за игру!
                                                     ''',
                                                     random_id=random.randint(0, 2 ** 64),
                                                     keyboard=curr_keyboard.get_keyboard())
                                    game = {'IsGameStarted': False, 'UsedCities': [],
                                            "LastLetter": [], "Disappointed": "no"}

                            else:
                                vk.messages.send(user_id=user_id,
                                                 message=random.choice(phrases["already_was"]),
                                                 random_id=random.randint(0, 2 ** 64),
                                                 keyboard=curr_keyboard.get_keyboard())
                        else:
                            vk.messages.send(user_id=user_id,
                                             message=f'''
                                             {random.choice(phrases["correct"])}
                                             Проверьте правильность написания и актуальность названия
                                             И не забывайте: только кириллица, дефис (-) и пробел
                                             ''',
                                             random_id=random.randint(0, 2 ** 64),
                                             keyboard=curr_keyboard.get_keyboard())
                    else:
                        vk.messages.send(user_id=user_id,
                                         message=f'Ну вообще-то вам на {"/".join(game["LastLetter"])}',
                                         random_id=random.randint(0, 2 ** 64),
                                         keyboard=curr_keyboard.get_keyboard())
                else:
                    vk.messages.send(user_id=user_id,
                                     message=random.choice(phrases["stupido"]),
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=curr_keyboard.get_keyboard())

            data[user] = game
            with open('users.json', encoding='UTF-8', mode='w') as users:
                json.dump(data, fp=users, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()

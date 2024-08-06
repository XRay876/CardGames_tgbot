from telebot import types
import telebot
import sqlite3
import os, random
from auth_data import token, admin_id
import time

bot = telebot.TeleBot(token)

conn = sqlite3.connect('game.db', check_same_thread=False)
cursor = conn.cursor()


def choose_game_markup():
    markup = types.InlineKeyboardMarkup(row_width=True)
    millionaires_club = types.InlineKeyboardButton(text='Клуб миллионеров', callback_data='millionaires')
    happiness_game = types.InlineKeyboardButton(text='Анатомия счастья', callback_data='happiness')
    markup.add(millionaires_club, happiness_game)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Добро пожаловать! \n\nЕсли вы еще не играли в трансформационные игры, то это возможность познакомиться с ними. Выберите одну из двух игр:', reply_markup=choose_game_markup())



@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == 'millionaires':
        video_path = 'materials/videos/freecompress-millionaires_start.mp4'
        with open(video_path, 'rb') as video:
            bot.send_video(call.message.chat.id, video)
        markup_mil_1 = types.InlineKeyboardMarkup(row_width=True)
        markup_mil_1.add(types.InlineKeyboardButton(text='ИГРАТЬ', callback_data='play_millionaires'),
                         types.InlineKeyboardButton(text='Инструкция', callback_data='instruction_millionaires'),
                         types.InlineKeyboardButton(text='Назад', callback_data='back'))
        bot.send_message(chat_id, text='Вы выбрали игру "Клуб миллионеров"', reply_markup=markup_mil_1)

    elif call.data == 'play_millionaires':
        video_path = 'materials/videos/freecompress-millionaires_instruction.mp4'
        with open(video_path, 'rb') as video:
            bot.send_video(call.message.chat.id, video)
        with open(f'materials/millionaires_field_0.png', 'rb') as photo:
            bot.send_photo(chat_id, photo)
        bot.send_message(chat_id, 'Посмотрите на поле. Сейчас вы находитесь в начале пути, бросайте кубик, чтобы продвинуться вперед!', reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
            types.InlineKeyboardButton(text='Бросить кубик', callback_data='drop_dice')))
        start_game(user_id, 'millionaires')

    elif call.data == 'happiness':
        video_path = 'materials/videos/freecompress-happiness_start.mp4'
        with open(video_path, 'rb') as video:
            bot.send_video(call.message.chat.id, video)
        markup_hap_1 = types.InlineKeyboardMarkup(row_width=True)
        markup_hap_1.add(types.InlineKeyboardButton(text='ИГРАТЬ', callback_data='play_happiness'),
                         types.InlineKeyboardButton(text='Инструкция', callback_data='instruction_happiness'),
                         types.InlineKeyboardButton(text='Назад', callback_data='back'))
        bot.send_message(chat_id, text='Вы выбрали игру "Анатомия счастья"', reply_markup=markup_hap_1)

    elif call.data == 'play_happiness':
        video_path = 'materials/videos/freecompress-happiness_instruction.mp4'
        with open(video_path, 'rb') as video:
            bot.send_video(call.message.chat.id, video)
        with open(f'materials/happiness_field_0.png', 'rb') as photo:
            bot.send_photo(chat_id, photo)
        bot.send_message(chat_id, 'Посмотрите на поле. Сейчас вы находитесь в начале пути, бросайте кубик, чтобы продвинуться вперед!', reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
            types.InlineKeyboardButton(text='Бросить кубик', callback_data='drop_dice')))
        start_game(user_id, 'happiness')

    elif call.data == 'drop_dice':
        roll_dice(chat_id, user_id)

    elif call.data == 'back':
        start(call.message)

    elif call.data == 'instruction_millionaires':
        bot.send_message(chat_id,
                         'В ДЕМО-ВЕРСИИ У ВАС БУДЕТ 3 ХОДА. \n\n1. Вы кидаете кубик и продвигаетесь на выпавшее количество шагов по полю игры ' +
                         '\n\n2. Попадаете на определенный раздел игры: «Деньги», «План роста», «Стратегия роста», «Уникальность», «Цель и ресурсы» \n\n3. Открываете выпавшую карту из этого раздела ' +
                         '\n\nКАЖДАЯ КАРТА - это задание, практика или подсказка, которые приблизят вас к цели!',
                         reply_markup=types.InlineKeyboardMarkup(row_width=True).add(types.InlineKeyboardButton(text='Играть', callback_data='play_millionaires')))

    elif call.data == 'instruction_happiness':
        bot.send_message(chat_id,
                         'В ДЕМО-ВЕРСИИ У ВАС БУДЕТ 3 ХОДА. \n\n1. Вы кидаете кубик и продвигаетесь на выпавшее количество шагов по полю игры ' +
                         '\n\n2. Попадаете на определенный раздел игры: «Деньги», «План роста», «Стратегия роста», «Уникальность», «Цель и ресурсы» \n\n3. Открываете выпавшую карту из этого раздела ' +
                         '\n\nКАЖДАЯ КАРТА - это задание, практика или подсказка, которые приблизят вас к цели!',
                         reply_markup=types.InlineKeyboardMarkup(row_width=True).add(types.InlineKeyboardButton(text='Играть', callback_data='play_happiness')))

    elif call.data == 'show_card':
        cursor.execute('SELECT position, moves, game FROM players WHERE user_id = ?', (user_id,))
        player = cursor.fetchone()
        if player:
            position, moves, game = player

            if game == 'happiness':

                if 1 <= position <= 3:
                    directory = 'materials/question_cards/urself_cards'
                elif 4 <= position <= 6:
                    directory = 'materials/question_cards/money'
                elif 7 <= position <= 9:
                    directory = 'materials/question_cards/family'
                elif 10 <= position <= 12:
                    directory = 'materials/question_cards/time'
                elif 13 <= position <= 15:
                    directory = 'materials/question_cards/aims'
                elif 16 <= position <= 18:
                    directory = 'materials/question_cards/carier'
                else:
                    directory = 'materials/question_cards/urself_cards'
                filename = random.choice(os.listdir(directory))
                with open(os.path.join(directory, filename), 'rb') as photo:
                    bot.send_photo(chat_id, photo)

            if game == 'millionaires':
                if position in [3, 7, 12, 17]:
                    directory = 'materials/question_cards_millionaires/money'
                elif position in [1, 5, 13, 18]:
                    directory = 'materials/question_cards_millionaires/plan'
                elif position in [2, 8, 15]:
                    directory = 'materials/question_cards_millionaires/resources'
                elif position in [4, 11, 14]:
                    directory = 'materials/question_cards_millionaires/strategy'
                elif position in [6, 10, 16]:
                    directory = 'materials/question_cards_millionaires/unique'
                elif position in [9]:
                    directory = 'materials/question_cards_millionaires/blank'
                else:
                    directory = 'materials/question_cards_millionaires/money'
                filename = random.choice(os.listdir(directory))
                with open(os.path.join(directory, filename), 'rb') as photo:
                    bot.send_photo(chat_id, photo)
            if moves >= 3:
                end_game(chat_id, user_id)
            else:
                markup = types.InlineKeyboardMarkup(row_width=True)
                markup.add(types.InlineKeyboardButton(text='Бросить кубик', callback_data='drop_dice'))
                bot.send_message(chat_id, text=f'Посмотрите на карту, ответьте на задание. Задумайтесь, почему именно этот раздел вам выпал, что он значит для вас? Запишите важные мысли, которые приходят в голову. И делайте следующий ход.',
                                 reply_markup=markup)
        # send_game_state(chat_id, user_id)


def start_game(user_id, game):
    cursor.execute('''
        INSERT OR REPLACE INTO players (user_id, position, moves, game)
        VALUES (?, 0, 0, ?)
    ''', (user_id, game))
    conn.commit()


def send_game_state(chat_id, user_id):
    cursor.execute('SELECT position, moves, game FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    if player:
        position, moves, game = player
        with open(f'materials/{game}_field_{position}.png', 'rb') as photo:
            bot.send_photo(chat_id, photo)


def roll_dice(chat_id, user_id):
    dice_msg = bot.send_dice(chat_id)
    time.sleep(4)
    dice_roll = dice_msg.dice.value
    cursor.execute('SELECT position, moves, game FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    if player:
        position, moves, game = player
        new_position = position + dice_roll
        new_moves = moves + 1
        cursor.execute('''
            UPDATE players
            SET position = ?, moves = ?
            WHERE user_id = ?
        ''', (new_position, new_moves, user_id))
        conn.commit()

        bot.send_message(chat_id,
                         text=f'Выпало число {dice_roll} ')

        send_game_state(chat_id, user_id)

        markup_show_card = types.InlineKeyboardMarkup(row_width=True)
        markup_show_card.add(types.InlineKeyboardButton(text='Показать карту', callback_data='show_card'))
        if game == 'happiness':

            if new_position in [1, 2, 3]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Вы сами"', reply_markup=markup_show_card)
            if new_position in [4, 5, 6]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Ресурсы и деньги"',
                                 reply_markup=markup_show_card)
            if new_position in [7, 8, 9]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Семья и окружение"',
                                 reply_markup=markup_show_card)
            if new_position in [10, 11, 12]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Свободное время"', reply_markup=markup_show_card)
            if new_position in [13, 14, 15]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Желания и цели"', reply_markup=markup_show_card)
            if new_position in [16, 17, 18]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Карьера и амбиции"',
                                 reply_markup=markup_show_card)
        else:
            if new_position in [3, 7, 12, 17]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Деньги"', reply_markup=markup_show_card)
            if new_position in [1, 5, 13, 18]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "План роста"',
                                 reply_markup=markup_show_card)
            if new_position in [2, 8, 15]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Цель и ресурсы"',
                                 reply_markup=markup_show_card)
            if new_position in [4, 11, 14]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Стратегия роста"', reply_markup=markup_show_card)
            if new_position in [6, 10, 16]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Уникальность"', reply_markup=markup_show_card)
            if new_position in [9]:
                bot.send_message(chat_id, text=f'Вам выпал раздел "Экстра"',
                                 reply_markup=markup_show_card)


def end_game(chat_id, user_id):
    markup_end = types.InlineKeyboardMarkup(row_width=True)
    markup_end.add(types.InlineKeyboardButton(text='(telegram) Записаться на полную версию игры', url='https://t.me/IrinaSem77'),
                   types.InlineKeyboardButton(text='(whatsapp) Записаться на полную версию игры',
                                              url='https://wa.me/79939142710'),
                   types.InlineKeyboardButton(text='Начать демо-игру заново', callback_data='back'))
    bot.send_message(chat_id, text='Вы прошли демо-версию игры! Надеюсь вам понравилось! \n\nВы также можете попробовать другую игру или сразу записаться на полную версию игры.', reply_markup=markup_end)
    cursor.execute('DELETE FROM players WHERE user_id = ?', (user_id,))
    conn.commit()


bot.infinity_polling()

import logging
import settings
import sqlite3
import time
from random import choice
from datetime import datetime
from sqlite3 import DatabaseError
from telegram.bot import Bot
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request
from telegram.ext import Updater, CommandHandler
from config import bot_say, chat_name, START, PHRASES


logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
         'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

print('bot has been started at ' + datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"))

conn = sqlite3.connect("mydatabase.db", check_same_thread = False)
cursor = conn.cursor()


class MQBot(Bot):
    def __init__(self, *args, is_queued_def=True, msg_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = msg_queue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super().send_message(*args, **kwargs)


def greet_user(update, context):
    text = 'Начинаем'
    update.message.reply_text(text)
    chat_id = str(update.effective_chat.id)
    sql_chat_id = chat_id.removeprefix('-')
    sql_query = f'create table if not exists chat_{sql_chat_id} (user text, count int, last_date text, chat_id int)'
    try:
        cursor.execute(sql_query)
        conn.commit()
        print(sql_query)
    except DatabaseError:
        update.message.reply_text('Exception creating table')

def add_user(update, context):
    text_from_tg = update.message.text
    new_user = text_from_tg.removeprefix('/add ')
    chat_id = str(update.effective_chat.id)
    sql_chat_id = chat_id.removeprefix('-')
    add_query = f"INSERT INTO chat_{sql_chat_id} (user, count, last_date, chat_id) VALUES ('{new_user}', null, null, {sql_chat_id})"
    try:
        cursor.execute(add_query)
        conn.commit()
        update.message.reply_text(f'Юзер {new_user} добавлен в базу')
        print(add_query)
    except DatabaseError:
        update.message.reply_text('Error add user')


def del_user(update, context):
    text_from_tg = update.message.text
    del_user = text_from_tg.removeprefix('/del ')
    chat_id = str(update.effective_chat.id)
    sql_chat_id = chat_id.removeprefix('-')
    del_query = f"DELETE FROM chat_{sql_chat_id} WHERE user = '{del_user}'"
    try:
        cursor.execute(del_query)
        conn.commit()
        update.message.reply_text(f'Юзер {del_user} удален из базы')
        print(del_query)
    except DatabaseError:
        update.message.reply_text('Error del user')



# Берет пользователя из базы и рандомит
def random_from_base(update, context):
    chat_id = str(update.effective_chat.id)
    sql_chat_id = chat_id.removeprefix('-')
    query_user = f"SELECT user from chat_{sql_chat_id} order by random() limit 1;"
    cursor.execute(query_user)
    users_frm_db = cursor.fetchall()
    subj = str(users_frm_db)
    rand_user = (''.join([c for c in subj if c not in settings.chars_to_remove]))
    return rand_user


def random_phrases(subject):
    in_db_num = int(subject)
    query_user = f"SELECT phrases from chat_phrases where count_num = {in_db_num} and chat_id = 0 order by random() limit 1;"
    cursor.execute(query_user)
    query = cursor.fetchall()
    subj = str(query)
    fetch_query = (''.join([c for c in subj if c not in settings.chars_to_remove]))
    return fetch_query

# Проверка даты последнего ролла
def check_date():
    query_date = f"SELECT last_date FROM users WHERE last_date = strftime('%d-%m-%Y', 'now') limit 1"
    cursor.execute(query_date)
    date_on_db = cursor.fetchall()
    subj_date = str(date_on_db)
    rand_date = (''.join([c for c in subj_date if c not in settings.chars_to_remove]))
    return(rand_date)



# Берет пользователя из функции выше и проверяет его на еблана дня
def roll(update,context):
    date = check_date()
    today = datetime.utcnow().strftime("%d-%m-%Y")
    if date == today:
        update.message.reply_text('Тебя учили читать, пёс? В чате СЕГОДНЯ уже проверяли.')
        time.sleep(2)
        update.message.reply_text('Перед тем как кликнуть - читай чат.')
        print('/roll')
    else:
        update.message.reply_text(random_phrases(1))
        time.sleep(2)
        update.message.reply_text(random_phrases(2))
        time.sleep(2)
        same = random_from_base()
        usr = f"'{str(same)}'"
        update.message.reply_text(f'Поздравляю тебя {same}')
        time.sleep(2)
        update.message.reply_text('Впрочем, никто и не удивлен.')
        update_query = "update users set count = count + 1, last_date = strftime('%d-%m-%Y','now') where user = " + usr
        cursor.execute(update_query)
        conn.commit()
        print('/roll')


# Прямой sql запрос в базу
def sql_query(update, context):
    user_id = update.effective_user.id
    text_from_tg = update.message.text
    new_text = text_from_tg.removeprefix('/sql ')
    try:
        if user_id == settings.ADMIN:
            cursor.execute(new_text)
            update.message.reply_text(cursor.fetchall())
            print('/sql')
        else:
            update.message.reply_text(f'Пошел нахуй со своим "{new_text}", самый умный тут?')
            print('/sql')
    except DatabaseError:
        update.message.reply_text('Exception')

# Выводит топ юзеров
def top(update, context):
    query_top = "SELECT user, count FROM users ORDER BY count DESC"
    cursor.execute(query_top)
    top_from_db = cursor.fetchall()
    print('/top')
    hey = 0
    total_string = ''
    for i in top_from_db:
        fio = i[0]
        num_of_wins = i[1]
        hey += 1
        total_string += ''.join(f'{hey}. {fio} - {num_of_wins} раз(а)\n')
    top_message = 'Итак, кто сколько раз "побеждал": \n' + total_string
    update.message.reply_text(top_message)

def new(update, context):
    firstname = update.effective_user.first_name
    lastname = update.effective_user.last_name
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    print(chat_id, username, firstname, lastname)


def main():
    request = Request(
        con_pool_size=8,
        proxy_url=PROXY['proxy_url'],
        urllib3_proxy_kwargs=PROXY['urllib3_proxy_kwargs']
    )
    bot = MQBot(settings.API_KEY, request=request)
    mybot = Updater(bot=bot, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('roll', roll))
    dp.add_handler(CommandHandler('sql', sql_query))
    dp.add_handler(CommandHandler('top', top))
    dp.add_handler(CommandHandler('chat_name', chat_name))
    dp.add_handler(CommandHandler('bot', bot_say))
    dp.add_handler(CommandHandler('new', new))
    dp.add_handler(CommandHandler('add', add_user))
    dp.add_handler(CommandHandler('del', del_user))


    logging.info('Бот Запустился' + datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"))
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()

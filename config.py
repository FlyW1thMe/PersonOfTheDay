import settings
import sqlite3


def bot_say(update, context):
    print('bot_say')
    user_id = update.effective_user.id
    if user_id == settings.ADMIN:
        text = update.message.text
        replace = text.removeprefix('/bot ')
        update.message.reply_text(f"Абсолютно с тобой согласен. Подтверждаю - {replace}")
    else:
        update.message.reply_text("А ты - пошел нахуй, пёс")


def b_day(update, context):
    pass



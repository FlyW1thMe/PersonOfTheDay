import settings

def chat_name(update, context):
    default_name_query = "SELECT title from chat_name where id = 1;"
    cursor.execute(default_name_query)
    default_name_output = cursor.fetchall()
    subj = str(default_name_output)
    default_name = (''.join([c for c in subj if c not in settings.chars_to_remove]))
    return default_name

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


START = ["Опять началось..", "Нууус, посмотрим-с", "Вуб-вуб, рандомирую и вычисляю",
         "Одному заняться нехуй, а все страдают", "Доброго денечка, уважаемые. Ну что, начнем?"
]


PHRASES = ["Обезьянам банан, а ты еблан", "Прошел день, прошло два, а тут все ебланы так же как и всегда",
           """Знаете я ещё ведущий ассессментов и могу за пол часа понять если у человека компетенции 
к занимаемым им должности или он просто еблан по знакомству! Так вот уверен из последнего, что с учетом вашего 
общения и того что мне известно о занимаемых вами должностях, скорее всего вы относитесь ко 2 -м!)""",
           "Если один спросит 'кто еблан по знакомству?', миллионы отзовутся:",
           "а кто это у нас такой маленький, а уже 'Еблан по знакомству?'",
           "У-у-у-у, сука! Ты победил, сейчас где-то плачет один 'ведущий ассессментов'",
           "Астрологи обьявили день 'Еблана по знакомству, поздравляю тебя'"
]

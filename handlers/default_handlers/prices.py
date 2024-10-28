from loader import bot
from keyboards.reply.create_markup import create_markup


@bot.message_handler(commands=['prices'])
def prices(message):
    msg = ('Психологическое консультирование — 60 минут / 4 000 рублей\n\n'
    'Психологическое консультирование в чате — 60 минут / 3 000 рублей\n\n'
    'Патопсихологическое обследование — 60 минут / 5 000 рублей\n\n'
    'Семейное консультирование — 90 минут / 7 000 рублей')
    buttons = [("Назад в меню ←←←", "back_to_the_menu")]
    markup = create_markup(buttons)
    bot.send_message(message.from_user.id, msg, reply_markup=markup)

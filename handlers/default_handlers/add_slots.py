from loader import bot
from states.overall import OverallState
from pg_maker import add_slots_in_db
from keyboards.reply.create_markup import create_markup
import re
from datetime import datetime


def is_valid_time(time_str):
    try:
        hour, minute = map(int, time_str.split(':'))
        return 0 <= hour < 24 and 0 <= minute < 60
    except ValueError:
        return False

def is_valid_date(date_str):
    date_str = date_str.strip()
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return parsed_date >= datetime.now().date()
    except ValueError:
        return False

@bot.message_handler(commands=['add_slots'])
def add_slots(message):
    bot.send_message(message.from_user.id, 'Введи дату в формате 2024-01-01 и время 15:30 ')
    bot.set_state(message.from_user.id, state=OverallState.add_slot)


@bot.message_handler(state=OverallState.add_slot)
def for_today(message):
    bot.set_state(message.from_user.id, state=OverallState.add_slot)
    buttons = [('Стоп', 'stop')]

    if message.text.lower() != 'стоп':
        all_slots = message.text.split('\n')
        day_from_msg = all_slots[0]
        if not is_valid_date(day_from_msg):
            bot.send_message(message.from_user.id, f"Дата {day_from_msg} кривая. Попробуй заново")
            return

        for time_slot in all_slots[1:]:
            if is_valid_time(time_slot):
                if not add_slots_in_db(day_from_msg, time_slot):
                    msg = f"{time_slot} уже есть в базе. Введи другое время"

                else:
                    msg = f"Слот {time_slot} добавлен. Чтобы остановиться, пиши 'стоп'"
            else:
                msg = f"Неправильное время в слоте {time_slot}"
            markup = create_markup(buttons)
            bot.send_message(message.from_user.id, msg, reply_markup=markup)
    else:
        bot.delete_state(message.from_user.id)
        bot.send_message(message.from_user.id, f"Все слоты записаны! ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("stop"))
def stop_adding_slots(call):
    bot.delete_state(call.from_user.id)
    buttons = [("Вернуться в меню ←←←  ", "back_to_the_menu")]
    markup = create_markup(buttons)
    bot.send_message(call.from_user.id, f"Все слоты записаны!", reply_markup=markup)

from babel.dates import format_date
from loader import bot
from states.overall import OverallState
from keyboards.reply.create_markup import create_markup
from pg_maker import show_free_slots, all_dates_for_buttons, slot_occupied_by


@bot.message_handler(commands=['all_occupied_slots'])
def all_occupied_slots(message):
    bot.delete_state(message.from_user.id)
    bot.set_state(message.from_user.id, state=OverallState.occupied_slot)

    buttons = []
    all_dates = all_dates_for_buttons(value=False)

    if all_dates:
        for date in all_dates:
            callback_data = f"occupied_day_{date[0]}"
            formated_date = format_date(date[0], format="d MMMM y", locale='ru')
            buttons.append((formated_date, callback_data))
        buttons.append(("⬇⬇ Назад в меню ⬇⬇", "back_to_the_menu"))
        markup = create_markup(buttons)

        try:
            bot.edit_message_text("Выберите день:", chat_id=message.message.chat.id,
                                  message_id=message.message.message_id, reply_markup=markup)
        except:
            bot.send_message(message.from_user.id, "Выберите день:", reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "Занятых слотов пока нет")


@bot.callback_query_handler(func=lambda call: call.data.startswith("occupied_day_"))
def chosen_day(call):
    data_parts = call.data.split('_')
    date = data_parts[2]
    buttons = []
    free_slots = show_free_slots(value=False, date=date)
    for date, time in free_slots:
        callback_data = f"occupied_slot_{date}_{time}"
        buttons.append((time, callback_data))

    buttons.append(('⬇ Назад ⬇', 'occupied_time_back'))
    markup = create_markup(buttons)
    if buttons:
        bot.edit_message_text("Выберите время: ", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)
    else:
        bot.send_message(call.from_user.id, "В этот день нет свободных слотов", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("occupied_slot_"))
def show_occupied_slot_callback(call):
    data_parts = call.data.split('_')
    date = data_parts[2]
    time = data_parts[3]
    username = slot_occupied_by(date, time)[0]
    buttons = (('⬇ Назад ⬇', 'occupied_time_back'),
               ("⬇⬇ Вернуться в меню ⬇⬇", "back_to_the_menu"))
    markup = create_markup(buttons)
    bot.edit_message_text(f"На это время записан {username}", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data == "occupied_time_back")
def back_to_the_day_occupied(call):
    all_occupied_slots(call)


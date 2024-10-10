from loader import bot
from states.overall import OverallState
from pg_maker import all_dates_for_buttons, delete_appointments_day, delete_appointments_slot, show_free_slots
from keyboards.reply.create_markup import create_markup
from babel.dates import format_date


@bot.message_handler(state=OverallState.delete_slot)
def for_delete(message):
    bot.delete_state(message.from_user.id)
    bot.set_state(message.from_user.id, state=OverallState.delete_slot)
    buttons = []
    all_dates = all_dates_for_buttons(value=True)

    for date in all_dates:
        callback_data = f"delete_day_{date[0]}"
        formated_date = format_date(date[0], format="d MMMM y", locale='ru')
        buttons.append((formated_date, callback_data))
    buttons.append(("Вернуться в меню ←←←", "back_to_the_menu"))
    markup = create_markup(buttons)

    if all_dates:
        try:
            bot.edit_message_text("Выберите день:", chat_id=message.message.chat.id,
                                  message_id=message.message.message_id, reply_markup=markup)
        except:
            bot.send_message(message.from_user.id, "Выберите день:", reply_markup=markup)
    else:
        buttons.insert(0, ('Добавить слоты', 'add_slots'))
        markup = create_markup(buttons)

        bot.edit_message_text("Нет дней со слотами", chat_id=message.message.chat.id,
                              message_id=message.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_day_"))
def delete_days(call):
    data_parts = call.data.split('_')
    date = data_parts[2]
    buttons = []

    free_slots = show_free_slots(value=True, date=date)
    for date, time in free_slots:
        callback_data = f"delete_slot_{date}_{time}"
        buttons.append((time, callback_data))
    buttons.append(('Удалить весь день', f'delete_all_day_{date}'))
    buttons.append(('Назад ←', 'back_to_delete'))
    buttons.append(("Вернуться в меню ←←←", "back_to_the_menu"))
    markup = create_markup(buttons)
    if buttons:
        bot.edit_message_text("Выберите время: ", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)
    else:
        bot.send_message(call.from_user.id, "В этот день нет свободных слотов", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_slot_"))
def delete_slots(call):
    data_parts = call.data.split('_')
    date = data_parts[2]
    time = data_parts[3]
    delete_appointments_slot(date, time)
    buttons = [("Удалить другой слот", "delete_slots"),
               ("Вернуться в меню ←←←", "back_to_the_menu")]
    markup = create_markup(buttons)
    bot.edit_message_text("Слот удален!", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_all_day_"))
def delete_all_day(call):
    data_parts = call.data.split('_')
    date = data_parts[3]
    delete_appointments_day(date)
    buttons = [("Удалить другой день", "delete_all_day"),
               ("Вернуться в меню ←←←", "back_to_the_menu")]
    markup = create_markup(buttons)
    bot.edit_message_text("Весь день удален!", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['back_to_delete'])
def back_to_the_day_delete(call):
    if call.data == 'back_to_delete':
        for_delete(call)

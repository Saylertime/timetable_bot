from loader import bot
from states.overall import OverallState
from keyboards.reply.create_markup import create_markup
from pg_maker import (show_free_slots, make_appointment, all_dates_for_buttons,
                      get_last_busy_appointment, has_name, add_users_name)
from babel.dates import format_date
from datetime import datetime


@bot.message_handler(commands=['see_slots'])
def see_slots(message):

    bot.delete_state(message.from_user.id)
    bot.set_state(message.from_user.id, state=OverallState.see_slot)

    buttons = []
    all_dates = all_dates_for_buttons(value=True)
    if all_dates:
        for date in all_dates:
            callback_data = f"day_{date[0]}"
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
        buttons.append(("⬇⬇ Назад в меню ⬇⬇", "back_to_the_menu"))
        markup = create_markup(buttons)
        msg = "Свободных слотов пока нет"
        try:
            bot.edit_message_text(msg, chat_id=message.message.chat.id,
                                      message_id=message.message.message_id, reply_markup=markup)
        except:
            bot.send_message(message.from_user.id, msg, reply_markup=markup)




@bot.callback_query_handler(func=lambda call: call.data.startswith("day_"))
def chosen_day(call):
    data_parts = call.data.split('_')
    date = data_parts[1]
    buttons = []
    free_slots = show_free_slots(value=True, date=date)
    for date, time in free_slots:
        callback_data = f"slot_{date}_{time}"
        buttons.append((time, callback_data))

    buttons.append(('⬇ Назад ⬇', 'time_back'))
    markup = create_markup(buttons)
    if buttons:
        bot.edit_message_text("Выберите время: ", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)
    else:
        bot.send_message(call.from_user.id, "В этот день нет свободных слотов", reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data.startswith("slot_"))
def chosen_time(call):

    last_appointment = get_last_busy_appointment(call.from_user.id)
    if last_appointment:
        date, time = last_appointment
        date = format_date(date, format="d MMMM y", locale='ru')
        time = time.strftime("%H:%M")
        buttons = [('Отменить запись',  'cancel_appointment'),
                   ('⬇ Назад к слотам ⬇', 'time_back')]
        markup = create_markup(buttons)
        bot.edit_message_text(f"У вас есть запись на {date} в {time}. Отменить ее?", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)
        return

    data_parts = call.data.split('_')
    date = data_parts[1]
    time = data_parts[2]
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    formated_date = format_date(date_obj, format="d MMMM", locale='ru')
    user_id = call.from_user.id
    try:
        make_appointment(user_id, date, time)
        button = [("⬇ Вернуться в меню ⬇", "back_to_the_menu")]
        markup = create_markup(button)

        if has_name(user_id):
            bot.edit_message_text(f"Вы записались на {date} в {time}!", chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, reply_markup=markup)

            # Сообщение себе
            bot.send_message("174795671", f"@{call.from_user.username} записался на {formated_date} в {time}",
                             reply_markup=markup)
        else:
            bot.set_state(call.from_user.id, OverallState.add_name)
            with bot.retrieve_data(call.from_user.id) as data:
                data['date'] = formated_date
                data['time'] = time
            bot.send_message(call.from_user.id, 'Пожалуйста, введите ваше имя и фамилию')

    except Exception as e:
        bot.send_message(call.from_user.id, f"Что-то пошло не так {e}  ")


@bot.message_handler(state=OverallState.add_name)
def add_name_in_db(message):
    try:
        add_users_name(message.from_user.id, message.text)
        bot.send_message(message.from_user.id, f'Спасибо, {message.text}! Вы успешно записались на прием')

        # Сообщение себе
        with bot.retrieve_data(message.from_user.id) as data:
            bot.send_message("174795671", f"{message.text} @{message.from_user.username} "
                                         f"записался на {data['date']} в {data['time']}")
    except:
        bot.send_message(message.from_user.id, f'Что-то пошло не так. Напишите Анне, '
                                               f'чтобы она записала вас вручную: @kafka0024')
    finally:
        bot.delete_state(message.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("time_back"))
def back_to_the_day(call):
    if call.data == 'time_back':
        see_slots(call)

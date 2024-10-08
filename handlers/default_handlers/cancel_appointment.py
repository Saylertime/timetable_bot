from loader import bot
from keyboards.reply.create_markup import create_markup
from pg_maker import my_appointment, cancel_appointment_from_bd
from babel.dates import format_date
from .see_slots import see_slots


@bot.message_handler(commands=['cancel_appointment'])
def cancel_appointment(message):

    bot.delete_state(message.from_user.id)
    if my_appointment(user_id=message.from_user.id):
        date, time = my_appointment(user_id=message.from_user.id)

        formated_date = format_date(date, format="d MMMM y", locale='ru')
        button = [('Отменить запись',  'cancel_appointment'),
                  ("⬇ Вернуться в меню ⬇", "back_to_the_menu")]
        markup = create_markup(button)

        try:
            bot.edit_message_text(f"Вы записаны на {formated_date}. Время: {time.strftime('%H:%M')}. "
                                               f"\nОтменить запись?", chat_id=message.message.chat.id,
                                  message_id=message.message.message_id, reply_markup=markup)
        except:
            bot.send_message(message.from_user.id, f"Вы записаны на {formated_date}. Время: {time.strftime('%H:%M')}. "
                                               f"\nОтменить запись?", reply_markup=markup)

    else:
        button = [('Посмотреть свободные слоты', 'see_slots')]
        markup = create_markup(button)
        bot.send_message(message.from_user.id, f"У вас пока нет записей", reply_markup=markup)




@bot.callback_query_handler(func=lambda call: call.data.startswith("see_slots"))
def see_slots_callback(call):
    if call.data == 'see_slots':
        see_slots(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_appointment"))
def cancel(call):
    cancel_appointment_from_bd(call.from_user.id)
    button = [('Посмотреть свободные слоты', 'see_slots')]
    markup = create_markup(button)
    bot.edit_message_text("Запись отменена! Хотите записаться на другое время?", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)
    # Сообщение себе
    bot.send_message("68086662", f"@{call.from_user.username} отменил запись")

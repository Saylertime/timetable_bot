from loader import bot
from keyboards.reply.create_markup import create_markup
from pg_maker import (add_user, my_appointment, is_notification_on,
                      change_notifications, all_users_with_notifications,
                      create_appointments_table, create_users, delete_table)
from .cancel_appointment import cancel_appointment
from .add_slots import add_slots
from .delete_slots import for_delete
from .all_occupied_slots import all_occupied_slots

@bot.message_handler(commands=['start'])
def start_message(message):
    create_appointments_table()
    create_users()

    bot.delete_state(message.from_user.id)
    user_id = message.from_user.id
    username = ""

    if message.from_user.username:
        username = "@" + message.from_user.username
    add_user(user_id, username)

    buttons = [('Посмотреть свободные слоты 🔎', 'see_slots')]
    if my_appointment(user_id=message.from_user.id):
        buttons.append((('Посмотреть/Отменить мою запись', 'my_appointment')))

    msg = f"{'Включить уведомления о новых слотах' if not is_notification_on(message.from_user.id) else 'Отключить уведомления'}"
    buttons.append((msg, 'add_notification'))

    # if message.from_user.username == 'saylertime':
    if message.from_user.id == 174795671:
        buttons.append(('Добавить слоты', 'add_slots'))
        buttons.append(('Удалить слоты', 'delete_slots'))
        buttons.append(('Отправить уведомление', 'send_notification'))
        buttons.append(('Все занятые слоты', 'all_occupied_slots'))

    markup = create_markup(buttons)
    try:
        lol = message.message.message_id

        bot.edit_message_text("Доброе пожаловать в Бот Психолог Анна Баранова ↓↓↓",
                              message.message.chat.id, message.message.message_id, reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Доброе пожаловать в Бот Психолог Анна Баранова ↓↓↓",
                         reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data in ['my_appointment', 'add_slots', 'delete_slots'])
def callback_query_start(call):
    if call.data == 'my_appointment':
        cancel_appointment(call)
    elif call.data == 'add_slots':
        add_slots(call)
    elif call.data == 'delete_slots':
        for_delete(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_the_menu"))
def back_to_the_menu_callback(call):
    start_message(call)


@bot.callback_query_handler(func=lambda call: call.data in ["add_notification",
                                                            "send_notification",
                                                            "all_occupied_slots"])
def add_notifications_callback(call):
    user_id = call.from_user.id
    value = False if is_notification_on(user_id) else True
    if call.data == 'add_notification':
        change_notifications(user_id, value)
        start_message(call)
    elif call.data == "send_notification":
        for user_id in all_users_with_notifications():
            bot.send_message(str(user_id), 'Появились новые слоты!')
        bot.send_message(call.from_user.id, 'Уведомление отправлено!')

    elif call.data == "all_occupied_slots":
        all_occupied_slots(call)


@bot.message_handler(state=None)
def bot_echo(message) -> None:

    if "УСТАНОВИТЬ" in message.text:
        create_users()
        create_appointments_table()
        bot.send_message(message.from_user.id, 'БД установлены')

    elif "СНЕСТИ" in message.text:
        delete_table()
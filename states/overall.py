from telebot.handler_backends import State, StatesGroup

class OverallState(StatesGroup):
    """ Класс со всеми необходимыми состояниями """

    add_slot = State()
    add_name = State()
    delete_slot = State()
    see_slot = State()
    occupied_slot = State()
    for_today = State()

from telebot import types


def create_markup(buttons):
    markup = types.InlineKeyboardMarkup()
    for item in buttons:
        if isinstance(item, tuple):
            text, callback_data = item
            markup.add(types.InlineKeyboardButton(text=text, callback_data=callback_data))
        elif isinstance(item, types.InlineKeyboardButton):
            markup.add(item)
        else:
            raise ValueError(f"Неизвестный тип кнопки: {item}")
    return markup


def create_markup_with_url(buttons):
    markup = types.InlineKeyboardMarkup()
    for text, url, callback_data in buttons:
        button = types.InlineKeyboardButton(text=text, url=url, callback_data=callback_data)
        markup.add(button)
    # for text, url in buttons:
    #     markup.add(types.InlineKeyboardButton(text=text, url=url))
    return markup

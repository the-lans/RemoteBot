from telebot import types

from backend_server.config import tgbot
from backend_server.func import group_elements


def bot_send_file(chat_id: int, filename: str):
    doc = open(filename, 'rb')
    msg = tgbot.send_document(chat_id, doc)
    doc.close()
    return msg


def make_menu_reply(
    prefix: str,
    groups: tuple,
    items: list,
    menu_index: int,
    text_back: str = '< Back',
    text_next: str = 'Next >',
    add_items: list = None,
):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(prefix + item) for item in items]
    button_back = types.KeyboardButton(text_back)
    button_next = types.KeyboardButton(text_next)
    menu = group_elements(buttons, groups, menu_index, button_back, button_next, add_items)
    if len(menu) > 0:
        for item in menu:
            markup.add(*item)
    else:
        markup = types.ReplyKeyboardRemove()
    return markup


def send_content(current_user, chat_id: int, output: str, srv_type: str):
    message_send, tmp_file = current_user.set_content(output, srv_type)
    if tmp_file:
        bot_send_file(chat_id, tmp_file)
        tgbot.send_message(chat_id, message_send + ' ...', reply_markup=current_user.markup)
    else:
        tgbot.send_message(chat_id, message_send, reply_markup=current_user.markup)

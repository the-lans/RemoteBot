from telebot import types
from backend_server.config import tgbot, main_conf
from backend_server.func import group_elements

menu_servers = 0


@tgbot.message_handler(commands=['start'])
def handle_start(message, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton('💡 ' + server.name) for server in main_conf['servers']]
    button_back = types.KeyboardButton('< Back')
    button_next = types.KeyboardButton('Next >')
    menu = group_elements(items, (2, 2), menu_servers, button_back, button_next)
    for item in menu:
        markup.add(*item)
    tgbot.send_message(message.chat.id, 'Select server', reply_markup=markup)

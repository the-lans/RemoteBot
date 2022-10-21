from telebot import types

from backend_server.config import tgbot, tgconf, main_conf
from backend_server.func import group_elements, break_into_blocks
from backend_server.func_bot import bot_send_file
from backend_server.user_settings import UserSettings

current_user = UserSettings()
def_commands = ['cd', 'lcd', 'pyenv', 'shell', 'cmd', 'get', 'put', 'local', 'sudo', 'bot']


def make_menu_server():
    prefix, groups = tgconf['menu_servers_prefix'], tgconf['menu_servers']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton(prefix + server['name']) for server in main_conf['servers']]
    button_back = types.KeyboardButton('< Back')
    button_next = types.KeyboardButton('Next >')
    menu = group_elements(items, groups, current_user.menu_servers, button_back, button_next)
    for item in menu:
        markup.add(*item)
    return markup


def command_select_server(chat_id: int, message_text: str):
    prefix, groups = tgconf['menu_servers_prefix'], tgconf['menu_servers']
    if message_text in ['< Back', 'Next >']:
        menu_servers_funcs = {'< Back': current_user.menu_servers_back, 'Next >': current_user.menu_servers_next}
        menu_servers_funcs[message_text](groups)
        idx0 = current_user.menu_servers + 1
        idx1 = min(current_user.menu_servers + groups[0] * groups[1], len(main_conf['servers']))
        tgbot.send_message(chat_id, f'{message_text}  {idx0}-{idx1}', reply_markup=make_menu_server())
    else:
        local_name = prefix + 'local'
        items = [prefix + server['name'] for server in main_conf['servers']]
        local_conf = main_conf['servers'][items.index(local_name)]
        current_user.set_local(local_conf)
        server_conf = local_conf if message_text == local_name else main_conf['servers'][items.index(message_text)]
        current_user.connect(server_conf)
        markup = types.ReplyKeyboardRemove()
        if message_text == local_name:
            message_send = f"Connection established: local"
        else:
            message_send = f"Connection established: {server_conf['user']}@{server_conf['ip']}:{server_conf['port']}"
        tgbot.send_message(chat_id, message_send, reply_markup=markup)


def command_work_session(chat_id: int, message_text: str):
    message_lst = break_into_blocks(message_text, def_commands)
    for message_item in message_lst:
        output, srv_type = current_user.con_send(chat_id, message_item)
        if output:
            markup = types.ReplyKeyboardRemove()
            message_send, tmp_file = current_user.set_content(output, srv_type)
            if tmp_file:
                msg = bot_send_file(chat_id, tmp_file)
                # tgbot.send_message(chat_id, message_send, reply_markup=markup, reply_to_message_id=msg.message_id)
                tgbot.send_message(chat_id, message_send + ' ...', reply_markup=markup)
            else:
                tgbot.send_message(chat_id, message_send, reply_markup=markup)


def command_bot_edit(chat_id: int, message_text: str):
    lines = message_text.split('\n')
    if lines[-1] in [':q', '\\q']:
        text = '\n'.join(lines[:-1]) + '\n'
        current_user.text_edit = current_user.text_edit + '\n' + text if current_user.text_edit else text
        current_user.stage = 'work_session'
        tgbot.send_message(chat_id, 'End text edit.')
    else:
        current_user.text_edit = (
            current_user.text_edit + '\n' + message_text if current_user.text_edit else message_text
        )


handle_text_funcs = {
    'select_server': command_select_server,
    'work_session': command_work_session,
    'bot_edit': command_bot_edit,
}


@tgbot.message_handler(commands=['start'])
def handle_start(message, res=False):
    chat_id = message.chat.id
    tgbot.send_message(chat_id, 'Select server', reply_markup=make_menu_server())
    current_user.stage = 'select_server'


@tgbot.message_handler(commands=['unconnect'])
def handle_start(message, res=False):
    chat_id = message.chat.id
    if current_user.stage == 'work_session':
        current_user.unconnect()
        tgbot.send_message(chat_id, 'Select server', reply_markup=make_menu_server())
        current_user.stage = 'select_server'


@tgbot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    message_text = message.text.strip()
    handle_text_funcs[current_user.stage](chat_id, message_text)

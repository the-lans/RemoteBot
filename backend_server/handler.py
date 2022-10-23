from telebot import types

from backend_server.config import tgbot, tgconf, main_conf
from backend_server.func import group_elements, break_into_blocks, str_del_startswith
from backend_server.func_bot import bot_send_file
from backend_server.user_settings import UserSettings

current_user = UserSettings()
def_commands = ['cd', 'lcd', 'pyenv', 'shell', 'cmd', 'get', 'put', 'local', 'sudo', 'bot']


def make_menu_reply(prefix, groups, items, menu_index, text_back='< Back', text_next='Next >', add_items=None):
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


def make_menu_com_history():
    return make_menu_reply(
        tgconf['menu_commands_prefix'],
        tgconf['menu_commands'],
        current_user.commands_history,
        current_user.menu_com_history,
        'bot back',
        'bot next',
    )


def make_menu_server():
    items = [server['name'] for server in main_conf['servers']]
    return make_menu_reply(tgconf['menu_servers_prefix'], tgconf['menu_servers'], items, current_user.menu_servers)


def command_select_server(chat_id: int, message_text: str):
    prefix, groups = tgconf['menu_servers_prefix'], tgconf['menu_servers']
    if message_text in ['< Back', 'Next >']:
        menu_servers_funcs = {'< Back': current_user.menu_servers_back, 'Next >': current_user.menu_servers_next}
        menu_servers_funcs[message_text](groups)
        tgbot.send_message(chat_id, f'{message_text}  {current_user.menu_servers + 1}', reply_markup=make_menu_server())
    else:
        local_name = prefix + 'local'
        items = [prefix + server['name'] for server in main_conf['servers']]
        local_conf = main_conf['servers'][items.index(local_name)]
        current_user.set_local(local_conf)
        server_conf = local_conf if message_text == local_name else main_conf['servers'][items.index(message_text)]
        current_user.connect(server_conf)
        markup = make_menu_com_history() if tgconf['menu_commands_exists'] else types.ReplyKeyboardRemove()
        if message_text == local_name:
            message_send = f"Connection established: local"
        else:
            message_send = f"Connection established: {server_conf['user']}@{server_conf['ip']}:{server_conf['port']}"
        tgbot.send_message(chat_id, message_send, reply_markup=markup)


def command_work_session(chat_id: int, message_text: str):
    message_text = str_del_startswith(message_text, tgconf['menu_commands_prefix'])
    current_user.add_command_history(message_text)
    current_user.add_srv_history(message_text)
    message_lst = break_into_blocks(message_text, def_commands)
    for message_item in message_lst:
        output, srv_type = current_user.con_send(chat_id, message_item)
        if output:
            markup = make_menu_com_history() if tgconf['menu_commands_exists'] else types.ReplyKeyboardRemove()
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

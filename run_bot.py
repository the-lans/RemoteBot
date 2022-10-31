from backend_server.config import tgbot


@tgbot.message_handler(commands=['start'])
def handle_start(message, res=False):
    chat_id = message.chat.id
    tgbot.send_message(chat_id, 'Hello, world!')


if __name__ == '__main__':
    tgbot.infinity_polling(timeout=70, long_polling_timeout=120)

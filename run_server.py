from backend_server.config import tgbot


if __name__ == '__main__':
    tgbot.infinity_polling(timeout=70, long_polling_timeout=120)

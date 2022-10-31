import sys

from backend_server.config import tgbot
from backend_server.handler import handle_start, handle_finish, handle_text
from backend_server.schedule import run_continuously


if __name__ == '__main__':
    stop_run_continuously = run_continuously(5)
    try:
        print('Server started')
        tgbot.infinity_polling(timeout=70, long_polling_timeout=120)
    except (KeyboardInterrupt, SystemExit):
        stop_run_continuously.set()
        print('Server finished')
        sys.exit(0)

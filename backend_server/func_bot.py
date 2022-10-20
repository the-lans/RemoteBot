from backend_server.config import tgbot


def bot_send_file(chat_id: int, filename: str):
    doc = open(filename, 'rb')
    msg = tgbot.send_document(chat_id, doc)
    doc.close()
    return msg

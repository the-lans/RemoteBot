from backend_server.config import tgconf, main_conf, DATA_DIR
from backend_server.file_change_tracking import FileChangeTracking
from backend_server.func_bot import send_message_file


def new_tracking(root_connect):
    tracking = {}
    for server_conf in main_conf['servers']:
        tracking_conf = server_conf.get('tracking', [])
        if tracking_conf:
            root_connect.connect(server_conf)
            if root_connect.test_connection():
                tracking_list = []
                for filename in tracking_conf:
                    tracking_file = FileChangeTracking(
                        filename,
                        DATA_DIR,
                        tgconf['threshold1'],
                        tgconf['threshold2'],
                        root_connect.is_srv,
                        root_connect,
                    )
                    tracking_list.append(tracking_file)
                root_connect.unconnect()
                tracking[server_conf['name']] = tracking_list
            else:
                print(f"Server not connected: {server_conf['name']}")
    return tracking


def file_tracking(tracking_files, current_user, root_connect):
    """Tasks: check file tracking"""
    for server_conf in main_conf['servers']:
        tracking_conf = tracking_files.get(server_conf['name'])
        if tracking_conf:
            root_connect.connect(server_conf)
            if root_connect.test_connection():
                for tracking_file in tracking_conf:
                    if tracking_file.check_try():
                        content, tmp_file = tracking_file.get_content()
                        if content and current_user.chat_id:
                            content = f"{server_conf['name']}\n{tracking_file.path}\n{content}"
                            send_message_file(current_user, current_user.chat_id, content, tmp_file)
                root_connect.unconnect()
            else:
                print(f"Server not connected: {server_conf['name']}")

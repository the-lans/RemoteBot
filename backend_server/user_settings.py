from time import sleep
from os.path import join, basename

from backend_server.config import tgconf, main_conf, DATA_DIR
from backend_server.func import cmd_parser, path_relative, path_join, dict_to_str, file_write, str_to_bool
from backend_server.func_bot import bot_send_file, send_content
from backend_server.file_change_tracking import FileChangeTracking
from backend_server import tracking_files, root_connect, RemoteConnect, file_tracking


class UserSettings(RemoteConnect):
    def __init__(self):
        super().__init__()
        self.menu_servers = 0
        self.menu_com_history = 0
        self.stage = None
        self.asynchronous = False
        self.tmp_file = FileChangeTracking(tmp_file=DATA_DIR)
        self.tmp_file.threshold1 = tgconf['threshold1']
        self.tmp_file.threshold2 = tgconf['threshold2']
        self.text_edit = ''
        self.commands_history = []
        self.srv_history = []
        self.tasks_process = []
        self.markup = None
        self.chat_id = None

    def connect(self, server_conf: dict):
        super().connect(server_conf)
        self.srv_history = []
        self.stage = 'work_session'

    def unconnect(self):
        super().unconnect()
        self.srv_history = []
        self.stage = 'select_server'

    def menu_servers_next(self, shape: tuple):
        self.menu_servers = min(self.menu_servers + 1, self.menu_pages_servers(shape) + 1)

    def menu_servers_back(self, shape: tuple):
        self.menu_servers = max(0, self.menu_servers - 1)

    @staticmethod
    def menu_pages_servers(shape: tuple):
        return (len(main_conf['servers']) - 1) // (shape[0] * shape[1]) + 1

    def menu_com_history_next(self, shape: tuple):
        self.menu_com_history = min(self.menu_com_history + 1, self.menu_pages_com_history(shape) - 1)

    def menu_com_history_back(self, shape: tuple):
        self.menu_com_history = max(0, self.menu_com_history - 1)

    def menu_pages_com_history(self, shape: tuple):
        return (len(self.commands_history) - 1) // (shape[0] * shape[1]) + 1

    def con_send(self, text: str) -> (str, str):
        # Check text
        text = text.strip()
        if not text:
            return None, None

        # Local server
        text_cmd = text.split(' ')
        first_cmd = text_cmd[0]
        if not self.is_srv and first_cmd.lower() not in ['cmd', 'get', 'put', 'local', 'sudo', 'bot']:
            text = f'local {text}'
            text_cmd.insert(0, 'local')

        # First command -> Set attr or (main_cmd, shell_com)
        first_cmd, args, kwargs = cmd_parser(text)
        first_cmd = first_cmd.lower()
        main_cmd = 'run'
        if first_cmd in ['cd', 'lcd']:
            return self.set_attr_cd(first_cmd, text_cmd[-1]), None
        elif first_cmd in ['pyenv', 'shell']:
            return self.set_attr_cmd(first_cmd, ' '.join(text_cmd[1:])), None
        elif first_cmd in ['cmd', 'get', 'put', 'local', 'sudo', 'bot']:
            main_cmd = first_cmd[:]
            shell_com = ' '.join(text_cmd[1:])
            first_cmd = text_cmd[1].lower()
        else:
            shell_com = text

        # Args & kwargs
        if main_cmd in ['local']:
            if self.shell:
                kwargs['shell'] = self.shell
        elif main_cmd in ['get', 'put']:
            pref0 = 'l' if main_cmd == 'put' else ''
            pref1 = 'l' if main_cmd == 'get' else ''
            if len(args) > 0 and path_relative(args[0]):
                args[0] = path_join(getattr(self, pref0 + 'cd'), args[0], getattr(self, pref0 + 'sys'))
            if len(args) > 1 and path_relative(args[1]):
                args[1] = path_join(getattr(self, pref1 + 'cd'), args[1], getattr(self, pref1 + 'sys'))

        # Commands fab
        second_cmd = args[0] if len(args) > 0 else None
        if first_cmd == 'fab' and second_cmd in main_conf['commands_fab_ext']:
            shell_com = f"{shell_com} --pathcd '{self.cd}' --pyenv '{self.pyenv}'"

        # Running
        try:
            message_success = 'Operation completed!'
            srv_type = self.get_type_server(main_cmd)
            if main_cmd in ['run', 'cmd', 'sudo']:
                cmd_func = {'run': self.con.run, 'cmd': self.con.run, 'sudo': self.con.sudo}
                with self.con.cd(self.cd):
                    com = f"{self.pyenv}\n{shell_com}" if first_cmd in main_conf['commands_pyenv'] else shell_com
                    result = cmd_func[main_cmd](com, hide=True, warn=True, asynchronous=self.asynchronous)
                    if self.asynchronous:
                        self.tasks_process.append(result)
                        message_success = f'{message_success} Async enabled.'
                    return self.format_out(result, message_success), srv_type
            elif main_cmd in ['get', 'put']:
                cmd_func = {'get': self.con.get, 'put': self.con.put}
                result = cmd_func[main_cmd](*args, **kwargs)
                return self.format_out(result, message_success), srv_type
            elif main_cmd in ['local']:
                com = (
                    f"cd {self.cd}\n{self.pyenv}\n{shell_com}"
                    if first_cmd in main_conf['commands_pyenv']
                    else f"cd {self.cd}\n{shell_com}"
                )
                result = self.con.local(com, shell=kwargs.get('shell'))
                return self.format_out(result, message_success), srv_type
            elif main_cmd in ['bot']:
                if len(args) > 0:
                    del args[0]
                result = self.command_bot(first_cmd, message_success, *args, **kwargs)
                return result, srv_type
        except Exception as err:
            return str(err), None
        return 'Unknown error', None

    def set_content(self, content: str, srv_type: str) -> (str, str):
        message, filename = self.tmp_file.set_content(content)
        if srv_type == 'local':
            if self.lencode and self.ldecode:
                message = message.encode(self.lencode).decode(self.ldecode).replace(u'\xa0', u' ')
        elif srv_type == 'server':
            if self.encode and self.decode:
                message = message.encode(self.encode).decode(self.decode).replace(u'\xa0', u' ')
        return message, filename

    def get_settings(self) -> dict:
        data = {
            name: getattr(self, name)
            for name in ['cd', 'lcd', 'pyenv', 'shell', 'encode', 'decode', 'lencode', 'ldecode', 'sys', 'lsys']
            if getattr(self, name)
        }
        data['tmp_file'] = self.tmp_file.tmp_file
        return data

    def command_bot(self, first_cmd: str, message_success: str, *args, **kwargs) -> str:
        output = message_success
        data = {}
        out_func = {'settings': dict_to_str, 'get': dict_to_str}

        if first_cmd == 'settings':
            data = self.get_settings()
        elif first_cmd == 'get':
            data = {name: getattr(self, name) for name in args}
        elif first_cmd == 'send':
            is_local = 'l' in kwargs and kwargs['l']
            args = self.get_absolute_path(args, is_local)
            filename = basename(args[0])
            if is_local:
                bot_send_file(self.chat_id, args[0])
            else:
                self.con.get(args[0], join(DATA_DIR, filename))
                bot_send_file(self.chat_id, join(DATA_DIR, filename))
        elif first_cmd == 'edit':
            self.text_edit = ''
            self.stage = 'bot_edit'
            output = 'Begin text edit.'
        elif first_cmd == 'push':
            is_local = 'l' in kwargs and kwargs['l']
            is_append = 'a' in kwargs and kwargs['a']
            args = self.get_absolute_path(args, is_local)
            filename = basename(args[0])
            if is_local:
                self.save_text_edit(args[0], is_append)
            else:
                self.save_text_edit(join(DATA_DIR, filename), is_append)
                self.con.put(join(DATA_DIR, filename), args[0])
        elif first_cmd in ['next', 'back']:
            groups = tgconf['menu_commands']
            if first_cmd == 'next':
                self.menu_com_history_next(groups)
            else:
                self.menu_com_history_back(groups)
            output = f'{first_cmd}: {self.menu_com_history + 1}'
        elif first_cmd == 'history':
            data = {'srv': self.srv_history, 'commands': self.commands_history}
            output = 'Commands history:\n' + '\n'.join(data[args[0]])
        elif first_cmd == 'fabfile':
            args = (
                path_join(self.lcd, self.current_server['fabfile'], self.lsys),
                path_join(self.cd, 'fabfile.py', self.sys),
            )
            self.con.put(*args, **kwargs)
        elif first_cmd == 'async':
            self.asynchronous = str_to_bool(args[0]) if len(args) > 0 else not self.asynchronous
        elif first_cmd == 'join':
            while self.tasks_process:
                task = self.tasks_process.pop()
                sout = self.format_out(task.join(), message_success)
                send_content(self, self.chat_id, sout, self.get_type_server('run'))
                sleep(1)
            output = 'End of job queue.'
        elif first_cmd == 'task':
            second_cmd = args[0]
            if second_cmd == 'tracking':
                file_tracking(tracking_files, self, root_connect)
        elif first_cmd == 'tasks':
            second_cmd = args[0]
            if second_cmd == 'on':
                main_conf['tasks'] = True
            elif second_cmd == 'off':
                main_conf['tasks'] = False
        else:
            output = None

        if first_cmd in out_func:
            output = out_func[first_cmd](data)
        return output

    def save_text_edit(self, filename: str, is_append=False):
        file_write(filename, self.text_edit, is_append)

    def add_command_history(self, message_text: str):
        for item in message_text.split('\n'):
            if item.lower() not in ['bot next', 'bot back']:
                self.commands_history.insert(0, item)
        self.commands_history = list(dict.fromkeys(self.commands_history))
        if len(self.commands_history) > main_conf['commands_history']:
            self.commands_history = self.commands_history[: main_conf['commands_history']]

    def add_srv_history(self, message_text: str):
        for item in message_text.split('\n'):
            if item.lower() not in ['bot next', 'bot back']:
                self.srv_history.append(item)

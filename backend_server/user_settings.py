from os.path import join, basename
from fabric import Connection
from fabric.runners import Result

from backend_server.config import tgconf, main_conf, DATA_DIR
from backend_server.func import cmd_parser, path_relative, path_join, dict_to_str, file_write
from backend_server.func_bot import bot_send_file
from backend_server.file_change_tracking import FileChangeTracking


class UserSettings:
    def __init__(self):
        self.menu_servers = 0
        self.menu_com_history = 0
        self.stage = None
        self.con = None
        self.is_srv = False
        self.cd = None
        self.lcd = DATA_DIR
        self.pyenv = None
        self.shell = None
        self.encode = None
        self.decode = None
        self.lencode = None
        self.ldecode = None
        self.sys = None
        self.lsys = None
        self.tmp_file = FileChangeTracking(tmp_file=DATA_DIR)
        self.tmp_file.threshold1 = tgconf['threshold1']
        self.tmp_file.threshold2 = tgconf['threshold2']
        self.text_edit = ''
        self.commands_history = []
        self.srv_history = []
        self.current_server = {}
        self.local_server = {}

    def connect(self, server_conf: dict):
        self.is_srv = False
        if 'ip' in server_conf:
            if server_conf['ip'] in ['127.0.0.1']:
                self.con = Connection(server_conf['ip'])
            else:
                self.con = Connection(
                    server_conf['ip'], user=server_conf.get('user', 'root'), port=server_conf.get('port', 22)
                )
                self.is_srv = True
        self.cd = server_conf.get('cd', None)
        self.lcd = server_conf.get('lcd', self.lcd)
        self.pyenv = server_conf.get('pyenv', None)
        self.shell = server_conf.get('shell', None)
        self.encode = server_conf.get('encode', None)
        self.decode = server_conf.get('decode', None)
        self.sys = server_conf.get('sys', None)
        self.srv_history = []
        self.current_server = server_conf
        self.stage = 'work_session'

    def set_local(self, local_conf: dict):
        self.lencode = local_conf.get('encode', None)
        self.ldecode = local_conf.get('decode', None)
        self.lsys = local_conf.get('sys', None)
        self.local_server = local_conf

    def unconnect(self):
        if self.con:
            self.con.close()
        self.con = None
        self.is_srv = False
        self.srv_history = []
        self.current_server = {}
        self.local_server = {}
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

    def set_attr_cmd(self, name: str, value: str) -> str:
        setattr(self, name, value)
        return f'{name}> {value}'

    def set_attr_cd(self, name: str, value: str) -> str:
        if path_relative(value):
            value = path_join(getattr(self, name), value, getattr(self, 'lsys' if name[0] == 'l' else 'sys'))
        return self.set_attr_cmd(name, value)

    @staticmethod
    def format_out(res: Result, mes_default: str = None) -> str:
        stdout = getattr(res, 'stdout', '').strip()
        stderr = getattr(res, 'stderr', '').strip()
        res = f'{stdout}\n{stderr}'.strip()
        return res if res else (mes_default if mes_default else '')

    def get_type_server(self, main_cmd: str) -> str:
        return 'local' if main_cmd == 'local' or not self.is_srv else 'server'

    def con_send(self, chat_id: int, text: str) -> (str, str):
        text = text.strip()
        if not text:
            return None, None

        text_cmd = text.split(' ')
        if not self.is_srv and text_cmd[0].lower() not in ['cmd', 'get', 'put', 'local', 'sudo', 'bot']:
            text = f'local {text}'
            text_cmd.insert(0, 'local')

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

        try:
            message_success = 'Operation completed!'
            srv_type = self.get_type_server(main_cmd)
            if main_cmd in ['run', 'cmd', 'sudo']:
                cmd_func = {'run': self.con.run, 'cmd': self.con.run, 'sudo': self.con.sudo}
                with self.con.cd(self.cd):
                    com = f'{self.pyenv}\n{shell_com}' if first_cmd in main_conf['commands_pyenv'] else shell_com
                    result = cmd_func[main_cmd](com, hide=True, asynchronous=False)
                    return self.format_out(result, message_success), srv_type
            elif main_cmd in ['get', 'put', 'local']:
                cmd_func = {'get': self.con.get, 'put': self.con.put, 'local': self.con.local}
                result = cmd_func[main_cmd](*args, **kwargs)
                return self.format_out(result, message_success), srv_type
            elif main_cmd in ['bot']:
                if len(args) > 0:
                    del args[0]
                result = self.command_bot(chat_id, first_cmd, message_success, *args, **kwargs)
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

    def get_absolute_path(self, args: tuple, is_local: bool = False):
        if self.is_srv and not is_local:
            return [path_join(self.cd, item, self.sys) if path_relative(item) else item for item in args]
        else:
            return [path_join(self.lcd, item, self.lsys) if path_relative(item) else item for item in args]

    def command_bot(self, chat_id: int, first_cmd: str, message_success: str, *args, **kwargs) -> str:
        output = None
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
                bot_send_file(chat_id, args[0])
            else:
                self.con.get(args[0], join(DATA_DIR, filename))
                bot_send_file(chat_id, join(DATA_DIR, filename))
            output = message_success
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
            output = message_success
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
            output = message_success

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

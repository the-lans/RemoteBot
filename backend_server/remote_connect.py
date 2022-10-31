from fabric import Connection
from fabric.runners import Result

from backend_server.config import main_conf, DATA_DIR
from backend_server.func import path_relative, path_join


class RemoteConnect:
    def __init__(self):
        self.con = None
        self.is_srv = False
        self.cd = None
        self.lcd = DATA_DIR
        self.shell = None
        self.pyenv = None
        self.sys = None
        self.lsys = None
        self.encode = None
        self.decode = None
        self.lencode = None
        self.ldecode = None
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
        self.shell = server_conf.get('shell', None)
        self.pyenv = server_conf.get('pyenv', None)
        self.sys = server_conf.get('sys', None)
        self.encode = server_conf.get('encode', None)
        self.decode = server_conf.get('decode', None)
        self.current_server = server_conf

    def set_local(self, local_conf: dict):
        self.lencode = local_conf.get('encode', None)
        self.ldecode = local_conf.get('decode', None)
        self.lsys = local_conf.get('sys', None)
        self.local_server = local_conf

    def test_connection(self):
        if self.get_type_server('run') == 'local':
            return True
        else:
            try:
                self.con.run('dir' if self.sys == 'win' else 'ls')
                return True
            except Exception:
                return False

    def unconnect(self):
        if self.con:
            self.con.close()
        self.con = None
        self.is_srv = False
        self.current_server = {}
        self.local_server = {}

    @staticmethod
    def format_out(res: Result, mes_default: str = None) -> str:
        stdout = getattr(res, 'stdout', '').strip()
        stderr = getattr(res, 'stderr', '').strip()
        res = f'{stdout}\n{stderr}'.strip()
        return res if res else (mes_default if mes_default else '')

    def get_type_server(self, main_cmd: str) -> str:
        return 'local' if main_cmd == 'local' or not self.is_srv else 'server'

    def get_absolute_path(self, args: tuple, is_local: bool = False):
        if self.is_srv and not is_local:
            return [path_join(self.cd, item, self.sys) if path_relative(item) else item for item in args]
        else:
            return [path_join(self.lcd, item, self.lsys) if path_relative(item) else item for item in args]

    def set_attr_cmd(self, name: str, value: str) -> str:
        setattr(self, name, value)
        return f'{name}> {value}'

    def set_attr_cd(self, name: str, value: str) -> str:
        if path_relative(value):
            value = path_join(getattr(self, name), value, getattr(self, 'lsys' if name[0] == 'l' else 'sys'))
        return self.set_attr_cmd(name, value)

    def run_fab(self, shell_com: str):
        with self.con.cd(self.cd):
            com = f"{self.pyenv}\nfab {shell_com}" if 'fab' in main_conf['commands_pyenv'] else shell_com
            result = self.con.run(com, hide=True, warn=True)
        return self.format_out(result)

    def func_path(self, fab: str, path: str) -> str:
        return self.run_fab(f"{fab} --path {path}")

    def read_path(self, path: str, pointer: int = 0):
        return self.run_fab(f"readfile --path {path} --pointer {pointer}")

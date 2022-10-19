from os import makedirs
from os.path import abspath, join, exists
import yaml
import configparser
from telebot import TeleBot

PATH_TGCONFIG = 'tgsettings.ini'
PATH_MAIN_CONF = 'conf.yaml'
DEFAULT_WORK_DIR = abspath(join(abspath(__file__), '../..'))
DATA_DIR = join(DEFAULT_WORK_DIR, 'data')


def read_tgconfig(filename: str) -> dict:
    """
    Reading telegram configuration.
    @param filename: File name.
    @return: (dict) - Сonfiguration.
    """
    cfg = configparser.ConfigParser(allow_no_value=True)
    cfg.read(filename, encoding='utf-8')
    conf = {
        'log_dir': cfg.get('DEFAULT', 'log_dir'),
        'log_file_name': cfg.get('DEFAULT', 'log_file_name'),
        'tglog': cfg.getboolean('DEFAULT', 'tglog'),
        'name_group': cfg.get('DEFAULT', 'name_group'),
        'token': cfg.get('DEFAULT', 'token'),
        'count_exeption': cfg.getint('DEFAULT', 'count_exeption'),
        'sleep_exeption': cfg.getfloat('DEFAULT', 'sleep_exeption'),
        'data_path': cfg.get('DEFAULT', 'data_path'),
        'threshold1': cfg.getint('DEFAULT', 'threshold1'),
        'threshold2': cfg.getint('DEFAULT', 'threshold2'),
    }
    return conf


def read_main_config(filename: str) -> dict:
    """
    Reading main configuration.
    @param filename: File name.
    @return: (dict) - Сonfiguration.
    """
    res = {}
    try:
        settings = yaml.safe_load(open(join(DEFAULT_WORK_DIR, filename)))
    except FileNotFoundError:
        settings = {}
    res['servers'] = settings.get('servers', [])
    return res


tgconf = read_tgconfig(PATH_TGCONFIG)
tgconf['threshold1'] = tgconf.get('threshold1', 50)
tgconf['threshold2'] = tgconf.get('threshold2', 70)
tgconf['data_path'] = tgconf.get('data_path', './data')

main_conf = read_main_config(PATH_MAIN_CONF)
for server_conf in main_conf['servers']:
    server_conf['ip'] = server_conf.get('ip', '127.0.0.1')
    server_conf['user'] = server_conf.get('user', 'root')
    server_conf['port'] = server_conf.get('port', 22)

for i in [DATA_DIR, tgconf['log_dir']]:
    if not exists(i):
        makedirs(i, exist_ok=True)

tgbot = TeleBot(tgconf['token']) if tgconf['tglog'] else None  # Telegram

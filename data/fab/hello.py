from time import sleep


def file_write(name, data, is_append=False):
    with open(name, 'at' if is_append else 'wt') as fp:
        fp.write(data)


def log_write(text, is_append=False):
    print(text)
    file_write('hello.txt', text + '\n', is_append=is_append)


if __name__ == '__main__':
    log_write('start', False)
    for ind in range(10):
        log_write(f'index={ind+1}', True)
        sleep(1)
    log_write('finish', True)

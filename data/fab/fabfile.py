from fabric import task
import os


def process_command(com, path=None, pyenv=None):
    command = ""
    if path:
        command += f"cd {path} && "
    if pyenv:
        command += f"{pyenv} && "
    command += com
    return command


@task
def hello(c, name='world'):
    print('Hello %s!' % name)
    c.run('uname -a')


@task
def sql(c, com, name='my_db'):
    c.run(f'export PATH=/usr/pgsql-10/bin:$PATH && psql -U postgres -d {name} -c "{com}"')


@task
def screen(c, com, pathcd='', pyenv=''):
    command = process_command(com, pathcd, pyenv)
    print(command)
    c.run(f'screen -d -m bash -c "{command}"', hide=True, pty=False)
    print("Operation 'screen' completed!")


@task
def getmtime(c, path):
    print(os.path.getmtime(path))


@task
def getsize(c, path):
    print(os.path.getsize(path))


@task
def readfile(c, path, pointer):
    with open(path, 'rt') as fp:
        fp.seek(int(pointer), 0)
        content = fp.read()
    print(content)

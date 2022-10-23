from fabric import task

# env.python = '/var/venv3.8/bin/python'


@task
def hello(c, name='world'):
    print('Hello %s!' % name)
    c.run('uname -a')


@task
def sql(c, com, name='my_db'):
    c.run(f"export PATH=/usr/pgsql-10/bin:$PATH && psql -U postgres -d {name} -c '{com}'")

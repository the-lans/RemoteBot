from fabric import task

# env.python = '/var/venv3.8/bin/python'


@task
def hello(c, name="world"):
    print("Hello %s!" % name)
    c.run("uname -a")

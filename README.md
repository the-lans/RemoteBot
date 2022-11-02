# RemoteBot
Bot for remote control

  

# Config

There are 2 configuration files:

- *tgsettings.ini* - Telegram bot configuration.
- *conf.yaml* - Internal functionality configuration.

## tgsettings.ini

```ini
log_dir = logs - Directory with logs.
log_file_name = ./logs/log_print.txt - Log file.
count_exeption = 10 - The number of times to repeat if an exception was thrown.
sleep_exeption = 0.1 - Pause between repetitions in seconds.
name_group = RemoteBot - The name of the bot.
token = 9999999999:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX - Bot token.
threshold1 = 256 - The lower bound of the message to be sent.
threshold2 = 300 - The upper limit of the message to be sent. If the number of characters in the message is greater than the specified limit, then it is reduced to the lower limit, and the rest of the text comes as a file.
menu_servers = 2,2 - Server selection menu (number of rows and columns, respectively).
menu_servers_prefix = '💡 ' - Prefix for the server menu item.
menu_commands_exists = True - Display command menu.
menu_commands = 3,2 - Command history menu (number of rows and columns, respectively).
menu_commands_prefix = '⛳ ' - Prefix for the command history menu item.
```

## conf.yaml

```yaml
servers: - Server list.
  -
    name: 'local' - Server name. 'local' if it is a local machine.
    ip: '127.0.0.1' 
    sys: win
    cd: 'E:\ProgramProjects\PublicGIT\RemoteBot'
    pyenv: 'conda activate bots'
    shell: 'C:\Windows\System32\cmd.exe' - Shell available.
    encode: cp1251 - Server encoding.
    decode: cp866 - Message encoding.
  -
    name: 'CentOS 7'
    ip: '192.168.0.10'- The address of the remote machine.
    user: root - Username.
    port: 22 - Number port.
    sys: lin - System: win - Windows, lin - Linux.
    cd: '/var/my_project' - Home directory.
    pyenv: 'source /var/venv3.8/bin/activate' - Change of environment (python).
    fabfile: 'fab/fabfile.py' - The local location of the fab file.
    tracking: - Tracking file changes on the server.
     - '/var/log/messages'
commands_pyenv: - Commands that require a Python environment.
  - pip
  - python
  - conda
  - fab
  - black
commands_fab_ext: - Passing fab-commands additional parameters.
  - screen
commands_history: 30 - Number of commands in history.
tasks: True - Allow to perform scheduled tasks.
```

  

# Telegram commands

|  Command   |                Description                 |
| :--------: | :----------------------------------------: |
|   /start   | Beginning of work. List of remote servers. |
| /unconnect | Close the connection to the remote server. |
|            |                                            |

  

# Predefined commands

| Command |           Example           |                         Description                          |
| :-----: | :-------------------------: | :----------------------------------------------------------: |
|   cd    |     cd /var/my_project      |       Setting the home directory on the remote server.       |
|   lcd   |        lcd E:\data\         |       Setting the home directory on the local machine.       |
|  pyenv  | pyenv 'conda activate bots' |              Installing the python environment.              |
|  shell  |       shell /bin/bash       |                     Shell installation.                      |
|   cmd   |    cmd /bin/program arg     |       Wrapper for commands that start with a slash /.        |
|   get   |    get ./file.txt .\data    |           Downloading a file from a remote server.           |
|   put   |   put .\data\file.txt ./    |             Uploading a file to a remote server.             |
|  local  |          local dir          |            Execute commands on the local machine.            |
|  sudo   |           sudo ls           | Execution of commands on a remote server with exclusive rights. |
|   bot   |        bot settings         |                    Bot internal commands.                    |
|         |                             |                                                              |

  

# Bot internal commands

These commands start like this: **`bot ...`**

|     Command      |         Example         |                         Description                          |
| :--------------: | :---------------------: | :----------------------------------------------------------: |
|     settings     |      bot settings       |                     Return user options                      |
|       get        |  bot get cd lcd shell   |                 Return selected user options                 |
|       send       | bot send -l ./test.txt  |    File to Telegram. The flag **-l** means local machine.    |
|       edit       |        bot edit         |                          Edit mode.                          |
|       push       | bot push -a ./test2.txt | Add new local/remote file. The flag **-l** means local machine. The flag **-a** means appending data to the end of the file. |
|   history srv    |     bot history srv     |                   N previous user commands                   |
| history commands |  bot history commands   | List of unique user commands. History commands from session. |
|     fabfile      |       bot fabfile       |             Moving a fabfile to a remote server.             |
|      async       |     bot async True      |                      Asynchronous call                       |
|       join       |        bot join         | Wait for execution and output as a message all asynchronous calls. |
|  tasks on / off  |      bot tasks off      |             Enabling/disabling scheduled tasks.              |
|       task       |    bot task tracking    |               Manual call of a scheduled task.               |
|  task tracking   |    bot task tracking    | Scheduled file tracking task. Checks if there have been changes in the given file recently. |
|                  |                         |                                                              |

  

# Fab commands

These commands start like this: **`fab ...`**

| Command  |                      Example                      |                         Description                          |
| :------: | :-----------------------------------------------: | :----------------------------------------------------------: |
|  hello   |               fab hello --name Ilya               |           Checking the output on a remote server.            |
|   sql    |    fab sql 'select * from filehash limit 10;'     |                  Execution of a SQL query.                   |
|  screen  |           fab screen 'python hello.py'            |     Executing a command in a separate *screen* session.      |
| getmtime |       fab getmtime --path=/var/log/messages       | System function. Getting the modification time of a file on a remote server. |
| getsize  |       fab getsize --path=/var/log/messages        | System function. Getting the size of a file on a remote server. |
| readfile | fab readfile --path /var/log/messages --pointer 0 | System function. Reading a file from a specific pointer position. |
|          |                                                   |                                                              |

  

# Bot operation scenario

1. We enter the start command. Select a server from the list of servers, connect to it.

![001](https://github.com/the-lans/RemoteBot/blob/main/image/001.png?raw=true)

  

2. We connected to the server via SSH. Now we can enter commands.

![002](https://github.com/the-lans/RemoteBot/blob/main/image/002.png?raw=true)

  

3. After some time, we receive a response from the server. If the message size is too large (adjusted by a parameter *threshold2*), then it is split into text and a file. You can view the entire message in the file. If command history is enabled, you will see these commands in the user menu.

![003](https://github.com/the-lans/RemoteBot/blob/main/image/003.png?raw=true)

  

# Fabfile

With this bot, you can enter commands from a fabfile and thus automate processes.
What do you need to do:

1. In the config (*config.yaml*), set the path to the fabfile on the local machine.
2. Connect to a remote server. Import a fabfile to a remote server using the command: **`bot fabfile`**
3. Run the corresponding task from the fabfile. For example: **`fab sql 'select * from filehash limit 10;'`**

Discord SelfBot
======

Installing
----------
**Python 3.8 or higher is required**
- Clone the repository:
    ```
    git clone https://github.com/HypedDomi/SelfBot.git
    ```
- Install the dependencies:
    ```
    cd SelfBot && pip install -r requirements.txt
    ```
    or if you on windows use the install.bat file

Setting up
----------
- Create a .env file in the root directory.
- Add the following to the .env file[^1]:
    ```
    TOKEN = <BOT TOKEN>
    PREFIX = <COMMAND PREFIX>
    STATUS = <online|idle|dnd|offline>
    LINUX_PASSWORD = <Linux Password>
    ```
- Install Node.js and Git[^2]

[^1]: The Linux password is only required if you using the bot as a service and want to use the restart command.

[^2]: Node.js is only required if you want to use the eval command with an javascript interpreter. Git is only required if you want to use the update command.

Running the bot
---------------
- Run the bot:
    ```
    python3 bot.py
    ```
    or if you on windows use the start.bat file

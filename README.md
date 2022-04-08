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
    PASSWORD = <User Password>
    ```
- Install Node.js[^2]

[^1]: The password is only required if you using the bot as a service and want to use the restart command.

[^2]: Node.js is only required if you want to use the eval command with an javascript interpreter.

Running the bot
---------------
- Run the bot:
    ```
    python3 bot.py
    ```
    or if you on windows use the start.bat file
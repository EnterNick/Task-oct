from scr.bot.bot import bot_setup
from scr.bot.data.db_session import global_init


if __name__ == '__main__':
    global_init('scr/db/users.sqlite')
    bot_setup()

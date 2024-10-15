from bot.bot import bot_setup
from data import db_session


def main():
    db_session.global_init(r'scr\db\users.sqlite')
    bot_setup()


if __name__ == '__main__':
    main()
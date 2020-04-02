# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

from .interface.database import botdb
from .interface.config import botcfg
from .interface.comms import comms
from .interface.events import events
from .interface.logs import logs
# from .interface.users import BotUsers


class SpiceBot():

    def __init__(self):
        self.info = "test"

        # Allow access to bot config file without "bot"
        self.config = botcfg

        # allow access to bot database without "bot"
        self.db = botdb
        self.db.initialize(self.config)

        # allow usage of bot.write without "bot"
        self.comms = comms
        self.comms.initialize(self.config)

        # setup logging
        self.logs = logs
        self.logs.setup_logs(self.config)

        # Custom Events system
        self.events = events

        # Internal user list
        # self.users = BotUsers()

        self.wordsdict = {
                        "onoff_list": ['activate', 'enable', 'on', 'deactivate', 'disable', 'off'],
                        "activate_list": ['activate',  'enable', 'on'],
                        "deactivate_list": ['deactivate', 'disable', 'off'],

                        "valid_hyphen_args": [
                                            "admin", "a",
                                            "debug", "d"
                                            ],

                        "numdict": {
                                    "last": -1,
                                    "first": 0
                                    },

                        "worddict": {
                                    "a": "admin",
                                    },
                        }

    # OSD shortcut
    def osd(self, messages, recipients=None, text_method='PRIVMSG', max_messages=-1):
        return self.comms.osd(messages, recipients, text_method, max_messages)


spicebot = SpiceBot()

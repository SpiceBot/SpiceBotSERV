# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

import inspect

from .interface.database import botdb
from .interface.config import botcfg
from .interface.comms import comms
from .interface.events import events
from .interface.logs import logs
from .interface.sopel_info import sopel_info
from .tools import class_create, startupmonologue, humanized_time
# from .interface.users import BotUsers


class SpiceBot():

    def __init__(self):

        # Basic SpiceBot info
        self.propagate_sb_info()

        # Basic Sopel Info
        self.propogate_sopel_info()

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

        # tools
        self.tools = class_create("tools")
        self.tools.startupmonologue = startupmonologue
        self.tools.humanized_time = humanized_time

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

    def propagate_sb_info(self):
        self.version = "0.1.0"

    def propogate_sopel_info(self):
        self.sopel_info = sopel_info

    # OSD shortcut
    def osd(self, messages, recipients=None, text_method='PRIVMSG', max_messages=-1):
        return self.comms.osd(messages, recipients, text_method, max_messages)


spicebot = SpiceBot()


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

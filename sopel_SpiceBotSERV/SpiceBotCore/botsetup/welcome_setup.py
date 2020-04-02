# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

import sopel

import inspect

from SpiceBotCore.spicebot import spicebot


@sopel.module.event("001")
@sopel.module.rule('.*')
def welcome_setup_start(bot, trigger):
    initialise_irc_backend(bot)


def initialise_irc_backend(bot):
    spicebot.comms.ircbackend_initialize(bot)


@sopel.module.event(spicebot.events.BOT_CONNECTED)
@sopel.module.rule('.*')
def bot_events_start(bot, trigger):
    spicebot.comms.hostmask_set(bot)


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

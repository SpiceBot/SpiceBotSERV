# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

import sopel

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

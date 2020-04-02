# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function
"""
This is the SpiceBot Events system.
"""
import sopel
from threading import Thread
import inspect

from SpiceBotCore.spicebot import spicebot


@sopel.module.event(spicebot.events.BOT_WELCOME, spicebot.events.BOT_READY, spicebot.events.BOT_CONNECTED, spicebot.events.BOT_LOADED)
@sopel.module.rule('.*')
def bot_events_complete(bot, trigger):
    """This is here simply to log to stderr that this was recieved."""
    spicebot.logs.log('SpiceBot_Events', trigger.args[1], True)


@sopel.module.event(spicebot.events.RPL_WELCOME)
@sopel.module.rule('.*')
def bot_events_connected(bot, trigger):

    # Handling for connection count
    spicebot.events.dict["RPL_WELCOME_Count"] += 1
    if spicebot.events.dict["RPL_WELCOME_Count"] > 1:
        spicebot.events.trigger(bot, spicebot.events.BOT_RECONNECTED, "Bot ReConnected to IRC")
    else:
        spicebot.events.trigger(bot, spicebot.events.BOT_WELCOME, "Welcome to the SpiceBot Events System")

    """For items tossed in a queue, this will trigger them accordingly"""
    Thread(target=events_thread, args=(bot,)).start()


def events_thread(bot):
    while True:
        if len(spicebot.events.dict["trigger_queue"]):
            pretriggerdict = spicebot.events.dict["trigger_queue"][0]
            spicebot.events.dispatch(bot, pretriggerdict)
            try:
                del spicebot.events.dict["trigger_queue"][0]
            except IndexError:
                pass


@sopel.module.event(spicebot.events.BOT_WELCOME)
@sopel.module.rule('.*')
def bot_events_start(bot, trigger):
    """This stage is redundant, but shows the system is working."""
    spicebot.events.trigger(bot, spicebot.events.BOT_READY, "Ready To Process module setup procedures")

    """Here, we wait until we are in at least one channel"""
    while not len(list(bot.channels.keys())) > 0:
        pass
    spicebot.events.trigger(bot, spicebot.events.BOT_CONNECTED, "Bot Connected to IRC")


@spicebot.events.startup_check_ready()
@sopel.module.event(spicebot.events.BOT_READY)
@sopel.module.rule('.*')
def bot_events_startup_complete(bot, trigger):
    """All events registered as required for startup have completed"""
    spicebot.events.trigger(bot, spicebot.events.BOT_LOADED, "All registered modules setup procedures have completed")


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

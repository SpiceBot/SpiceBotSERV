# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

# import sopel
from sopel import module

import inspect

from .prerun import prerun
from .messagelog import msglog_debug

"""
Triggers for usage
"""


# prefix command
@prerun('module')
@module.commands('spicebot')
def trigger_module_command(bot, trigger, spicebot, currun):
    execute_start(bot, trigger, spicebot, currun)


# bot.nick do this
@prerun('nickname')
@module.nickname_commands('spicebot')
def trigger_nickname_command(bot, trigger, spicebot, currun):
    execute_start(bot, trigger, spicebot, currun)


"""
Command Processing
"""


def execute_start(bot, trigger, spicebot, currun):
    msglog_debug(currun.messagesid, "Player is allowed to continue", lineno())


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

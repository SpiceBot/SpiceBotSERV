# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function
"""StartupMonologue class"""

import inspect


class BotMonologue():

    def __init__(self):

        self.dict = {}


startupmonologue = BotMonologue()


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

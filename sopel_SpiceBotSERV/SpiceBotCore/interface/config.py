# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

import sys
import os
import configparser
import inspect

from sopel.cli.run import build_parser, get_configuration


class BotConfig():

    def __init__(self):
        self.dict = {}

        # opts input
        self.opts = self.get_opts()

        # Load config
        self.config = get_configuration(self.opts)

        self.setup_config()

        # load as dict
        config = configparser.ConfigParser()
        config.read(self.config.filename)
        for each_section in config.sections():
            if each_section.lower() not in list(self.dict.keys()):
                self.dict[each_section.lower()] = dict()
            for (each_key, each_val) in config.items(each_section):
                if each_key.lower() not in list(self.dict[each_section.lower()].keys()):
                    self.dict[each_section.lower()][each_key.lower()] = each_val

    def setup_config(self):
        self.config.core.basename = os.path.basename(self.config.filename).rsplit('.', 1)[0]
        self.config.core.prefix_list = str(self.config.core.prefix).replace("\\", '').split("|")

    def define_section(self, name, cls_, validate=True):
        return self.config.define_section(name, cls_, validate)

    def __getattr__(self, name):
        ''' will only get called for undefined attributes '''
        """We will try to find a core value, or return None"""
        if hasattr(self.config.core, name):
            return eval("self.config.core." + name)
        elif name.lower() in list(self.dict["core"].keys()):
            return self.dict["core"][str(name).lower()]
        elif hasattr(self.config, name):
            return eval("self.config." + name)
        else:
            return None

    def get_opts(self):
        parser = build_parser()
        if not len(sys.argv[1:]):
            argv = ['legacy']
        else:
            argv = sys.argv[1:]
        return parser.parse_args(argv)


botcfg = BotConfig()


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

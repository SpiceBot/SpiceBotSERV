# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function
"""A way to track users"""

import threading

from .database import db as botdb


class BotUsers():

    def __init__(self):
        self.lock = threading.Lock()
        self.dict = {
                    "all": botdb.get_plugin_value("spicebot", 'users') or {},
                    "online": [],
                    "offline": [],
                    "away": [],
                    "current": {},
                    "registered": botdb.get_plugin_value("spicebot", 'regged_users') or [],
                    "register_check": {},
                    "identified": [],
                    }
        """during setup, all users from database are offline until marked online"""
        self.lock.acquire()
        self.dict["offline"] = list(self.dict["all"].keys())
        self.lock.release()

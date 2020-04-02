# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

import json

from sopel.tools import Identifier

from sopel.db import SopelDB, NickValues, ChannelValues, PluginValues
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
BASE = declarative_base()


class SpiceDB(object):

    # NICK FUNCTIONS

    def adjust_nick_value(self, nick, key, value):
        """Sets the value for a given key to be associated with the nick."""
        nick = Identifier(nick)
        value = json.dumps(value, ensure_ascii=False)
        nick_id = self.get_nick_id(nick)
        session = self.ssession()
        try:
            result = session.query(NickValues) \
                .filter(NickValues.nick_id == nick_id) \
                .filter(NickValues.key == key) \
                .one_or_none()
            # NickValue exists, update
            if result:
                result.value = float(result.value) + float(value)
                session.commit()
            # DNE - Insert
            else:
                new_nickvalue = NickValues(nick_id=nick_id, key=key, value=float(value))
                session.add(new_nickvalue)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def adjust_nick_list(self, nick, key, entries, adjustmentdirection):
        """Sets the value for a given key to be associated with the nick."""
        nick = Identifier(nick)
        if not isinstance(entries, list):
            entries = [entries]
        entries = json.dumps(entries, ensure_ascii=False)
        nick_id = self.get_nick_id(nick)
        session = self.ssession()
        try:
            result = session.query(NickValues) \
                .filter(NickValues.nick_id == nick_id) \
                .filter(NickValues.key == key) \
                .one_or_none()
            # NickValue exists, update
            if result:
                if adjustmentdirection == 'add':
                    for entry in entries:
                        if entry not in result.value:
                            result.value.append(entry)
                elif adjustmentdirection == 'del':
                    for entry in entries:
                        while entry in result.value:
                            result.value.remove(entry)
                session.commit()
            # DNE - Insert
            else:
                values = []
                if adjustmentdirection == 'add':
                    for entry in entries:
                        if entry not in values:
                            values.append(entry)
                elif adjustmentdirection == 'del':
                    for entry in entries:
                        while entry in values:
                            values.remove(entry)
                new_nickvalue = NickValues(nick_id=nick_id, key=key, value=values)
                session.add(new_nickvalue)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    # CHANNEL FUNCTIONS

    def adjust_channel_value(self, channel, key, value):
        """Sets the value for a given key to be associated with the channel."""
        channel = Identifier(channel).lower()
        value = json.dumps(value, ensure_ascii=False)
        session = self.ssession()
        try:
            result = session.query(ChannelValues) \
                .filter(ChannelValues.channel == channel)\
                .filter(ChannelValues.key == key) \
                .one_or_none()
            # ChannelValue exists, update
            if result:
                result.value = float(result.value) + float(value)
                session.commit()
            # DNE - Insert
            else:
                new_channelvalue = ChannelValues(channel=channel, key=key, value=float(value))
                session.add(new_channelvalue)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def adjust_channel_list(self, channel, key, entries, adjustmentdirection):
        """Sets the value for a given key to be associated with the channel."""
        channel = Identifier(channel).lower()
        if not isinstance(entries, list):
            entries = [entries]
        entries = json.dumps(entries, ensure_ascii=False)
        session = self.ssession()
        try:
            result = session.query(ChannelValues) \
                .filter(ChannelValues.channel == channel)\
                .filter(ChannelValues.key == key) \
                .one_or_none()
            # ChannelValue exists, update
            if result:
                if adjustmentdirection == 'add':
                    for entry in entries:
                        if entry not in result.value:
                            result.value.append(entry)
                elif adjustmentdirection == 'del':
                    for entry in entries:
                        while entry in result.value:
                            result.value.remove(entry)
                session.commit()
            # DNE - Insert
            else:
                values = []
                if adjustmentdirection == 'add':
                    for entry in entries:
                        if entry not in values:
                            values.append(entry)
                elif adjustmentdirection == 'del':
                    for entry in entries:
                        while entry in values:
                            values.remove(entry)
                new_channelvalue = ChannelValues(channel=channel, key=key, value=values)
                session.add(new_channelvalue)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    # PLUGIN FUNCTIONS

    def adjust_plugin_value(self, plugin, key, value):
        """Sets the value for a given key to be associated with the plugin."""
        plugin = plugin.lower()
        value = json.dumps(value, ensure_ascii=False)
        session = self.ssession()
        try:
            result = session.query(PluginValues) \
                .filter(PluginValues.plugin == plugin)\
                .filter(PluginValues.key == key) \
                .one_or_none()
            # PluginValue exists, update
            if result:
                result.value = float(result.value) + float(value)
                session.commit()
            # DNE - Insert
            else:
                new_pluginvalue = PluginValues(plugin=plugin, key=key, value=float(value))
                session.add(new_pluginvalue)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def adjust_plugin_list(self, plugin, key, entries, adjustmentdirection):
        """Sets the value for a given key to be associated with the plugin."""
        plugin = plugin.lower()
        if not isinstance(entries, list):
            entries = [entries]
        entries = json.dumps(entries, ensure_ascii=False)
        session = self.ssession()
        try:
            result = session.query(PluginValues) \
                .filter(PluginValues.plugin == plugin)\
                .filter(PluginValues.key == key) \
                .one_or_none()
            # PluginValue exists, update
            if result:
                if adjustmentdirection == 'add':
                    for entry in entries:
                        if entry not in result.value:
                            result.value.append(entry)
                elif adjustmentdirection == 'del':
                    for entry in entries:
                        while entry in result.value:
                            result.value.remove(entry)
                session.commit()
            # DNE - Insert
            else:
                values = []
                if adjustmentdirection == 'add':
                    for entry in entries:
                        if entry not in values:
                            values.append(entry)
                elif adjustmentdirection == 'del':
                    for entry in entries:
                        while entry in values:
                            values.remove(entry)
                new_pluginvalue = PluginValues(plugin=plugin, key=key, value=values)
                session.add(new_pluginvalue)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()


class BotDatabase():

    def __init__(self):
        self.db = None
        self.dict = {
                    "bot": {
                            "nick": None,
                            },
                    }

    def initialize(self, config):
        SopelDB.adjust_nick_value = SpiceDB.adjust_nick_value
        SopelDB.adjust_nick_list = SpiceDB.adjust_nick_list

        SopelDB.adjust_channel_value = SpiceDB.adjust_channel_value
        SopelDB.adjust_channel_list = SpiceDB.adjust_channel_list

        SopelDB.adjust_plugin_value = SpiceDB.adjust_plugin_value
        SopelDB.adjust_plugin_list = SpiceDB.adjust_plugin_list

        self.db = SopelDB(config)
        BASE.metadata.create_all(self.db.engine)
        self.dict["bot"]["nick"] = config.core.nick

    def __getattr__(self, name):
        ''' will only get called for undefined attributes '''
        if hasattr(self.db, name):
            return eval("self.db." + name)
        else:
            return None

    """Nick"""

    def adjust_nick_value(self, nick, key, value):
        return self.db.adjust_nick_value(nick, key, value)

    def adjust_nick_list(self, nick, key, entries, adjustmentdirection):
        return self.db.adjust_nick_list(nick, key, entries, adjustmentdirection)

    """Bot"""

    def get_bot_value(self, key):
        return self.db.get_nick_value(self.dict["bot"]["nick"], key)

    def set_bot_value(self, key, value):
        return self.db.set_nick_value(self.dict["bot"]["nick"], key, value)

    def delete_bot_value(self, key):
        return self.db.delete_nick_value(self.dict["bot"]["nick"], key)

    def adjust_bot_value(self, key, value):
        return self.db.adjust_nick_value(self.dict["bot"]["nick"], key, value)

    def adjust_bot_list(self, key, entries, adjustmentdirection):
        return self.db.adjust_nick_list(self.dict["bot"]["nick"], key, entries, adjustmentdirection)

    """Channels"""

    def adjust_channel_value(self, channel, key, value):
        return self.db.adjust_channel_value(channel, key, value)

    def adjust_channel_list(self, nick, key, entries, adjustmentdirection):
        return self.db.adjust_channel_list(nick, key, entries, adjustmentdirection)

    """Plugins"""

    def adjust_plugin_value(self, plugin, key, value):
        return self.db.adjust_plugin_value(plugin, key, value)

    def adjust_plugin_list(self, plugin, key, entries, adjustmentdirection):
        return self.db.adjust_plugin_list(plugin, key, entries, adjustmentdirection)

# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

from sopel.tools import Identifier
from sopel.irc.utils import safe

import threading
# import time
import sys
if sys.version_info.major >= 3:
    from collections import abc

if sys.version_info.major >= 3:
    unicode = str


class BotComms():

    def __init__(self):
        self.ircbackend = None
        self.sending = threading.RLock()
        self.stack = {}
        self.dict = {
                    "bot": {
                            "nick": None,
                            "hostmask": None,
                            },
                    }

    def initialize(self, config):
        self.dict["bot"]["nick"] = config.core.nick

    def ircbackend_initialize(self, bot):
        self.dict["bot"]["hostmask"] = bot.users.get(bot.nick).hostmask
        self.ircbackend = bot.backend
        self.ircdispatch = bot.dispatch

    def write(self, args, text=None):
        while not self.ircbackend:
            pass
        args = [safe(arg) for arg in args]
        self.ircbackend.send_command(*args, text=text)

    def get_message_recipientgroups(self, recipients, text_method):
        """
        Split recipients into groups based on server capabilities.
        This defaults to 4

        Input can be
            * unicode string
            * a comma-seperated unicode string
            * list
            * dict_keys handy for list(bot.channels.keys())
        """

        if sys.version_info.major >= 3:
            if isinstance(recipients, abc.KeysView):
                recipients = [x for x in recipients]
        if isinstance(recipients, dict):
            recipients = [x for x in recipients]

        if not isinstance(recipients, list):
            recipients = recipients.split(",")

        if not len(recipients):
            raise ValueError("Recipients list empty.")

        if text_method == 'NOTICE':
            maxtargets = 4
        elif text_method in ['PRIVMSG', 'ACTION']:
            maxtargets = 4
        maxtargets = int(maxtargets)

        recipientgroups = []
        while len(recipients):
            recipients_part = ','.join(x for x in recipients[-maxtargets:])
            recipientgroups.append(recipients_part)
            del recipients[-maxtargets:]

        return recipientgroups

    def get_available_message_bytes(self, recipientgroups, text_method):
        """
        Get total available bytes for sending a message line

        Total sendable bytes is 512
            * 15 are reserved for basic IRC NOTICE/PRIVMSG and a small buffer.
            * The bots hostmask plays a role in this count
                Note: if unavailable, we calculate the maximum length of a hostmask
            * The recipients we send to also is a factor. Multiple recipients reduces
              sendable message length
        """

        if text_method == 'ACTION':
            text_method_bytes = (len('PRIVMSG')
                                 + len("\x01ACTION \x01")
                                 )
        else:
            text_method_bytes = len(text_method)

        if self.dict["bot"]["hostmask"]:
            hostmaskbytes = len((self.dict["bot"]["hostmask"]).encode('utf-8'))
        else:
            hostmaskbytes = (len((self.dict["bot"]["nick"]).encode('utf-8'))  # Bot's NICKLEN
                             + 1  # (! separator)
                             + len('~')  # (for the optional ~ in user)
                             + 9  # max username length
                             + 1  # (@ separator)
                             + 63  # <hostname> has a maximum length of 63 characters.
                             )

        # find the maximum target group length, and use the max
        groupbytes = []
        for recipients_part in recipientgroups:
            groupbytes.append(len((recipients_part).encode('utf-8')))

        max_recipients_bytes = max(groupbytes)

        allowedLength = (512
                         - len(':') - hostmaskbytes
                         - len(' ') - text_method_bytes - len(' ')
                         - max_recipients_bytes
                         - len(' :')
                         - len('\r\n')
                         )

        return allowedLength

    def get_sendable_message_list(self, messages, max_length=400):
        """Get a sendable ``text`` message list.
        :param str txt: unicode string of text to send
        :param int max_length: maximum length of the message to be sendable
        :return: a tuple of two values, the sendable text and its excess text
        We're arbitrarily saying that the max is 400 bytes of text when
        messages will be split. Otherwise, we'd have to account for the bot's
        hostmask, which is hard.
        The `max_length` is the max length of text in **bytes**, but we take
        care of unicode 2-bytes characters, by working on the unicode string,
        then making sure the bytes version is smaller than the max length.
        """

        if not isinstance(messages, list):
            messages = [messages]

        messages_list = ['']
        message_padding = 4 * " "

        for message in messages:
            if len((messages_list[-1] + message_padding + message).encode('utf-8')) <= max_length:
                if messages_list[-1] == '':
                    messages_list[-1] = message
                else:
                    messages_list[-1] = messages_list[-1] + message_padding + message
            else:
                text_list = []
                while len(message.encode('utf-8')) > max_length and not message.isspace():
                    last_space = message.rfind(' ', 0, max_length)
                    if last_space == -1:
                        # No last space, just split where it is possible
                        splitappend = message[:max_length]
                        if not splitappend.isspace():
                            text_list.append(splitappend)
                        message = message[max_length:]
                    else:
                        # Split at the last best space found
                        splitappend = message[:last_space]
                        if not splitappend.isspace():
                            text_list.append(splitappend)
                        message = message[last_space:]
                if len(message.encode('utf-8')) and not message.isspace():
                    text_list.append(message)
                messages_list.extend(text_list)

        return messages_list

    def osd(self, messages, recipients=None, text_method='PRIVMSG', max_messages=-1):
        """Send ``text`` as a PRIVMSG, CTCP ACTION, or NOTICE to ``recipients``.

        In the context of a triggered callable, the ``recipient`` defaults to
        the channel (or nickname, if a private message) from which the message
        was received.

        By default, unless specified in the configuration file, there is some
        built-in flood protection. Messages displayed over 5 times in 2 minutes
        will be displayed as '...'.

        The ``recipient`` can be in list format or a comma seperated string,
        with the ability to send to multiple recipients simultaneously. The
        default recipients that the bot will send to is 4 if the IRC server
        doesn't specify a limit for TARGMAX.

        Text can be sent to this function in either string or list format.
        List format will insert as small buffering space between entries in the
        list.

        There are 512 bytes available in a single IRC message. This includes
        hostmask of the bot as well as around 15 bytes of reserved IRC message
        type. This also includes the destinations/recipients of the message.
        This will split given strings/lists into a displayable format as close
        to the maximum 512 bytes as possible.

        If ``max_messages`` is given, the split mesage will display in as many
        lines specified by this argument. Specifying ``0`` or a negative number
        will display without limitation. By default this is set to ``-1`` when
        called directly. When called from the say/msg/reply/notice/action it
        will default to ``1``.
        """

        if not hasattr(self, 'stack'):
            self.stack = {}

        text_method = text_method.upper()
        if text_method == 'SAY' or text_method not in ['NOTICE', 'ACTION']:
            text_method = 'PRIVMSG'

        recipientgroups = self.get_message_recipientgroups(recipients, text_method)
        available_bytes = self.get_available_message_bytes(recipientgroups, text_method)
        messages_list = self.get_sendable_message_list(messages, available_bytes)

        if max_messages >= 1:
            messages_list = messages_list[:max_messages]

        text_method_orig = text_method

        for recipientgroup in recipientgroups:
            text_method = text_method_orig

            recipient_id = Identifier(recipientgroup)

            recipient_stack = self.stack.setdefault(recipient_id, {
                'messages': [],
                'flood_left': 999,
                'dots': 0,
            })
            recipient_stack['dots'] = 0

            with self.sending:

                for text in messages_list:

                    if recipient_stack['dots'] <= 3:
                        if text_method == 'ACTION':
                            text = '\001ACTION {}\001'.format(text)
                            self.write(('PRIVMSG', recipientgroup), text)
                            text_method = 'PRIVMSG'
                        elif text_method == 'NOTICE':
                            self.write(('NOTICE', recipientgroup), text)
                        else:
                            self.write(('PRIVMSG', recipientgroup), text)

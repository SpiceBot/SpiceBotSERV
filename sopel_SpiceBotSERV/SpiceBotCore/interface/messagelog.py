# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

from .comms import comms

import inspect
import uuid


class MessageLog():

    def __init__(self):
        self.dict = {}
        self.message_display = dict()
        self.used_error_ids = [0]
        self.completed = []
        self.write = []
        self.error_message_dict = {
                                    "command_inchan_only": "$command must be run in channel.",
                                    "admin_switch_unauth": "The admin switch (-a) is for use by authorized nicks ONLY.",
                                    }

    def messagelog_assign(self, trigger):
        return str(id(trigger.time))

    def messagelog_error_get(self, errormsg):
        for error_id in list(self.error_message_dict.keys()):
            if self.error_message_dict[error_id] == errormsg:
                return error_id
        unique_id = "0"
        while str(unique_id) in self.used_error_ids:
            unique_id = str(uuid.uuid4())
        self.used_error_ids.append(unique_id)
        self.error_message_dict[unique_id] = errormsg
        return unique_id

    def messagelog_start(self, bot, trigger, log_id):

        if not trigger.is_privmsg:
            channelname = trigger.sender
        else:
            channelname = None

        self.message_display[log_id] = {
                                        "trigger": {
                                                "nick": trigger.nick,
                                                "sender": channelname,
                                                },
                                        "bot": {
                                                "nick": bot.nick
                                                },
                                        "messages": [],
                                        "inchannel": trigger.is_privmsg,
                                        "channel_triggered": trigger.args[0],
                                        "channel_replyto": trigger.sender,
                                        "debuglevel": 0,
                                        }

    def messagelog_debuglevel(self, log_id, debuglevel=0):
        if int(debuglevel) > self.message_display[log_id]["debuglevel"]:
            self.message_display[log_id]["debuglevel"] = int(debuglevel)
            self.messagelog_debug(log_id, "Debug mode set to level " + str(debuglevel), lineno())

    def messagelog_error(self, log_id, error_id):

        newloglist = []
        error_exists_prior = False

        if error_id not in self.error_message_dict:
            error_id = self.messagelog_error_get(error_id)

        for existing_messagedict in self.message_display[log_id]["messages"]:
            if existing_messagedict["type"] == "error":
                if existing_messagedict["error_id"] == error_id:
                    error_exists_prior = True
                    existing_messagedict["count"] += 1
            newloglist.append(existing_messagedict)

        if not error_exists_prior:
            newmessagedict = {"type": "error", "error_id": error_id, "count": 1}
            newloglist.append(newmessagedict)

        self.message_display[log_id]["messages"] = newloglist

    def messagelog_error_admins(self, bot, log_id, message):
        recipients = list(bot.config.admins)
        comms.osd(["Attention Bot Admin: ", message], recipients, 'notice')
        # TODO deublevel trigger
        return

    def messagelog(self, log_id, message, recipients=None):

        if not recipients:
            if self.message_display[log_id]["trigger"]["sender"]:
                recipients = [self.message_display[log_id]["trigger"]["sender"]]
            else:
                recipients = [self.message_display[log_id]["trigger"]["nick"]]

        if not isinstance(recipients, list):
            recipients == [recipients]

        messagedict = {"type": "normal", "message": message, "recipients": recipients}

        self.message_display[log_id]["messages"].append(messagedict)

    def messagelog_debug(self, log_id, message, linenum, debuglevel=3):

        if linenum:
            message += str("    " + str(linenum))

        messagedict = {"type": "debug", "message": message, "debuglevel": debuglevel}

        self.message_display[log_id]["messages"].append(messagedict)

    def messagelog_action(self, log_id, message, recipients=None):

        if not recipients:
            if self.message_display[log_id]["trigger"]["sender"]:
                recipients = [self.message_display[log_id]["trigger"]["sender"]]
            else:
                recipients = [self.message_display[log_id]["trigger"]["nick"]]

        if not isinstance(recipients, list):
            recipients == [recipients]

        messagedict = {"type": "action", "message": message, "recipients": recipients}

        self.message_display[log_id]["messages"].append(messagedict)

    def messagelog_private(self, log_id, message):

        recipients = [self.message_display[log_id]["trigger"]["nick"]]

        messagedict = {"type": "private", "message": message, "recipients": recipients}

        self.message_display[log_id]["messages"].append(messagedict)

    def messagelog_mark_completed(self, log_id):
        if str(log_id) not in self.completed:
            self.completed.append(str(log_id))

    def messagelog_exit(self, bot, log_id):

        current_messages = []
        current_errors = []

        for messagedict in self.message_display[log_id]["messages"]:

            if messagedict["type"] == "error":
                if messagedict["error_id"] not in self.error_message_dict.keys():
                    message = "Error missing for ID '" + str(messagedict["error_id"]) + "'"
                else:
                    message = self.error_message_dict[messagedict["error_id"]]
                message += " (" + str(messagedict["count"]) + ")"
                message = self.messagelog_fillin(message, log_id)
                current_errors.append(message)
            else:
                if len(current_errors):
                    currenterrordict = {"type": "error", "message": current_errors}
                    current_messages.append(currenterrordict)
                    current_errors = []
                messagedict["message"] = self.messagelog_fillin(messagedict["message"], log_id)
                current_messages.append(messagedict)
        if len(current_errors):
            currenterrordict = {"type": "error", "message": current_errors}
            current_messages.append(currenterrordict)
            current_errors = []

        for messagedict in current_messages:

            if messagedict["type"] == 'error':
                comms.osd(messagedict['message'], self.message_display[log_id]["trigger"]["nick"], 'notice')

            elif messagedict["type"] == 'debug':
                if int(messagedict["debuglevel"]) <= int(self.message_display[log_id]["debuglevel"]):
                    comms.osd(messagedict['message'], self.message_display[log_id]["trigger"]["nick"], 'notice')

            elif messagedict["type"] == 'private':
                comms.osd(messagedict['message'], messagedict["recipients"], 'notice')

            elif len(messagedict["recipients"]) > 1:
                comms.osd(messagedict['message'], messagedict["recipients"], 'notice')

            elif len(messagedict["recipients"]) == 1:
                if messagedict["recipients"][0] == self.message_display[log_id]["trigger"]["nick"]:
                    comms.osd(messagedict['message'], self.message_display[log_id]["trigger"]["nick"], 'notice')
                elif messagedict["type"] == 'action':
                    comms.osd(messagedict['message'], messagedict["recipients"], 'action')
                else:
                    comms.osd(messagedict['message'], messagedict["recipients"], 'say')

            else:
                comms.osd(messagedict['message'], messagedict["recipients"], 'say')

        self.messagelog_kill(log_id)

    def messagelog_fillin(self, message, log_id):

        for botval in ["nick"]:
            fullbotval = str("$bot." + botval)
            fullbotvaleval = self.message_display[log_id]["bot"][botval]
            if fullbotval in message:
                message = str(message.replace(fullbotval, fullbotvaleval))

        for triggerval in ["nick", "sender"]:
            fulltriggerval = str("$trigger." + triggerval)
            fulltriggervaleval = self.message_display[log_id]["trigger"][triggerval]
            if fulltriggerval in message:
                if fulltriggervaleval:
                    message = str(message.replace(fulltriggerval, fulltriggervaleval))
                else:
                    if triggerval == "sender":
                        message = str(message.replace("$trigger.sender", 'privmsg'))
                    else:
                        message = str(message.replace(fulltriggerval, str(fulltriggervaleval)))

        if "$current_chan" in message:
            if self.message_display[log_id]["inchannel"]:
                message = str(message.replace("$current_chan", self.message_display[log_id]["channel_triggered"]))
            else:
                message = str(message.replace("$current_chan", 'privmsg'))

        return message

    def messagelog_kill(self, log_id):
        if log_id in self.message_display:
            del self.message_display[log_id]
        if log_id in self.completed:
            self.completed.remove(log_id)


messagelog = MessageLog()


"""
Message Handling
"""


def msglog(bot, log_id, message, recipients=None):
    messagelog.messagelog(log_id, message, recipients)


def msglog_private(bot, log_id, message):
    messagelog.messagelog_private(log_id, message)


def msglog_error(bot, log_id, message):
    messagelog.messagelog_error(log_id, message)


def msglog_debug(log_id, message, linenum=None):
    messagelog.messagelog_debug(log_id, message, linenum)


def msglog_action(bot, log_id, message, recipients=None):
    messagelog.messagelog_action(log_id, message, recipients)


def msglog_exit(bot, log_id):
    messagelog.messagelog_exit(bot, log_id)


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function
"""
This is the SpiceBot Prerun system.
"""

from sopel.tools import Identifier

import functools
import copy
import time
from word2number import w2n
import inspect
import inspect

import spicemanip

from .spicebot import spicebot

from .tools import class_create
from .messagelog import messagelog


def prerun(t_command_type='module'):

    def actual_decorator(function):

        @functools.wraps(function)
        def internal_prerun(bot, trigger, *args, **kwargs):

            bot.say(str(id(trigger)))
            bot.say(str(trigger.raw))
            spicebot.comms.write(("PRIVMSG", "deathbybandaid"), "test")

            log_id = messagelog.messagelog_assign(trigger)
            messagelog.messagelog_start(bot, trigger, log_id)
            messagelog.messagelog_debug(log_id, "currun Prerun Process Started", lineno(), 1)
            messagelog.messagelog_debug(log_id, "Message Log System Started", lineno(), 2)

            # Create dynamic class
            currun = class_create('currun')
            currun.default = 'currun'
            messagelog.messagelog_debug(log_id, "currun class() Created", lineno(), 3)

            currun.instigator = str(trigger.nick)

            currun.start = time.time()
            messagelog.messagelog_debug(log_id, "currun Start Time Set", lineno(), 4)

            # bot valid prefix
            currun.prefix_list = str(bot.config.core.prefix).replace("\\", '').split("|")

            if t_command_type == "nickname":
                check_nick = spicemanip.main(trigger.args[1], 1).lower()
                if check_nick != str(bot.nick).lower():
                    messagelog.messagelog_debug(log_id, "Command is a nickname_command but does not start with bot.nick", lineno(), 3)
                    messagelog.messagelog_exit(bot, currun.messagesid)
                    return
                messagelog.messagelog_debug(log_id, "Command is a nickname_command", lineno(), 3)
            elif t_command_type == "module":
                if not str(trigger.args[1]).startswith(tuple(currun.prefix_list)):
                    messagelog.messagelog_debug(log_id, "Command is a module_command but doesn't have a prefix", lineno(), 3)
                    messagelog.messagelog_exit(bot, currun.messagesid)
                    return
                messagelog.messagelog_debug(log_id, "Command is a module_command", lineno(), 3)

            trigger_command_type = str(t_command_type)

            # Primary command used for trigger, and a list of all words
            trigger_args, trigger_command, trigger_prefix = make_trigger_args(trigger.args[1], trigger_command_type)
            messagelog.messagelog_debug(log_id, "triggerargs created", lineno(), 4)

            # Argsdict Defaults
            argsdict_default = {}
            argsdict_default["type"] = trigger_command_type
            argsdict_default["com"] = trigger_command
            argsdict_default["trigger_prefix"] = trigger_prefix

            # messagelog ID
            argsdict_default["log_id"] = log_id
            currun.messagesid = log_id

            if argsdict_default["type"] == 'nickname':
                argsdict_default["comtext"] = "'" + bot.nick + " " + argsdict_default["com"] + "'"
            else:
                argsdict_default["comtext"] = "'" + argsdict_default["com"] + "'"

            # split into && groupings
            and_split = trigger_and_split(trigger_args)
            messagelog.messagelog_debug(log_id, "triggerargs split by &&", lineno(), 4)

            # Create dict listings for currun.dict
            argsdict_list = trigger_argsdict_list(argsdict_default, and_split)
            messagelog.messagelog_debug(log_id, "argsdict assembled per triggerargs split", lineno(), 4)

            # Run the function for all splits

            runcount = 0
            try:
                for argsdict in argsdict_list:
                    runcount += 1
                    messagelog.messagelog_debug(log_id, "Processing Split " + str(runcount) + "/" + str(len(argsdict_list)), lineno(), 2)
                    currun.dict = copy.deepcopy(argsdict)

                    currun.adminswitch = False

                    currun.dict["runcount"] = runcount

                    currun.dict["args"], currun.dict["hyphen_args"], currun.dict["debuglevel"] = trigger_hyphen_args(currun)

                    args_pass, currun = trigger_hyphen_arg_handler(bot, trigger, currun)

                    currun.dict["completestring"] = spicemanip.main(currun.dict['args'], 0)

                    if args_pass:

                        currun.dict["comdict"] = trigger_subcom_info(currun.dict["args"])

                        if trigger_runstatus(bot, trigger, currun):
                            function(bot, trigger, spicebot, currun, *args, **kwargs)
            except Exception as e:
                messagelog.messagelog(bot, currun.messagesid, str(e))
            finally:
                messagelog.messagelog_exit(bot, currun.messagesid)
                # messagelog.messagelog_mark_completed(currun.messagesid)

        return internal_prerun
    return actual_decorator


def make_trigger_args(triggerargs_one, trigger_command_type='module'):
    trigger_args = spicemanip.main(triggerargs_one, 'create')
    if trigger_command_type in ['nickname']:
        trigger_prefix = None
        # if trigger_prefix.isupper() or trigger_prefix.islower():
        #    trigger_prefix = None
        trigger_command = spicemanip.main(trigger_args, 2).lower()
        trigger_args = spicemanip.main(trigger_args, '3+', 'list')
    elif trigger_command_type in ['action']:
        trigger_prefix = None
        trigger_command = spicemanip.main(trigger_args, 1).lower()
        trigger_args = spicemanip.main(trigger_args, '2+', 'list')
    else:
        trigger_prefix = spicemanip.main(trigger_args, 1).lower()[0]
        trigger_command = spicemanip.main(trigger_args, 1).lower()[1:]
        trigger_args = spicemanip.main(trigger_args, '2+', 'list')
    return trigger_args, trigger_command, trigger_prefix


def trigger_and_split(trigger_args):
    trigger_args_list_split = spicemanip.main(trigger_args, "split_&&")
    if not len(trigger_args_list_split):
        trigger_args_list_split.append([])
    return trigger_args_list_split


def trigger_argsdict_list(argsdict_default, and_split):
    prerun_split = []
    for trigger_args_part in and_split:
        argsdict_part = copy.deepcopy(argsdict_default)
        argsdict_part["args"] = spicemanip.main(trigger_args_part, 'create')
        prerun_split.append(argsdict_part)
    return prerun_split


def trigger_runstatus(bot, trigger, currun):

    # Bots can't run commands
    if Identifier(trigger.nick) == bot.nick:
        return False

    return True


def trigger_cant_run(bot, trigger, currun, message=None):
    if message:
        messagelog.messagelog_error(currun.dict["log_id"], message)
    return False


def trigger_hyphen_args(currun):

    hyphen_args = []
    trigger_args_unhyphend = []
    debuglevel = 0
    for worditem in currun.dict["args"]:
        if str(worditem).startswith("--"):
            clipped_word = str(worditem[2:]).lower()

            # valid arg above
            if clipped_word in spicebot.wordsdict["valid_hyphen_args"]:
                if str(clipped_word) in list(spicebot.wordsdict["worddict"].keys()):
                    hyphen_args.append(spicebot.wordsdict["worddict"][clipped_word])
                else:
                    hyphen_args.append(clipped_word)

            elif clipped_word.startswith("debug"):
                hyphen_args.append(clipped_word)

            # numbered args
            elif str(clipped_word).isdigit():
                hyphen_args.append(int(clipped_word))
            elif clipped_word in list(spicebot.wordsdict["numdict"].keys()):
                hyphen_args.append(int(spicebot.wordsdict["numdict"][clipped_word]))

            else:

                # check if arg word is a number
                try:
                    clipped_word = w2n.word_to_num(str(clipped_word))
                    hyphen_args.append(int(clipped_word))

                # word is not a valid arg or number
                except ValueError:
                    trigger_args_unhyphend.append(worditem)
        else:
            trigger_args_unhyphend.append(worditem)

    # only one arg allowed per && split
    finalargs = []
    specialargs = ["admin"]
    singlehyphen = False
    for hyphenarg in hyphen_args:
        if hyphenarg in specialargs:
            finalargs.append(hyphenarg)
        elif hyphenarg == "debug":
            debuglevel = 1
            finalargs.append(hyphenarg)
        elif hyphenarg.startswith("debug"):
            debuglevel = hyphenarg.split("debug")[-1]
            finalargs.append("debug")
        else:
            if not singlehyphen:
                finalargs.append(hyphenarg)
                singlehyphen = True

    return trigger_args_unhyphend, finalargs, debuglevel


def trigger_hyphen_arg_handler(bot, trigger, currun):

    if "debug" in currun.dict["hyphen_args"]:
        messagelog.messagelog_debuglevel(currun.messagesid, currun.dict["debuglevel"])

    if messagelog.message_display[currun.messagesid]["debuglevel"] and "debug" not in currun.dict["hyphen_args"]:
        currun.dict["hyphen_args"].append("debug")

    if "admin" in currun.dict["hyphen_args"]:
        messagelog.messagelog_debug(currun.messagesid, "--admin switch has been used", lineno(), 3)
        currun.adminswitch = True

    if not len(currun.dict["hyphen_args"]):
        return True, currun

    if "debug" in currun.dict["hyphen_args"]:
        return True, currun

    if "admin" in currun.dict["hyphen_args"]:
        return True, currun

    return True, currun


def trigger_subcom_info(args):

    comdict = {
                "command": False,
                }

    return comdict


"""
Other
"""


def lineno():
    """Returns the current line number in our program."""
    linenum = inspect.currentframe().f_back.f_lineno
    frameinfo = inspect.getframeinfo(inspect.currentframe())
    filename = frameinfo.filename
    return str("File:  " + str(filename) + "    Line:  " + str(linenum))

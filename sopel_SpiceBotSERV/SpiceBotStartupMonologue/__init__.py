# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function
"""
This is the SpiceBot StartupMonologue system.
"""
import sopel

from SpiceBotCore.spicebot import spicebot

import time


@sopel.module.event(spicebot.events.BOT_CHANNELS)
@sopel.module.rule('.*')
def bot_startup_monologue_start(bot, trigger):
    # Startup
    spicebot.logs.log('SpiceBot_StartupMonologue', bot.nick + " is now starting. Please wait while I load my configuration")
    bot.osd(" is now starting. Please wait while I load my configuration.", list(bot.channels.keys()), 'ACTION')
    spicebot.events.trigger(bot, spicebot.events.BOT_STARTUPMONOLOGUE_CONNECTED, "SpiceBot_StartupMonologue")


@sopel.module.event(spicebot.events.BOT_CONNECTED)
@sopel.module.rule('.*')
def bot_startup_monologue_sopel_version(bot, trigger):
    spicebot.events.trigger(bot, spicebot.events.BOT_STARTUPMONOLOGUE_VERSION, "SpiceBot_StartupMonologue")
    spicebot.startupmonologue.dict["sopel_version"] = "Sopel " + str(spicebot.version.sopel["version_local_num"])
    spicebot.startupmonologue.dict["spicebot_version"] = "SpiceBot " + str(spicebot.version.spicebot["version_local_num"])


@sopel.module.event(spicebot.events.BOT_CHANNELS)
@sopel.module.rule('.*')
def bot_startup_monologue_channels(bot, trigger):
    botcount = spicebot.channels.total_bot_channels()
    servercount = spicebot.channels.total_channels()
    displayval = "I am in " + str(botcount) + " of " + str(servercount) + " channel(s) available on this server."
    spicebot.startupmonologue.dict["channels"] = displayval
    spicebot.logs.log('SpiceBot_StartupMonologue', displayval)
    spicebot.events.trigger(bot, spicebot.events.BOT_STARTUPMONOLOGUE_CHANNELS, "SpiceBot_StartupMonologue")


@sopel.module.event(spicebot.events.BOT_COMMANDS)
@sopel.module.rule('.*')
def bot_startup_monologue_commands(bot, trigger):
    availablecomsnum, availablecomsfiles = 0, []
    for commandstype in list(spicebot.commands.dict['commands'].keys()):
        availablecomsnum += len(list(spicebot.commands.dict['commands'][commandstype].keys()))
        for validcom in list(spicebot.commands.dict['commands'][commandstype].keys()):
            if "filepath" in list(spicebot.commands.dict['commands'][commandstype][validcom].keys()):
                filepath = spicebot.commands.dict['commands'][commandstype][validcom]["filepath"].lower()
                if filepath not in availablecomsfiles:
                    availablecomsfiles.append(filepath)
    availablecomsfiles = len(availablecomsfiles)
    displayval = "There are " + str(availablecomsnum) + " commands available in " + str(availablecomsfiles) + " files."
    spicebot.startupmonologue.dict["commands"] = displayval
    spicebot.logs.log('SpiceBot_StartupMonologue', displayval)
    spicebot.events.trigger(bot, spicebot.events.BOT_STARTUPMONOLOGUE_COMMANDS, "SpiceBot_StartupMonologue")


@sopel.module.event(spicebot.events.BOT_AI)
@sopel.module.rule('.*')
def bot_startup_monologue_ai(bot, trigger):
    availablecomsnum = spicebot.botai.dict['patterncounts']
    availablecomsfiles = spicebot.botai.dict['filecounts']
    displayval = "There are " + str(availablecomsnum) + " AI pattern matches available in " + str(availablecomsfiles) + " files."
    spicebot.startupmonologue.dict["ai"] = displayval
    spicebot.logs.log('SpiceBot_StartupMonologue', displayval)
    spicebot.events.trigger(bot, spicebot.events.BOT_STARTUPMONOLOGUE_AI, "SpiceBot_StartupMonologue")


@sopel.module.event(spicebot.events.BOT_READY)
@sopel.module.rule('.*')
def bot_startup_monologue_releasenotes(bot, trigger):
    newnotes = False
    for notefile in list(spicebot.releasenotes.notes.keys()):
        if len(spicebot.releasenotes.notes[notefile]["new"]):
            newnotes = True
    if newnotes:
        displayval = "Check Release Notes for News"
        spicebot.startupmonologue.dict["releasenotes"] = displayval
        spicebot.logs.log('SpiceBot_StartupMonologue', displayval)
    spicebot.events.trigger(bot, spicebot.events.BOT_STARTUPMONOLOGUE_RNOTES, "SpiceBot_StartupMonologue")


@sopel.module.event(spicebot.events.BOT_LOADED)
@sopel.module.rule('.*')
def bot_startup_monologue_display(bot, trigger):
    dispmsg = [" startup complete"]
    for messagekey in list(spicebot.startupmonologue.dict.keys()):
        dispmsg.append(spicebot.startupmonologue.dict[messagekey])
    if spicebot.events.dict["RPL_WELCOME_Count"] == 1:
        timesince = spicebot.humanized_time(time.time() - spicebot.events.BOT_UPTIME)
        if timesince == "just now":
            timesince = "1 second"
        dispmsg.append("Startup took " + timesince)
    # Announce to chan, then handle some closing stuff
    spicebot.logs.log('SpiceBot_StartupMonologue', bot.nick + " startup complete")
    bot.osd(dispmsg, list(bot.channels.keys()), 'ACTION')
    spicebot.events.trigger(bot, spicebot.events.BOT_STARTUPMONOLOGUE, "SpiceBot_StartupMonologue")
    spicebot.logs.log('SpiceBot_StartupMonologue', "Startup Monologue has been issued to all channels.", True)


@sopel.module.event(spicebot.events.BOT_STARTUPMONOLOGUE)
@sopel.module.rule('.*')
def bot_startup_monologue_errors(bot, trigger):

    debuglines = spicebot.logs.stdio_logs_fetch()

    searchphrasefound = []
    for line in debuglines:
        if str(line).endswith("failed to load") and not str(line).startswith("0"):
            searchphrasefound.append(line)

    if len(searchphrasefound):
        for foundphase in searchphrasefound:
            spicebot.logs.log('SpiceBot_Logs', str(foundphase))
        searchphrasefound.insert(0, "Notice to Bot Admins: ")
        searchphrasefound.append("Run the debug command for more information.")
        bot.osd(searchphrasefound, list(bot.channels.keys()))
    else:
        spicebot.logs.log('SpiceBot_Logs', "No issues found at bot startup!", True)

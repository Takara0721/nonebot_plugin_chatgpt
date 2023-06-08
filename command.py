from nonebot.adapters.onebot.v11 import MessageSegment
from .data import voiceJson
from .data import V_PATH
import random
import asyncio
import re
from pathlib import Path

# 检测命令并调用
async def useCommand(command, user_session, matcher):
    commandDict = {
        "help" : help,
        "refresh" : refresh,
        "clear" : clear,
        "reset character" : resetCharacter,
        "set character.*" : setCharacter,
        "雌小鬼语音包" : voicePackage
    }
    for key in commandDict.keys():
        findCommand = re.compile(key).findall(command)
        if len(findCommand) != 0 and findCommand[0] == command:
            return await commandDict[key](
                command = command,
                commandList = commandDict.keys(), 
                user_session = user_session, 
                matcher = matcher
            )
    return "未知指令，请输入#help查看全部指令"

# help指令
async def help(**kwargs):
    reply =  "目前机器人可使用指令如下：\n"
    for commandText in kwargs["commandList"]:
        reply += f"--#{commandText}\n"
    return reply

# refresh指令
async def refresh(**kwargs):
    kwargs["user_session"].refresh()
    return "会话已刷新"

# clear指令
async def clear(**kwargs):
    kwargs["user_session"].reset()
    return "会话已重置"

# reset character指令
async def resetCharacter(**kwargs):
    kwargs["user_session"].reset_preset()
    return "人格已重置"

# set character [内置人格/自定义] [自定义人格描述]命令
async def setCharacter(**kwargs):
    command = kwargs["command"]
    if len(command) == 12:
        args = ""
    else:
        args = command[13:].strip()
    return kwargs["user_session"].set_preset(args)

# 发送服务器内语音文件到qq内
async def voicePackage(**kwargs):
    voiceIfm = random.choice(voiceJson)
    voice = voiceIfm["o"]
    voiceText = voiceIfm["s"]
    voicePath = Path(f"{V_PATH}{voice}")
    await kwargs["matcher"].send(MessageSegment.record(file=voicePath))
    return voiceText

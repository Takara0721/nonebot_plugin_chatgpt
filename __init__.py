from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Message, MessageEvent, GroupMessageEvent, PrivateMessageEvent, MessageSegment
from nonebot.params import Arg, CommandArg, ArgPlainText, CommandArg, Matcher
from nonebot.log import logger
from .command import *
from .session import *
import re

# if chatgpt_image_render:
#     from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_htmlrender import md_to_pic

# 使用指令
commandChat = on_command("#", priority=10, block=True, rule=to_me())
@commandChat.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    session_id = event.get_session_id()
    msg = arg.extract_plain_text().strip()
    user_session = get_user_session(session_id)
    reply = await useCommand(msg, user_session, matcher)
    await matcher.finish(reply)


user_lock = {}

# 基本聊天
commonChat = on_command(priority=100, block=True, **matcher_params)
@commonChat.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    session_id = event.get_session_id()
    msg = arg.extract_plain_text().strip()

    if not msg:
        return

    if session_id in user_lock and user_lock[session_id]:
        await matcher.finish("消息太快啦～请稍后", at_sender=True)

    user_lock[session_id] = True
    try:
        await matcher.send("消息处理中...")
        resp = await get_user_session(session_id).get_chat_response(msg)

        re_formula = re.compile(r'\$.+?\$')
        formulas = re_formula.findall(resp)

        # 如果开启图片渲染，或返回内容含有Latex数学公式格式
        if chatgpt_image_render or len(formulas):
            if resp.count("```") % 2 != 0:
                resp += "\n```"
            img = await md_to_pic(resp)
            resp = MessageSegment.image(img)

        # 发送消息
        # 如果是私聊直接发送
        try:
            if isinstance(event, PrivateMessageEvent):
                await matcher.send(resp, at_sender=True)
            else:
                # 如果不是则以回复的形式发送
                message_id = event.message_id
                await matcher.send(MessageSegment.reply(message_id) + resp, at_sender=True)
        except:
            img = await md_to_pic(resp)
            resp = MessageSegment.image(img)
            await matcher.send("消息发送失败可能是被风控,本回复已转为图片模式" + resp, at_sender=True)
    except Exception as e:
        print(f"INFO:发生错误: {e}")
    finally:
        user_lock[session_id] = False
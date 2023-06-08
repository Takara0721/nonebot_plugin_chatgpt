import asyncio
from typing import Awaitable

import openai

def get_chat_response(key, msg):
    # openai.api_base = "https://api.chatanywhere.cn/v1"
    openai.api_key = key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=msg,
            stream=True,
        )
        res = {'role': '', 'content': ''}
        for event in response:
            if event['choices'][0]['finish_reason'] == 'stop':
                #print(f'收到的完成数据: {res}')
                break
            for delta_k, delta_v in event['choices'][0]['delta'].items():
                #print(f'流响应数据: {delta_k} = {delta_v}')
                res[delta_k] += delta_v
        #messages.append(completion)  # 直接在传入参数 messages 中追加消息

        return res, True
    except Exception as e:
        return f"发生错误: {e}", False
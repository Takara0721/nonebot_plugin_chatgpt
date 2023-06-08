import asyncio
from .config import *
from .openai import get_chat_response
from pathlib import Path
import json

characterList = {
    "默认":"你是一个名叫Alice并乐于助人的AI助手。",
    "猫娘":"你是一只可爱猫娘，名叫Alice，且有着每一句话最后都会带上喵~"
}

api_index = 0

class Session:
    def __init__(self, id):
        self.session_id = id
        self.preset = characterList["默认"]
        self.load_user_session()
    
    def fileOperate(self, mode: str, content: str):
        path = f'conversations/{self.session_id}.data'
        if (mode == 'r'):
            with open(path, 'r', encoding='utf-8') as f:
                chats = list(map(json.loads, f.read().split('\n')[:-1]))
                self.conversation = [{"role": "system", "content": self.preset}] + chats
        else:
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)


    # 重置会话
    def reset(self):
        self.conversation = [{"role": "system", "content": self.preset}]
        self.fileOperate('w', '')

    # 清空对话列表
    def refresh(self):
        self.conversation = [{"role": "system", "content": self.preset}]

    # 重置人格
    def reset_preset(self):
        self.preset = characterList["默认"]
        self.conversation[0]['content'] = self.preset

    # 设置人格
    def set_preset(self, msg: str):
        if msg in characterList.keys():
            self.preset = characterList[msg]
            self.conversation[0]['content'] = self.preset
            return "设置成功"
        elif msg.startswith("自定义"):
            if len(msg) == 3:
                return "自定义人格不可为空"
            self.preset = msg[3:].strip()
            if len(self.preset) == 0:
                return "自定义人格不可为空"
            self.conversation[0]['content'] = self.preset
            return "自定义人格设置成功"
        else:
            reply = "未知人格，目前已有人格如下：\n"
            for character in characterList:
                reply += f"--{character}\n"
            reply += "或使用自定义人格"
            return reply
            

    # 导入用户会话
    def load_user_session(self):
        if Path(f'conversations/{self.session_id}.data').exists():
            self.fileOperate('r', '')
        else:
            Path('conversations').mkdir(exist_ok=True)
            self.reset()

    # 导出用户会话
    def dump_user_session(self, msg: str):
        logger.debug("dump session")
        self.fileOperate('a', msg + '\n')
    
    # 处理用户对话
    def handleConversation(self, msg, res):
        self.dump_user_session(json.dumps({"role": "user", "content": msg}))

        self.conversation.append({"role": "assistant", "content": res['content']})
        self.dump_user_session(json.dumps({"role": "assistant", "content": res['content']}))
        print(f'{len(self.conversation)} | {self.conversation[-2:]}')
        return res['content']

    # 会话
    async def get_chat_response(self, msg) -> str:
        # if (len(self.conversation) >= 21):
        #     self.conversation = [self.conversation[0]] + self.conversation[len(self.conversation)-18:]
        self.conversation.append({"role": "user", "content": msg})


        global api_index
        api_index = (api_index + 1) % len(api_key_list)
        logger.debug(f"使用 API: {api_index}")
        res, ok = await asyncio.get_event_loop().run_in_executor(None, get_chat_response, api_key_list[api_index],
                                                                 self.conversation)

        if ok and res['content'] != '':
            return self.handleConversation(msg, res)
        else:
            if 'Please reduce the length of the messages.' in res or res['content'] == '':
                print(f"INFO:{res}")
                self.conversation = [self.conversation[0]] + self.conversation[-3:]
                res, ok = await asyncio.get_event_loop().run_in_executor(None, get_chat_response, api_key_list[api_index],
                                                                 self.conversation)
                if ok:
                    return self.handleConversation(msg, res)
                else:
                    self.conversation.pop()
                    return res
            else:
                self.conversation.pop()
                return res


user_session = {}

def get_user_session(user_id) -> Session:
    if user_id not in user_session:
        user_session[user_id] = Session(user_id)
    return user_session[user_id]
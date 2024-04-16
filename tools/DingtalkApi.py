import requests
import json

class Sender:
    def __init__(self):

        self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/dc3ef7c0-fc17-45ce-a2f7-c5b625df604a'
        #self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/9dcaa6a2-1561-41cf-a93f-d83b6850cf2d'
        self.__headers = {'Content-Type': 'application/json'}

    def send(self, text):
        payload_message = {"msg_type": "text", "content": {"text": text}}

        return requests.request("POST", self.url, headers=self.__headers, data=json.dumps(payload_message))
class Sender2:
    def __init__(self):

        self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/2c5ca051-9aad-4958-9b8c-a27a8e0bfa92'
        #self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/9dcaa6a2-1561-41cf-a93f-d83b6850cf2d'
        self.__headers = {'Content-Type': 'application/json'}

    def send(self, text):
        payload_message = {"msg_type": "text", "content": {"text": text}}

        return requests.request("POST", self.url, headers=self.__headers, data=json.dumps(payload_message))


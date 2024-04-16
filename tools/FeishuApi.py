import requests
import json

class Sender:
    def __init__(self):

        self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/22aa3ee1-f2f6-43b5-b9f1-76618b2d9c11'
        #self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/9dcaa6a2-1561-41cf-a93f-d83b6850cf2d'
        self.__headers = {'Content-Type': 'application/json'}

    def send(self, text):
        payload_message = {"msg_type": "text", "content": {"text": text}}

        return requests.request("POST", self.url, headers=self.__headers, data=json.dumps(payload_message))


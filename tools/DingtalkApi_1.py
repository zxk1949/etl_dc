import requests
import json

class Sender:
    def __init__(self):

        #self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/dc3ef7c0-fc17-45ce-a2f7-c5b625df604a'
        self.url = 'https://open.feishu.cn/open-apis/bot/v2/hook/12ec2e9a-611c-4fc8-8afc-d99ed04f2a3c'
        self.__headers = {'Content-Type': 'application/json'}

    def send(self, text):
        payload_message = {"msg_type": "text", "content": {"text": text}}

        return requests.request("POST", self.url, headers=self.__headers, data=json.dumps(payload_message))


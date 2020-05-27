import requests
import json


class QYWX(object):
    def __init__(self):
        self.qy_id = 'ww58d668fc292f65d4'
        self.secret = 'Op9sApq3g7YBr_sEXBwTX-G7YQO0c5SUnzIlGPHnF_I'
        self.token = ''

    def get_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + self.qy_id + '&corpsecret=' + self.secret
        token = json.loads(requests.get(url).text)
        self.token = token.get('access_token')

    def push_mes(self, content, user, toparty=""):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.token
        body = {
            "touser": user,
            "toparty": toparty,
            "totag": "",
            "msgtype": "text",
            "agentid": 1000053,
            "text": {
                "content": content
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        res = requests.post(url, json=body)
        res = json.loads(res.text)
        if res.get('errcode') == 0:
            return '发送成功'

    def upload_file(self, filename, filepath):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=' + self.token + '&type=file'
        payload = {'Content-Type': 'multipart/form-data;', 'filename': filename, 'filelength': '220'}
        files = [
            ('file', open(filepath, 'rb'))
        ]
        res = requests.post(url, headers={}, data=payload, files=files)
        res = json.loads(res.text)
        if res.get('errcode') == 0:
            media_id = json.loads(res.text).get('media_id')
            return media_id

    def push_file(self, media_id, user):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.token
        body = {
            "touser": user,
            "toparty": "",
            "totag": "",
            "msgtype": "file",
            "agentid": 1000002,
            "file": {
                "media_id": media_id
            },
            "safe": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        res = requests.post(url=url, json=body)
        res = json.loads(res.text)
        if res.get('errcode') == 0:
            return '发送成功'


# if __name__ == '__main__':


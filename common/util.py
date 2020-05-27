#  -*- coding:utf-8 -*-
# __author__ = 'hlm'
import datetime
import hashlib
import hmac
import random
import string
import requests
import time


def gen_random_string(str_len):
    random_char_list = []
    for _ in range(str_len):
        random_char = random.choice(string.ascii_letters + string.digits)
        random_char_list.append(random_char)
    random_string = ''.join(random_char_list)
    return random_string


def gen_sub_string(str_):
    str_len = len(str_)
    if str_len > 1:
        star_index = random.randint(0, str_len - 1)
        str_ = str_[0:star_index]
    return str_


def gen_random_int(min_num, max_num):
    return random.randint(min_num, max_num)


def get_sign(*args):
    content = ''.join(args).encode('ascii')
    SECRET_KEY = "DebugTalk"
    sign_key = SECRET_KEY.encode('ascii')
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign


def get_token(url, headers, data):
    response = requests.post(url=url, headers=headers, data=data, verify=False)
    if response.status_code == 500:
        response = requests.post(url=url, headers=headers, json=data, verify=False)
        token = response.json()["data"]["auth"]["access_token"]
    else:
        token = response.json()["access_token"]
    return "Bearer " + token


def get_timestamp():
    t = time.time()
    result = int(round(t * 1000))
    return result


def get_today_timestamp():
    t = int(time.mktime(datetime.date.today().timetuple()))
    result = int(round(t * 1000))
    return result


def get_tomorrow_timestamp():
    t = int(time.mktime(datetime.date.today().timetuple())) + 86400
    result = int(round(t * 1000))
    return result


def get_time():
    t = time.time()
    result = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.localtime(t))
    return result


def get_strftime():
    t = time.time()
    result = time.strftime('%Y.%m.%d %H:%M', time.localtime(t))
    return result


def get_date():
    t = time.time()
    result = time.strftime('%Y-%m-%d', time.localtime(t))
    return result


def change_int(str_id):
    if '.' in str_id:
        decimal = str_id.split('.')[1]
        int_id = str_id.split('.')[0]
        result = int_id + 1 if decimal > 5 else int_id
    else:
        result = int(str_id)
    return result


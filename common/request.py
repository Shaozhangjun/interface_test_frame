# -*- coding:utf-8 -*-
# __author__ = 'szj'
import requests
import json


class RequestInterface(object):
    def __response(self, response):
        dur_time = response.elapsed.total_seconds() * 1000  # 发送请求和响应到达时间，单位ms
        if response.text.startswith(('[', '{')):
            result = {'status': response.status_code, 'data': json.loads(response.text), 'dur_time': dur_time}
        else:
            result = {'status': response.status_code, 'data': response.text, 'dur_time': dur_time}
        return result

    def __http_get(self, url, timeout, header, param):
        """
        定义GET请求，参数在接口地址后，需要拼接
        :param url: 接口地址
        :param header: 请求头文件
        :param param: 接口请求参数
        :return: 字典结果
        """
        try:
            get_res = requests.get(url=url, headers=header, params=param, verify=False, timeout=timeout)
            get_result = self.__response(get_res)
        except Exception as error:
            get_result = {'synyi_test_frame_track': error.args[0]}
        return get_result

    def __http_post(self, url, timeout, header, param, body, post_type):
        """
        定义POST请求， 参数在body中
        :param url: 接口地址
        :param header: 请求头文件
        :param param: 接口请求参数
        :param body: 接口请求数据
        :return: 字典结果
        """
        try:
            if post_type == 0:
                post_res = requests.post(url=url, headers=header, params=param, data=body.encode(encoding='UTF-8'),
                                         verify=False, timeout=timeout)
            else:
                with open(body, 'rb') as f:
                    post_res = requests.post(url=url, headers=header, params=param, data=f, verify=False,
                                             timeout=timeout)
            post_result = self.__response(post_res)
        except Exception as error:
            post_result = {'synyi_test_frame_track': error.args[0]}
        return post_result

    def __http_put(self, url, timeout, header, param, body):
        """
        定义PUT请求， 参数在body中
        :param url: 接口地址
        :param header: 请求头文件
        :param param: 接口请求参数
        :param body: 接口请求数据
        :return: 字典结果
        """
        try:
            put_res = requests.put(url=url, headers=header, params=param, data=body.encode(encoding='UTF-8'),
                                   verify=False, timeout=timeout)
            put_result = self.__response(put_res)
        except Exception as error:
            put_result = {'synyi_test_frame_track': error.args[0]}
        return put_result

    def __http_del(self, url, timeout, header, param, body):
        """
        定义DELETE请求， 参数在body中
        :param url: 接口地址
        :param header: 请求头文件
        :param param: 接口请求参数
        :param body: 接口请求数据
        :return: 字典结果
        """
        try:
            del_res = requests.delete(url=url, headers=header, params=param, data=body.encode(encoding='UTF-8'),
                                   verify=False, timeout=timeout)
            del_result = self.__response(del_res)
        except Exception as error:
            del_result = {'synyi_test_frame_track': error.args[0]}
        return del_result

    def http_request(self, url, header, param, timeout, method, post_type, body):
        """
        统一处理HTTP请求
        :param post_type:
        :param method:
        :param url: 接口地址
        :param header: 请求头文件
        :param param: 接口请求参数
        :param body: post接口请求数据
        :param timeout: 超时设置
        :return: 字典结果
        """
        result = {'status': 500, 'data': "", 'dur_time': ""}
        if method.lower() == 'get':  # 判断接口请求类型是否为get
            # 调用__http_get()函数请求
            result = self.__http_get(url, timeout, header, param)
        elif method.lower() == 'post':
            # 调用__http_post()函数请求
            result = self.__http_post(url, timeout, header, param, body, post_type)
        elif method.lower() == 'put':
            # 调用__http_put()函数请求
            result = self.__http_put(url, timeout, header, param, body)
        elif method.lower() == 'delete':
            # 调用__http_del()函数请求
            result = self.__http_del(url, timeout, header, param, body)
        return result


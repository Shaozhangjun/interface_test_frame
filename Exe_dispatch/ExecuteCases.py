# -*- coding:utf-8 -*-
# __author__ = 'szj'
import json

from Exe_core.check import check_sort, set_key_value
from Exe_dispatch.ReadCases import ReadCaseInfo
from common.request import RequestInterface
from common.log import Logger
from Exe_core.compare import compare

sy_log = Logger(__name__)


class Execute(RequestInterface):

    def execute_case(self, path, *case_suites):
        """
        逐条执行用例
        :param path: 加载case的路径
        :param case_suites: 指定测试用例执行
        :return:
        """
        if case_suites:
            all_cases, inter_value, db_config, timeout = ReadCaseInfo(path).pretreated_case(case_suites[0])
        else:
            all_cases, inter_value, db_config, timeout = ReadCaseInfo(path).pretreated_case()
        sheet_result = []
        for index, sheet_cases in enumerate(all_cases):
            key_value = inter_value[index]['inter_value']
            response_list, test_result_list, result_data_list, res_code_list, res_time_list = [], [], [], [], []
            time_ = 0
            sheet_name = sheet_cases['sheet_name']
            sy_log.logger.info("------------------- 测试模块: %s -------------------" % sheet_name)
            # 遍历sheet 逐条执行case
            for case in sheet_cases['sheet_value']:
                test_result = 'fail'
                # check 参数
                case_id = case['case_id']
                sy_log.logger.info("测试用例ID-%s -- 开始测试:%s " % (case_id, case['case_name']))

                url = case['url']
                sy_log.logger.info("请求url:%s " % url)

                method = case['method']
                sy_log.logger.info("请求方式:%s " % method)

                header = check_sort(case['header'], key_value, path, db_config)
                if "synyi_test_frame_track" in header:
                    res_code_list.append('0')
                    response_list.append('0')
                    res_time_list.append('0')
                    result_data_list.append('参数依赖接口执行出错，此条用例失败')
                    test_result_list.append(test_result)
                    continue
                sy_log.logger.info("请求header:%s " % header)
                case['header'] = header
                if header:
                    header = json.loads(header)

                param = check_sort(case['param'], key_value, path, db_config)
                if "synyi_test_frame_track" in param:
                    res_code_list.append('0')
                    response_list.append('0')
                    res_time_list.append('0')
                    result_data_list.append('参数依赖接口执行出错，此条用例失败')
                    test_result_list.append(test_result)
                    continue
                sy_log.logger.info("请求param:%s " % param)
                case['param'] = param

                body = check_sort(case['body'], key_value, path, db_config)
                if "synyi_test_frame_track" in body:
                    res_code_list.append('0')
                    response_list.append('0')
                    res_time_list.append('0')
                    result_data_list.append('参数依赖接口执行出错，此条用例失败')
                    test_result_list.append(test_result)
                    continue
                sy_log.logger.info("请求body:%s " % body)
                case['body'] = body

                post_type = 1 if '$upfile{' in body else 0

                # 判断请求之前的操作
                if case['exe_before']:
                    exe_before = check_sort(case['exe_before'], key_value, path, db_config)
                    if "synyi_test_frame_track" in exe_before:
                        res_code_list.append('0')
                        response_list.append('0')
                        res_time_list.append('0')
                        result_data_list.append('参数依赖接口执行出错，此条用例失败')
                        test_result_list.append(test_result)
                        continue
                    sy_log.logger.info("执行请求前操作:%s " % exe_before)

                # 执行请求
                response = self.http_request(url, header, param, timeout, method, post_type, body)
                if "synyi_test_frame_track" in response:
                    res_code_list.append('0')
                    response_list.append('0')
                    res_time_list.append('0')
                    result_data_list.append(response['synyi_test_frame_track'])
                    test_result_list.append(test_result)
                    continue

                res_code_list.append(response['status'])
                sy_log.logger.info("返回状态码:%s " % response['status'])

                response_list.append(response['data'])
                sy_log.logger.info("返回结果:%s " % response['data'])

                res_time_list.append(response['dur_time'])

                if response['status'] == case['status_except']:
                    if 'inter_value' in case:
                        key_value = set_key_value(case['inter_value'], response['data'], key_value)
                    if case['check_before']:
                        check_before = check_sort(case['check_before'], key_value, path, db_config)
                        if "synyi_test_frame_track" in check_before:
                            result_data_list.append('参数依赖接口执行出错，此条用例失败')
                            test_result_list.append(test_result)
                            continue
                        sy_log.logger.info("执行校验前操作:%s " % check_before)
                    if response['data']:
                        if case['checks']:
                            result = compare(case['checks'], response['data'], key_value, db_config)
                        else:
                            result = {'result': True, 'result_data': '无断言不需校验'}

                    else:
                        result = {'result': True, 'result_data': '状态码校验正确，返回值为空'}

                    # 判断断言之后的操作
                    if case['check_after']:
                        check_after = check_sort(case['check_after'], key_value, path, db_config)
                        if isinstance(check_after, dir):
                            sy_log.logger.info("执行检验后操作失败")
                        sy_log.logger.info("执行校验后操作:%s " % check_after)
                    if result['result']:
                        time_ += 1
                        test_result = 'pass'
                    result_data_list.append(result['result_data'])
                else:
                    result_data_list.append("请求响应码不对，不进行断言匹配")
                sy_log.logger.info("测试结果:%s" % test_result)
                sy_log.logger.info("---------------------------------------------------------\n")
                test_result_list.append(test_result)

            result_value = {'res_code_list': res_code_list, 'res_time_list': res_time_list, 'time': time_,
                            'response_list': response_list, 'test_result_list': test_result_list,
                            'result_data_list': result_data_list}
            sheet_result.append({'sheet_name': sheet_name, 'result': result_value})
            sy_log.logger.info(
                "测试用例数:%d 通过:%d 失败:%d \n\n" % (len(sheet_cases['sheet_value']), time_, len(sheet_cases['sheet_value']) - time_))

        case_result = {'cases_list': all_cases, "sheet_result": sheet_result}
        return case_result


if __name__ == '__main__':
    a = {"2": 1, "1": 2}
    print(len(a))
